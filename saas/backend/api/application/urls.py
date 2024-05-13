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
    path("", views.ApplicationView.as_view(), name="open.application"),
    path("policies/", views.ApplicationCustomPolicyView.as_view(), name="open.application_policy"),
    path("approval_bot/user/", views.ApprovalBotUserCallbackView.as_view(), name="open.approval_bot_user"),
    path("approval_bot/role/", views.ApprovalBotRoleCallbackView.as_view(), name="open.approval_bot_role"),
    path("<str:sn>/", views.ApplicationDetailView.as_view({"get": "retrieve"}), name="open.application_detail"),
]
