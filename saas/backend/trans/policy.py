# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-权限中心(BlueKing-IAM) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

主要是将API请求里的操作或操作组合等权限数据，转换为PolicyBean或List[PolicyBean]，便于进行下一步处理
"""
from collections import defaultdict
from typing import Any, Dict, List, Optional

from pydantic.tools import parse_obj_as

from backend.biz.action import ActionBean, ActionBeanList, ActionBiz, ActionCheckBiz, ActionResourceGroupForCheck
from backend.biz.policy import (
    ConditionBean,
    InstanceBean,
    PathNodeBean,
    PolicyBean,
    PolicyBeanList,
    RelatedResourceBean,
)
from backend.common.cache import cachedmethod
from backend.common.error_codes import error_codes
from backend.service.models.policy import ResourceGroup
from backend.util.uuid import gen_uuid


class PolicyTrans:
    action_biz = ActionBiz()
    action_check_biz = ActionCheckBiz()

    def _gen_instance_condition_by_aggregate_resources(
        self, aggregate_resource_types: List[Dict]
    ) -> Optional[ConditionBean]:
        """
        将操作聚合里选择的资源实例转换为Policy里资源的Condition
        [{
            system_id,
            id,
            instances: [
                {id, name},
                ...
            ]
        }]
        """
        if not aggregate_resource_types:
            return None

        instance_beans: List[InstanceBean] = []
        for aggregate_resource_type in aggregate_resource_types:
            system_id, resource_type_id, instances = (
                aggregate_resource_type["system_id"],
                aggregate_resource_type["id"],
                aggregate_resource_type["instances"],
            )

            instance_beans.append(
                InstanceBean(
                    type=resource_type_id,
                    path=[
                        [PathNodeBean(system_id=system_id, type=resource_type_id, id=i["id"], name=i["name"])]
                        for i in instances
                    ],
                )
            )

        return ConditionBean(instances=instance_beans, attributes=[])

    def _gen_policy_by_action_and_condition(
        self, action: ActionBean, condition: Optional[ConditionBean], expired_at: int
    ) -> PolicyBean:
        """通过操作模型和选择里实例的Condition生成对应策略"""
        return PolicyBean(
            action_id=action.id,
            resource_groups=[
                ResourceGroup(
                    id=gen_uuid(),
                    related_resource_types=[
                        RelatedResourceBean(
                            system_id=rrt.system_id, type=rrt.id, condition=[condition] if condition else []
                        )
                        for rrt in action.related_resource_types
                    ],
                )
            ],
            expired_at=expired_at,
        )

    @cachedmethod(timeout=60)  # 缓存1分钟
    def _get_action_list(self, system_id: str) -> ActionBeanList:
        """获取某个系统的操作列表"""
        return self.action_biz.list(system_id)

    def _get_action(self, system_id: str, action_id: str) -> ActionBean:
        """查询操作的权限模型"""
        action_list = self._get_action_list(system_id)
        action = action_list.get(action_id)
        if not action:
            raise error_codes.VALIDATE_ERROR.format(f"system({system_id}) has not action({action_id})")

        return action

    def from_aggregate_actions(self, aggregations: List[Dict]) -> Dict[str, PolicyBeanList]:
        """
        操作聚合数据转换为策略
        [
            {
                actions: [
                    {system_id, id},
                    ...
                ]
                aggregate_resource_types: [{
                    system_id,
                    id,
                    instances: [
                        {id, name},
                        ...
                    ]
                }]
                expired_at,
            },
            ...  // 不同资源类型的操作聚合
        ]

        return: {system_id: PolicyBeanList}
        """
        system_policies_dict: Dict[str, List[PolicyBean]] = defaultdict(list)
        for aggregation in aggregations:
            expired_at = aggregation.get("expired_at", 0)
            # 资源
            condition = self._gen_instance_condition_by_aggregate_resources(aggregation["aggregate_resource_types"])
            # 遍历操作，给每个操作绑定上对应的资源实例
            for a in aggregation["actions"]:
                # 查询操作的权限模型
                action = self._get_action(a["system_id"], a["id"])
                # 生成对应策略
                policy = self._gen_policy_by_action_and_condition(action, condition, expired_at)
                system_policies_dict[a["system_id"]].append(policy)

        # 将List[PolicyBean] 转换为PolicyBeanList
        system_policy_bean_list_dict = {
            system_id: PolicyBeanList(
                system_id,
                list(policies),
                need_fill_empty_fields=False,
                # 保证转换后的数据与权限模型是符合的
                need_check_instance_selection=True,
            )
            for system_id, policies in system_policies_dict.items()
        }

        return system_policy_bean_list_dict

    def from_actions(self, system_id: str, actions: List[Dict]) -> PolicyBeanList:
        """
        前端添加的操作权限数据，转换为策略
         actions: [
            {
                id,
                type,
                related_resource_types: [
                    {
                        system_id,
                        type,
                        condition: [
                            {
                                id,
                                instances: [
                                    {
                                        type,
                                        name,
                                        path: [
                                            [
                                                {system_id, type, type_name, id, name},
                                                ...
                                            ]
                                        ]
                                    }
                                ]
                                attributes: [
                                    {
                                        id,
                                        name,
                                        values: [
                                            {id, name},
                                            ...
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
                policy_id,
                expired_at
            }
        ]
        """
        # 1. 初步检查是否合法数据，与权限模型是否一致
        self.action_check_biz.check_action_resource_group(
            system_id, parse_obj_as(List[ActionResourceGroupForCheck], actions)
        )
        # 2. 转为PolicyBeanList
        policy_list = PolicyBeanList(
            system_id,
            parse_obj_as(List[PolicyBean], actions),
            need_fill_empty_fields=False,
            # 保证转换后的数据与权限模型是符合的
            need_check_instance_selection=True,
        )

        return policy_list

    def from_aggregate_actions_and_actions(self, system_id: str, data: Dict[str, Any]) -> PolicyBeanList:
        """
        转换前端数据为policies

        {
            actions: [
                {
                    id,
                    type,
                    related_resource_types: [
                        {
                            system_id,
                            type,
                            condition: [
                                {
                                    id,
                                    instances: [
                                        {
                                            type,
                                            name,
                                            path: [
                                                [
                                                    {system_id, type, type_name, id, name},
                                                    ...
                                                ]
                                            ]
                                        }
                                    ]
                                    attributes: [
                                        {
                                            id,
                                            name,
                                            values: [
                                                {id, name},
                                                ...
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                    policy_id,
                    expired_at
                }
            ],
            aggregations: [
                {
                    actions: [
                        {system_id, id},
                        ...
                    ]
                    aggregate_resource_types: [{
                        system_id,
                        id,
                        instances: [
                            {id, name},
                            ...
                        ]
                    }]
                    expired_at,
                }
            ]
        }
        """
        # 1. 非聚合的操作权限处理
        policy_list = self.from_actions(system_id, data["actions"])

        # 2. 聚合的操作权限处理
        agg_policy_list_dict = self.from_aggregate_actions(data["aggregations"])
        # NOTE 当前聚合只支持单一系统，所以直接取申请的系统的策略
        agg_policy_list = agg_policy_list_dict.get(system_id, PolicyBeanList(system_id=system_id, policies=[]))

        # 3. 合并策略
        return policy_list.add(agg_policy_list)
