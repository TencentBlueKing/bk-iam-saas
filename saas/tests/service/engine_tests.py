"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-权限中心(BlueKing-IAM) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import pytest
from blue_krill.web.std_error import APIError

from backend.service.engine import EngineService, PolicyResource
from backend.service.models.policy import (
    Attribute,
    Condition,
    Instance,
    PathNode,
    PathNodeList,
    Policy,
    RelatedResource,
    ResourceGroup,
    ResourceGroupList,
    Value,
)


class TestEngineService:
    def test_gen_search_policy_resources(self):
        svc = EngineService()
        policy_resources = svc.gen_search_policy_resources(
            [Policy(action_id="action", policy_id=0, expired_at=0, resource_groups=ResourceGroupList(__root__=[]))]
        )

        assert policy_resources == [PolicyResource(action_id="action", resources=[])]

    def test_gen_query_by_policy_ok(self):
        svc = EngineService()
        policy_resource = svc._gen_query_by_policy(
            Policy(action_id="action", policy_id=0, expired_at=0, resource_groups=ResourceGroupList(__root__=[]))
        )

        assert policy_resource == PolicyResource(action_id="action", resources=[])

    def test_gen_query_by_policy_fail(self):
        svc = EngineService()

        policy = Policy(
            action_id="action",
            policy_id=0,
            expired_at=0,
            resource_groups=ResourceGroupList(
                __root__=[
                    ResourceGroup(
                        related_resource_types=[
                            RelatedResource(system_id="system", type="type1", condition=[]),
                            RelatedResource(system_id="system", type="type2", condition=[]),
                        ]
                    )
                ]
            ),
        )

        with pytest.raises(APIError):
            svc._gen_query_by_policy(policy)

    def test_gen_query_by_policy_ok_two(self):
        svc = EngineService()
        policy_resource = svc._gen_query_by_policy(
            Policy(
                action_id="action",
                policy_id=0,
                expired_at=0,
                resource_groups=ResourceGroupList(
                    __root__=[
                        ResourceGroup(
                            related_resource_types=[
                                RelatedResource(system_id="system", type="type", condition=[]),
                            ]
                        )
                    ]
                ),
            )
        )

        assert policy_resource == PolicyResource(action_id="action", resources=[])

    def test_gen_query_by_policy_ok_three(self):
        svc = EngineService()
        policy_resource = svc._gen_query_by_policy(
            Policy(
                action_id="action",
                policy_id=0,
                expired_at=0,
                resource_groups=ResourceGroupList(
                    __root__=[
                        ResourceGroup(
                            related_resource_types=[
                                RelatedResource(
                                    system_id="system",
                                    type="type",
                                    condition=[
                                        Condition(
                                            id="",
                                            instances=[
                                                Instance(
                                                    type="type",
                                                    path=[
                                                        PathNodeList(
                                                            __root__=[
                                                                PathNode(
                                                                    id="id",
                                                                    name="name",
                                                                    system_id="system",
                                                                    type="type",
                                                                )
                                                            ]
                                                        )
                                                    ],
                                                )
                                            ],
                                            attributes=[
                                                Attribute(id="os", name="os", values=[Value(id="linux", name="linux")])
                                            ],
                                        )
                                    ],
                                ),
                            ]
                        )
                    ]
                ),
            )
        )

        assert policy_resource == PolicyResource(
            action_id="action",
            resources=[
                {
                    "system": "system",
                    "type": "type",
                    "id": "id",
                    "attribute": {
                        "os": ["linux"],
                    },
                }
            ],
        )

    def test_gen_resources_by_condition(self):
        svc = EngineService()
        resources = svc._gen_resources_by_condition(
            RelatedResource(system_id="system", type="type", condition=[]),
            Condition(
                id="",
                instances=[
                    Instance(
                        type="type",
                        path=[
                            PathNodeList(__root__=[PathNode(id="id", name="name", system_id="system", type="type")])
                        ],
                    )
                ],
                attributes=[Attribute(id="os", name="os", values=[Value(id="linux", name="linux")])],
            ),
        )

        assert resources == [
            {
                "system": "system",
                "type": "type",
                "id": "id",
                "attribute": {
                    "os": ["linux"],
                },
            }
        ]

    def test_gen_resource_by_path_ok(self):
        svc = EngineService()
        resource = svc._gen_resource_by_path(
            RelatedResource(system_id="system", type="type", condition=[]),
            {"os": "linux"},
            [
                PathNode(id="id1", name="name", system_id="system", type="parent"),
                PathNode(id="id2", name="name", system_id="system", type="type"),
            ],
        )

        assert resource == {
            "system": "system",
            "type": "type",
            "id": "id2",
            "attribute": {
                "os": "linux",
                "_bk_iam_path_": "/parent,id1/",
            },
        }

    def test_gen_resource_by_path_ok_two(self):
        svc = EngineService()
        resource = svc._gen_resource_by_path(
            RelatedResource(system_id="system", type="type", condition=[]),
            {"os": ["linux"]},
            [
                PathNode(id="id1", name="name", system_id="system", type="parent1"),
                PathNode(id="id2", name="name", system_id="system", type="parent2"),
            ],
        )

        assert resource == {
            "system": "system",
            "type": "type",
            "id": "*",
            "attribute": {
                "os": ["linux"],
                "_bk_iam_path_": "/parent1,id1/parent2,id2/",
            },
        }
