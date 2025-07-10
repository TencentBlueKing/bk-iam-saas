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
        views.ManagementGradeManagerViewSet.as_view({"get": "list", "post": "create"}),
        name="open.management.v1.grade_manager",
    ),
    path(
        "grade_managers/<int:id>/",
        views.ManagementGradeManagerViewSet.as_view({"put": "update"}),
        name="open.management.v1.grade_manager",
    ),
    # 分级管理员成员
    path(
        "grade_managers/<int:id>/members/",
        views.ManagementGradeManagerMemberViewSet.as_view({"get": "list", "post": "create", "delete": "destroy"}),
        name="open.management.v1.grade_manager_member",
    ),
    # 用户组
    path(
        "grade_managers/<int:id>/groups/",
        views.ManagementGradeManagerGroupViewSet.as_view({"get": "list", "post": "create"}),
        name="open.management.v1.grade_manager_group",
    ),
    path(
        "groups/<int:id>/",
        views.ManagementGroupViewSet.as_view({"put": "update", "delete": "destroy"}),
        name="open.management.v1.group",
    ),
    # 用户组成员
    path(
        "groups/<int:id>/members/",
        views.ManagementGroupMemberViewSet.as_view({"get": "list", "post": "create", "delete": "destroy"}),
        name="open.management.v1.group_member",
    ),
    # 用户组自定义权限
    path(
        "groups/<int:id>/policies/",
        views.ManagementGroupPolicyViewSet.as_view({"post": "create", "delete": "destroy"}),
        name="open.management.v1.group_policy",
    ),
    # 用户组自定义权限 - 操作级别的变更，不涉及Resources
    path(
        "groups/<int:id>/actions/policies/",
        views.ManagementGroupActionPolicyViewSet.as_view({"delete": "destroy"}),
        name="open.management.v1.group_action",
    ),
    # 用户
    path(
        "users/grade_managers/",
        views.ManagementUserGradeManagerViewSet.as_view({"get": "list"}),
        name="open.management.v1.user_grade_manager",
    ),
    path(
        "users/grade_managers/<int:id>/groups/",
        views.ManagementUserGradeManagerGroupViewSet.as_view({"get": "list"}),
        name="open.management.v1.user_grade_manager_group",
    ),
    # 用户组申请单
    path(
        "groups/applications/",
        views.ManagementGroupApplicationViewSet.as_view({"post": "create"}),
        name="open.management.v1.group_application",
    ),
]
