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
    path("", views.GroupViewSet.as_view({"get": "list", "post": "create"}), name="group.group"),
    path(
        "members/",
        views.GroupsMemberViewSet.as_view({"post": "create"}),
        name="group.members",
    ),
    path("transfer/", views.GroupTransferView.as_view(), name="group.transfer"),
    path("search/", views.GroupSearchViewSet.as_view({"post": "search"}), name="group.search"),
    # 用户组详情
    path(
        "<str:id>/",
        views.GroupViewSet.as_view({"get": "retrieve", "put": "update", "delete": "destroy"}),
        name="group.detail",
    ),
    path(
        "<str:id>/members/",
        views.GroupMemberViewSet.as_view({"get": "list", "post": "create", "delete": "destroy"}),
        name="group.members",
    ),
    path(
        "<str:id>/members_renew/",
        views.GroupMemberUpdateExpiredAtViewSet.as_view({"post": "create"}),
        name="group.members.renew",
    ),
    path(
        "<str:id>/transfer/",
        views.GradeManagerGroupTransferView.as_view({"post": "post"}),
        name="group.grade_manager_transfer",
    ),
    # 用户组的模板
    path("<str:id>/templates/", views.GroupTemplateViewSet.as_view({"get": "list"}), name="group.templates"),
    path(
        "<str:id>/templates/<int:template_id>/",
        views.GroupTemplateViewSet.as_view({"get": "retrieve", "delete": "destroy"}),
        name="group.template_detail",
    ),
    # 用户组对应的角色的模板列表
    path(
        "<str:id>/role/templates/",
        views.GroupRoleTemplatesViewSet.as_view({"get": "list"}),
        name="group.role_templates",
    ),
    # 用户组有权限的系统
    path("<str:id>/systems/", views.GroupSystemViewSet.as_view({"get": "list"}), name="group.list_policy_system"),
    # 权限模板和自定义权限
    path(
        "<str:id>/policies/",
        views.GroupPolicyViewSet.as_view({"get": "list", "post": "create", "delete": "destroy", "put": "update"}),
        name="group.list_policy",
    ),
    path(
        "<str:id>/templates/<int:template_id>/condition_compare/",
        views.GroupTemplateConditionCompareView.as_view({"post": "create"}),
        name="group.template_condition_compare",
    ),
    path(
        "<str:id>/policies/condition_compare/",
        views.GroupCustomPolicyConditionCompareView.as_view({"post": "create"}),
        name="group.custom_policy_condition_compare",
    ),
]
