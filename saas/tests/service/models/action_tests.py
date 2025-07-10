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

from backend.service.action import Action
from backend.service.models.action import RelatedResourceType
from backend.service.models.instance_selection import ChainNode, InstanceSelection


class TestAction:
    def test_index_of_related_resource_type(self):
        action = Action(
            id="id",
            name="name",
            name_en="name_en",
            description="description",
            description_en="description_en",
            related_resource_types=[
                RelatedResourceType(
                    id="host",
                    system_id="bk_cmdb",
                    name_alias="test",
                    name_alias_en="test",
                    instance_selections=[
                        InstanceSelection(
                            id="test1",
                            system_id="bk_cmdb",
                            name="test1",
                            name_en="test1",
                            ignore_iam_path=False,
                            resource_type_chain=[ChainNode(system_id="bk_cmdb", id="host")],
                        )
                    ],
                )
            ],
        )

        assert action.index_of_related_resource_type("bk_cmdb", "host") == 0
        assert action.index_of_related_resource_type("bk_cmdb", "host1") == -1
