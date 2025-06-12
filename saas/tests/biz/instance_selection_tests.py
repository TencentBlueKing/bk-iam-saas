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

from mock import MagicMock, patch

from backend.biz.instance_selection import ChainNodeBean, InstanceSelectionList, RawInstanceSelectionBean
from backend.service.models.resource_type import ResourceTypeDict
from backend.service.resource_type import ResourceTypeService


class TestInstanceSelectionList:
    def test_list_system_id(self):
        isl = InstanceSelectionList(
            [
                RawInstanceSelectionBean(
                    id="",
                    name="",
                    name_en="",
                    is_dynamic=False,
                    resource_type_chain=[
                        ChainNodeBean(system_id="system", id="test1"),
                        ChainNodeBean(system_id="system", id="test2"),
                    ],
                )
            ]
        )
        assert isl._list_system_id() == ["system"]

    def test_fill_chain_node_name(self):
        isl = InstanceSelectionList(
            [
                RawInstanceSelectionBean(
                    id="",
                    name="",
                    name_en="",
                    is_dynamic=False,
                    resource_type_chain=[
                        ChainNodeBean(system_id="system", id="test1"),
                        ChainNodeBean(system_id="system", id="test2"),
                    ],
                )
            ]
        )

        with patch.object(
            ResourceTypeService,
            "get_system_resource_type_dict",
            MagicMock(
                side_effect=lambda *args: ResourceTypeDict(
                    data={
                        ("system", "test1"): {"name": "name1", "name_en": "name_en1"},
                        ("system", "test2"): {"name": "name2", "name_en": "name_en2"},
                    }
                )
            ),
        ) as fake_get_resource_type_dict:
            isl.fill_chain_node_name()

            fake_get_resource_type_dict.assert_called()

        assert isl.selections[0].resource_type_chain[0].name == "name1"
        assert isl.selections[0].resource_type_chain[0].name_en == "name_en1"
        assert isl.selections[0].resource_type_chain[1].name == "name2"
        assert isl.selections[0].resource_type_chain[1].name_en == "name_en2"
