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
    path(
        "",
        views.SubjectTemplateViewSet.as_view({"get": "list", "post": "create"}),
        name="subject.template",
    ),
    path(
        "members/",
        views.SubjectTemplatesMemberCreateViewSet.as_view({"post": "create"}),
        name="subject.template_batch_member",
    ),
    path(
        "<int:id>/",
        views.SubjectTemplateViewSet.as_view({"get": "retrieve", "delete": "destroy", "put": "update"}),
        name="subject.template_detail",
    ),
    path(
        "<int:id>/groups/",
        views.SubjectTemplateGroupViewSet.as_view({"get": "list", "delete": "destroy"}),
        name="subject.template_group",
    ),
    path(
        "<int:id>/members/",
        views.SubjectTemplateMemberViewSet.as_view({"get": "list", "delete": "destroy", "post": "create"}),
        name="subject.template_member",
    ),
]
