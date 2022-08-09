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
        "templates/",
        include(
            [
                path(
                    "",
                    views.MgmtTemplateViewSet.as_view({"get": "list"}),
                    name="mgmt.template.template",
                ),
                path(
                    "<int:id>/",
                    views.MgmtTemplateViewSet.as_view({"get": "retrieve", "delete": "destroy", "patch": "partial_update"}),
                    name="mgmt.template.detail",
                ),
                path(
                    "<int:id>/members/",
                    views.MgmtTemplateMemberViewSet.as_view({"get": "list"}),
                    name="mgmt.template.members",
                ),
                # 权限模板更新 api
                path(
                    "<int:id>/",
                    include(
                        [
                            # 模板更新预提交
                            path(
                                "pre_update/",
                                views.MgmtTemplatePreUpdateViewSet.as_view({"get": "list", "post": "create", "delete": "destroy"}),
                                name="mgmt.template.pre_update",
                            ),
                            # 用户组同步预提交
                            path(
                                "pre_group_sync/",
                                views.MgmtTemplatePreGroupSyncViewSet.as_view({"post": "create"}),
                                name="mgmt.template.pre_group_sync",
                            ),
                            # 用户组预览
                            path(
                                "groups_preview/",
                                views.MgmtTemplateGroupSyncPreviewViewSet.as_view({"get": "list"}),
                                name="mgmt.template.groups_preview",
                            ),
                            # 模板更新提交
                            path(
                                "update_commit/",
                                views.MgmtTemplateUpdateCommitViewSet.as_view({"post": "create"}),
                                name="mgmt.template.update_commit",
                            ),

                        ]
                    )
                )
            ]
        )
    )
]
