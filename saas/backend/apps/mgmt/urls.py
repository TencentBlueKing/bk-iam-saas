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
from django.urls import include, path

from backend.apps.mgmt import views

urlpatterns = [
    path(
        "white_list/",
        include(
            [
                path(
                    "apis/",
                    views.ApiViewSet.as_view({"get": "list"}),
                    name="mgmt.api",
                ),
                path(
                    "admin_apis/",
                    views.AdminApiWhiteListViewSet.as_view({"get": "list", "post": "create"}),
                    name="mgmt.admin_api.white_list",
                ),
                path(
                    "admin_apis/<int:id>/",
                    views.AdminApiWhiteListViewSet.as_view({"delete": "destroy"}),
                    name="mgmt.admin_api.delete_white_list",
                ),
                path(
                    "authorization_apis/",
                    views.AuthorizationApiWhiteListViewSet.as_view({"get": "list", "post": "create"}),
                    name="mgmt.authorization_api.white_list",
                ),
                path(
                    "authorization_apis/<int:id>/",
                    views.AuthorizationApiWhiteListViewSet.as_view({"delete": "destroy"}),
                    name="mgmt.authorization_api.delete_white_list",
                ),
                path(
                    "management_apis/",
                    views.ManagementApiWhiteListViewSet.as_view({"get": "list", "post": "create"}),
                    name="mgmt.management_api.white_list",
                ),
                path(
                    "management_apis/<int:id>/",
                    views.ManagementApiWhiteListViewSet.as_view({"delete": "destroy"}),
                    name="mgmt.management_api.delete_white_list",
                ),
            ]
        ),
    ),
    path(
        "long_task/",
        include(
            [
                path(
                    "",
                    views.LongTaskViewSet.as_view({"get": "list"}),
                    name="mgmt.long_task",
                ),
                path(
                    "<int:id>/",
                    views.LongTaskViewSet.as_view({"get": "retrieve", "post": "retry"}),
                    name="mgmt.long_task",
                ),
            ]
        ),
    ),
    path(
     "group/",
        include(
            [
                path("", views.GroupViewSet.as_view({"get": "list"}), name="mgmt.group"),
                path("transfer/", views.GroupTransferView.as_view(), name="mgmt.group.transfer"),
                # 用户组详情
                path(
                    "<str:id>/",
                    views.GroupViewSet.as_view({"get": "retrieve", "put": "update", "delete": "destroy"}),
                    name="mgmt.group.detail",
                ),
                path(
                    "<str:id>/members/",
                    views.GroupMemberViewSet.as_view({"get": "list", "post": "create", "delete": "destroy"}),
                    name="mgmt.group.members",
                ),
                path(
                    "<str:id>/members_renew/",
                    views.GroupMemberUpdateExpiredAtViewSet.as_view({"post": "create"}),
                    name="mgmt.group.members.renew",
                ),
                path("<str:id>/templates/", views.GroupTemplateViewSet.as_view({"get": "list"}),
                     name="mgmt.group.templates"),
                path(
                    "<str:id>/templates/<int:template_id>/",
                    views.GroupTemplateViewSet.as_view({"get": "retrieve"}),
                    name="mgmt.group.template_detail",
                ),
                # 用户组有权限的系统
                path("<str:id>/systems/",
                     views.GroupSystemViewSet.as_view({"get": "list"}),
                     name="mgmt.group.list_policy_system"),
                # 权限模板和自定义权限
                path(
                    "<str:id>/policies/",
                    views.GroupPolicyViewSet.as_view(
                        {"get": "list", "post": "create", "delete": "destroy", "put": "update"}),
                    name="mgmt.group.list_policy",
                ),

            ]
        )
    ),
    path(
        "role/",
        include(
            [
                path(
                    "subject_scope/",
                    views.RoleSubjectScopeView.as_view(),
                    name="mgmt.role.subject_scope"),
                path(
                    "authorization_scope_actions/",
                    views.RoleAuthorizationScopeView.as_view(),
                    name="mgmt.role.authorization_scope_actions",
                ),
            ]
        )
    ),
    path(
        "system/",
        include(
            [
                path(
                    "",
                    views.SystemViewSet.as_view({"get": "list"}),
                    name="mgmt.role.subject_scope"),
            ]
        )
    ),
    path(
        "action/",
        include(
            [
                path("", views.ActionViewSet.as_view({"get": "list"}), name="mgmt.action.list_action"),

            ]
        )
    ),
    path(
        "template/",
        include(
            [
                path("", views.TemplateViewSet.as_view({"get": "list"}), name="mgmt.action.list_action"),

            ]
        )
    )
]
