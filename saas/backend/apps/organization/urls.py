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
    path("categories/", views.CategoryViewSet.as_view({"get": "list"}), name="organization.category"),
    path(
        "departments/<int:department_id>/",
        views.DepartmentViewSet.as_view({"get": "list"}),
        name="organization.department",
    ),
    path("users/query/", views.UserView.as_view(), name="organization.user_query"),
    path("users/departments/", views.UserDepartmentView.as_view(), name="organization.user_department_query"),
    path("search/", views.OrganizationViewSet.as_view({"get": "list"}), name="organization.search"),
    path("sync_task/", views.OrganizationSyncTaskView.as_view(), name="organization.sync_task"),
    path(
        "sync_records/", views.OrganizationSyncRecordViewSet.as_view({"get": "list"}), name="organization.sync_records"
    ),
    path(
        "sync_records/<int:id>/",
        views.OrganizationSyncRecordViewSet.as_view({"delete": "destroy"}),
        name="organization.sync_record_delete",
    ),
    path(
        "sync_records/<int:id>/logs/",
        views.OrganizationSyncRecordViewSet.as_view({"get": "retrieve"}),
        name="organization.sync_record_error_log",
    ),
]
