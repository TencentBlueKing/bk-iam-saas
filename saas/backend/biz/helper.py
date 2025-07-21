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

from typing import Any, Dict, List, Tuple

from django.db import transaction

from backend.apps.application.models import Application
from backend.apps.group.models import Group, GroupAuthorizeLock
from backend.apps.organization.models import Department, User
from backend.apps.role.models import (
    Role,
    RoleCommonAction,
    RoleRelatedObject,
    RoleRelation,
    RoleScope,
    RoleSource,
    RoleUser,
    RoleUserSystemPermission,
    ScopeSubject,
)
from backend.apps.subject_template.models import SubjectTemplate, SubjectTemplateGroup
from backend.apps.template.models import PermTemplatePolicyAuthorized
from backend.biz.policy import ExpiredPolicy, PolicyQueryBiz
from backend.biz.subject_template import SubjectTemplateBiz
from backend.common.error_codes import error_codes
from backend.common.time import expired_at_display
from backend.service.constants import (
    ADMIN_USER,
    ApplicationStatus,
    ApplicationType,
    GroupMemberType,
    RoleRelatedObjectType,
    RoleType,
    SubjectType,
)
from backend.service.models.subject import Subject

from .group import GroupBiz, SubjectGroupBean
from .role import RoleBiz
from .template import TemplateBiz


class RoleWithPermGroupBiz:
    """
    角色同步权限用户组操作
    """

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.role_biz = RoleBiz(self.tenant_id)
        self.group_biz = GroupBiz(self.tenant_id)

    def delete_role_member(self, role: Role, username: str, operator: str = ADMIN_USER):
        """
        删除成员，同时删除相关的权限
        """
        self.role_biz.delete_member(role.id, username)

        if role.sync_perm:
            self.group_biz.update_sync_perm_group_by_role(role, operator, sync_members=True)

    def batch_add_grade_manager_member(self, role: Role, usernames: List[str], operator: str = ADMIN_USER):
        """
        批量增加分级管理员成员
        """
        # 批量添加成员 (添加时去重)
        self.role_biz.add_grade_manager_members(role.id, usernames)

        # 同步权限用户组成员
        if role.sync_perm:
            self.group_biz.update_sync_perm_group_by_role(role, operator, sync_members=True)

    def batch_delete_grade_manager_member(self, role: Role, usernames: List[str], operator: str = ADMIN_USER):
        """
        批量删除分级管理员成员
        """
        self.role_biz.delete_grade_manager_member(role.id, usernames)

        # 同步权限用户组成员
        if role.sync_perm:
            self.group_biz.update_sync_perm_group_by_role(role, operator, sync_members=True)


class RoleDeleteHelper:
    """
    角色删除操作 (只能操作分级管理员/子集管理员)

    1. 删除分级管理员创建的所有用户组
    2. 删除分级管理员创建的权限模板
    3. 删除分级管理员创建的通用操作
    4. 删除分级管理员的系统权限
    5. 删除分级管理员的授权范围数据
    6. 删除分级管理员的所有成员
    7. 删除分级管理员的 role_source
    8. 删除分级管理员的人员模版
    """

    def __init__(self, role_id: int) -> None:
        # 1. 校验是否为分级管理员/子集管理员
        role = Role.objects.filter(
            id=role_id, type__in=[RoleType.GRADE_MANAGER.value, RoleType.SUBSET_MANAGER.value]
        ).first()
        if not role:
            raise error_codes.NOT_FOUND_ERROR.format(f"role[{role_id}] not exists")

        self._role = role
        self.tenant_id = role.tenant_id
        self.role_biz = RoleBiz(self.tenant_id)
        self.group_biz = GroupBiz(self.tenant_id)
        self.template_biz = TemplateBiz(self.tenant_id)
        self.subject_template_biz = SubjectTemplateBiz(self.tenant_id)

    def delete(self):
        """
        删除 role
        """
        if self._role.type == RoleType.GRADE_MANAGER.value:
            self._delete_subset_manager()

        self._delete_role_group()
        self._delete_role_subject_template()
        self._delete_role_template()
        self._delete_role()

    def _delete_role_group(self):
        """
        删除角色创建的用户组
        """
        group_ids = list(
            RoleRelatedObject.objects.filter(
                role_id=self._role.id, object_type=RoleRelatedObjectType.GROUP.value
            ).values_list("object_id", flat=True)
        )

        for group_id in group_ids:
            GroupAuthorizeLock.objects.filter(group_id=group_id).delete()
            self.group_biz.delete(group_id)

    def _delete_role_subject_template(self):
        """
        删除角色创建的用户组
        """
        template_ids = list(
            RoleRelatedObject.objects.filter(
                role_id=self._role.id, object_type=RoleRelatedObjectType.SUBJECT_TEMPLATE.value
            ).values_list("object_id", flat=True)
        )

        for template_id in template_ids:
            self.subject_template_biz.delete(template_id)

    def _delete_role_template(self):
        """
        删除角色创建的权限模板
        """
        template_ids = list(
            RoleRelatedObject.objects.filter(
                role_id=self._role.id, object_type=RoleRelatedObjectType.TEMPLATE.value
            ).values_list("object_id", flat=True)
        )

        for template_id in template_ids:
            PermTemplatePolicyAuthorized.objects.filter(template_id=template_id).delete()
            self.template_biz.delete(template_id)

    def _delete_subset_manager(self):
        """
        删除分级管理员的子集管理员
        """
        role_ids = list(RoleRelation.objects.filter(parent_id=self._role.id).values_list("role_id", flat=True))

        for role_id in role_ids:
            RoleDeleteHelper(role_id).delete()

    def _delete_role(self):
        """
        删除角色创建的其它资源

        删除分级管理员创建的通用操作
        删除分级管理员的系统权限
        删除分级管理员的授权范围数据
        删除分级管理员的所有成员
        删除分级管理员的 role_source
        """
        with transaction.atomic():
            RoleCommonAction.objects.filter(role_id=self._role.id).delete()
            RoleUserSystemPermission.objects.filter(role_id=self._role.id).delete()
            RoleScope.objects.filter(role_id=self._role.id).delete()
            ScopeSubject.objects.filter(role_id=self._role.id).delete()
            RoleUser.objects.filter(role_id=self._role.id).delete()
            RoleSource.objects.filter(role_id=self._role.id).delete()
            Role.objects.filter(id=self._role.id).delete()

            if self._role.type == RoleType.SUBSET_MANAGER.value:
                RoleRelation.objects.filter(role_id=self._role.id).delete()


