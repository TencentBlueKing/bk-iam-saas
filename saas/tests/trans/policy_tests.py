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

import pytest
from blue_krill.web.std_error import APIError
from django.conf import settings
from mock import MagicMock, Mock, patch

from backend.biz.action import ActionBean, ActionBeanList, RelatedResourceTypeBean
from backend.biz.policy import ConditionBean, PolicyBeanList
from backend.trans.policy import PolicyTrans


class TestPolicyTrans:
    def test_gen_instance_condition_by_aggregate_resources(self):
        trans = PolicyTrans(settings.BK_APP_TENANT_ID)
        condition = trans._gen_instance_condition_by_aggregate_resources(
            [
                {
                    "system_id": "system",
                    "id": "type",
                    "instances": [
                        {"id": "id", "name": "name"},
                    ],
                }
            ]
        )

        assert len(condition.instances) == 1

    def test_gen_policy_by_action_and_condition(self):
        trans = PolicyTrans(settings.BK_APP_TENANT_ID)
        policy = trans._gen_policy_by_action_and_condition(
            ActionBean(
                id="action1",
                name="action1",
                name_en="action1",
                description="",
                description_en="",
                related_resource_types=[RelatedResourceTypeBean(system_id="system", id="type", name="", name_en="")],
            ),
            ConditionBean(id="", instances=[], attributes=[]),
            expired_at=0,
        )

        assert policy.action_id == "action1"
        assert len(policy.resource_groups) == 1
        assert policy.expired_at == 0

    def test_get_action(self):
        trans = PolicyTrans(settings.BK_APP_TENANT_ID)
        trans._get_action_list = Mock(
            return_value=ActionBeanList(
                [
                    ActionBean(
                        id="action1",
                        name="action1",
                        name_en="action1",
                        description="",
                        description_en="",
                        related_resource_types=[
                            RelatedResourceTypeBean(system_id="system", id="type", name="", name_en="")
                        ],
                    )
                ]
            )
        )
        action = trans._get_action("system", "action1")
        assert action.id == "action1"

        with pytest.raises(APIError):
            trans._get_action("system", "action2")

    def test_from_aggregate_actions(self):
        trans = PolicyTrans(settings.BK_APP_TENANT_ID)
        trans._get_action_list = Mock(
            return_value=ActionBeanList(
                [
                    ActionBean(
                        id="action1",
                        name="action1",
                        name_en="action1",
                        description="",
                        description_en="",
                        related_resource_types=[
                            RelatedResourceTypeBean(system_id="system", id="type", name="", name_en="")
                        ],
                    )
                ]
            )
        )

        with patch.object(
            PolicyBeanList, "check_instance_selection", MagicMock(side_effect=lambda: None)
        ) as fake_check_instance_selection:
            policy_list_dict = trans.from_aggregate_actions(
                [
                    {
                        "actions": [
                            {"system_id": "system", "id": "action1"},
                        ],
                        "aggregate_resource_types": [
                            {
                                "system_id": "system",
                                "id": "type",
                                "instances": [
                                    {"id": "id", "name": "name"},
                                ],
                            }
                        ],
                        "expired_at": 0,
                    }
                ]
            )

            fake_check_instance_selection.assert_called()

        assert len(policy_list_dict) == 1
        assert len(policy_list_dict["system"].policies) == 1

    def test_from_actions(self):
        trans = PolicyTrans(settings.BK_APP_TENANT_ID)
        trans.action_check_biz.check_action_resource_group = Mock(return_value=None)
        with patch.object(
            PolicyBeanList, "check_instance_selection", MagicMock(side_effect=lambda: None)
        ) as fake_check_instance_selection:
            policy_list = trans.from_actions(
                "system",
                [
                    {
                        "id": "action2",
                        "resource_groups": [],
                        "expired_at": 0,
                    }
                ],
            )
            fake_check_instance_selection.assert_called()

        assert policy_list.system_id == "system"
        assert len(policy_list.policies) == 1

    def test_from_aggregate_actions_and_actions(self):
        trans = PolicyTrans(settings.BK_APP_TENANT_ID)
        trans.action_check_biz.check_action_resource_group = Mock(return_value=None)
        trans._get_action_list = Mock(
            return_value=ActionBeanList(
                [
                    ActionBean(
                        id="action1",
                        name="action1",
                        name_en="action1",
                        description="",
                        description_en="",
                        related_resource_types=[
                            RelatedResourceTypeBean(system_id="system", id="type", name="", name_en="")
                        ],
                    )
                ]
            )
        )

        with patch.object(
            PolicyBeanList, "check_instance_selection", MagicMock(side_effect=lambda: None)
        ) as fake_check_instance_selection:
            policy_list = trans.from_aggregate_actions_and_actions(
                "system",
                {
                    "actions": [
                        {
                            "id": "action2",
                            "resource_groups": [],
                            "expired_at": 0,
                        }
                    ],
                    "aggregations": [
                        {
                            "actions": [
                                {"system_id": "system", "id": "action1"},
                            ],
                            "aggregate_resource_types": [
                                {
                                    "system_id": "system",
                                    "id": "type",
                                    "instances": [
                                        {"id": "id", "name": "name"},
                                    ],
                                }
                            ],
                            "expired_at": 0,
                        }
                    ],
                },
            )

            fake_check_instance_selection.assert_called()

        assert policy_list.system_id == "system"
        assert len(policy_list.policies) == 2
