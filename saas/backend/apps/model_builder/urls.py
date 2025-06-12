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
        "",
        views.UserMockSystemModelViewSet.as_view({"post": "create", "get": "list"}),
        name="model_builder.user_mock_system_model",
    ),
    path(
        "<int:id>/",
        include(
            [
                path(
                    "",
                    views.MockSystemModelViewSet.as_view(
                        {
                            "get": "retrieve",
                            # "post": "add_part",
                            "put": "update_part",
                            "delete": "delete_part",
                        }
                    ),
                    name="model_builder.mock_system_model",
                ),
                path(
                    "systems/", views.SystemListView.as_view({"get": "list_system"}), name="model_builder.list_system"
                ),
                path(
                    "resource_types/",
                    views.ResourceTypeListView.as_view({"get": "list_resource_type"}),
                    name="model_builder.list_resource_type",
                ),
                path(
                    "instance_selections/",
                    views.InstanceSelectionListView.as_view({"get": "list_instance_selection"}),
                    name="model_builder.list_instance_selection",
                ),
                path(
                    "json/",
                    views.GenerateJsonView.as_view({"post": "generate_json"}),
                    name="model_builder.generate_json",
                ),
                path(
                    "is_id_exists/",
                    views.ModelDataIdExistsViewSet.as_view({"get": "exists"}),
                    name="model_builder.model_data_id_exists",
                ),
            ]
        ),
    ),
    path("is_id_exists/", views.IdExistsViewSet.as_view({"get": "exists"}), name="model_builder.id_exists"),
]
