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

from backend.service.policy import PolicyService
from tests.test_util.factory import PolicyFactory


class PolicyServiceTests(TestCase):
    def test_check_policy_instance_count(self):
        policy_factory = PolicyFactory()
        policy = policy_factory.example()

        policy.related_resource_types[0].instances_count = mock.Mock(return_value=10)

        svc = PolicyService()
        svc.check_policy_instance_count(policy)

        with self.assertRaises(Exception):
            policy.related_resource_types[0].instances_count = mock.Mock(return_value=10001)
            svc.check_policy_instance_count(policy)
