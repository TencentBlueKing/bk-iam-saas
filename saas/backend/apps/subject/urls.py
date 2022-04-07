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
    path(
        "<str:subject_type>/<str:subject_id>/",
        include(
            [
                path(
                    "groups/",
                    views.SubjectGroupViewSet.as_view({"get": "list", "delete": "destroy"}),
                    name="subject.group",
                ),
                path(
                    "roles/",
                    views.SubjectRoleViewSet.as_view({"get": "list"}),
                    name="subject.roles_with_permission",
                ),
                path(
                    "systems/", views.SubjectSystemViewSet.as_view({"get": "list"}), name="subject.list_policy_system"
                ),
                path(
                    "policies/",
                    views.SubjectPolicyViewSet.as_view({"get": "list", "delete": "destroy"}),
                    name="subject.list_policy",
                ),
                path(
                    "policies/<int:pk>/",
                    views.SubjectPolicyViewSet.as_view({"put": "update"}),
                    name="subject.policy_detail",
                ),
                path(
                    "policies/<int:pk>/<str:resource_group_id>/",
                    views.SubjectPolicyResourceGroupDeleteViewSet.as_view({"delete": "destroy"}),
                    name="subject.resource_group_delete",
                ),
            ]
        ),
    )
]
