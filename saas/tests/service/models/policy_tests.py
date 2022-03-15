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
from copy import deepcopy

import pytest

from backend.service.models.instance_selection import InstanceSelection, PathResourceType
from backend.service.models.policy import PathNode, PathNodeList


@pytest.fixture()
def path_node():
    return PathNode(
        id="id",
        name="name",
        system_id="system_id",
        type="type",
    )


class TestPathNode:
    def test_equals(self, path_node: PathNode):
        assert path_node == path_node
        copied_path_node = deepcopy(path_node)
        copied_path_node.type = "type1"
        assert path_node != copied_path_node
        copied_path_node = deepcopy(path_node)
        copied_path_node.system_id = "system_id1"
        assert path_node != copied_path_node

    def test_to_path_resource_type(self, path_node: PathNode):
        assert path_node.to_path_resource_type() == PathResourceType(system_id="system_id", id="type")

    def test_match_resource_type(sef, path_node: PathNode):
        assert path_node.match_resource_type("system_id", "type")


@pytest.fixture()
def path_node_list(path_node):
    copied_path_node = deepcopy(path_node)
    copied_path_node.type = "type1"
    return PathNodeList(__root__=[path_node, copied_path_node])


@pytest.fixture()
def instance_selection():
    return InstanceSelection(
        id="id",
        system_id="system_id",
        name="name",
        name_en="name_en",
        ignore_iam_path=False,
        resource_type_chain=[{"system_id": "system_id", "id": "type"}, {"system_id": "system_id", "id": "type1"}],
    )


class TestPathNodeList:
    def test_match_selection(self, path_node_list: PathNodeList, instance_selection: InstanceSelection):
        copied_path_node_list = deepcopy(path_node_list)
        copied_path_node_list.pop(1)
        assert copied_path_node_list.match_selection("system_id", "type", None)
        assert path_node_list.match_selection("system_id", "type", instance_selection)

    def test_ignore_path(self, path_node_list: PathNodeList, instance_selection: InstanceSelection):
        instance_selection.ignore_iam_path = True
        new_path_node_list = path_node_list.ignore_path(instance_selection)
        assert len(new_path_node_list) == 1
        assert new_path_node_list[0].type == "type1"
