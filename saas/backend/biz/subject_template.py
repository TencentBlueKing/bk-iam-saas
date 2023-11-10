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
from datetime import datetime
from typing import Dict, List, Optional

from django.conf import settings
from django.db import transaction
from django.db.models import Count
from django.utils.translation import gettext as _
from pydantic import BaseModel

from backend.apps.organization.models import User
from backend.apps.role.models import Role, RoleRelatedObject
from backend.apps.subject_template.models import SubjectTemplate, SubjectTemplateGroup, SubjectTemplateRelation
from backend.biz.subject import SubjectInfoList
from backend.common.error_codes import error_codes
from backend.service.constants import RoleRelatedObjectType, RoleType, SubjectType
from backend.service.models.subject import Subject
from backend.service.subject_template import SubjectTemplateService
from backend.util.time import utc_to_local


class SubjectTemplateMemberBean(BaseModel):
    type: str
    id: str
    name: str = ""
    full_name: str = ""
    member_count: int = 0
    user_departments: Optional[List[str]] = None
    created_time: datetime


class SubjectTemplateCheckBiz:
    def check_member_count(self, subject_template_id: int, new_member_count: int):
        """
        检查人员模版成员数量未超限
        """
        exists_count = SubjectTemplateRelation.objects.filter(template_id=subject_template_id).count()
        member_limit = settings.SUBJECT_AUTHORIZATION_LIMIT.get("subject_template_member_limit", 1000)
        if exists_count + new_member_count > member_limit:
            raise error_codes.VALIDATE_ERROR.format(
                _("超过人员模版最大可添加成员数{}").format(member_limit),
                True,
            )

    def check_role_subject_template_name_unique(self, role_id: int, name: str, template_id: int = 0):
        """
        检查人员模版的名字是否已存在
        """
        role_template_ids = RoleRelatedObject.objects.list_role_object_ids(
            role_id, RoleRelatedObjectType.SUBJECT_TEMPLATE.value
        )
        if template_id in role_template_ids:
            role_template_ids.remove(template_id)
        if SubjectTemplate.objects.filter(name=name, id__in=role_template_ids).exists():
            raise error_codes.CONFLICT_ERROR.format(_("存在同名人员模版"))

    def check_role_subject_template_limit(self, role: Role, new_subject_template_count: int):
        """
        检查角色下的人员模版数量是否超限
        """
        # 只针对普通分级管理，对于超级管理员和系统管理员则无限制
        if role.type in [RoleType.SUPER_MANAGER.value, RoleType.SYSTEM_MANAGER.value]:
            return

        limit = settings.SUBJECT_AUTHORIZATION_LIMIT["grade_manager_subject_template_limit"]
        role_group_ids = RoleRelatedObject.objects.list_role_object_ids(
            role.id, RoleRelatedObjectType.SUBJECT_TEMPLATE.value
        )
        if len(role_group_ids) + new_subject_template_count > limit:
            raise error_codes.VALIDATE_ERROR.format(
                _("超过分级管理员最大可创建人员模版数{}").format(limit),
                True,
            )


class SubjectTemplateBiz:
    svc = SubjectTemplateService()

    def create(
        self,
        role: Role,
        name: str,
        description: str,
        creator: str,
        subjects: List[Subject],
        readonly: bool = False,
        source_group_id: int = 0,
    ) -> SubjectTemplate:
        with transaction.atomic():
            # 创建template
            subject_template = self.svc.create(
                name=name,
                description=description,
                creator=creator,
                subjects=subjects,
                readonly=readonly,
                source_group_id=source_group_id,
            )

            # 关联角色
            RoleRelatedObject.objects.create_subject_template_relation(role.id, subject_template.id)

        return subject_template

    def get_group_count_dict(self, template_ids: List[int]) -> Dict[int, int]:
        q = (
            SubjectTemplateGroup.objects.filter(template_id__in=template_ids)
            .values("template_id")
            .annotate(count=Count("id"))
        )
        return {item["template_id"]: item["count"] for item in q}

    def delete(self, template_id: int):
        return self.svc.delete(template_id)

    def delete_group(self, template_id: int, group_id: int):
        return self.svc.delete_group(template_id, group_id)

    def add_members(self, template_id: int, members: List[Subject]):
        return self.svc.add_members(template_id, members)

    def delete_members(self, template_id: int, members: List[Subject]):
        return self.svc.delete_members(template_id, members)

    def convert_to_subject_template_members(
        self, relations: List[SubjectTemplateRelation]
    ) -> List[SubjectTemplateMemberBean]:
        subjects = [Subject(type=relation.subject_type, id=relation.subject_id) for relation in relations]
        subject_info_list = SubjectInfoList(subjects)

        # 查询用户的部门
        usernames = [one.id for one in subjects if one.type == SubjectType.USER.value]
        user_dict = {u.username: u for u in User.objects.filter(username__in=usernames)} if usernames else {}

        # 组合数据结构
        subject_template_member_beans = []
        for subject, relation in zip(subjects, relations):
            subject_info = subject_info_list.get(subject)
            if not subject_info:
                continue

            # 填充用户所属的部门
            user_departments = None
            if subject.type == SubjectType.USER.value:
                user = user_dict.get(subject.id, None)
                if user:
                    user_departments = [d.full_name for d in user.departments]

            subject_template_member_bean = SubjectTemplateMemberBean(
                created_time=utc_to_local(relation.created_time),
                user_departments=user_departments,
                **subject_info.dict(),
            )
            subject_template_member_beans.append(subject_template_member_bean)

        return subject_template_member_beans

    def search_member_by_keyword(self, template_id: int, keyword: str) -> List[SubjectTemplateMemberBean]:
        """根据关键词 获取指定人员模版成员列表"""
        queryset = SubjectTemplateRelation.objects.filter(template_id=template_id)
        subject_template_members = self.convert_to_subject_template_members(queryset)
        hit_members = list(
            filter(lambda m: keyword in m.id.lower() or keyword in m.name.lower(), subject_template_members)
        )

        return hit_members
