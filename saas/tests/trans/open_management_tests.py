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

import mock
from django.conf import settings
from mock import MagicMock, patch

from backend.biz.policy import PolicyBeanList
from backend.trans.open_management import GradeManagerTrans, ManagementCommonTrans


class TestManagementCommonTrans:
    def test_to_policy_list_for_batch_action_and_resources(self):
        trans = ManagementCommonTrans(settings.BK_APP_TENANT_ID)
        trans.action_check_biz.check = mock.Mock(return_value=None)

        with (
            patch.object(
                PolicyBeanList, "fill_empty_fields", MagicMock(side_effect=lambda: None)
            ) as fake_fill_empty_fields,
            patch.object(
                PolicyBeanList, "check_instance_selection", MagicMock(side_effect=lambda: None)
            ) as fake_check_instance_selection,
        ):
            policy_list = trans.to_policy_list_for_batch_action_and_resources(
                "system",
                ["action1", "action2"],
                [
                    {
                        "system": "system",
                        "type": "type",
                        "paths": [
                            [
                                {
                                    "system": "system",
                                    "type": "type",
                                    "id": "id",
                                    "name": "name",
                                }
                            ]
                        ],
                    }
                ],
            )

            fake_fill_empty_fields.assert_called()
            fake_check_instance_selection.assert_called()

        assert policy_list.system_id == "system"
        assert len(policy_list.policies) == 2


class TestGradeManagerTrans:
    def test_to_role_info(self):
        trans = GradeManagerTrans(settings.BK_APP_TENANT_ID)
        trans.action_check_biz.check = mock.Mock(return_value=None)

        with (
            patch.object(
                PolicyBeanList, "fill_empty_fields", MagicMock(side_effect=lambda: None)
            ) as fake_fill_empty_fields,
            patch.object(
                PolicyBeanList, "check_instance_selection", MagicMock(side_effect=lambda: None)
            ) as fake_check_instance_selection,
        ):
            role = trans.to_role_info(
                {
                    "system": "system",
                    "name": "test",
                    "description": "description",
                    "members": [{"username": "admin"}],
                    "authorization_scopes": [
                        {
                            "system": "system",
                            "actions": [
                                {
                                    "id": "action1",
                                },
                                {
                                    "id": "action2",
                                },
                            ],
                            "resources": [
                                {
                                    "system": "system",
                                    "type": "type",
                                    "paths": [
                                        [
                                            {
                                                "system": "system",
                                                "type": "type",
                                                "id": "id",
                                                "name": "name",
                                            }
                                        ]
                                    ],
                                }
                            ],
                        }
                    ],
                },
                source_system_id="system",
            )

            fake_fill_empty_fields.assert_called()
            fake_check_instance_selection.assert_called()

        assert role.source_system_id == "system"
        assert role.name == "test"
        assert len(role.members) == 1
        assert len(role.authorization_scopes[0].actions) == 2
