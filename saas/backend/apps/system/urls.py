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

from backend.apps.group.views import SystemGroupViewSet
from backend.apps.role.views.role import SystemGradeManagerViewSet

from . import views

urlpatterns = [
    path("", views.SystemViewSet.as_view({"get": "list"}), name="system.list_system"),
    # 获取指定系统的资源类别
    path(
        "resource_types/",
        views.ResourceTypeViewSet.as_view({"get": "list_resource_types"}),
        name="system.list_resource_types",
    ),
    # 蓝盾定制页面
    # 分级管理员列表
    path(
        "<str:system_id>/grade_managers/",
        SystemGradeManagerViewSet.as_view({"get": "list"}),
        name="system.list_system_role",
    ),
    # 用户组列表
    path(
        "<str:system_id>/grade_managers/<int:role_id>/groups/",
        SystemGroupViewSet.as_view({"get": "list"}),
        name="system.list_system_group",
    ),
    # 定制前端配置
    path(
        "<str:system_id>/custom_frontend_settings/",
        views.SystemCustomFrontendSettingsView.as_view(),
        name="system.custom_frontend_settings",
    ),
]
