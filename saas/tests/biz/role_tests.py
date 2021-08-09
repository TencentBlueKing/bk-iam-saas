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
from django.test import TestCase

from backend.biz.policy import InstanceBean
from backend.biz.role import ActionScopeDiffer


class TestInstanceDiff(TestCase):
    def test_instance(self):
        template_instances = [
            InstanceBean(
                type="",
                path=[
                    [
                        {"type": "biz", "id": "biz1"},
                        {"type": "set", "id": "set1"},
                        {"type": "module", "id": "module1"},
                        {"type": "host", "id": "host1"},
                    ]
                ],
            ),
            InstanceBean(type="", path=[[{"type": "biz", "id": "biz2"}, {"type": "set", "id": "set2"}]]),
        ]

        scope_instances = [
            InstanceBean(type="", path=[[{"type": "biz", "id": "biz1"}]]),
            InstanceBean(type="", path=[[{"type": "biz", "id": "biz2"}]]),
        ]

        self.assertTrue(ActionScopeDiffer(None, None)._diff_instances(template_instances, scope_instances))

    def test_false(self):
        template_instances = [
            InstanceBean(
                type="",
                path=[
                    [
                        {"type": "biz", "id": "biz1"},
                        {"type": "set", "id": "set1"},
                        {"type": "module", "id": "module1"},
                        {"type": "host", "id": "host1"},
                    ]
                ],
            ),
            InstanceBean(type="", path=[[{"type": "biz", "id": "biz3"}, {"type": "set", "id": "set2"}]]),
        ]

        scope_instances = [
            InstanceBean(type="", path=[[{"type": "biz", "id": "biz1"}]]),
            InstanceBean(type="", path=[[{"type": "biz", "id": "biz2"}]]),
        ]

        self.assertFalse(ActionScopeDiffer(None, None)._diff_instances(template_instances, scope_instances))
