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

from backend.service.models.instance_selection import ChainNode, InstanceSelection, PathResourceType


class TestInstanceSelection:
    def test_match_path_ignore_path(self):
        ins = InstanceSelection(
            id="id",
            system_id="system",
            name="",
            name_en="",
            ignore_iam_path=True,
            resource_type_chain=[ChainNode(system_id="system", id="test1"), ChainNode(system_id="system", id="test2")],
        )

        assert ins.match_path([PathResourceType(system_id="system", id="test2")])

    def test_match_path_false(self):
        ins = InstanceSelection(
            id="id",
            system_id="system",
            name="",
            name_en="",
            ignore_iam_path=False,
            resource_type_chain=[ChainNode(system_id="system", id="test1"), ChainNode(system_id="system", id="test2")],
        )

        assert not ins.match_path(
            [PathResourceType(system_id="system", id="test1"), PathResourceType(system_id="system", id="test3")]
        )

    def test_match_path_false_two(self):
        ins = InstanceSelection(
            id="id",
            system_id="system",
            name="",
            name_en="",
            ignore_iam_path=False,
            resource_type_chain=[ChainNode(system_id="system", id="test1"), ChainNode(system_id="system", id="test2")],
        )

        assert not ins.match_path(
            [
                PathResourceType(system_id="system", id="test1"),
                PathResourceType(system_id="system", id="test2"),
                PathResourceType(system_id="system", id="test2"),
                PathResourceType(system_id="system", id="test3"),
            ]
        )

    def test_match_path_ok(self):
        ins = InstanceSelection(
            id="id",
            system_id="system",
            name="",
            name_en="",
            ignore_iam_path=False,
            resource_type_chain=[ChainNode(system_id="system", id="test1"), ChainNode(system_id="system", id="test2")],
        )

        assert ins.match_path(
            [
                PathResourceType(system_id="system", id="test1"),
                PathResourceType(system_id="system", id="test2"),
                PathResourceType(system_id="system", id="test2"),
                PathResourceType(system_id="system", id="test2"),
            ]
        )

    def test_match_path_two(self):
        ins = InstanceSelection(
            id="id",
            system_id="system",
            name="",
            name_en="",
            ignore_iam_path=False,
            resource_type_chain=[ChainNode(system_id="system", id="test1"), ChainNode(system_id="system", id="test2")],
        )

        assert ins.match_path(
            [PathResourceType(system_id="system", id="test1"), PathResourceType(system_id="system", id="test2")]
        )

    def test_list_match_path_system_id_ignore_path(self):
        ins = InstanceSelection(
            id="id",
            system_id="system",
            name="",
            name_en="",
            ignore_iam_path=True,
            resource_type_chain=[ChainNode(system_id="system", id="test1"), ChainNode(system_id="system", id="test2")],
        )

        assert ins.list_match_path_system_id([PathResourceType(system_id="", id="test2")]) == ["system"]

    def test_list_match_path_system_id_ok(self):
        ins = InstanceSelection(
            id="id",
            system_id="system",
            name="",
            name_en="",
            ignore_iam_path=False,
            resource_type_chain=[ChainNode(system_id="system", id="test1"), ChainNode(system_id="system", id="test2")],
        )

        assert ins.list_match_path_system_id(
            [
                PathResourceType(system_id="", id="test1"),
                PathResourceType(system_id="", id="test2"),
                PathResourceType(system_id="", id="test2"),
                PathResourceType(system_id="", id="test2"),
            ]
        ) == ["system", "system", "system", "system"]
