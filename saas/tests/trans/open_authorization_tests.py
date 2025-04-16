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
from blue_krill.web.std_error import APIError
from mock import MagicMock, Mock, patch

from backend.biz.action import ActionBean, ActionBeanList, RelatedResourceTypeBean
from backend.biz.policy import PolicyBeanList
from backend.trans.open import OpenPolicy
from backend.trans.open_authorization import AuthorizationTrans


class TestAuthorizationTrans:
    def test_to_policy_list_for_instance(self):
        trans = AuthorizationTrans()
        trans.action_check_biz.check = Mock(return_value=None)

        with (
            patch.object(
                PolicyBeanList, "fill_empty_fields", MagicMock(side_effect=lambda: None)
            ) as fake_fill_empty_fields,
            patch.object(
                PolicyBeanList, "check_instance_selection", MagicMock(side_effect=lambda: None)
            ) as fake_check_instance_selection,
        ):
            policy_list = trans.to_policy_list_for_instance(
                "system",
                "action1",
                [
                    {
                        "system": "system",
                        "type": "type",
                        "id": "id",
                        "name": "name",
                    }
                ],
            )

            fake_fill_empty_fields.assert_called()
            fake_check_instance_selection.assert_called()

        assert policy_list.system_id == "system"
        assert len(policy_list.policies) == 1
        assert policy_list.policies[0].action_id == "action1"

    def test_to_policy_list_for_instances(self):
        trans = AuthorizationTrans()
        trans.action_check_biz.check = Mock(return_value=None)

        with (
            patch.object(
                PolicyBeanList, "fill_empty_fields", MagicMock(side_effect=lambda: None)
            ) as fake_fill_empty_fields,
            patch.object(
                PolicyBeanList, "check_instance_selection", MagicMock(side_effect=lambda: None)
            ) as fake_check_instance_selection,
        ):
            policy_list = trans.to_policy_list_for_instances(
                "system",
                ["action1", "action2"],
                [
                    {
                        "system": "system",
                        "type": "type",
                        "instances": [
                            {
                                "id": "id",
                                "name": "name",
                            }
                        ],
                    }
                ],
            )

            fake_fill_empty_fields.assert_called()
            fake_check_instance_selection.assert_called()

        assert policy_list.system_id == "system"
        assert len(policy_list.policies) == 2
        assert policy_list.policies[0].action_id == "action1"

    def test_to_policy_list_for_path(self):
        trans = AuthorizationTrans()
        trans.action_check_biz.check = Mock(return_value=None)

        with (
            patch.object(
                PolicyBeanList, "fill_empty_fields", MagicMock(side_effect=lambda: None)
            ) as fake_fill_empty_fields,
            patch.object(
                PolicyBeanList, "check_instance_selection", MagicMock(side_effect=lambda: None)
            ) as fake_check_instance_selection,
            patch.object(
                OpenPolicy, "fill_instance_system", MagicMock(side_effect=lambda: None)
            ) as fake_fill_instance_system,
        ):
            policy_list = trans.to_policy_list_for_path(
                "system",
                "action1",
                [
                    {
                        "system": "system",
                        "type": "type",
                        "path": [
                            {
                                "system": "system",
                                "type": "type",
                                "id": "id",
                                "name": "name",
                            }
                        ],
                    }
                ],
            )

            fake_fill_empty_fields.assert_called()
            fake_check_instance_selection.assert_called()
            fake_fill_instance_system.assert_called()

        assert policy_list.system_id == "system"
        assert len(policy_list.policies) == 1
        assert policy_list.policies[0].action_id == "action1"

    def test_to_policy_list_for_paths(self):
        trans = AuthorizationTrans()
        trans.action_check_biz.check = Mock(return_value=None)

        with (
            patch.object(
                PolicyBeanList, "fill_empty_fields", MagicMock(side_effect=lambda: None)
            ) as fake_fill_empty_fields,
            patch.object(
                PolicyBeanList, "check_instance_selection", MagicMock(side_effect=lambda: None)
            ) as fake_check_instance_selection,
            patch.object(
                OpenPolicy, "fill_instance_system", MagicMock(side_effect=lambda: None)
            ) as fake_fill_instance_system,
        ):
            policy_list = trans.to_policy_list_for_paths(
                "system",
                ["action1", "action2"],
                [
                    {
                        "system": "system",
                        "type": "type",
                        "path": [
                            {
                                "system": "system",
                                "type": "type",
                                "id": "id",
                                "name": "name",
                            }
                        ],
                    }
                ],
            )

            fake_fill_empty_fields.assert_called()
            fake_check_instance_selection.assert_called()
            fake_fill_instance_system.assert_called()

        assert policy_list.system_id == "system"
        assert len(policy_list.policies) == 2
        assert policy_list.policies[0].action_id == "action1"
        assert policy_list.policies[1].action_id == "action2"

    def test_gen_action_for_resources_of_creator(self):
        trans = AuthorizationTrans()
        trans.action_biz.list = Mock(
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

        with pytest.raises(APIError):
            trans._gen_action_for_resources_of_creator("system", ["action2"], [])

        actions = trans._gen_action_for_resources_of_creator("system", ["action1"], [])
        assert len(actions) == 1
        assert actions[0]["system_id"] == "system"
        assert actions[0]["action_id"] == "action1"

    def test_to_policy_list_for_instances_of_creator(self):
        trans = AuthorizationTrans()
        trans.action_check_biz.check = Mock(return_value=None)
        trans.action_biz.list = Mock(
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

        with (
            patch.object(
                PolicyBeanList, "fill_empty_fields", MagicMock(side_effect=lambda: None)
            ) as fake_fill_empty_fields,
            patch.object(
                PolicyBeanList, "check_instance_selection", MagicMock(side_effect=lambda: None)
            ) as fake_check_instance_selection,
            patch.object(
                OpenPolicy, "fill_instance_system", MagicMock(side_effect=lambda: None)
            ) as fake_fill_instance_system,
            patch.object(
                OpenPolicy, "fill_instance_name", MagicMock(side_effect=lambda: None)
            ) as fake_fill_instance_name,
        ):
            policy_list = trans.to_policy_list_for_instances_of_creator(
                "system",
                ["action1"],
                "type",
                [
                    {
                        "id": "id",
                        "name": "name",
                        "ancestors": [{"system": "system", "type": "ancestor", "id": "ancestor1"}],
                    }
                ],
            )

            fake_fill_empty_fields.assert_called()
            fake_check_instance_selection.assert_called()
            fake_fill_instance_system.assert_called()
            fake_fill_instance_name.assert_called()

        assert policy_list.system_id == "system"
        assert len(policy_list.policies) == 1
        assert policy_list.policies[0].action_id == "action1"
        assert (
            len(
                policy_list.policies[0]
                .resource_groups[0]
                .related_resource_types[0]
                .condition[0]
                .instances[0]
                .path[0]
                .__root__
            )
            == 2
        )

    def test_to_policy_list_for_attributes_of_creator(self):
        trans = AuthorizationTrans()
        trans.action_check_biz.check = Mock(return_value=None)
        trans.action_biz.list = Mock(
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

        with (
            patch.object(
                PolicyBeanList, "fill_empty_fields", MagicMock(side_effect=lambda: None)
            ) as fake_fill_empty_fields,
            patch.object(
                PolicyBeanList, "check_instance_selection", MagicMock(side_effect=lambda: None)
            ) as fake_check_instance_selection,
        ):
            policy_list = trans.to_policy_list_for_attributes_of_creator(
                "system",
                ["action1"],
                "type",
                [
                    {
                        "id": "id",
                        "name": "name",
                        "values": [
                            {"id": "id", "name": "name"},
                        ],
                    },
                ],
            )

            fake_fill_empty_fields.assert_called()
            fake_check_instance_selection.assert_called()

        assert policy_list.system_id == "system"
        assert len(policy_list.policies) == 1
        assert policy_list.policies[0].action_id == "action1"
        assert len(policy_list.policies[0].resource_groups[0].related_resource_types[0].condition[0].instances) == 0
        assert len(policy_list.policies[0].resource_groups[0].related_resource_types[0].condition[0].attributes) == 1
