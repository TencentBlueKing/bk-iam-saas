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

from backend.apps.role.models import Role, RoleCommonAction
from backend.common.filters import InitialFilterSet


class GradeMangerFilter(InitialFilterSet):
    name = filters.CharFilter(lookup_expr="icontains", label="名称")
    hidden = filters.BooleanFilter(method="hidden_filter", initial=True)

    class Meta:
        model = Role
        fields = ["name", "hidden"]

    def hidden_filter(self, queryset, name, value):
        if value:
            return queryset.filter(hidden=False)
        return queryset


class RoleCommonActionFilter(filters.FilterSet):
    system_id = filters.CharFilter(label="系统id")

    class Meta:
        model = RoleCommonAction
        fields = ["system_id"]


class SystemGradeMangerFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr="icontains", label="名称")

    class Meta:
        model = Role
        fields = ["name"]
