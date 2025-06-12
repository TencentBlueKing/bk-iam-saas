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

from backend.biz.resource_creator_action import ResourceCreatorActionBean, ResourceCreatorActionBiz
from backend.service.models.resource_creator_action import ResourceCreatorActionConfigItem, ResourceCreatorActionInfo


class TestResourceCreatorActionBiz:
    def test_tiled_resource_creator_action(self):
        biz = ResourceCreatorActionBiz()
        resources = biz._tiled_resource_creator_action(
            [
                ResourceCreatorActionConfigItem(
                    id="1",
                    actions=[ResourceCreatorActionInfo(id="action1", required=True)],
                    sub_resource_types=[
                        ResourceCreatorActionConfigItem(
                            id="2",
                            actions=[ResourceCreatorActionInfo(id="action2", required=True)],
                            sub_resource_types=[],
                        )
                    ],
                )
            ]
        )

        assert resources == [
            ResourceCreatorActionBean(id="1", action_ids=["action1"]),
            ResourceCreatorActionBean(id="2", action_ids=["action2"]),
        ]
