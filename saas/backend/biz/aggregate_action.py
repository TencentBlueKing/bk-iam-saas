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

from typing import List

from pydantic import BaseModel
from pydantic.tools import parse_obj_as

from backend.service.action import ActionList, ActionService
from backend.service.aggregate_action import AggregateActionsService
from backend.service.models.aggregation_action import AggregateAction, AggregateResourceType
from backend.service.resource_type import ResourceTypeService


# model for frontend
class AggregateResourceTypeBean(AggregateResourceType):
    name: str = ""
    name_en: str = ""


class AggregateActionBean(AggregateAction):
    name: str = ""
    name_en: str = ""


class AggregateActionsBean(BaseModel):
    system_id: str
    actions: List[AggregateActionBean]
    aggregate_resource_types: List[AggregateResourceTypeBean]


class AggregateActionsList:
    def __init__(self, tenant_id: str, aggregate_action_list: List[AggregateActionsBean]) -> None:
        self.tenant_id = tenant_id
        self.aggregate_actions = aggregate_action_list

    def _list_resource_type_system_id(self):
        system_ids_set = set()
        for aa in self.aggregate_actions:
            for art in aa.aggregate_resource_types:
                system_ids_set.add(art.system_id)

        return list(system_ids_set)

    def fill_action_name(self):
        action_svc = ActionService(self.tenant_id)
        for one in self.aggregate_actions:
            action_list = ActionList(action_svc.list(one.system_id))

            for action in one.actions:
                named_action = action_list.get(action.id)
                action.name, action.name_en = (named_action.name, named_action.name_en) if named_action else ("", "")

    def fill_resource_type_name(self):
        system_ids = self._list_resource_type_system_id()
        name_provider = ResourceTypeService().get_system_resource_type_dict(system_ids)

        for aa in self.aggregate_actions:
            for art in aa.aggregate_resource_types:
                art.name, art.name_en = name_provider.get_name(art.system_id, art.id)


class AggregateActionsBiz:
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.svc = AggregateActionsService()

    def list(self, system_ids: List[str]) -> List[AggregateActionsBean]:
        """
        获取业务的聚合操作列表
        """
        svc_aggregate_actions = self.svc.list(system_ids)

        aggregate_action_list = AggregateActionsList(
            self.tenant_id, parse_obj_as(List[AggregateActionsBean], svc_aggregate_actions)
        )
        aggregate_action_list.fill_action_name()
        aggregate_action_list.fill_resource_type_name()

        return aggregate_action_list.aggregate_actions
