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
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from backend.common.error_codes import error_codes
from backend.service.models.action import Action

from .instance_selection import InstanceSelection, PathResourceType
from .policy import ResourceInstance, group_paths

# TODO 只设计结构相关的转换, 重构提到 biz.open 相关模块
# TODO 需要删除这个文件


class ResourceCreatorSingleAction(BaseModel):
    """
    新建关联配置中单个Action
    """

    id: str
    required: bool


class ResourceCreatorActionConfig(BaseModel):
    """
    资源类型对应的被创建时所需的Action配置等
    """

    id: str
    actions: List[ResourceCreatorSingleAction]
    sub_resource_types: Optional[List["ResourceCreatorActionConfig"]] = None

    def get_resource_type_actions_map(self) -> Dict[str, List[ResourceCreatorSingleAction]]:
        """
        资源类型与Actions的映射，包括递归的
        """
        rta = {self.id: self.actions}

        if self.sub_resource_types:
            for srt in self.sub_resource_types:
                rta.update(srt.get_resource_type_actions_map())

        return rta


ResourceCreatorActionConfig.update_forward_refs()


class ResourceCreatorAction(BaseModel):
    """
    新建关联配置
    """

    mode: str
    config: List[ResourceCreatorActionConfig]


class ApplyPathNode(BaseModel):
    """
    申请与授权的拓扑节点
    """

    system_id: str = ""
    type: str
    id: str
    name: str

    def to_path_resource_type(self) -> PathResourceType:
        return PathResourceType(system_id=self.system_id, id=self.type)


class ApplyPathNodeList:
    def __init__(self, path: List[ApplyPathNode]) -> None:
        self.path = path

    def fill_instance_system(self, instance_selections: List[InstanceSelection]):
        """
        填充实例缺失的system_id
        """
        match_selections = self._list_match_instance_selections(instance_selections)
        if self.need_fill_system():
            self._fill_node_system_id_by_instance_selections(match_selections)

    def need_fill_system(self):
        """
        是否需要填充system_id
        """
        return not all([node.system_id for node in self.path])

    def _list_match_instance_selections(self, instance_selections: List[InstanceSelection]) -> List[InstanceSelection]:
        """
        筛选出匹配的实例视图
        """
        path_resource_types = [node.to_path_resource_type() for node in self.path]
        selections = [selection for selection in instance_selections if selection.match_path(path_resource_types)]
        if not selections:
            self._raise_match_selection_fail_exception()

        return selections

    def _fill_node_system_id_by_instance_selections(self, instance_selections: List[InstanceSelection]):
        """
        使用是视图填充path中缺失的system_id
        """
        # 取匹配的实例视图的第一个来做填充
        first_match_selection = instance_selections[0]
        path_resource_types = [node.to_path_resource_type() for node in self.path]

        # 获取到实例视图提供的系统列表, 填充到现有的path中
        system_ids = first_match_selection.list_match_path_system_id(path_resource_types)
        for node, system_id in zip(self.path, system_ids):
            node.system_id = system_id

        # 如果有多个实例视图可以匹配, 所有实例视图返回的system_ids必须一致
        for selection in instance_selections[1:]:
            if system_ids != selection.list_match_path_system_id(path_resource_types):
                self._raise_match_selection_fail_exception()

    def _raise_match_selection_fail_exception(self):
        raise error_codes.VALIDATE_ERROR.format("resource({}) not satisfy instance selection".format(self.path))


class ApplyRelatedResourceType(BaseModel):
    """
    申请与授权的关联资源
    """

    system_id: str
    type: str
    instances: List[List[ApplyPathNode]]
    attributes: List[Any] = []

    def to_resource_instance(self) -> ResourceInstance:
        """
        转换授权的资源结构
        """
        instances = group_paths(self.dict()["instances"])

        return ResourceInstance(
            system_id=self.system_id, type=self.type, instances=instances, type_name=self.type, type_name_en=self.type
        )

    def iter_path_list(self):
        for path in self.instances:
            yield ApplyPathNodeList(path)


# TODO 提到biz业务逻辑
class ApplyAction(BaseModel):
    """
    申请与授权的操作
    """

    id: str
    related_resource_types: List[ApplyRelatedResourceType]

    def fill_instance_system(self, action: Action):
        """
        填充实例缺失的system_id
        """
        for system_rrt, rrt in zip(action.related_resource_types, self.related_resource_types):
            selections = system_rrt.instance_selections
            if not selections:
                continue

            # 填充instance system_id
            for path_list in rrt.iter_path_list():
                path_list.fill_instance_system(selections)

    @classmethod
    def from_path(cls, data: Any) -> "ApplyAction":
        """
        授权到单个拓扑转换
        """
        return cls(
            id=data["action"]["id"],
            related_resource_types=[
                ApplyRelatedResourceType(
                    system_id=resource["system"],
                    type=resource["type"],
                    instances=[[ApplyPathNode(system_id=node["system"], **node) for node in resource["path"]]],
                )
                for resource in data["resources"]
            ],
        )

    @classmethod
    def from_batch_path(cls, data: Any) -> "ApplyAction":
        """
        批量拓扑授权转换
        """
        return cls(
            id=data["actions"][0]["id"],
            related_resource_types=[
                ApplyRelatedResourceType(
                    system_id=resource["system"],
                    type=resource["type"],
                    instances=[
                        [ApplyPathNode(system_id=node["system"], **node) for node in path]
                        for path in resource["paths"]
                    ],
                )
                for resource in data["resources"]
            ],
        )

    @classmethod
    def from_instance(cls, data: Any) -> "ApplyAction":
        """
        实例授权转换
        """
        return cls(
            id=data["action"]["id"],
            related_resource_types=[
                ApplyRelatedResourceType(
                    system_id=resource["system"],
                    type=resource["type"],
                    instances=[[ApplyPathNode(system_id=resource["system"], **resource)]],
                )
                for resource in data["resources"]
            ],
        )

    @classmethod
    def from_batch_instance(cls, data: Any) -> "ApplyAction":
        """
        批量实例授权转换
        """
        return cls(
            id=data["actions"][0]["id"],
            related_resource_types=[
                ApplyRelatedResourceType(
                    system_id=resource["system"],
                    type=resource["type"],
                    instances=[
                        [ApplyPathNode(system_id=resource["system"], type=resource["type"], **instance)]
                        for instance in resource["instances"]
                    ],
                )
                for resource in data["resources"]
            ],
        )


class ApplyActionList:
    def __init__(self, apply_actions: List[ApplyAction]) -> None:
        self.apply_actions = apply_actions

    def fill_instance_system(self, system_id: str):
        """
        填充实例缺失的system_id
        """
        from backend.service.action import ActionList, ActionService

        # TODO !!! service model 不能直接调用service, 提取到biz后, 没有问题
        actions = ActionService().list(system_id)
        action_list = ActionList(actions)

        for apply_action in self.apply_actions:
            action = action_list.get(apply_action.id)
            if not action:
                continue
            apply_action.fill_instance_system(action)
