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

from backend.service.instance_selection import InstanceSelectionService
from backend.service.models.instance_selection import ChainNode, InstanceSelection, PathResourceType
from backend.service.resource_type import ResourceTypeService


class PathResourceTypeBean(PathResourceType):
    pass


class ChainNodeBean(ChainNode):
    name: str = ""
    name_en: str = ""


class BaseInstanceSelection(BaseModel):
    resource_type_chain: List[ChainNodeBean]

    def get_chain_system_set(self):
        return {node.system_id for node in self.resource_type_chain}


# NOTE: 这里存在 system_id / ignore_iam_path, 用于上层业务
class InstanceSelectionBean(BaseInstanceSelection, InstanceSelection):
    """
    业务层实例视图数据定义
    继承 Service 里 InstanceSelection 的所有字段和方法，
    但是 resource_type_chain 不一样多了一些字段和方法，所以这里继承的顺序必须是先
    BaseInstanceSelection，后 InstanceSelection
    """

    def match_path(self, path: List[PathResourceTypeBean]) -> bool:
        """匹配实例的链路是否与实例的链路是否一致"""
        return super().match_path(parse_obj_as(List[PathResourceType], path))

    def list_match_path_system_id(self, path: List[PathResourceTypeBean]) -> List[str]:
        """
        获取 path 匹配的 system_id 列表，用于填充 path 缺失的 system_id
        """
        return super().list_match_path_system_id(parse_obj_as(List[PathResourceType], path))


# NOTE: 原始注册的实例视图，此时未被引用，无需 system_id/ignore_iam_path
class RawInstanceSelectionBean(BaseInstanceSelection):
    id: str
    name: str
    name_en: str
    is_dynamic: bool


class InstanceSelectionList:
    def __init__(self, selections) -> None:  # Tuple[BizInstanceSelection, BizRawInstanceSelection]
        self.selections = selections

    def _list_system_id(self):
        """
        获取所有视图节点的 system_id
        """
        if not self.selections:
            return []

        return list(set.union(*[selection.get_chain_system_set() for selection in self.selections]))

    def fill_chain_node_name(self):
        """
        填充视图节点的 name
        """
        system_ids = self._list_system_id()
        name_provider = ResourceTypeService().get_system_resource_type_dict(system_ids)

        for selection in self.selections:
            for node in selection.resource_type_chain:
                node.name, node.name_en = name_provider.get_name(node.system_id, node.id)


class InstanceSelectionBiz:
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.svc = InstanceSelectionService(tenant_id)

    def list_by_action_resource_type(
        self, system_id: str, action_id: str, resource_type_system_id: str, resource_type_id: str
    ) -> List[InstanceSelectionBean]:
        """
        获取操作关联资源类型的实例视图列表
        用于前端展示
        """
        selections = self.svc.list_by_action_resource_type(
            system_id, action_id, resource_type_system_id, resource_type_id
        )
        if not selections:
            return []

        biz_selections = parse_obj_as(List[InstanceSelectionBean], selections)
        return self._fill_chain_node_name(biz_selections)

    def list_raw_by_system(self, system_id: str) -> List[RawInstanceSelectionBean]:
        """
        model builder 获取注册模型的实例视图
        """
        selections = self.svc.list_raw_by_system(system_id)
        biz_selections = parse_obj_as(List[RawInstanceSelectionBean], selections)
        return self._fill_chain_node_name(biz_selections)

    def _fill_chain_node_name(self, biz_selections):
        selection_list = InstanceSelectionList(biz_selections)
        selection_list.fill_chain_node_name()
        return selection_list.selections
