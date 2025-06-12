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

from backend.apps.application.views import ApplicationApprovalView

from . import views

urlpatterns = [
    # 兼容老数据：回调接口
    path("approve/<str:callback_id>/", ApplicationApprovalView.as_view(), name="application.approve"),
    # 审批流程
    path("processes/", views.ApprovalProcessViewSet.as_view({"get": "list"}), name="approval.approval_process"),
    # 自定义权限审批流程
    path(
        "processes/actions/",
        views.ActionApprovalProcessViewSet.as_view({"get": "list", "post": "create"}),
        name="approval.action_approval_process",
    ),
    # 加入用户组审批流程
    path(
        "processes/groups/",
        views.GroupApprovalProcessViewSet.as_view({"get": "list", "post": "create"}),
        name="approval.group_approval_process",
    ),
    # 默认流程设置
    path(
        "processes/global_config/",
        views.ApprovalProcessGlobalConfigViewSet.as_view({"get": "list", "post": "create"}),
        name="approval.approval_process_global_config",
    ),
    # 操作的敏感等级数量
    path(
        "sensitivity_level/count/",
        views.SystemActionSensitivityLevelCountViewSet.as_view({"get": "list"}),
        name="approval.system_action_sensitivity_level_count",
    ),
    path(
        "sensitivity_level/actions/",
        views.ActionSensitivityLevelViewSet.as_view({"post": "create"}),
        name="approval.action_sensitivity_level_update",
    ),
]
