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

from typing import Dict, Generator, Generic, Hashable, List, Tuple, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=Hashable)


class TreeNode(BaseModel, Generic[T]):
    id: T
    children: List["TreeNode"] = []
    parent_id: T | None = None


def build_forest_with_parent_relations(relations: List[Tuple[T, T | None]]) -> List[TreeNode]:
    """根据提供的父子关系构建树/森林，父子关系结构：(node_id, parent_id)"""
    node_map: Dict[T, TreeNode[T]] = {
        node_id: TreeNode(id=node_id, parent_id=parent_id) for node_id, parent_id in relations
    }
    roots = []
    for node_id, parent_id in relations:
        node = node_map[node_id]
        if not (parent_id and parent_id in node_map):
            roots.append(node)
            # 如果没有父节点或父节点不在映射中，则认为是根节点
            node.parent_id = None
            continue

        node_map[parent_id].children.append(node)

    return roots


def bfs_traversal_tree(root: TreeNode) -> Generator[TreeNode, None, None]:
    """广度优先遍历树，确保父节点都在子节点之前"""
    queue = [root]
    while queue:
        node = queue.pop(0)
        yield node
        queue.extend(node.children)
