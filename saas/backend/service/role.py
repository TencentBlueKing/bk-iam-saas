# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云 - 权限中心 (BlueKing-IAM) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import json
from collections import defaultdict
from typing import Any, List, Optional, Tuple

from django.db import transaction
from django.utils.translation import gettext as _
from pydantic import BaseModel, Field, parse_obj_as

from backend.apps.group.models import Group
from backend.apps.role.models import (
    Role,
    RoleRelatedObject,
    RoleRelation,
    RoleScope,
    RoleSource,
    RoleUser,
    RoleUserSystemPermission,
    ScopeSubject,
)
from backend.apps.template.models import PermTemplate, PermTemplatePolicyAuthorized
from backend.common.error_codes import error_codes
from backend.component import iam
from backend.util.json import json_dumps
from backend.util.model import PartialModel

from .constants import (
    DEFAULT_RESOURCE_GROUP_ID,
    RoleRelatedObjectType,
    RoleScopeType,
    RoleSourceType,
    RoleType,
    SubjectType,
)
from .models import ResourceGroupList, Subject


class AuthScopeAction(BaseModel):
    id: str = Field(alias="action_id")
    resource_groups: ResourceGroupList

    def __init__(self, **data: Any):
        # NOTE 兼容 role, group 授权信息的旧版结构
        if "resource_groups" not in data and "related_resource_types" in data:
            if not data["related_resource_types"]:
                data["resource_groups"] = []
            else:
                data["resource_groups"] = [
                    # NOTE: 固定 resource_group_id 方便删除逻辑
                    {
                        "id": DEFAULT_RESOURCE_GROUP_ID,
                        "related_resource_types": data.pop("related_resource_types"),
                    }
                ]

        super().__init__(**data)

    class Config:
        allow_population_by_field_name = True  # 支持 alias 字段同时传 action_id 与 id


class AuthScopeSystem(BaseModel):
    system_id: str
    actions: List[AuthScopeAction]


class UserRole(BaseModel):
    id: int
    type: str
    name: str
    name_en: str
    description: str

    members: Optional[List[str]] = None

    @classmethod
    def convert_from_role(cls, role, members: Optional[List[str]] = None):
        return cls(
            id=role.id,
            type=role.type,
            name=role.name,
            name_en=role.name_en,
            description=role.description,
            members=members,
        )


class UserRoleMember(BaseModel):
    id: int
    type: str
    name: str
    members: list


class RoleMember(BaseModel):
    username: str


class RoleInfo(PartialModel):
    code: str = ""
    name: str
    name_en: str = ""
    description: str
    type: str = RoleType.GRADE_MANAGER.value
    inherit_subject_scope: bool = False
    sync_perm: bool = False
    sync_subject_template: bool = False

    members: List[RoleMember]
    subject_scopes: List[Subject] = []
    authorization_scopes: List[AuthScopeSystem] = []

    # NOTE: 只在 role 创建时有用
    source_system_id: str = ""
    hidden: bool = False

    @property
    def member_usernames(self):
        return [member.username for member in self.members]


class CommonAction(BaseModel):
    id: int = 0
    system_id: str
    name: str
    name_en: str = ""
    action_ids: List[str]


