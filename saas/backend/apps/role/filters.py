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

from backend.apps.role.models import Role, RoleCommonAction, RoleUser
from backend.common.filters import InitialFilterSet


class GradeMangerFilter(InitialFilterSet):
    name = filters.CharFilter(lookup_expr="icontains", label="名称")
    hidden = filters.BooleanFilter(method="hidden_filter", initial=True)
    with_super = filters.BooleanFilter(method="with_super_filter", initial=False)

    class Meta:
        model = Role
        fields = ["name", "hidden"]

    def hidden_filter(self, queryset, name, value):
        if value:
            return queryset.filter(hidden=False)
        return queryset

    def with_super_filter(self, queryset, name, value):
        return queryset


class RoleCommonActionFilter(filters.FilterSet):
    system_id = filters.CharFilter(label="系统id")

    class Meta:
        model = RoleCommonAction
        fields = ["system_id"]


class RoleSearchFilter(GradeMangerFilter):
    member = filters.CharFilter(label="成员", method="member_filter")
    with_super = filters.BooleanFilter(method="with_super_filter", initial=False)

    class Meta:
        model = Role
        fields = ["name", "hidden", "member"]

    def member_filter(self, queryset, name, value):
        role_ids = list(RoleUser.objects.filter(username=value).values_list("role_id", flat=True))
        return queryset.filter(id__in=role_ids)

    def with_super_filter(self, queryset, name, value):
        return queryset
