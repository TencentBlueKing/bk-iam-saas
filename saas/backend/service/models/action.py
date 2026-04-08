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

import logging
from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel
from pydantic.fields import Field

from backend.service.constants import SelectionMode

from .instance_selection import InstanceSelection

logger = logging.getLogger("app")


class RelatedResourceType(BaseModel):
    system_id: str
    id: str
    selection_mode: str = SelectionMode.INSTANCE.value
    name: str = Field(alias="name_alias")
    name_en: str = Field(alias="name_alias_en")
    instance_selections: List[InstanceSelection] = []

    class Config:
        allow_population_by_field_name = True

    def __init__(self, **data: Any):
        if "instance_selections" in data and not isinstance(data["instance_selections"], list):
            data["instance_selections"] = []

        super().__init__(**data)

        if hasattr(self, "instance_selections"):
            # 过滤掉有错误数据的实例视图
            self.instance_selections = _filter_error_instance_selection(
                self.system_id, self.id, self.instance_selections
            )


class RelatedEnvironment(BaseModel):
    type: str


class Action(BaseModel):
    id: str
    name: str
    name_en: str
    description: str
    description_en: str
    type: str = ""
    hidden: bool = False
    related_resource_types: List[RelatedResourceType] = []
    related_actions: List[str] = []  # 依赖操作
    related_environments: List[RelatedEnvironment] = []
    sensitivity: int = 1

    tenant_id: str = ""

    def __init__(self, **data: Any):
        if "related_actions" in data and data["related_actions"] is None:
            data["related_actions"] = []
        if "related_environments" in data and data["related_environments"] is None:
            data["related_environments"] = []
        super().__init__(**data)

    def get_related_resource_type(self, system_id: str, resource_type_id: str) -> Optional[RelatedResourceType]:
        for rrt in self.related_resource_types:
            if rrt.system_id == system_id and rrt.id == resource_type_id:
                return rrt
        return None

    def index_of_related_resource_type(self, system_id: str, resource_type_id: str) -> int:
        for i, rrt in enumerate(self.related_resource_types):
            if rrt.system_id == system_id and rrt.id == resource_type_id:
                return i
        return -1

    def is_unrelated(self) -> bool:
        """
        是否是非关联
        """
        return len(self.related_resource_types) == 0

    def get_env_type_set(self) -> Set[str]:
        return {e.type for e in self.related_environments}


def _filter_error_instance_selection(
    system_id: str, resource_type_id: str, selections: List[InstanceSelection]
) -> List[InstanceSelection]:
    """
    过滤错误的实例视图：实例视图中不能存在资源类型 id 相同但是 system_id 不同的资源类型
    """
    checked_selections: List[InstanceSelection] = []

    resource_type_system: Dict[str, str] = {}
    for selection in selections:
        # 检验实例视图节点不存在类型 id 一样，系统 id 不一样的情况
        for node in selection.resource_type_chain:
            if node.id in resource_type_system and resource_type_system[node.id] != node.system_id:
                logger.error(
                    "system: %s related_type: %s "
                    "instance_selection: %s resource_type: %s, "
                    "resource_type_system_id: %s conflict",
                    system_id,
                    resource_type_id,
                    selection,
                    node.id,
                    node.system_id,
                )
                break

            resource_type_system[node.id] = node.system_id
        else:
            checked_selections.append(selection)

    return checked_selections
