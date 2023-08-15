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
    path("groups/", views.UserGroupViewSet.as_view({"get": "list", "delete": "destroy"}), name="user.group"),
    path(
        "departments/-/groups/",
        views.UserDepartmentGroupViewSet.as_view({"get": "list"}),
        name="user.department.group",
    ),
    path("groups_expire_soon/", views.UserGroupRenewViewSet.as_view({"get": "list"}), name="user.group.renew"),
    path(
        "profile/newbie/",
        views.UserProfileNewbieViewSet.as_view({"get": "list", "post": "create"}),
        name="user.profile.newbie",
    ),
    path("common_actions/", views.UserCommonActionViewSet.as_view({"get": "list"}), name="user.common_action"),
    path("roles/", views.RoleViewSet.as_view({"get": "list"}), name="user.role"),
    path(
        "groups/search/",
        views.UserGroupSearchViewSet.as_view({"post": "search"}),
        name="user.group.search",
    ),
    path(
        "departments/-/groups/search/",
        views.UserDepartmentGroupSearchViewSet.as_view({"post": "search"}),
        name="user.department.group.search",
    ),
    path(
        "policies/search/",
        views.UserPolicySearchViewSet.as_view({"post": "search"}),
        name="user.policy.group.search",
    ),
]