class RoleService:
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id

    def list_subject_scope(self, role_id: int) -> List[Subject]:
        """查询 role 的 subject 授权范围"""
        role_scope = RoleScope.objects.filter(role_id=role_id, type=RoleScopeType.SUBJECT.value).first()
        if not role_scope:
            return []

        return parse_obj_as(List[Subject], json.loads(role_scope.content))

    def list_auth_scope(self, role_id: int) -> List[AuthScopeSystem]:
        """查询 role 的 policy 授权范围"""
        role_scope = RoleScope.objects.filter(role_id=role_id, type=RoleScopeType.AUTHORIZATION.value).first()
        if not role_scope:
            return []

        return parse_obj_as(List[AuthScopeSystem], json.loads(role_scope.content))

    def list_user_role(self, user_id: str, with_permission: bool = False, with_hidden: bool = True) -> List[UserRole]:
        """查询用户的角色列表"""
        role_ids = list(RoleUser.objects.filter(username=user_id).values_list("role_id", flat=True))

        if not with_permission:
            return self.list_by_ids(role_ids, with_hidden=with_hidden)

        roles = Role.objects.exclude(type=RoleType.GRADE_MANAGER.value).filter(id__in=role_ids)
        role_dict = {role.id: role for role in roles}

        role_user_system_perms = RoleUserSystemPermission.objects.filter(role_id__in=role_dict.keys())
        roles_with_permission = []

        for role_user_system_perm in role_user_system_perms:
            if user_id in role_user_system_perm.enabled_users or role_user_system_perm.global_enabled:
                role = role_dict[role_user_system_perm.role_id]
                roles_with_permission.append(UserRole.convert_from_role(role))
        return roles_with_permission

    def list_paging_user_role(self, user_id: str, limit: int, offset: int) -> Tuple[int, List[UserRole]]:
        queryset = RoleUser.objects.filter(username=user_id)
        count = queryset.count()

        role_ids = list(queryset.values_list("role_id", flat=True)[offset : offset + limit])
        return count, self.list_by_ids(role_ids)

    def list_members_by_role_id(self, role_id: int) -> List[str]:
        """查询指定角色的成员列表"""
        return list(RoleUser.objects.filter(role_id=role_id).values_list("username", flat=True))

    def list_by_ids(self, role_ids: List[int], with_hidden: bool = True) -> List[UserRole]:
        roles = Role.objects.filter(id__in=role_ids)
        if not with_hidden:
            roles = roles.filter(hidden=False)

        # 填充 role 的成员
        ids = [role.id for role in roles]
        role_members = defaultdict(list)
        for role_user in RoleUser.objects.filter(role_id__in=ids).only("role_id", "username"):
            role_members[role_user.role_id].append(role_user.username)

        data = [UserRole.convert_from_role(role, role_members.get(role.id, None)) for role in roles]

        # 按超级管理员 - 系统管理员 - 分级管理员排序
        sort_index = [
            RoleType.SUPER_MANAGER.value,
            RoleType.SYSTEM_MANAGER.value,
            RoleType.GRADE_MANAGER.value,
            RoleType.SUBSET_MANAGER.value,
        ]
        return sorted(data, key=lambda r: sort_index.index(r.type))

    def create(self, info: RoleInfo, creator: str, add_member=True) -> Role:
        """创建 Role"""
        with transaction.atomic():
            role = Role(
                tenant_id=self.tenant_id,
                code=info.code,
                name=info.name,
                name_en=info.name_en,
                description=info.description,
                type=info.type,
                inherit_subject_scope=info.inherit_subject_scope,
                sync_perm=info.sync_perm,
                creator=creator,
                updater=creator,
                source_system_id=info.source_system_id,
                hidden=info.hidden,
            )
            role.save(force_insert=True)

            if add_member:
                self._add_members(role.id, info.member_usernames)

            self._create_role_scope(role.id, info.subject_scopes, info.authorization_scopes)

        return role

    def create_subset_manager(self, grade_manager: Role, info: RoleInfo, creator: str) -> Role:
        """
        创建子集管理员
        """
        with transaction.atomic():
            role = self.create(info, creator, add_member=True)
            RoleRelation.objects.create(tenant_id=self.tenant_id, parent_id=grade_manager.id, role_id=role.id)

        return role

    def _add_members(self, role_id: int, members: List[str]):
        """Role 增加成员"""
        role_users = [RoleUser(tenant_id=self.tenant_id, role_id=role_id, username=username) for username in members]
        if role_users:
            RoleUser.objects.bulk_create(role_users, batch_size=100)

    def _create_role_scope(self, role_id: int, subjects: List[Subject], systems: List[AuthScopeSystem]):
        """创建 Role 的授权范围"""
        # 1. 创建策略授权范围
        system_scope = RoleScope(
            tenant_id=self.tenant_id,
            role_id=role_id,
            type=RoleScopeType.AUTHORIZATION.value,
            content=json_dumps([system.dict() for system in systems]),
        )
        system_scope.save(force_insert=True)

        # 2. 创建授权对象的限制范围
        subject_scope = RoleScope(
            tenant_id=self.tenant_id,
            role_id=role_id,
            type=RoleScopeType.SUBJECT.value,
            content=json_dumps([subject.dict() for subject in subjects]),
        )
        subject_scope.save(force_insert=True)

        # 3. 创建授权对象限制范围的反查数据
        subjects = [
            ScopeSubject(
                tenant_id=self.tenant_id,
                role_scope_id=subject_scope.id,
                role_id=role_id,
                subject_type=subject.type,
                subject_id=subject.id,
            )
            for subject in subjects
        ]

        if subjects:
            ScopeSubject.objects.bulk_create(subjects)

    def update(self, role: Role, info: RoleInfo, updater: str):
        """更新 Role"""
        # 查询实际 RoleInfo 里哪些字段可用
        update_fields = info.get_partial_fields()

        with transaction.atomic():
            # 基本信息
            if "name" in update_fields:
                role.name = info.name
                role.name_en = info.name_en
            if "description" in update_fields:
                role.description = info.description
            if role.type == RoleType.SUBSET_MANAGER.value and "inherit_subject_scope" in update_fields:
                role.inherit_subject_scope = info.inherit_subject_scope
            if "sync_perm" in update_fields:
                role.sync_perm = info.sync_perm

            role.updater = updater
            role.save()

            # 分级管理员成员
            if "members" in update_fields:
                self._update_members(role, info.member_usernames)

            # 可授权的权限范围
            if "authorization_scopes" in update_fields:
                self.update_role_auth_scope(role.id, info.authorization_scopes)

            # 可授权的人员范围
            if "subject_scopes" in update_fields:
                self.update_role_subject_scope(role.id, info.subject_scopes)

    def _update_members(self, role: Role, members: List[str], need_sync_backend_role: bool = False):
        """
        更新 Role 成员

        NOTE: 只变更 readonly 为 False 的成员
        """
        role_id = role.id

        # 查询用户的已设置为 readonly 的成员
        readonly_usernames = set(
            RoleUser.objects.filter(role_id=role_id, readonly=True, tenant_id=self.tenant_id).values_list(
                "username", flat=True
            )
        )

        # NOTE readonly 的成员只能通过其它逻辑处理
        update_usernames = [username for username in members if username not in readonly_usernames]

        new_members = sorted(set(update_usernames), key=update_usernames.index)  # 去重，但保持顺序不变
        old_members = list(RoleUser.objects.filter(role_id=role_id, readonly=False).values_list("username", flat=True))

        # 由于需要保持顺序不变，所以需要看是否变化了包括顺序，如果改变了则直接全删除，然后全添加
        if new_members != old_members:
            # 全删除
            RoleUser.objects.filter(role_id=role_id, readonly=False, tenant_id=self.tenant_id).delete()
            # 重新全部添加
            self._add_members(role_id, new_members)

        # 同步后端的 role 信息
        if need_sync_backend_role:
            # 需要新增的和删除的成员
            created_members = set(new_members) - set(old_members)
            deleted_members = set(old_members) - set(new_members)
            # 向 IAM 后台同步
            self._create_backend_role_member(role, list(created_members))
            self._delete_backend_role_member(role, list(deleted_members))

    def _create_backend_role_member(self, role: Role, created_members: List[str]):
        """创建后端 role 成员"""
        if created_members:
            iam.create_subject_role(
                [{"type": SubjectType.USER.value, "id": u} for u in created_members],
                role.type,
                role.code or "SUPER",
            )

    def _delete_backend_role_member(self, role: Role, deleted_members: List[str]):
        """删除后端 role 成员"""
        if deleted_members:
            iam.delete_subject_role(
                [{"type": SubjectType.USER.value, "id": u} for u in deleted_members],
                role.type,
                role.code or "SUPER",
            )

    def update_role_auth_scope(self, role_id: int, systems: List[AuthScopeSystem]):
        """更新 Role 可授权的权限范围"""
        RoleScope.objects.filter(role_id=role_id, type=RoleScopeType.AUTHORIZATION.value).update(
            content=json_dumps([system.dict() for system in systems])
        )

    def update_role_subject_scope(self, role_id: int, subjects: List[Subject]):
        """更新 Role 可授权的人员范围"""
        # 1. 修改授权对象的限制范围
        RoleScope.objects.filter(role_id=role_id, type=RoleScopeType.SUBJECT.value).update(
            content=json_dumps([subject.dict() for subject in subjects])
        )

        # 2. 更新 role subject scope 关系
        self._update_scope_subject(role_id, subjects)

    def _update_scope_subject(self, role_id: int, subjects: List[Subject]):
        """更新 scope subject 关系"""
        role_scope = RoleScope.objects.filter(role_id=role_id, type=RoleScopeType.SUBJECT.value).only("id").first()
        role_scope_id = role_scope.id

        query = ScopeSubject.objects.filter(role_scope_id=role_scope_id, role_id=role_id)
        data_subjects = set(subjects)
        old_subjects = {Subject(type=s.subject_type, id=s.subject_id) for s in query}

        new_subjects = list(data_subjects - old_subjects)
        del_subjects = list(old_subjects - data_subjects)

        if new_subjects:
            subjects = [
                ScopeSubject(
                    tenant_id=self.tenant_id,
                    role_scope_id=role_scope_id,
                    role_id=role_id,
                    subject_type=subject.type,
                    subject_id=subject.id,
                )
                for subject in new_subjects
            ]
            ScopeSubject.objects.bulk_create(subjects, batch_size=100)

        del_departments, del_users = [], []
        for s in del_subjects:
            if s.type == SubjectType.DEPARTMENT.value:
                del_departments.append(s.id)
            elif s.type == SubjectType.USER.value:
                del_users.append(s.id)
            else:
                ScopeSubject.objects.filter(
                    role_scope_id=role_scope_id, role_id=role_id, subject_type=s.type, subject_id=s.id
                ).delete()

        if del_departments:
            ScopeSubject.objects.filter(
                role_scope_id=role_scope_id,
                role_id=role_id,
                subject_type=SubjectType.DEPARTMENT.value,
                subject_id__in=del_departments,
            ).delete()

        if del_users:
            ScopeSubject.objects.filter(
                role_scope_id=role_scope_id,
                role_id=role_id,
                subject_type=SubjectType.USER.value,
                subject_id__in=del_users,
            ).delete()

    def modify_system_manager_members(self, role_id: int, members: List[str]):
        """修改系统管理员的成员"""
        role = Role.objects.get(id=role_id)
        # 判断是否系统管理员
        if role.type != RoleType.SYSTEM_MANAGER.value:
            return

        self._update_members(
            role, members, need_sync_backend_role=role.system_permission_enabled_content.global_enabled
        )

    def modify_system_manager_member_system_permission(self, role_id: int, need_sync_backend_role: bool):
        """系统管理员的成员系统权限是否开启"""
        role = Role.objects.get(id=role_id)
        # 判断是否系统管理员
        if role.type != RoleType.SYSTEM_MANAGER.value:
            return

        global_enabled = role.system_permission_enabled_content.global_enabled
        # 没有修改则不需要更新
        if global_enabled == need_sync_backend_role:
            return

        with transaction.atomic():
            # DB 数据更新
            RoleUserSystemPermission.update_global_enabled(role_id, need_sync_backend_role, self.tenant_id)
            # 向 IAM 后台同步更新，看 enabled 进行删除或增加操作
            usernames = RoleUser.objects.filter(role_id=role_id).values_list("username", flat=True)
            if not usernames:
                return

            if need_sync_backend_role:
                self._create_backend_role_member(role, created_members=usernames)
                return

            self._delete_backend_role_member(role, deleted_members=usernames)

    def add_super_manager_member(self, username: str, need_sync_backend_role: bool):
        """
        添加超级管理员成员
        # NOTE：被 migration(role.0008_auto_20201230_1653) 调用到了
        # 如果代码有调整，需要注意是否需要调整 migration，避免出现循环依赖导致 migrate 失败
        # 目前依赖 3 张表：Role/RoleUser/RoleUserSystemPermission
        """
        role = Role.objects.get(type=RoleType.SUPER_MANAGER.value, tenant_id=self.tenant_id)
        # 判断是否已存在
        if username in role.members:
            return
        # 添加成员
        RoleUser.objects.create(tenant_id=self.tenant_id, role_id=role.id, username=username)

        # 未拥有所有系统的权限，则无需再操作
        if not need_sync_backend_role:
            return

        with transaction.atomic():
            # 1. DB 记录，拥有所有系统的权限
            RoleUserSystemPermission.add_enabled_users(role.id, username, self.tenant_id)
            # 2. 向 IAM 后台同步更新
            self._create_backend_role_member(role, created_members=[username])

    def delete_super_manager_member(self, username: str):
        """删除超级管理员成员"""
        role = Role.objects.get(type=RoleType.SUPER_MANAGER.value, tenant_id=self.tenant_id)
        if username not in role.members:
            return
        # 删除成员
        RoleUser.objects.filter(role_id=role.id, username=username).delete()

        # 之前没有启用拥有所有系统权限，则无需操作
        if username not in role.system_permission_enabled_content.enabled_users:
            return

        with transaction.atomic():
            # 1. DB 记录，删除对应权限
            RoleUserSystemPermission.delete_enabled_users(role.id, username, self.tenant_id)
            # 2. 向 IAM 后台同步更新
            self._delete_backend_role_member(role, deleted_members=[username])

    def update_super_manager_member_system_permission(self, username: str, need_sync_backend_role: bool):
        role = Role.objects.get(type=RoleType.SUPER_MANAGER.value, tenant_id=self.tenant_id)
        # 判断是否已存在
        if username not in role.members:
            return

        old_enabled = username in role.system_permission_enabled_content.enabled_users
        # 未变化，则无需修改
        if old_enabled == need_sync_backend_role:
            return

        with transaction.atomic():
            if need_sync_backend_role:
                # 1. DB 记录，拥有所有系统的权限
                RoleUserSystemPermission.add_enabled_users(role.id, username, self.tenant_id)
                # 2. 向 IAM 后台同步更新
                self._create_backend_role_member(role, created_members=[username])
                return

            # 1. DB 记录，删除对应权限
            RoleUserSystemPermission.delete_enabled_users(role.id, username, self.tenant_id)
            # 2. 向 IAM 后台同步更新
            self._delete_backend_role_member(role, deleted_members=[username])

    def delete_member(self, role_id: int, username: str):
        """
        角色删除成员
        """
        if Role.objects.filter(type=RoleType.SUPER_MANAGER.value, id=role_id).exists():
            self.delete_super_manager_member(username)
            return

        with transaction.atomic():
            if not RoleUser.objects.filter(role_id=role_id, username=username).delete()[0]:
                return

            role = Role.objects.get(id=role_id)
            if role.type == RoleType.SYSTEM_MANAGER.value and role.system_permission_enabled_content.global_enabled:
                self._delete_backend_role_member(role, deleted_members=[username])

    def add_grade_manager_members(self, role_id: int, usernames: List[str]):
        """
        批量添加分级管理员成员
        特别注意：不可用于超级管理员和系统管理员
        """
        # 先去除已经存在的
        exist_members = set(
            RoleUser.objects.filter(tenant_id=self.tenant_id, role_id=role_id).values_list("username", flat=True)
        )
        members = [
            RoleUser(tenant_id=self.tenant_id, role_id=role_id, username=u)
            for u in usernames
            if u not in exist_members
        ]
        if members:
            RoleUser.objects.bulk_create(members, batch_size=100)

    def get_role_by_group_id(self, group_id: int) -> Role:
        """通过用户组 ID 查询其对应的角色"""
        # 查询用户组的来源角色
        role_related_object = RoleRelatedObject.objects.get(
            object_type=RoleRelatedObjectType.GROUP.value, object_id=group_id
        )
        # 查询角色
        return Role.objects.get(id=role_related_object.role_id)

    def get_parent_id(self, role_id: int) -> int:
        """获取角色的父角色 ID"""
        relation = RoleRelation.objects.filter(role_id=role_id).first()
        if not relation:
            return 0

        return relation.parent_id

    def list_user_role_for_system(self, user_id: str, system_id: str) -> List[UserRole]:
        """
        获取用户的角色列表，且只能是某个系统通过 API 创建的
        """
        # 查询用户加入的所有角色
        all_roles = self.list_user_role(user_id)

        # 需要过滤出 source_system_id 通过 API 创建的
        role_ids = [r.id for r in all_roles]
        system_role_ids = set(
            RoleSource.objects.filter(
                source_system_id=system_id, source_type=RoleSourceType.API.value, role_id__in=role_ids
            ).values_list("role_id", flat=True)
        )

        return [r for r in all_roles if r.id in system_role_ids]

    def list_system_common_actions(self, system_id: str) -> List[CommonAction]:
        """
        查询后端默认的常用操作
        """
        try:
            data = iam.get_common_actions(system_id)
            return [
                CommonAction(
                    system_id=system_id,
                    name=ca["name"],
                    name_en=ca["name_en"],
                    action_ids=[a["id"] for a in ca["actions"]],
                )
                for ca in data
            ]
        except Exception:  # pylint: disable=broad-except
            pass

        return []

    def transfer_groups_role(self, group_ids: List[int], role_id: int):
        """
        转移用户组角色关系
        """
        # 排除只读用户组
        group_ids = list(Group.objects.filter(id__in=group_ids, readonly=False).values_list("id", flat=True))

        # 排除默认跟随角色权限的用户组
        group_ids = list(
            RoleRelatedObject.objects.filter(
                object_type=RoleRelatedObjectType.GROUP.value, object_id__in=group_ids, sync_perm=False
            ).values_list("object_id", flat=True)
        )

        # 查询所有用户组的权限模板，检查查询的模板是否关联了除了选中的用户组的其它用户组
        template_ids = list(
            PermTemplatePolicyAuthorized.objects.filter(
                subject_type=SubjectType.GROUP.value, subject_id__in=group_ids
            ).values_list("template_id", flat=True)
        )

        if template_ids:
            over_template_ids = list(
                PermTemplatePolicyAuthorized.objects.filter(
                    subject_type=SubjectType.GROUP.value, template_id__in=template_ids
                )
                .exclude(subject_id__in=group_ids)
                .values_list("template_id", flat=True)
            )

            if len(over_template_ids) != 0:
                # 存在权限模板关联了其它用户组的情况
                names = PermTemplate.objects.filter(id__in=over_template_ids).values_list("name", flat=True)
                raise error_codes.GROUP_TRANSFER_ERROR.format(
                    _("权限模板 [{}] 已被用户组关联，请解除关联后再转移。").format("|".join(names)), True
                )

        # 转移用户组，权限模板的角色归属
        with transaction.atomic():
            RoleRelatedObject.objects.filter(
                object_type=RoleRelatedObjectType.GROUP.value, object_id__in=group_ids
            ).update(role_id=role_id)

            if template_ids:
                RoleRelatedObject.objects.filter(
                    object_type=RoleRelatedObjectType.TEMPLATE.value, object_id__in=template_ids
                ).update(role_id=role_id)
