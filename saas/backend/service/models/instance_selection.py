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


class PathResourceType(BaseModel):
    """
    用于做视图校验的结构
    !!! 所有需要做视图校验的地方，都需要先转换成 PathResourceType
    """

    system_id: str
    id: str


class ChainNode(BaseModel):
    system_id: str
    id: str

    def match_resource_type(self, resource_type: PathResourceType) -> bool:
        # 兼容无权限申请的 system_id 可能为空情况
        return self.id == resource_type.id and (resource_type.system_id in (self.system_id, ""))

    def match_chain_node(self, node: "ChainNode") -> bool:
        return self.system_id == node.system_id and self.id == node.id

    def __hash__(self):
        return hash((self.system_id, self.id))

    def __eq__(self, other) -> bool:
        return self.system_id == other.system_id and self.id == other.id


# NOTE: 这里存在 system_id / ignore_iam_path, 用于上层业务
class InstanceSelection(BaseModel):
    id: str
    system_id: str
    name: str
    name_en: str
    ignore_iam_path: bool
    resource_type_chain: List[ChainNode]

    tenant_id: str = ""

    def match_path(self, path: List[PathResourceType]) -> bool:
        """
        匹配实例的链路是否与实例的链路是否一致
        """
        # 如果是忽略路径的实例视图，并且实例链路只有一层，可以只匹配视图的最后一层
        if self.ignore_iam_path and len(path) == 1:  # noqa: SIM102
            if self.resource_type_chain[-1].match_resource_type(path[0]):
                return True

        # 严格匹配视图与实例的每个一个节点
        for chain_node, resource_type in zip(self.resource_type_chain, path, strict=False):
            if not chain_node.match_resource_type(resource_type):
                return False

        # !!! 用户管理的特殊逻辑，对于长度大于视图链路的路径，所有后面的节点需要与视图的最后一个节点匹配
        if len(path) > len(self.resource_type_chain):
            last_chain_node = self.resource_type_chain[-1]
            for resource_type in path[len(self.resource_type_chain) :]:
                if not last_chain_node.match_resource_type(resource_type):
                    return False

        return True

    def list_match_path_system_id(self, path: List[PathResourceType]) -> List[str]:
        """
        获取 path 匹配的 system_id 列表，用于填充 path 缺失的 system_id
        !!! path 必须与视图匹配才能调用
        """
        assert self.match_path(path)

        if self.ignore_iam_path and len(path) == 1:
            last_chain_node = self.resource_type_chain[-1]
            if last_chain_node.match_resource_type(path[0]):
                return [last_chain_node.system_id]

        system_ids = [chain_node.system_id for chain_node, _ in zip(self.resource_type_chain, path, strict=False)]

        if len(path) > len(self.resource_type_chain):
            last_chain_node = self.resource_type_chain[-1]
            for _ in path[len(self.resource_type_chain) :]:
                system_ids.append(last_chain_node.system_id)

        return system_ids


# NOTE: 原始注册的实例视图，此时未被引用，无需 system_id/ignore_iam_path
class RawInstanceSelection(BaseModel):
    id: str
    name: str
    name_en: str
    is_dynamic: bool
    resource_type_chain: List[ChainNode]
