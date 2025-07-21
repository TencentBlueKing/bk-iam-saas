# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云 - 权限中心 (BlueKing-IAM) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from typing import List, Optional

from backend.apps.group.models import Group
from backend.apps.organization.models import Department, User
from backend.service.constants import SubjectType
from backend.service.models import Subject
from backend.service.subject import SubjectService


class SubjectInfo(Subject):
    name: str = ""
    full_name: str = ""
    member_count: int = 0


class SubjectInfoList:
    def __init__(self, subjects: List[Subject]) -> None:
        self.subjects = self._to_subject_infos(subjects)
        self._subject_dict = {Subject.parse_obj(subject_info): subject_info for subject_info in self.subjects}

    def get(self, subject: Subject) -> Optional[SubjectInfo]:
        return self._subject_dict.get(subject, None)

    def _to_subject_infos(self, subjects: List[Subject]) -> List[SubjectInfo]:  # noqa: C901
        """自动根据 Type 和 ID 填充 Subject 基本信息"""
        # 分组查询
        usernames, department_ids, group_ids = [], [], []
        for subject in subjects:
            if subject.type == SubjectType.USER.value:
                usernames.append(subject.id)
            elif subject.type == SubjectType.DEPARTMENT.value:
                department_ids.append(subject.id)
            elif subject.type == SubjectType.GROUP.value:
                group_ids.append(subject.id)

        object_dict = {}
        # 查询用户
        if len(usernames) != 0:
            users = User.objects.filter(username__in=usernames)
            object_dict.update({(SubjectType.USER.value, u.username): u for u in users})
        # 查询部门
        if len(department_ids) != 0:
            departments = Department.objects.filter(id__in=list(map(int, department_ids)))
            object_dict.update({(SubjectType.DEPARTMENT.value, str(d.id)): d for d in departments})
        # 查询用户组
        if len(group_ids) != 0:
            groups = Group.objects.filter(id__in=list(map(int, group_ids)))
            object_dict.update({(SubjectType.GROUP.value, str(g.id)): g for g in groups})

        subject_infos = []
        # 遍历填充相关字段
        for subject in subjects:
            subject_info = SubjectInfo.parse_obj(subject)
            # 默认值
            subject_info.name = subject.id
            subject_info.full_name = subject.id

            obj = object_dict.get((subject.type, subject.id), None)
            if not obj:
                subject_infos.append(subject_info)
                continue

            if subject.type == SubjectType.USER.value:
                subject_info.name = obj.display_name

            elif subject.type == SubjectType.DEPARTMENT.value:
                subject_info.name = obj.name
                subject_info.full_name = obj.full_name
                subject_info.member_count = obj.recursive_member_count

            elif subject.type == SubjectType.GROUP.value:
                subject_info.name = obj.name
                subject_info.member_count = obj.member_count

            subject_infos.append(subject_info)

        return subject_infos


class SubjectBiz:
    # 直通的方法
    list_freezed_subjects = SubjectService.__dict__["list_freezed_subjects"]
    freeze_users = SubjectService.__dict__["freeze_users"]
    unfreeze_users = SubjectService.__dict__["unfreeze_users"]

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.subject_svc = SubjectService()
