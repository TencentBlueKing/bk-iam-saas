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

from backend.apps.role.models import Role
from backend.service.constants import ADMIN_USER

from .group import GroupBiz
from .role import RoleBiz


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
