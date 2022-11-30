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
from backend.biz.application_process import InstanceApproverHandler
from backend.biz.policy import PolicyBean
from backend.biz.resource import ResourceNodeBean

from .policy_tests import condition_bean, instance_bean, path_node_bean, policy_bean, related_resource_bean  # noqa


class TestInstanceApproverHandler:
    def test_list_approver_resource_node_by_policy(self, policy_bean: PolicyBean):  # noqa
        handler = InstanceApproverHandler()
        resource_nodes = handler._list_approver_resource_node_by_policy(policy_bean)

        assert resource_nodes == [
            ResourceNodeBean(id="id1", system_id="system_id", type="type1"),
        ]
