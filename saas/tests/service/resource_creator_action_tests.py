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
import mock
from django.test import TestCase

from backend.service.models import ResourceCreatorActionConfig, ResourceCreatorSingleAction
from backend.service.resource_creator_action import ResourceCreatorAction, ResourceCreatorActionService


class ResourceCreatorActionServiceTests(TestCase):
    def test_get_resource_type_actions_map(self):
        rcac = ResourceCreatorActionConfig(
            **{
                "id": "test",
                "actions": [{"id": "test1", "required": False}, {"id": "test2", "required": False}],
                "sub_resource_types": [
                    {
                        "id": "test3",
                        "actions": [{"id": "test4", "required": False}, {"id": "test5", "required": False}],
                        "sub_resource_types": [],
                    }
                ],
            }
        )

        svc = ResourceCreatorActionService()
        svc.get = mock.Mock(return_value=ResourceCreatorAction(mode="test", config=[rcac]))

        result = svc._get_resource_type_actions_map("test")
        self.assertEqual(
            result,
            {
                "test": [
                    ResourceCreatorSingleAction(**{"id": "test1", "required": False}),
                    ResourceCreatorSingleAction(**{"id": "test2", "required": False}),
                ],
                "test3": [
                    ResourceCreatorSingleAction(**{"id": "test4", "required": False}),
                    ResourceCreatorSingleAction(**{"id": "test5", "required": False}),
                ],
            },
        )

    def test_get_actions(self):
        svc = ResourceCreatorActionService()
        svc._get_resource_type_actions_map = mock.Mock(
            return_value={
                "test": [
                    ResourceCreatorSingleAction(**{"id": "test1", "required": False}),
                    ResourceCreatorSingleAction(**{"id": "test2", "required": False}),
                ],
                "test3": [
                    ResourceCreatorSingleAction(**{"id": "test4", "required": False}),
                    ResourceCreatorSingleAction(**{"id": "test5", "required": False}),
                ],
            }
        )

        with self.assertRaises(Exception):
            svc.get_actions("test", "testx")

        result = svc.get_actions("test", "test")
        self.assertEqual(result, ["test1", "test2"])
