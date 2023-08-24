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
from django.urls import path

from . import views

urlpatterns = [
    # 分级管理员
    path(
        "grade_managers/",
        views.GradeManagerViewSet.as_view({"get": "list", "post": "create"}),
        name="role.grade_manager",
    ),
    path(
        "grade_managers/<int:id>/",
        views.GradeManagerViewSet.as_view({"get": "retrieve", "put": "update", "patch": "partial_update"}),
        name="role.grade_manager_detail",
    ),
    path(
        "authorization_scope_actions/",
        views.RoleAuthorizationScopeView.as_view(),
        name="role.authorization_scope_actions",
    ),
    path("subject_scope/", views.RoleSubjectScopeView.as_view(), name="role.subject_scope"),
    path("<int:id>/members/", views.RoleMemberView.as_view(), name="role.member"),
    # 系统管理员
    path("system_manager/", views.SystemManagerViewSet.as_view({"get": "list"}), name="role.system_manager"),
    path(
        "system_manager/<int:id>/member_system_permissions/",
        views.MemberSystemPermissionView.as_view(),
        name="role.system_manager_member_system_permissions",
    ),
    path(
        "system_manager/<int:id>/members/", views.SystemManagerMemberView.as_view(), name="role.system_manager_member"
    ),
    # 超级管理员
    path(
        "super_manager/members/",
        views.SuperManagerMemberViewSet.as_view(
            {"get": "list", "post": "create", "delete": "destroy", "put": "update"}
        ),
        name="role.super_manager_member",
    ),
    # 通用操作
    path(
        "common_actions/",
        views.RoleCommonActionViewSet.as_view({"get": "list", "post": "create"}),
        name="role.common_action",
    ),
    path(
        "common_actions/<int:id>/",
        views.RoleCommonActionViewSet.as_view({"delete": "destroy"}),
        name="role.delete_common_action",
    ),
    path("users/query/", views.UserView.as_view(), name="role.user_query"),
    path(
        "groups_renew/",
        views.RoleGroupRenewViewSet.as_view({"get": "list", "post": "create"}),
        name="role.groups_renew",
    ),
    path(
        "groups_renew/<int:id>/members/",
        views.RoleGroupMembersRenewViewSet.as_view({"get": "list"}),
        name="role.group_members_renew",
    ),
    path(
        "auth_scope_include_user_roles/",
        views.AuthScopeIncludeUserRoleView.as_view(),
        name="role.auth_scope_include_user_roles",
    ),
    path(
        "query_authorized_subjects/",
        views.QueryAuthorizedSubjectsViewSet.as_view({"post": "post"}),
        name="role.query_authorized_subjects",
    ),
    path(
        "query_authorized_subjects/export/",
        views.QueryAuthorizedSubjectsViewSet.as_view({"post": "export"}),
        name="role.query_authorized_subjects.export",
    ),
    # 子集管理员
    path(
        "subset_managers/",
        views.SubsetManagerViewSet.as_view({"get": "list", "post": "create"}),
        name="role.subset_manager",
    ),
    path(
        "subset_managers/<int:id>/",
        views.SubsetManagerViewSet.as_view({"get": "retrieve", "put": "update", "patch": "partial_update"}),
        name="role.subset_manager_detail",
    ),
    path(
        "grade_managers/<int:id>/subset_managers/",
        views.UserSubsetManagerViewSet.as_view({"get": "list"}),
        name="role.user_subset_manager",
    ),
    path("subject_scope_check/", views.RoleSubjectScopCheckView.as_view(), name="role.subject_scope_check"),
    path("search/", views.RoleSearchViewSet.as_view({"get": "list"}), name="role.role_search"),
    path("group_config/", views.RoleGroupConfigView.as_view(), name="role.group_config"),
]