def get_role_expired_group_members(role: Role, expired_at_before: int, expired_at_after: int) -> List[Dict[str, Any]]:  # noqa: C901, PLR0912
    """
    获取角色已过期或即将过期的用户组成员
    """
    group_biz = GroupBiz(role.tenant_id)

    group_members: List[Dict[str, Any]] = []

    group_ids = list(
        RoleRelatedObject.objects.filter(role_id=role.id, object_type=RoleRelatedObjectType.GROUP.value).values_list(
            "object_id", flat=True
        )
    )
    if not group_ids:
        return group_members

    # 需要查询用户组已过期的成员
    group_subjects = group_biz.list_group_subject_before_expired_at_by_ids(group_ids, expired_at_before)
    for gs in group_subjects:
        # role 只通知部门相关的权限续期
        if gs.subject.type == SubjectType.USER.value:
            continue

        # 判断过期时间是否在区间内
        if gs.expired_at < expired_at_after:
            continue

        group_members.append(
            {
                "id": int(gs.group.id),
                "name": "",
                "subject_type": gs.subject.type,
                "subject_id": gs.subject.id,
                "subject_name": "",
                "expired_at": gs.expired_at,
                "expired_at_display": expired_at_display(gs.expired_at),
            }
        )

    # 填充部门名称
    department_ids = [int(m["subject_id"]) for m in group_members if m["subject_type"] == SubjectType.DEPARTMENT.value]
    if department_ids:
        qs = Department.objects.filter(id__in=department_ids).only("id", "name")
        department_name_map = {d.id: d.name for d in qs}

        for m in group_members:
            if m["subject_type"] == SubjectType.DEPARTMENT.value:
                m["subject_name"] = department_name_map.get(int(m["subject_id"]), "")

    # 查询有人员模版过期的用户组
    qs = SubjectTemplateGroup.objects.filter(
        expired_at__range=(expired_at_after, expired_at_before), group_id__in=group_ids
    )
    for s in qs:
        group_members.append(
            {
                "id": s.group_id,
                "name": "",
                "subject_type": GroupMemberType.TEMPLATE.value,
                "subject_id": str(s.template_id),
                "subject_name": "",
                "expired_at": s.expired_at,
                "expired_at_display": expired_at_display(s.expired_at),
            }
        )

    # 填充人员模版名称
    template_ids = [int(m["subject_id"]) for m in group_members if m["subject_type"] == GroupMemberType.TEMPLATE.value]
    if template_ids:
        qs = SubjectTemplate.objects.filter(id__in=template_ids).only("id", "name")
        template_name_map = {d.id: d.name for d in qs}

        for m in group_members:
            if m["subject_type"] == GroupMemberType.TEMPLATE.value:
                m["subject_name"] = template_name_map.get(int(m["subject_id"]), "")

    if not group_members:
        return group_members

    # 填充用户组名称
    groups = Group.objects.filter(id__in=[gm["id"] for gm in group_members]).only("id", "name")
    group_name_map = {g.id: g.name for g in groups}

    for m in group_members:
        m["name"] = group_name_map.get(int(m["id"]), "")

    group_members.sort(key=lambda x: (x["id"], x["subject_type"], x["subject_id"]))

    return group_members


def get_user_expired_groups_policies(
    user: User, expired_at_before: int, expired_at_after: int
) -> Tuple[List[SubjectGroupBean], List[ExpiredPolicy]]:
    """
    获取用户已过期或即将过期的用户组与权限策略
    """
    tenant_id = user.tenant_id

    group_biz = GroupBiz(tenant_id)
    policy_biz = PolicyQueryBiz(tenant_id)

    username = user.username
    subject = Subject.from_username(username)

    # 注意：rbac 用户所属组很大，这里会变成多次查询，也变成多次 db io (单次 1000 个)
    groups = [
        group
        for group in group_biz.list_all_subject_group_before_expired_at(subject, expired_at_before)
        if group.expired_at > expired_at_after
    ]

    policies = policy_biz.list_expired(subject, expired_at_before)
    policies = [p for p in policies if p.expired_at > expired_at_after]

    if not groups and not policies:
        return groups, policies

    # 查询当前用户未处理的续期单，如果已经有相关数据，过滤掉
    for application in Application.objects.filter(
        applicant=username,
        type__in=[ApplicationType.RENEW_ACTION.value, ApplicationType.RENEW_GROUP.value],
        status=ApplicationStatus.PENDING.value,
    ):
        data = application.data
        if application.type == ApplicationType.RENEW_ACTION.value:
            action_set = {
                (data["system"]["id"], action.get("id", action.get("action_id"))) for action in data["actions"]
            }
            policies = [p for p in policies if (p.system.id, p.action.id) not in action_set]

        elif application.type == ApplicationType.RENEW_GROUP.value:
            group_id_set = {group["id"] for group in data["groups"]}
            groups = [g for g in groups if g.id not in group_id_set]

    return groups, policies
