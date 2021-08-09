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
    path("instance/", views.AuthInstanceView.as_view(), name="open.auth_instance"),
    path("path/", views.AuthPathView.as_view(), name="open.auth_path"),
    path("batch_instance/", views.AuthBatchInstanceView.as_view(), name="open.auth_batch_instance"),
    path("batch_path/", views.AuthBatchPathView.as_view(), name="open.auth_batch_path"),
    path(
        "resource_creator_action/",
        views.ResourceCreatorActionView.as_view(),
        name="open.grant_resource_creator_action",
    ),
    path(
        "batch_resource_creator_action/",
        views.BatchResourceCreatorActionView.as_view(),
        name="open.grant_batch_resource_creator_action",
    ),
    path(
        "resource_creator_action_attribute/",
        views.ResourceCreatorActionAttributeView.as_view(),
        name="open.grant_resource_creator_action_attribute",
    ),
]
