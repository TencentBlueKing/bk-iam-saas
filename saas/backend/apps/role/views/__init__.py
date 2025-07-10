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

from .group_member import (
    RoleGroupMemberCleanViewSet,
    RoleGroupMemberDepartmentGroupViewSet,
    RoleGroupMemberDepartmentTemplateGroupViewSet,
    RoleGroupMemberGroupViewSet,
    RoleGroupMemberResetViewSet,
    RoleGroupMemberTemplateGroupViewSet,
    RoleGroupMemberViewSet,
)
from .permission_audit import QueryAuthorizedSubjectsViewSet
from .role import (
    AuthScopeIncludeUserRoleView,
    GradeManagerViewSet,
    MemberSystemPermissionView,
    RoleAuthorizationScopeView,
    RoleCommonActionViewSet,
    RoleGroupConfigView,
    RoleGroupMembersRenewViewSet,
    RoleGroupRenewViewSet,
    RoleMemberView,
    RoleNotificationConfigView,
    RoleSearchViewSet,
    RoleSubjectScopCheckView,
    RoleSubjectScopeView,
    SubsetManagerViewSet,
    SuperManagerMemberViewSet,
    SystemManagerMemberView,
    SystemManagerViewSet,
    UserSubsetManagerViewSet,
    UserView,
)

__all__ = [
    "QueryAuthorizedSubjectsViewSet",
    "AuthScopeIncludeUserRoleView",
    "GradeManagerViewSet",
    "MemberSystemPermissionView",
    "RoleAuthorizationScopeView",
    "RoleCommonActionViewSet",
    "RoleGroupConfigView",
    "RoleNotificationConfigView",
    "RoleGroupMembersRenewViewSet",
    "RoleGroupRenewViewSet",
    "RoleMemberView",
    "RoleSearchViewSet",
    "RoleSubjectScopeView",
    "SuperManagerMemberViewSet",
    "SystemManagerMemberView",
    "SystemManagerViewSet",
    "UserView",
    "SubsetManagerViewSet",
    "UserSubsetManagerViewSet",
    "RoleSubjectScopCheckView",
    "RoleGroupMemberViewSet",
    "RoleGroupMemberTemplateGroupViewSet",
    "RoleGroupMemberDepartmentTemplateGroupViewSet",
    "RoleGroupMemberGroupViewSet",
    "RoleGroupMemberDepartmentGroupViewSet",
    "RoleGroupMemberCleanViewSet",
    "RoleGroupMemberResetViewSet",
]
