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

from pydantic import parse_obj_as

from backend.component import iam

from .models import ActionGroup


class ActionGroupService:
    def list(self, system_id: str) -> List[ActionGroup]:
        """
        获取ActionGroup
        """
        action_groups = iam.get_action_groups(system_id)
        return parse_obj_as(List[ActionGroup], action_groups)
