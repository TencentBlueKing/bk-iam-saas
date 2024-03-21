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
from django_filters import rest_framework as filters

from backend.apps.group.models import Group
from backend.apps.role.models import RoleRelatedObject, Role
from backend.service.constants import RoleRelatedObjectType


class GroupFilter(filters.FilterSet):
    id = filters.NumberFilter(label="ID")
    name = filters.CharFilter(label="名字", lookup_expr="icontains")
    description = filters.CharFilter(label="描述", lookup_expr="icontains")
    grade_manager_id = filters.NumberFilter(method="grade_manager_id_filter", label="分级管理员ID")

    class Meta:
        model = Group
        fields = ["name", "id", "description", "grade_manager_id"]

    def grade_manager_id_filter(self, queryset, name, value):
        group_ids = RoleRelatedObject.objects.list_role_object_ids(value, RoleRelatedObjectType.GROUP.value)
        return queryset.filter(id__in=group_ids)


class GradeManagerFilter(filters.FilterSet):
    name = filters.CharFilter(label="名字", lookup_expr="icontains")

    class Meta:
        model = Role
        fields = [
            "name",
        ]
