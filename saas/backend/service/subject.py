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

from typing import Dict, List

from pydantic import parse_obj_as

from backend.component import iam

from .models import Subject

# from .constants import SubjectType


class SubjectService:
    def list_freezed_subjects(self) -> List[Subject]:
        """
        冻结用户列表
        """
        data = iam.list_freezed_subjects()
        return parse_obj_as(List[Subject], data)

    def freeze_users(self, subjects: List[Dict]):
        # def freeze_users(self, usernames: List[str]):
        """
        批量冻结用户
        """
        # subjects = [{"type": SubjectType.USER.value, "id": username} for username in usernames]
        iam.freeze_subjects(subjects)

    def unfreeze_users(self, subjects: List[Dict]):
        # def unfreeze_users(self, usernames: List[str]):
        """
        批量解冻用户
        """
        # subjects = [{"type": SubjectType.USER.value, "id": username} for username in usernames]
        iam.unfreeze_subjects(subjects)
