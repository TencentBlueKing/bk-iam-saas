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

from typing import List, Union

from pydantic import BaseModel

from backend.service.constants import SubjectType


class Subject(BaseModel):
    type: str
    id: str

    def __hash__(self):
        return hash((self.type, self.id))

    def __eq__(self, other):
        return self.type == other.type and self.id == other.id

    @classmethod
    def from_username(cls, username: str) -> "Subject":
        return cls(type=SubjectType.USER.value, id=username)

    @classmethod
    def from_group_id(cls, group_id: Union[int, str]) -> "Subject":
        return cls(type=SubjectType.GROUP.value, id=str(group_id))

    @classmethod
    def from_department_id(cls, department_id: Union[int, str]) -> "Subject":
        return cls(type=SubjectType.DEPARTMENT.value, id=str(department_id))

    @classmethod
    def from_usernames(cls, usernames: List[str]) -> List["Subject"]:
        return [cls.from_username(username) for username in usernames]


class Applicant(Subject):
    """
    权限申请人
    """

    display_name: str
