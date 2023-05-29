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

import pytest

from backend.apps.role.tasks import AuthScopeMerger
from backend.service.role import AuthScopeAction, AuthScopeSystem
from backend.util.uuid import gen_uuid


@pytest.fixture()
def old_action_auth_scope() -> AuthScopeAction:
    return AuthScopeAction.parse_obj(
        {
            "id": "test",
            "resource_groups": [
                {
                    "related_resource_types": [
                        {
                            "system_id": "test",
                            "type": "type",
                            "condition": [
                                {
                                    "id": gen_uuid(),
                                    "instances": [
                                        {
                                            "type": "type",
                                            "path": [
                                                [
                                                    {
                                                        "id": "id1",
                                                        "name": "name1",
                                                        "system_id": "test",
                                                        "type": "type",
                                                    }
                                                ]
                                            ],
                                        }
                                    ],
                                    "attributes": [],
                                }
                            ],
                        },
                    ]
                }
            ],
        }
    )


@pytest.fixture()
def new_action_auth_scope() -> AuthScopeAction:
    return AuthScopeAction.parse_obj(
        {
            "id": "test",
            "resource_groups": [
                {
                    "related_resource_types": [
                        {
                            "system_id": "test",
                            "type": "type",
                            "condition": [
                                {
                                    "id": gen_uuid(),
                                    "instances": [
                                        {
                                            "type": "type",
                                            "path": [
                                                [
                                                    {
                                                        "id": "id2",
                                                        "name": "name2",
                                                        "system_id": "test",
                                                        "type": "type",
                                                    }
                                                ]
                                            ],
                                        }
                                    ],
                                    "attributes": [],
                                }
                            ],
                        },
                    ]
                }
            ],
        }
    )


class TestAuthScopeMerger:
    def test_merge_action_auth_scope(self, old_action_auth_scope, new_action_auth_scope):
        AuthScopeMerger(None, None)._merge_action_auth_scope(old_action_auth_scope, new_action_auth_scope)
        assert (
            len(old_action_auth_scope.resource_groups[0].related_resource_types[0].condition[0].instances[0].path) == 2
        )

    def test_merge_system_auth_scope(self, old_action_auth_scope, new_action_auth_scope):
        old = AuthScopeSystem(
            system_id="test",
            actions=[
                AuthScopeAction.parse_obj(
                    {
                        "id": "test1",
                        "resource_groups": [
                            {
                                "related_resource_types": [
                                    {
                                        "system_id": "test",
                                        "type": "type",
                                        "condition": [
                                            {
                                                "id": gen_uuid(),
                                                "instances": [
                                                    {
                                                        "type": "type",
                                                        "path": [
                                                            [
                                                                {
                                                                    "id": "id2",
                                                                    "name": "name2",
                                                                    "system_id": "test",
                                                                    "type": "type",
                                                                }
                                                            ]
                                                        ],
                                                    }
                                                ],
                                                "attributes": [],
                                            }
                                        ],
                                    },
                                ]
                            }
                        ],
                    }
                ),
                old_action_auth_scope,
            ],
        )

        new = AuthScopeSystem(
            system_id="test",
            actions=[
                new_action_auth_scope,
                AuthScopeAction.parse_obj(
                    {
                        "id": "test2",
                        "resource_groups": [
                            {
                                "related_resource_types": [
                                    {
                                        "system_id": "test",
                                        "type": "type",
                                        "condition": [
                                            {
                                                "id": gen_uuid(),
                                                "instances": [
                                                    {
                                                        "type": "type",
                                                        "path": [
                                                            [
                                                                {
                                                                    "id": "id2",
                                                                    "name": "name2",
                                                                    "system_id": "test",
                                                                    "type": "type",
                                                                }
                                                            ]
                                                        ],
                                                    }
                                                ],
                                                "attributes": [],
                                            }
                                        ],
                                    },
                                ]
                            }
                        ],
                    }
                ),
            ],
        )

        AuthScopeMerger(None, None)._merge_system_auth_scope(old, new)
        assert len(old.actions) == 3
        assert len(old.actions[1].resource_groups[0].related_resource_types[0].condition[0].instances[0].path) == 2

    def test_merge(self):
        old = [AuthScopeSystem(system_id="test1", actions=[]), AuthScopeSystem(system_id="test2", actions=[])]
        new = [AuthScopeSystem(system_id="test2", actions=[]), AuthScopeSystem(system_id="test3", actions=[])]
        all = AuthScopeMerger(old, new).merge()
        assert len(all) == 3
