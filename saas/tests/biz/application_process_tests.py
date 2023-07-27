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
from backend.biz.application_process import GradeManagerApproverHandler, InstanceApproverHandler
from backend.biz.policy import ConditionBean, InstanceBean, PathNodeBean, PolicyBean, RelatedResourceBean
from backend.biz.resource import ResourceNodeBean

from .policy_tests import condition_bean, instance_bean, path_node_bean, policy_bean, related_resource_bean  # noqa


class TestInstanceApproverHandler:
    def test_list_approver_resource_node_by_policy(self, policy_bean: PolicyBean):  # noqa
        handler = InstanceApproverHandler("test")
        resource_nodes = handler._list_approver_resource_node_by_policy(policy_bean)

        assert resource_nodes == [
            ResourceNodeBean(id="id1", system_id="system_id", type="type1"),
        ]


class TestGradeManagerApproverHandler:
    def test_split_label_resource_policy(self):
        policy = PolicyBean(
            action_id="biz_view",
            related_resource_types=[
                RelatedResourceBean(
                    system_id="bk_cmdb",
                    type="biz",
                    condition=[
                        ConditionBean(
                            instances=[
                                InstanceBean(
                                    path=[
                                        [
                                            PathNodeBean(
                                                id="biz1",
                                                name="biz1",
                                                system_id="bk_cmdb",
                                                type="biz",
                                                type_name="biz1",
                                                type_name_en="biz1",
                                            )
                                        ],
                                        [
                                            PathNodeBean(
                                                id="biz2",
                                                name="biz2",
                                                system_id="bk_cmdb",
                                                type="biz",
                                                type_name="biz2",
                                                type_name_en="biz2",
                                            )
                                        ],
                                    ],
                                    type="biz",
                                ),
                                InstanceBean(
                                    path=[
                                        [
                                            PathNodeBean(
                                                id="biz1",
                                                name="biz1",
                                                system_id="bk_cmdb",
                                                type="biz",
                                                type_name="biz1",
                                                type_name_en="biz1",
                                            ),
                                            PathNodeBean(
                                                id="host1",
                                                name="host1",
                                                system_id="bk_cmdb",
                                                type="host",
                                                type_name="host1",
                                                type_name_en="host1",
                                            ),
                                        ],
                                        [
                                            PathNodeBean(
                                                id="biz2",
                                                name="biz2",
                                                system_id="bk_cmdb",
                                                type="biz",
                                                type_name="biz2",
                                                type_name_en="biz2",
                                            ),
                                            PathNodeBean(
                                                id="*",
                                                name="*",
                                                system_id="bk_cmdb",
                                                type="host",
                                                type_name="*",
                                                type_name_en="*",
                                            ),
                                        ],
                                        [
                                            PathNodeBean(
                                                id="host2",
                                                name="host1",
                                                system_id="bk_cmdb",
                                                type="host",
                                                type_name="host1",
                                                type_name_en="host1",
                                            ),
                                        ],
                                    ],
                                    type="host",
                                ),
                            ],
                            attributes=[],
                        )
                    ],
                )
            ],
        )

        handler = GradeManagerApproverHandler("test")
        label_resource_policy = handler._split_label_resource_policy(policy)

        assert len(label_resource_policy) == 2
        biz1 = ResourceNodeBean(system_id="bk_cmdb", type="biz", id="biz1")
        assert biz1 in label_resource_policy
        assert label_resource_policy[biz1] == PolicyBean(
            action_id="biz_view",
            related_resource_types=[
                RelatedResourceBean(
                    system_id="bk_cmdb",
                    type="biz",
                    condition=[
                        ConditionBean(
                            instances=[
                                InstanceBean(
                                    path=[
                                        [
                                            PathNodeBean(
                                                id="biz1",
                                                name="biz1",
                                                system_id="bk_cmdb",
                                                type="biz",
                                                type_name="biz1",
                                                type_name_en="biz1",
                                            )
                                        ],
                                    ],
                                    type="biz",
                                ),
                                InstanceBean(
                                    path=[
                                        [
                                            PathNodeBean(
                                                id="biz1",
                                                name="biz1",
                                                system_id="bk_cmdb",
                                                type="biz",
                                                type_name="biz1",
                                                type_name_en="biz1",
                                            ),
                                            PathNodeBean(
                                                id="host1",
                                                name="host1",
                                                system_id="bk_cmdb",
                                                type="host",
                                                type_name="host1",
                                                type_name_en="host1",
                                            ),
                                        ],
                                    ],
                                    type="host",
                                ),
                            ],
                            attributes=[],
                        )
                    ],
                )
            ],
        )

        biz2 = ResourceNodeBean(system_id="bk_cmdb", type="biz", id="biz2")
        assert biz2 in label_resource_policy
        assert label_resource_policy[biz2] == PolicyBean(
            action_id="biz_view",
            related_resource_types=[
                RelatedResourceBean(
                    system_id="bk_cmdb",
                    type="biz",
                    condition=[
                        ConditionBean(
                            instances=[
                                InstanceBean(
                                    path=[
                                        [
                                            PathNodeBean(
                                                id="biz2",
                                                name="biz2",
                                                system_id="bk_cmdb",
                                                type="biz",
                                                type_name="biz2",
                                                type_name_en="biz2",
                                            )
                                        ],
                                    ],
                                    type="biz",
                                ),
                                InstanceBean(
                                    path=[
                                        [
                                            PathNodeBean(
                                                id="biz2",
                                                name="biz2",
                                                system_id="bk_cmdb",
                                                type="biz",
                                                type_name="biz2",
                                                type_name_en="biz2",
                                            ),
                                            PathNodeBean(
                                                id="*",
                                                name="*",
                                                system_id="bk_cmdb",
                                                type="host",
                                                type_name="*",
                                                type_name_en="*",
                                            ),
                                        ],
                                    ],
                                    type="host",
                                ),
                            ],
                            attributes=[],
                        )
                    ],
                )
            ],
        )
