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

from collections import defaultdict
from typing import Dict, List, Optional

from pydantic import BaseModel
from pydantic.tools import parse_obj_as

from backend.biz.action import ActionBean, ActionBeanList
from backend.service.action import ActionService
from backend.service.action_group import ActionGroupService
from backend.service.models import ActionGroup


class ActionGroupBean(BaseModel):
    name: str
    name_en: str
    actions: List[ActionBean] = []
    sub_groups: List["ActionGroupBean"] = []

    def is_empty(self) -> bool:
        return not self.actions and not self.sub_groups

    @property
    def all_actions(self) -> List[ActionBean]:
        """操作分组里的所有操作"""
        actions = list(self.actions)
        for ag in self.sub_groups:
            actions.extend(ag.all_actions)
        return actions

    @classmethod
    def new_uncategorized(cls, actions: List[ActionBean]) -> "ActionGroupBean":
        return cls.parse_obj({"name": "未分类", "name_en": "uncategorized", "actions": actions})


ActionGroupBean.update_forward_refs()


class ActionGroupWithIDBean(ActionGroupBean):
    id: int = 0  # NOTE 仅用于前端筛选
    sub_groups: List["ActionGroupWithIDBean"] = []


ActionGroupWithIDBean.update_forward_refs()


class ActionGroupBiz:
    action_svc = ActionService()
    action_group_svc = ActionGroupService()

    def list_by_actions(self, system_id: str, actions: List[ActionBean]) -> List[ActionGroupBean]:
        """
        获取ActionGroup列表
        """
        if not actions:
            return []

        action_groups = self.action_group_svc.list(system_id)
        if not action_groups:
            return [ActionGroupBean.new_uncategorized(actions)]

        action_list = ActionBeanList(actions)
        action_group_beans = self._gen_action_group_beans(action_groups, action_list)

        uncategorized_group = self._gen_uncategorized(actions, action_group_beans)
        if uncategorized_group:
            action_group_beans.append(uncategorized_group)
        return action_group_beans

    def _gen_uncategorized(
        self, actions: List[ActionBean], action_group_beans: List[ActionGroupBean]
    ) -> Optional[ActionGroupBean]:
        # 处理未归类的操作
        group_action_ids = []
        for group in action_group_beans:
            group_action_ids.extend([action.id for action in group.all_actions])

        uncategorized_actions = [a for a in actions if a.id not in set(group_action_ids)]
        if uncategorized_actions:
            return ActionGroupBean.new_uncategorized(uncategorized_actions)
        return None

    def _gen_action_group_bean(self, action_group: ActionGroup, action_list: ActionBeanList) -> ActionGroupBean:
        """
        生成单个操作组

        1. 填充所有操作为ActionBean
        2. 递归生成子操作组
        """
        action_group_bean = ActionGroupBean(name=action_group.name, name_en=action_group.name_en)

        for one in action_group.actions:
            action = action_list.get(one.id)
            if not action:
                continue
            action_group_bean.actions.append(action)

        action_group_bean.sub_groups = self._gen_action_group_beans(action_group.sub_groups, action_list)
        return action_group_bean

    def _gen_action_group_beans(
        self, action_groups: List[ActionGroup], action_list: ActionBeanList
    ) -> List[ActionGroupBean]:
        """
        批量生成操作组
        剔除空的操作组数据
        """
        action_group_beans = [self._gen_action_group_bean(one, action_list) for one in action_groups]
        return [one for one in action_group_beans if not one.is_empty()]

    def list_with_frontend_id_by_actions(
        self, system_id: str, actions: List[ActionBean]
    ) -> List[ActionGroupWithIDBean]:
        """
        获取某个系统完整的操作分组
        """
        action_group_beans = parse_obj_as(List[ActionGroupWithIDBean], self.list_by_actions(system_id, actions))
        self._fill_frontend_id(action_group_beans)  # NOTE id 仅用于前端筛选
        return action_group_beans

    def _fill_frontend_id(self, action_groups: List[ActionGroupWithIDBean], start_id: int = 1) -> int:
        """
        填充action_group_id, 这里的ID仅仅为了前端过滤而已，无其它后台用途
        使用深度遍历方式填充ID
        """
        for ag in action_groups:
            ag.id = start_id
            start_id += 1
            if ag.sub_groups:
                start_id = self._fill_frontend_id(ag.sub_groups, start_id)
        return start_id

    def get_actions_by_frontend_id(
        self, system_id: str, actions: List[ActionBean], action_group_id: int
    ) -> List[ActionBean]:
        """
        获取操作分组里的Action
        """
        action_groups = self.list_with_frontend_id_by_actions(system_id, actions)
        for ag in action_groups:
            action_group = self._find_by_frontend_id(ag, action_group_id)
            if action_group is not None:
                return action_group.all_actions
        return []

    def _find_by_frontend_id(
        self, action_group: ActionGroupWithIDBean, action_group_id: int
    ) -> Optional[ActionGroupWithIDBean]:
        """根据ID查询对应的action_group"""
        if action_group.id == action_group_id:
            return action_group
        # 递归查找是否有符合的
        for ag in action_group.sub_groups:
            sub_group = self._find_by_frontend_id(ag, action_group_id)
            if sub_group is not None:
                return sub_group
        return None

    def get_action_same_group_dict(self, system_id: str, action_ids: List[str]) -> Dict[str, List[str]]:
        """
        生成相同操作分组字典

        result = {
            action_id: [action_id, action_id, ...] # 同一个分组的action_id
        }
        """
        action_groups = self.action_group_svc.list(system_id)
        if not action_groups:
            return {}

        return self._find_action_same_group(action_groups, action_ids)

    def _find_action_same_group(self, action_groups: List[ActionGroup], action_ids: List[str]) -> Dict[str, List[str]]:
        """
        查找action_id在同一个分组中的其他操作
        """
        result: Dict[str, List[str]] = defaultdict(list)
        for action_group in action_groups:
            for action in action_group.actions:
                if action.id in action_ids:
                    result[action.id].extend(
                        [a.id for a in action_group.actions if a.id not in action_ids]
                    )  # 兼容可能一个操作在多个分组中
                    continue

            if not action_group.sub_groups:
                continue

            sub_result = self._find_action_same_group(action_group.sub_groups, action_ids)

            for k, v in sub_result.items():
                result[k].extend(v)

        return result
