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
from typing import List

from django.db import transaction

from backend.apps.group.models import GroupAuthorizeLock
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
from backend.apps.template.models import PermTemplatePolicyAuthorized
from backend.biz.subject_template import SubjectTemplateBiz
from backend.common.error_codes import error_codes
from backend.service.constants import ADMIN_USER, RoleRelatedObjectType, RoleType

from .group import GroupBiz
from .role import RoleBiz
from .template import TemplateBiz


class RoleWithPermGroupBiz:
    """
    角色同步权限用户组操作
    """

    role_biz = RoleBiz()
    group_biz = GroupBiz()

    def delete_role_member(self, role: Role, username: str, operator: str = ADMIN_USER):
        """
        删除成员, 同时删除相关的权限
        """
        self.role_biz.delete_member(role.id, username)

        if role.sync_perm:
            self.group_biz.update_sync_perm_group_by_role(role, operator, sync_members=True)

    def batch_add_grade_manager_member(self, role: Role, usernames: List[str], operator: str = ADMIN_USER):
        """
        批量增加分级管理员成员
        """
        # 批量添加成员(添加时去重)
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
    角色删除操作(只能操作分级管理员/子集管理员)

    1. 删除分级管理员创建的所有用户组
    2. 删除分级管理员创建的权限模板
    3. 删除分级管理员创建的通用操作
    4. 删除分级管理员的系统权限
    5. 删除分级管理员的授权范围数据
    6. 删除分级管理员的所有成员
    7. 删除分级管理员的role_source
    8. 删除分级管理员的人员模版
    """

    role_biz = RoleBiz()
    group_biz = GroupBiz()
    template_biz = TemplateBiz()
    subject_template_biz = SubjectTemplateBiz()

    def __init__(self, role_id: int) -> None:
        # 1. 校验是否为分级管理员/子集管理员
        role = Role.objects.filter(
            id=role_id, type__in=[RoleType.GRADE_MANAGER.value, RoleType.SUBSET_MANAGER.value]
        ).first()
        if not role:
            raise error_codes.NOT_FOUND_ERROR.format(f"role[{role_id}] not exists")

        self._role = role

    def delete(self):
        """
        删除role
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
        删除分级管理员的role_source
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
