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
from backend.apps.policy.models import Policy
from backend.apps.template.models import PermTemplatePolicyAuthorized
from backend.biz.group import GroupBiz
from backend.biz.open import ApplicationPolicyListCache
from backend.common.cache import cached
from backend.common.filters import InitialFilterSet
from backend.component import iam
from backend.service.constants import SubjectType


@cached(timeout=30)
def _list_pre_application_group_ids(cache_id: str):
    policy_list = ApplicationPolicyListCache().get(cache_id)
    return GroupBiz().list_pre_application_groups(policy_list)


class GroupFilter(InitialFilterSet):
    system_id = filters.CharFilter(method="system_id_filter", label="系统id")
    creator = filters.CharFilter(label="创建人")
    username = filters.CharFilter(method="username_filter", label="用户名")
    department_id = filters.CharFilter(method="department_id_filter", label="组织ID")
    id = filters.NumberFilter(label="ID")
    name = filters.CharFilter(label="名字", lookup_expr="icontains")
    description = filters.CharFilter(label="描述", lookup_expr="icontains")
    role_id = filters.NumberFilter(method="role_id_filter", label="角色ID")
    cache_id = filters.CharFilter(label="cache_id", method="cache_id_filter")
    hidden = filters.BooleanFilter(method="hidden_filter", initial=True)
    apply_disable = filters.BooleanFilter(label="不可被申请")

    class Meta:
        model = Group
        fields = [
            "system_id",
            "creator",
            "username",
            "department_id",
            "name",
            "id",
            "description",
            "role_id",
            "hidden",
            "apply_disable",
        ]

    def system_id_filter(self, queryset, name, value):
        template_group_ids = list(
            PermTemplatePolicyAuthorized.objects.filter(
                subject_type=SubjectType.GROUP.value, system_id=value
            ).values_list("subject_id", flat=True)
        )
        custom_group_ids = list(
            Policy.objects.filter(subject_type=SubjectType.GROUP.value, system_id=value).values_list(
                "subject_id", flat=True
            )
        )
        return queryset.filter(id__in=template_group_ids + custom_group_ids)

    def username_filter(self, queryset, name, value):
        return self._subject_filter(queryset, SubjectType.USER.value, value)

    def department_id_filter(self, queryset, name, value):
        return self._subject_filter(queryset, SubjectType.DEPARTMENT.value, value)

    def _subject_filter(self, queryset, _type, _id):
        # NOTE: 可能会有性能问题, 分页查询用户的所有组列表
        data = iam.list_all_subject_groups(_type, _id)
        group_ids = [int(g["id"]) for g in data]
        return queryset.filter(id__in=group_ids)

    def role_id_filter(self, queryset, name, value):
        return queryset

    def cache_id_filter(self, queryset, name, value):
        group_ids = _list_pre_application_group_ids(value)
        return queryset.filter(id__in=group_ids)

    def hidden_filter(self, queryset, name, value):
        if value:
            return queryset.filter(hidden=False)
        return queryset


class GroupTemplateSystemFilter(filters.FilterSet):
    system_id = filters.CharFilter(label="系统id")

    class Meta:
        model = PermTemplatePolicyAuthorized
        fields = ["system_id"]
