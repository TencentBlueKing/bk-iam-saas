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

from . import views

urlpatterns = [
    path("", views.TemplateViewSet.as_view({"get": "list", "post": "create"}), name="template.template"),
    path(
        "<int:id>/",
        views.TemplateViewSet.as_view({"get": "retrieve", "delete": "destroy", "patch": "partial_update"}),
        name="template.detail",
    ),
    path(
        "<int:id>/members/",
        views.TemplateMemberViewSet.as_view({"get": "list", "delete": "destroy"}),
        name="template.members",
    ),
    # 权限模板更新 api
    path(
        "<int:id>/",
        include(
            [
                # 模板更新预提交
                path(
                    "pre_update/",
                    views.TemplatePreUpdateViewSet.as_view({"get": "list", "post": "create", "delete": "destroy"}),
                    name="template.pre_update",
                ),
                # 用户组同步预提交
                path(
                    "pre_group_sync/",
                    views.TemplatePreGroupSyncViewSet.as_view({"post": "create"}),
                    name="template.pre_group_sync",
                ),
                # 生成克隆的操作数据
                path(
                    "clone_action/",
                    views.TemplateGenerateCloneGroupPolicyViewSet.as_view({"post": "create"}),
                    name="template.clone_action",
                ),
                # 用户组预览
                path(
                    "groups_preview/",
                    views.TemplateGroupSyncPreviewViewSet.as_view({"get": "list"}),
                    name="template.groups_preview",
                ),
                # 模板更新提交
                path(
                    "update_commit/",
                    views.TemplateUpdateCommitViewSet.as_view({"post": "create"}),
                    name="template.update_commit",
                ),
                # 转换成自定义权限
                path(
                    "convert_to_custom_policy/",
                    views.TemplateConvertToCustomPolicyViewSet.as_view({"post": "create"}),
                    name="template.convert_to_custom_policy",
                ),
            ]
        ),
    ),
]
