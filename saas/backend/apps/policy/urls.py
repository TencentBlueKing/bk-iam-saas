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
    path("", views.PolicyViewSet.as_view({"get": "list", "delete": "destroy"}), name="policy.list_policy"),
    path("<int:pk>/", views.PolicyViewSet.as_view({"put": "update"}), name="policy.detail"),
    path(
        "<int:pk>/<str:resource_group_id>/",
        views.PolicyResourceGroupDeleteViewSet.as_view({"delete": "destroy"}),
        name="policy.resource_group_delete",
    ),
    path("systems/", views.PolicySystemViewSet.as_view({"get": "list"}), name="policy.list_policy_system"),
    path(
        "expire_soon/", views.PolicyExpireSoonViewSet.as_view({"get": "list"}), name="policy.list_policy_expire_soon"
    ),
    path(
        "related/",
        views.RelatedPolicyViewSet.as_view({"post": "create"}),
        name="policy.generate_related_policy",
    ),
    path(
        "resource_copy/",
        views.BatchPolicyResourceCopyViewSet.as_view({"post": "create"}),
        name="policy.resource_copy",
    ),
    path(
        "recommended/",
        views.RecommendPolicyViewSet.as_view({"get": "list"}),
        name="policy.generate_recommend_policy",
    ),
]
