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
from backend.trans.open import OpenPolicy
from backend.trans.open_application import AccessSystemApplicationTrans


class TestAccessSystemApplicationTrans:
    def test_to_policy_list(self):
        trans = AccessSystemApplicationTrans(settings.BK_APP_TENANT_ID)

        trans.action_check_biz.check = mock.Mock(return_value=None)

        with (
            patch.object(
                PolicyBeanList, "fill_empty_fields", MagicMock(side_effect=lambda: None)
            ) as fake_fill_empty_fields,
            patch.object(
                PolicyBeanList, "check_instance_selection", MagicMock(side_effect=lambda: None)
            ) as fake_check_instance_selection,
            patch.object(
                OpenPolicy, "fill_instance_system", MagicMock(side_effect=lambda tenant_id: None)
            ) as fake_fill_instance_system,
            patch.object(
                OpenPolicy, "fill_instance_name", MagicMock(side_effect=lambda tenant_id: None)
            ) as fake_fill_instance_name,
        ):
            policy_list = trans.to_policy_list(
                {
                    "system": "system",
                    "actions": [
                        {
                            "id": "action1",
                            "related_resource_types": [
                                {
                                    "system": "system",
                                    "type": "type",
                                    "instances": [
                                        [
                                            {
                                                "system": "system",
                                                "type": "type",
                                                "id": "id",
                                            }
                                        ]
                                    ],
                                    "attributes": [],
                                }
                            ],
                        }
                    ],
                }
            )

            fake_fill_empty_fields.assert_called()
            fake_check_instance_selection.assert_called()
            fake_fill_instance_system.assert_called()
            fake_fill_instance_name.assert_called()

        assert policy_list.system_id == "system"
        assert len(policy_list.policies) == 1
