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

from typing import List, Tuple

from backend.util.tree import TreeNode, bfs_traversal_tree, build_forest_with_parent_relations


def test_build_forest_with_tree_parent_relations():
    """理想情况，只有一棵树"""
    relations = [("A", None), ("B", "A"), ("C", "A"), ("D", "B"), ("E", "B")]
    roots = build_forest_with_parent_relations(relations)
    assert roots == [
        TreeNode(
            id="A",
            children=[
                TreeNode(
                    id="B",
                    children=[TreeNode(id="D", parent_id="B"), TreeNode(id="E", parent_id="B")],
                    parent_id="A",
                ),
                TreeNode(id="C", parent_id="A"),
            ],
            parent_id=None,
        )
    ]


def test_build_forest_with_forest_parent_relations():
    """森林关系测试"""
    relations = [("A", None), ("C", "B"), ("D", "B"), ("B", None)]
    roots = build_forest_with_parent_relations(relations)
    assert roots == [
        TreeNode(id="A", parent_id=None),
        TreeNode(id="B", children=[TreeNode(id="C", parent_id="B"), TreeNode(id="D", parent_id="B")], parent_id=None),
    ]


def test_build_forest_with_invalid_parent_relations():
    """森林关系测试，但是某父节点丢失"""
    relations = [("A", None), ("C", "B"), ("D", "B")]
    roots = build_forest_with_parent_relations(relations)
    assert roots == [TreeNode(id="A"), TreeNode(id="C"), TreeNode(id="D")]


def test_build_forest_with_empty_parent_relations():
    """空关系测试"""
    relations: List[Tuple[str, str | None]] = []
    roots = build_forest_with_parent_relations(relations)
    assert len(roots) == 0


def test_bfs_traversal_tree():
    """正常情况测试"""
    root = TreeNode(
        id="A",
        children=[
            TreeNode(id="B"),
            TreeNode(id="C"),
            TreeNode(
                id="D",
                children=[
                    TreeNode(id="E"),
                ],
            ),
        ],
    )
    nodes = list(bfs_traversal_tree(root))
    assert [n.id for n in nodes] == ["A", "B", "C", "D", "E"]


def test_bfs_traversal_tree_single():
    """单个节点测试"""
    root = TreeNode(id="A")
    nodes = list(bfs_traversal_tree(root))
    assert nodes == [root]
