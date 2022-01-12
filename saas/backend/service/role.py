# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-权限中心(BlueKing-IAM) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import json
import logging
from typing import Any, List

from django.db import transaction
from django.utils.translation import gettext as _
from pydantic import BaseModel, Field, parse_obj_as

from backend.apps.role.models import (
    Role,
    RoleRelatedObject,
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

from .constants import (
    DEAULT_RESOURCE_GROUP_ID,
    RoleRelatedObjectType,
    RoleScopeType,
    RoleSourceTypeEnum,
    RoleType,
    SubjectType,
)
from .models import ResourceGroupList, Subject

logger = logging.getLogger("app")


class AuthScopeAction(BaseModel):
    id: str = Field(alias="action_id")
    resource_groups: ResourceGroupList

    def __init__(self, **data: Any):
        # NOTE 兼容 role, group授权信息的旧版结构
        if "resource_groups" not in data and "related_resource_types" in data:
            if not data["related_resource_types"]:
                data["resource_groups"] = []
            else:
                data["resource_groups"] = [
                    # NOTE: 固定resource_group_id方便删除逻辑
                    {
                        "id": DEAULT_RESOURCE_GROUP_ID,
                        "related_resource_types": data.pop("related_resource_types"),
                    }
                ]

        super().__init__(**data)

    class Config:
        allow_population_by_field_name = True  # 支持alias字段同时传 action_id 与 id


class AuthScopeSystem(BaseModel):
    system_id: str
    actions: List[AuthScopeAction]


class UserRole(BaseModel):
    id: int
    type: str
    name: str
    name_en: str
    description: str


class UserRoleMember(BaseModel):
    id: int
    type: str
    name: str
    members: list


class RoleInfo(BaseModel):
    code: str = ""
    name: str
    name_en: str = ""
    description: str
    type: str = RoleType.RATING_MANAGER.value

    members: List[str]
    subject_scopes: List[Subject] = []
    authorization_scopes: List[AuthScopeSystem] = []


class CommonAction(BaseModel):
    id: int = 0
    system_id: str
    name: str
    name_en: str = ""
    action_ids: List[str]


class RoleService:
    def list_subject_scope(self, role_id: int) -> List[Subject]:
        """查询role的subject授权范围"""
        role_scope = RoleScope.objects.filter(role_id=role_id, type=RoleScopeType.SUBJECT.value).first()
        if not role_scope:
            return []

        return parse_obj_as(List[Subject], json.loads(role_scope.content))

    def list_auth_scope(self, role_id: int) -> List[AuthScopeSystem]:
        """查询role的policy授权范围"""
        role_scope = RoleScope.objects.filter(role_id=role_id, type=RoleScopeType.AUTHORIZATION.value).first()
        if not role_scope:
            return []

        return parse_obj_as(List[AuthScopeSystem], json.loads(role_scope.content))

    def list_user_role(self, user_id: str) -> List[UserRole]:
        """查询用户的角色列表"""
        role_ids = RoleUser.objects.filter(username=user_id).values_list("role_id", flat=True)
        return self.list_by_ids(role_ids)

    def list_members_by_role_id(self, role_id: int):
        """查询指定角色的成员列表"""
        members = list(RoleUser.objects.filter(role_id=role_id).values_list("username", flat=True))
        return members

    def list_by_ids(self, role_ids: List[int]) -> List[UserRole]:
        roles = Role.objects.filter(id__in=role_ids)
        data = [
            UserRole(id=role.id, type=role.type, name=role.name, name_en=role.name_en, description=role.description)
            for role in roles
        ]

        # 按超级管理员 - 系统管理员 - 分级管理员排序
        sort_index = [RoleType.SUPER_MANAGER.value, RoleType.SYSTEM_MANAGER.value, RoleType.RATING_MANAGER.value]
        sorted_data = sorted(data, key=lambda r: sort_index.index(r.type))
        return sorted_data

    def create(self, info: RoleInfo, creator: str) -> Role:
        """创建Role"""
        with transaction.atomic():
            role = Role(
                code=info.code,
                name=info.name,
                name_en=info.name_en,
                description=info.description,
                type=info.type,
                creator=creator,
                updater=creator,
            )
            role.save(force_insert=True)

            self._add_members(role.id, info.members)
            self._create_role_scope(role.id, info.subject_scopes, info.authorization_scopes)

        return role

    def _add_members(self, role_id: int, usernames: List[str]):
        """Role增加成员"""
        role_users = [RoleUser(role_id=role_id, username=username) for username in usernames]
        if role_users:
            RoleUser.objects.bulk_create(role_users, batch_size=100)

    def _create_role_scope(self, role_id: int, subjects: List[Subject], systems: List[AuthScopeSystem]):
        """创建Role的授权范围"""
        # 1. 创建策略授权范围
        system_scope = RoleScope(
            role_id=role_id,
            type=RoleScopeType.AUTHORIZATION.value,
            content=json_dumps([system.dict() for system in systems]),
        )
        system_scope.save(force_insert=True)

        # 2. 创建授权对象的限制范围
        subject_scope = RoleScope(
            role_id=role_id,
            type=RoleScopeType.SUBJECT.value,
            content=json_dumps([subject.dict() for subject in subjects]),
        )
        subject_scope.save(force_insert=True)

        # 3. 创建授权对象限制范围的反查数据
        subjects = [
            ScopeSubject(
                role_scope_id=subject_scope.id, role_id=role_id, subject_type=subject.type, subject_id=subject.id
            )
            for subject in subjects
        ]

        if subjects:
            ScopeSubject.objects.bulk_create(subjects)

    def update(self, role: Role, info: RoleInfo, updater: str, partial=False):
        """更新Role"""
        with transaction.atomic():
            role.name = info.name
            role.name_en = info.name_en
            role.description = info.description
            role.updater = updater
            role.save()

            self._update_members(role, info.members)
            if not partial:
                self._update_role_scope(role.id, info.subject_scopes, info.authorization_scopes)

    def _update_members(self, role: Role, members: List[str], need_sync_backend_role: bool = False):
        """更新Role成员"""
        role_id = role.id
        new_members = sorted(set(members), key=members.index)  # 去重，但保持顺序不变
        old_members = list(RoleUser.objects.filter(role_id=role_id).values_list("username", flat=True))

        # 由于需要保持顺序不变，所以需要看是否变化了包括顺序，如果改变了则直接全删除，然后全添加
        if new_members != old_members:
            # 全删除
            RoleUser.objects.filter(role_id=role_id).delete()
            # 重新全部添加
            self._add_members(role_id, new_members)

        # 同步后端的role信息
        if need_sync_backend_role:
            # 需要新增的和删除的成员
            created_members = set(new_members) - set(old_members)
            deleted_members = set(old_members) - set(new_members)
            # 向IAM后台同步
            self._create_backend_role_member(role, list(created_members))
            self._delete_backend_role_member(role, list(deleted_members))

    def _create_backend_role_member(self, role: Role, created_members: List[str]):
        """创建后端role成员"""
        if created_members:
            iam.create_subject_role(
                [{"type": SubjectType.USER.value, "id": u} for u in created_members],
                role.type,
                role.code or "SUPER",
            )

    def _delete_backend_role_member(self, role: Role, deleted_members: List[str]):
        """删除后端role成员"""
        if deleted_members:
            iam.delete_subject_role(
                [{"type": SubjectType.USER.value, "id": u} for u in deleted_members],
                role.type,
                role.code or "SUPER",
            )

    def _update_role_scope(self, role_id: int, subjects: List[Subject], systems: List[AuthScopeSystem]):
        """更新Role的授权范围"""
        # 1. 修改系统操作的限制范围
        self.update_role_auth_scope(role_id, systems)

        # 2. 修改授权对象的限制范围
        self._update_role_subject_scope(role_id, subjects)

    def update_role_auth_scope(self, role_id: int, systems: List[AuthScopeSystem]):
        """更新Role可授权的权限范围"""
        RoleScope.objects.filter(role_id=role_id, type=RoleScopeType.AUTHORIZATION.value).update(
            content=json_dumps([system.dict() for system in systems])
        )

    def _update_role_subject_scope(self, role_id: int, subjects: List[Subject]):
        """更新Role可授权的人员范围"""
        # 1. 修改授权对象的限制范围
        RoleScope.objects.filter(role_id=role_id, type=RoleScopeType.SUBJECT.value).update(
            content=json_dumps([subject.dict() for subject in subjects])
        )

        # 2. 更新role subject scope 关系
        self._update_scope_subject(role_id, subjects)

    def _update_scope_subject(self, role_id: int, subjects: List[Subject]):
        """更新scope subject关系"""
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
                    role_scope_id=role_scope_id, role_id=role_id, subject_type=subject.type, subject_id=subject.id
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
            # DB数据更新
            RoleUserSystemPermission.update_global_enabled(role_id, need_sync_backend_role)
            # 向IAM后台同步更新，看enabled进行删除或增加操作
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
        # NOTE：被migration(role.0008_auto_20201230_1653)调用到了
        # 如果代码有调整，需要注意是否需要调整migration，避免出现循环依赖导致migrate失败
        # 目前依赖3张表：Role/RoleUser/RoleUserSystemPermission
        """
        role = Role.objects.get(type=RoleType.SUPER_MANAGER.value)
        # 判断是否已存在
        if username in role.members:
            return
        # 添加成员
        RoleUser.objects.create(role_id=role.id, username=username)

        # 未拥有所有系统的权限，则无需再操作
        if not need_sync_backend_role:
            return

        with transaction.atomic():
            # 1. DB记录，拥有所有系统的权限
            RoleUserSystemPermission.add_enabled_users(role.id, username)
            # 2. 向IAM后台同步更新
            self._create_backend_role_member(role, created_members=[username])

    def delete_super_manager_member(self, username: str):
        """删除超级管理员成员"""
        role = Role.objects.get(type=RoleType.SUPER_MANAGER.value)
        if username not in role.members:
            return
        # 删除成员
        RoleUser.objects.filter(role_id=role.id, username=username).delete()

        # 之前没有启用拥有所有系统权限，则无需操作
        if username not in role.system_permission_enabled_content.enabled_users:
            return

        with transaction.atomic():
            # 1. DB记录，删除对应权限
            RoleUserSystemPermission.delete_enabled_users(role.id, username)
            # 2. 向IAM后台同步更新
            self._delete_backend_role_member(role, deleted_members=[username])

    def update_super_manager_member_system_permission(self, username: str, need_sync_backend_role: bool):
        role = Role.objects.get(type=RoleType.SUPER_MANAGER.value)
        # 判断是否已存在
        if username not in role.members:
            return

        old_enabled = username in role.system_permission_enabled_content.enabled_users
        # 未变化，则无需修改
        if old_enabled == need_sync_backend_role:
            return

        with transaction.atomic():
            if need_sync_backend_role:
                # 1. DB记录，拥有所有系统的权限
                RoleUserSystemPermission.add_enabled_users(role.id, username)
                # 2. 向IAM后台同步更新
                self._create_backend_role_member(role, created_members=[username])
                return

            # 1. DB记录，删除对应权限
            RoleUserSystemPermission.delete_enabled_users(role.id, username)
            # 2. 向IAM后台同步更新
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
        exist_members = set(RoleUser.objects.filter(role_id=role_id).values_list("username", flat=True))
        members = [RoleUser(role_id=role_id, username=u) for u in usernames if u not in exist_members]
        if members:
            RoleUser.objects.bulk_create(members, batch_size=100)

    def get_role_by_group_id(self, group_id: int) -> Role:
        """通过用户组ID查询其对应的角色"""
        # 查询用户组的来源角色
        role_related_object = RoleRelatedObject.objects.get(
            object_type=RoleRelatedObjectType.GROUP.value, object_id=group_id
        )
        # 查询角色
        return Role.objects.get(id=role_related_object.role_id)

    def list_user_role_for_system(self, user_id: str, system_id: str) -> List[UserRole]:
        """
        获取用户的角色列表，且只能是某个系统通过API创建的
        """
        # 查询用户加入的所有角色
        all_roles = self.list_user_role(user_id)

        # 需要过滤出source_system_id通过API创建的
        role_ids = [r.id for r in all_roles]
        system_role_ids = set(
            RoleSource.objects.filter(
                source_system_id=system_id, source_type=RoleSourceTypeEnum.API.value, role_id__in=role_ids
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
        # 查询所有用户组的权限模板, 检查查询的模板是否关联了除了选中的用户组的其它用户组
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
                    _("权限模板 [{}] 关联了其它用户组, 请移除关系后再转移.").format("|".join(names)), True
                )

        # 转移用户组, 权限模板的角色归属
        with transaction.atomic():
            RoleRelatedObject.objects.filter(
                object_type=RoleRelatedObjectType.GROUP.value, object_id__in=group_ids
            ).update(role_id=role_id)

            if template_ids:
                RoleRelatedObject.objects.filter(
                    object_type=RoleRelatedObjectType.TEMPLATE.value, object_id__in=template_ids
                ).update(role_id=role_id)
