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

from typing import List

from django.core.management.base import BaseCommand
from django.core.paginator import Paginator
from pydantic import parse_obj_as

from backend.apps.group.models import Group
from backend.apps.role.models import Role, RoleRelatedObject
from backend.apps.subject_template.models import SubjectTemplate
from backend.biz.subject_template import SubjectTemplateBiz
from backend.component.iam import list_all_subject_member
from backend.service.constants import RoleRelatedObjectType, RoleType, SubjectType
from backend.service.models.subject import Subject


class Command(BaseCommand):
    help = "migrate bk ci subject template from group"

    def handle(self, *args, **options):
        subject_template_biz = SubjectTemplateBiz()

        queryset = Role.objects.filter(source_system_id="bk_ci_rbac", type=RoleType.GRADE_MANAGER.value).order_by("id")

        paginator = Paginator(queryset, 100)

        for i in paginator.page_range:
            for role in paginator.page(i):
                # 遍历role创建每一个group
                group_ids = list(
                    RoleRelatedObject.objects.filter(
                        role_id=role.id, object_type=RoleRelatedObjectType.GROUP.value
                    ).values_list("object_id", flat=True)
                )

                exist_subject_template_ids = list(
                    RoleRelatedObject.objects.filter(
                        role_id=role.id, object_type=RoleRelatedObjectType.SUBJECT_TEMPLATE.value
                    ).values_list("object_id", flat=True)
                )

                for group in Group.objects.filter(id__in=group_ids):
                    # 已创建过, 不需要重复创建
                    if (
                        exist_subject_template_ids
                        and SubjectTemplate.objects.filter(id__in=exist_subject_template_ids, name=group.name).exists()
                    ):
                        continue

                    members = list_all_subject_member(SubjectType.GROUP.value, str(group.id))

                    # 创建人员模版
                    subject_template_biz.create(
                        role,
                        group.name,
                        group.description,
                        group.creator,
                        parse_obj_as(List[Subject], members),
                        readonly=True,
                        source_group_id=group.id,
                    )
