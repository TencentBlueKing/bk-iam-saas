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
from typing import Dict, List, Optional

from pydantic import parse_obj_as

from backend.apps.approval.models import ActionProcessRelation
from backend.common.cache import cachedmethod
from backend.component import iam

from .models import Action


class ActionList:
    def __init__(self, actions: List[Action]) -> None:
        self.actions = actions
        self._action_dict = {action.id: action for action in actions}

    def get(self, _id: str) -> Optional[Action]:
        return self._action_dict.get(_id, None)

    def filter(self, action_ids: List[str]) -> List[Action]:
        return [action for action in self.actions if action.id in action_ids]


class ActionService:
    """Action相关查询与操作"""

    full_fields = (
        "id,name,name_en,related_resource_types,version,type,hidden,description,description_en,"
        "related_actions,related_environments,sensitivity"
    )

    @cachedmethod(timeout=60)
    def list(self, system_id: str) -> List[Action]:
        """获取系统的Action列表"""
        actions = iam.list_action(system_id, fields=self.full_fields)
        return parse_obj_as(List[Action], actions)

    def get(self, system_id: str, action_id: str) -> Action:
        """
        获取Action
        """
        return Action.parse_obj(iam.get_action(system_id, action_id))

    def new_action_list(self, system_id: str) -> ActionList:
        """
        生成ActionList
        """
        return ActionList(self.list(system_id))

    def delete(self, system_id: str, action_id: str):
        """删除操作"""
        iam.delete_action(system_id, action_id)

    def get_action_sensitivity_level_map(self, system_id: str) -> Dict[str, str]:
        action_sensitivity_level = {}
        for action_level in ActionProcessRelation.objects.filter(system_id=system_id).values(
            "action_id", "sensitivity_level"
        ):
            action_sensitivity_level[action_level["action_id"]] = action_level["sensitivity_level"]
        return action_sensitivity_level
