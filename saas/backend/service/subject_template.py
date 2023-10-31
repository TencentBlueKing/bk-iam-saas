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
from typing import List, Optional

from django.db import transaction

from backend.apps.subject_template.models import SubjectTemplate, SubjectTemplateGroup, SubjectTemplateRelation
from backend.component import iam
from backend.service.constants import SubjectType
from backend.service.models.subject import Subject


class SubjectTemplateService:
    def create(self, name: str, description: str, subjects: List[Subject], creator: str) -> SubjectTemplate:
        template = SubjectTemplate(
            name=name,
            description=description,
            creator=creator,
        )

        relations = [
            SubjectTemplateRelation(
                template_id=template.id,
                subject_type=subject.type,
                subject_id=subject.id,
            )
            for subject in subjects
        ]

        template.save()
        if relations:
            SubjectTemplateRelation.objects.bulk_create(relations)

        return template

    # 迁移到service
    def delete(self, template_id: int):
        subjects = self._list_subjects(template_id)

        if subjects:
            groups = SubjectTemplateGroup.objects.filter(template_id=template_id)
            for group in groups:
                self.delete_group(template_id, group.id, subjects)

        with transaction.atomic():
            SubjectTemplate.objects.filter(id=template_id).delete()
            SubjectTemplateRelation.objects.filter(template_id=template_id).delete()

    # 迁移到service
    def delete_group(self, template_id: int, group_id: int, subjects: Optional[List[Subject]] = None):
        # 查询所有成员
        if not subjects:
            subjects = self._list_subjects(template_id)

        if not subjects:
            return

        with transaction.atomic():
            # 删除关联关系
            count, _ = SubjectTemplateGroup.objects.filter(template_id=template_id, group_id=group_id).delete()

            if count != 0:
                # 调用后台接口删除数据
                data = [
                    {"template_id": template_id, "group_id": group_id, "type": subject.type, "id": subject.id}
                    for subject in subjects
                ]
                iam.delete_subject_template_groups(data)

    def _list_subjects(self, template_id):
        queryset = SubjectTemplateRelation.objects.filter(template_id=template_id)
        subjects = [Subject(type=relation.subject_type, id=relation.subject_id) for relation in queryset]

        return subjects

    def add_members(self, template_id: int, members: List[Subject]):
        # 排除不存在的数据
        members = self._filter_exists_members(template_id, members)
        if not members:
            return

        groups = SubjectTemplateGroup.objects.filter(template_id=template_id)
        # 拼接调用后台的数据
        backend_subjects = [
            {
                "template_id": template_id,
                "group_id": group.group_id,
                "type": subject.type,
                "id": subject.id,
                "expired_at": group.expired_at,
            }
            for subject in members
            for group in groups
        ]

        # 批量添加
        relations = [
            SubjectTemplateRelation(
                template_id=template_id,
                subject_type=subject.type,
                subject_id=subject.id,
            )
            for subject in members
        ]

        with transaction.atomic():
            SubjectTemplateRelation.objects.bulk_create(relations)

            # 调用后台接口
            if backend_subjects:
                iam.create_subject_template_groups(backend_subjects)

    def delete_members(self, template_id: int, members: List[Subject]):
        # 排除不存在的数据
        members = self._filter_exists_members(template_id, members)
        if not members:
            return

        groups = SubjectTemplateGroup.objects.filter(template_id=template_id)
        # 拼接调用后台的数据
        backend_subjects = [
            {
                "template_id": template_id,
                "group_id": group.group_id,
                "type": subject.type,
                "id": subject.id,
            }
            for subject in members
            for group in groups
        ]

        with transaction.atomic():
            # 批量删除
            user_ids = [subject.id for subject in members if subject.type == SubjectType.USER.value]
            if user_ids:
                SubjectTemplateRelation.objects.filter(
                    template_id=template_id, subject_type=SubjectType.USER.value, subject_id__in=user_ids
                ).delete()

            department_ids = [subject.id for subject in members if subject.type == SubjectType.DEPARTMENT.value]
            if department_ids:
                SubjectTemplateRelation.objects.filter(
                    template_id=template_id, subject_type=SubjectType.DEPARTMENT.value, subject_id__in=department_ids
                ).delete()

            # 调用后台接口
            if backend_subjects:
                iam.delete_subject_template_groups(backend_subjects)

    def _filter_exists_members(self, template_id: int, members: List[Subject]):
        subjects = self._list_subjects(template_id)
        return [subject for subject in members if subject in subjects]
