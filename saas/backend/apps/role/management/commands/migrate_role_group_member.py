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
from django.core.management.base import BaseCommand
from django.core.paginator import Paginator

from backend.apps.role.models import Role, RoleGroupMember, RoleRelatedObject, RoleRelation
from backend.component.iam import list_all_subject_member
from backend.service.constants import RoleRelatedObjectType, RoleType, SubjectType


class Command(BaseCommand):
    help = "migrate role group member"

    def handle(self, *args, **options):
        queryset = Role.objects.order_by("id")

        paginator = Paginator(queryset, 100)

        for i in paginator.page_range:
            for role in paginator.page(i):
                # 如果role类型为二级管理员, 需要查询到二级管理员对应的一级管理员
                if role.type == RoleType.SUBSET_MANAGER.value:
                    role_id = RoleRelation.objects.filter(role_id=role.id).first().parent_id
                    subset_id = role.id
                else:
                    role_id = role.id
                    subset_id = 0

                # 遍历role创建每一个group
                for group_id in RoleRelatedObject.objects.filter(
                    role_id=role_id, object_type=RoleRelatedObjectType.GROUP.value
                ).values_list("object_id", flat=True):
                    # 查询group的所有成员
                    members = list_all_subject_member(SubjectType.GROUP.value, str(group_id))
                    # 创建role group member
                    role_group_member = [
                        RoleGroupMember(
                            role_id=role_id,
                            subset_id=subset_id,
                            group_id=group_id,
                            subject_type=one["type"],
                            subject_id=one["id"],
                        )
                        for one in members
                    ]

                    if role_group_member:
                        RoleGroupMember.objects.bulk_create(role_group_member, batch_size=100, ignore_conflicts=True)
