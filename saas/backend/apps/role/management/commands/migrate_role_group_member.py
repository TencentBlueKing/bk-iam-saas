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
from typing import Dict, Tuple

from django.core.management.base import BaseCommand
from django.core.paginator import Paginator
from django.db import transaction

from backend.apps.organization.models import Department, User
from backend.apps.role.models import RoleGroupMember, RoleRelatedObject, RoleRelation
from backend.component.iam import list_all_subject_groups
from backend.service.constants import RoleRelatedObjectType
from backend.service.models.subject import Subject


class Command(BaseCommand):
    help = "migrate role group member"

    _cache: Dict[int, Tuple[int, int]] = {}

    def handler_user(self):
        queryset = User.objects.order_by("id")
        paginator = Paginator(queryset, 1000)
        for i in paginator.page_range:
            for user in paginator.page(i):
                subject = Subject.from_username(user.username)
                groups = list_all_subject_groups(subject.type, subject.id)

                role_group_member = []
                for group in groups:
                    group_id = group["id"]
                    role_id, subset_id = self._get_role_and_subset_id(group_id)
                    if role_id == 0:
                        continue

                    role_group_member.append(
                        RoleGroupMember(
                            role_id=role_id,
                            subset_id=subset_id,
                            group_id=group_id,
                            subject_type=subject.type,
                            subject_id=subject.id,
                        )
                    )

                if role_group_member:
                    with transaction.atomic():
                        RoleGroupMember.objects.bulk_create(role_group_member, batch_size=100, ignore_conflicts=True)

    def handler_department(self):
        queryset = Department.objects.order_by("id")
        paginator = Paginator(queryset, 1000)
        for i in paginator.page_range:
            for department in paginator.page(i):
                subject = Subject.from_department_id(department.id)
                groups = list_all_subject_groups(subject.type, subject.id)

                role_group_member = []
                for group in groups:
                    group_id = group["id"]
                    role_id, subset_id = self._get_role_and_subset_id(group_id)
                    if role_id == 0:
                        continue

                    role_group_member.append(
                        RoleGroupMember(
                            role_id=role_id,
                            subset_id=subset_id,
                            group_id=group_id,
                            subject_type=subject.type,
                            subject_id=subject.id,
                        )
                    )

                if role_group_member:
                    with transaction.atomic():
                        RoleGroupMember.objects.bulk_create(role_group_member, batch_size=100, ignore_conflicts=True)

    def _get_role_and_subset_id(self, group_id):
        if group_id in self._cache:
            return self._cache[group_id]

        obj = RoleRelatedObject.objects.filter(
            object_id=group_id, object_type=RoleRelatedObjectType.GROUP.value
        ).first()
        if not obj:
            self._cache[group_id] = (0, 0)
            return self._cache[group_id]

        role_id = obj.role_id
        relation = RoleRelation.objects.filter(role_id=role_id).first()
        if not relation:
            self._cache[group_id] = (role_id, 0)
            return self._cache[group_id]

        subset_id = role_id
        role_id = relation.parent_id

        self._cache[group_id] = (role_id, subset_id)
        return self._cache[group_id]

    def handle(self, *args, **options):
        self.handler_user()
        self.handler_department()
