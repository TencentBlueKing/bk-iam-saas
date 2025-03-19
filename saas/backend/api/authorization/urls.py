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
    # 授权
    # 单Action单实例
    path("instance/", views.resource.AuthInstanceView.as_view(), name="open.auth_instance"),
    # 单Action单拓扑路径
    path("path/", views.resource.AuthPathView.as_view(), name="open.auth_path"),
    # 批量Action批量实例
    path("batch_instance/", views.resource.AuthBatchInstanceView.as_view(), name="open.auth_batch_instance"),
    # 批量Action批量拓扑
    path("batch_path/", views.resource.AuthBatchPathView.as_view(), name="open.auth_batch_path"),
    # 新建关联授权
    # 新建关联授权 - 单一实例授权
    path(
        "resource_creator_action/",
        views.resource_creator_action.ResourceCreatorActionView.as_view(),
        name="open.grant_resource_creator_action",
    ),
    # 新建关联授权 - 批量实例授权
    path(
        "batch_resource_creator_action/",
        views.resource_creator_action.BatchResourceCreatorActionView.as_view(),
        name="open.grant_batch_resource_creator_action",
    ),
    # 新建关联授权 - 属性授权
    path(
        "resource_creator_action_attribute/",
        views.resource_creator_action.ResourceCreatorActionAttributeView.as_view(),
        name="open.grant_resource_creator_action_attribute",
    ),
    # 单个属性授权
    path(
        "action_attribute/",
        views.action.ActionAttributeView.as_view(),
        name="open.grant_action_attribute",
    ),
]
