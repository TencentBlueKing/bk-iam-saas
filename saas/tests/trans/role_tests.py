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

from backend.biz.action import ActionBean, ActionBeanList, RelatedResourceTypeBean
from backend.biz.policy import PolicyBeanList
from backend.service.models.subject import Subject
from backend.trans.role import RoleTrans


class TestRoleTrans:
    def test_from_role_data(self):
        trans = RoleTrans(settings.BK_APP_TENANT_ID)

        trans.policy_trans.action_check_biz.check_action_resource_group = mock.Mock(return_value=None)
        trans.policy_trans._get_action_list = mock.Mock(
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
                PolicyBeanList, "check_resource_name", MagicMock(side_effect=lambda: None)
            ) as fake_check_resource_name,
        ):
            role = trans.from_role_data(
                {
                    "name": "role",
                    "description": "role",
                    "members": [{"username": "admin"}],
                    "subject_scopes": [{"type": "*", "id": "*"}],
                    "authorization_scopes": [
                        {
                            "system_id": "system",
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
                        }
                    ],
                }
            )

            fake_fill_empty_fields.assert_called()
            fake_check_instance_selection.assert_called()
            fake_check_resource_name.assert_called()

        assert role.name == "role"
        assert role.member_usernames == ["admin"]
        assert role.subject_scopes == [Subject(type="*", id="*")]
        assert role.authorization_scopes[0].system_id == "system"
        assert len(role.authorization_scopes[0].actions) == 2
