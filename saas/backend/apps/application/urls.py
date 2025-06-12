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
    path("", views.ApplicationViewSet.as_view({"get": "list", "post": "create"}), name="application.application"),
    path("<int:pk>/", views.ApplicationViewSet.as_view({"get": "retrieve"}), name="application.detail"),
    path("<int:pk>/cancel/", views.ApplicationViewSet.as_view({"put": "cancel"}), name="application.cancel"),
    path("<str:callback_id>/approve/", views.ApplicationApprovalView.as_view(), name="application.approve"),
    path("condition_compare/", views.ConditionView.as_view(), name="application.condition_compare"),
    path("group/", views.ApplicationByGroupView.as_view(), name="application.group"),
    path("grade_manager/", views.ApplicationByGradeManagerView.as_view(), name="application.grade_manager"),
    path(
        "grade_manager_updated/",
        views.ApplicationByGradeManagerUpdatedView.as_view(),
        name="application.grade_manager_updated",
    ),
    path("group_renew/", views.ApplicationByRenewGroupView.as_view(), name="application.group.renew"),
    path("policy_renew/", views.ApplicationByRenewPolicyView.as_view(), name="application.policy.renew"),
    path("temporary_policy/", views.ApplicationByTemporaryPolicyView.as_view(), name="application.temporary_policy"),
]
