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
from copy import deepcopy

from django.test import TestCase

from backend.biz.policy import PolicyBean, PolicyBeanList
from tests.test_util.factory import PolicyFactory


class ApplicationServiceTests(TestCase):
    def test_filter_application_policies(self):
        policy_factory = PolicyFactory()
        policy = policy_factory.example()

        policy2 = deepcopy(policy)
        policy2.related_resource_types[0].condition[0].instances = []

        policy3 = deepcopy(policy)
        policy3.id = "action"

        policy_list1 = PolicyBeanList("system_id", [PolicyBean(**policy2.dict())])
        policy_list2 = PolicyBeanList("system_id", [PolicyBean(**policy.dict()), PolicyBean(**policy3.dict())])

        policies = policy_list2.sub(policy_list1).policies
        self.assertEqual(len(policies), 2)

    def test_merge_apply_policies(self):
        policy_factory = PolicyFactory()
        policy = policy_factory.example()

        policy2 = deepcopy(policy)
        policy2.related_resource_types[0].condition[0].instances = []

        policy3 = deepcopy(policy)
        policy3.id = "action"

        policy_list1 = PolicyBeanList("system_id", [PolicyBean(**policy2.dict())])
        policy_list2 = PolicyBeanList("system_id", [PolicyBean(**policy.dict()), PolicyBean(**policy3.dict())])

        policies = policy_list1.add(policy_list2).policies

        self.assertEqual(len(policies), 2)
