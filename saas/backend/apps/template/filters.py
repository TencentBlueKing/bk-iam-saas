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
from backend.apps.template.models import PermTemplate, PermTemplatePolicyAuthorized


class TemplateMemberFilter(filters.FilterSet):
    name = filters.CharFilter(method="name_filter", label="用户组名")

    class Meta:
        model = PermTemplatePolicyAuthorized
        fields = ["name"]

    def name_filter(self, queryset, name, value):
        group_ids = list(Group.objects.filter(name__icontains=value).values_list("id", flat=True))
        return queryset.filter(subject_id__in=group_ids)


class TemplateFilter(filters.FilterSet):
    system_id = filters.CharFilter(label="系统id")
    creator = filters.CharFilter(label="创建人")
    name = filters.CharFilter(label="名字", lookup_expr="icontains")
    description = filters.CharFilter(label="描述", lookup_expr="icontains")
    group_id = filters.NumberFilter(method="group_id_filter", label="用户组id")

    class Meta:
        model = PermTemplate
        fields = ["system_id", "creator", "name", "description"]

    def group_id_filter(self, queryset, name, value):
        return queryset
