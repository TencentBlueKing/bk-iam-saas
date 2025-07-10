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

from backend.biz.policy import PathNodeBean
from backend.biz.template import ChainList, ChainNodeList
from backend.service.models.instance_selection import ChainNode


class TestChainNodeList:
    def test_match_prefix(self):
        cnl = ChainNodeList([ChainNode(system_id="system", id="id1"), ChainNode(system_id="system", id="id2")])

        assert cnl.match_prefix(ChainNodeList([ChainNode(system_id="system", id="id1")]))
        assert not cnl.match_prefix(ChainNodeList([ChainNode(system_id="system", id="id2")]))
        assert cnl.match_prefix(
            ChainNodeList([ChainNode(system_id="system", id="id1"), ChainNode(system_id="system", id="id2")])
        )

    def test_is_match_path(self):
        cnl = ChainNodeList([ChainNode(system_id="system_id", id="id1"), ChainNode(system_id="system_id", id="id2")])
        assert cnl.is_match_path(
            [
                PathNodeBean(
                    id="id",
                    name="name",
                    system_id="system_id",
                    type="id1",
                    type_name="type_name",
                    type_name_en="type_name_en",
                ),
                PathNodeBean(
                    id="id2",
                    name="name",
                    system_id="system_id",
                    type="id2",
                    type_name="type_name",
                    type_name_en="type_name_en",
                ),
            ]
        )

        assert not cnl.is_match_path(
            [
                PathNodeBean(
                    id="id1",
                    name="name",
                    system_id="system_id",
                    type="id1",
                    type_name="type_name",
                    type_name_en="type_name_en",
                ),
                PathNodeBean(
                    id="id2",
                    name="name",
                    system_id="system_id",
                    type="id2",
                    type_name="type_name",
                    type_name_en="type_name_en",
                ),
                PathNodeBean(
                    id="id3",
                    name="name",
                    system_id="system_id",
                    type="id3",
                    type_name="type_name",
                    type_name_en="type_name_en",
                ),
            ]
        )

        assert not cnl.is_match_path(
            [
                PathNodeBean(
                    id="id2",
                    name="name",
                    system_id="system_id",
                    type="id2",
                    type_name="type_name",
                    type_name_en="type_name_en",
                ),
            ]
        )


class TestChainList:
    def test_append(self):
        cnl = ChainNodeList([ChainNode(system_id="system", id="id1"), ChainNode(system_id="system", id="id2")])
        cl = ChainList([cnl])

        cl.append(cnl)
        assert len(cl.chains) == 1
        cl.append(ChainNodeList([ChainNode(system_id="system", id="id3")]))
        assert len(cl.chains) == 2

    def test_match_prefix(self):
        cnl = ChainNodeList([ChainNode(system_id="system", id="id1"), ChainNode(system_id="system", id="id2")])
        cl = ChainList([cnl])

        ncl = cl.match_prefix(cl)

        assert ncl.length == 1
