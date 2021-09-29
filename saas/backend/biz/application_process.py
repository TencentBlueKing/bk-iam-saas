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
from abc import ABC, abstractmethod
from copy import deepcopy
from typing import List

from pydantic import BaseModel

from backend.biz.resource import ResourceBiz, ResourceNodeAttributeDictBean, ResourceNodeBean
from backend.service.constants import ANY_ID
from backend.service.models.approval import ApprovalProcessWithNodeProcessor

from .policy import ConditionBean, InstanceBean, PolicyBean, PolicyEmptyException, RelatedResourceBean


class PolicyProcess(BaseModel):
    """
    策略关联的审批流程对象

    用于自定义申请
    """

    policy: PolicyBean
    process: ApprovalProcessWithNodeProcessor


class PolicyProcessHandler(ABC):
    """
    处理policy - process的管道
    """

    @abstractmethod
    def handle(self, policy_process_list: List[PolicyProcess]) -> List[PolicyProcess]:
        pass


class InstanceAproverHandler(PolicyProcessHandler):
    """
    实例审批人处理管道
    """

    resource_biz = ResourceBiz()

    def handle(self, policy_process_list: List[PolicyProcess]) -> List[PolicyProcess]:
        # 返回的结果
        policy_process_results = []
        # 需要处理的有实例审批人节点的policy_process
        policy_process_with_approver_node = []
        # 需要查询实例审批人的资源实例
        resource_nodes = set()

        for policy_process in policy_process_list:
            # 没有实例审批人节点不需要处理
            if not policy_process.process.has_instance_approver_node():
                policy_process_results.append(policy_process)
                continue

            # 保存需要处理实例审批人的policy_process
            policy_process_with_approver_node.append(policy_process)
            # 筛选出需要查询实例审批人的资源实例
            for resource_node in self._list_approver_resource_node_by_policy(policy_process.policy):
                resource_nodes.add(resource_node)

        # 没有需要查询资源审批人的实例节点
        if not resource_nodes:
            return policy_process_list

        # 查询资源实例的审批人
        resource_approver_dict = self.resource_biz.fetch_resource_approver(list(resource_nodes))
        if resource_approver_dict.is_empty():
            return policy_process_list

        # 依据实例审批人信息, 拆分policy, 添加到结果中
        for policy_process in policy_process_with_approver_node:
            policy_process_results.extend(
                self._split_policy_process_by_resource_approver_dict(policy_process, resource_approver_dict)
            )

        return policy_process_results

    def _split_policy_process_by_resource_approver_dict(
        self, policy_process: PolicyProcess, resource_approver_dict: ResourceNodeAttributeDictBean
    ) -> List[PolicyProcess]:
        """
        通过实例审批人信息, 分离policy_process为独立的实例policy
        """
        if len(policy_process.policy.related_resource_types) != 1:
            return [policy_process]

        policy = policy_process.policy
        process = policy_process.process
        rrt = policy.related_resource_types[0]

        policy_process_list: List[PolicyProcess] = []
        for condition in rrt.condition:
            # 忽略有属性的condition
            if not condition.has_no_attributes():
                continue

            # 遍历所有的实例路径, 筛选出有查询有实例审批人的实例
            for instance in condition.instances:
                for path in instance.path:
                    last_node = path[-1]
                    if last_node.id == ANY_ID:
                        if len(path) < 2:
                            continue
                        last_node = path[-2]

                    resource_node = ResourceNodeBean.parse_obj(last_node)
                    if not resource_approver_dict.get_attribute(resource_node):
                        continue

                    # 复制出单实例的policy
                    copied_policy = self._copy_policy_by_instance_path(policy, rrt, instance, path)

                    # 复制出新的审批流程, 并填充实例审批人
                    copied_process = deepcopy(process)
                    copied_process.set_instance_approver(resource_approver_dict.get_attribute(resource_node))

                    policy_process_list.append(PolicyProcess(policy=copied_policy, process=copied_process))

        # 如果没有拆分处理部分实例, 直接返回原始的policy_process
        if not policy_process_list:
            return [policy_process]

        # 把原始的策略剔除拆分的部分
        for part_policy_process in policy_process_list:
            try:
                policy_process.policy.remove_related_resource_types(part_policy_process.policy.related_resource_types)
            except PolicyEmptyException:
                # 如果原始的策略全部删完了, 直接返回拆分的部分
                return policy_process_list

        # 原始拆分后剩余的部分填回来
        policy_process_list.append(policy_process)
        return policy_process_list

    def _copy_policy_by_instance_path(self, policy, rrt, instance, path):
        # 复制出单实例的policy
        copied_policy = PolicyBean(
            related_resource_types=[
                RelatedResourceBean(
                    condition=[
                        ConditionBean(
                            attributes=[],
                            instances=[InstanceBean(path=[path], **instance.dict(exclude={"path"}))],
                        )
                    ],
                    **rrt.dict(exclude={"condition"}),
                )
            ],
            **policy.dict(exclude={"related_resource_types"}),
        )
        return copied_policy

    def _list_approver_resource_node_by_policy(self, policy: PolicyBean) -> List[ResourceNodeBean]:
        """列出policies中所有资源的节点"""
        # 需要查询资源实例审批人的节点集合
        resource_node_set = set()
        # 只支持关联1个资源类型的操作查询资源审批人
        if len(policy.related_resource_types) != 1:
            return []

        rrt = policy.related_resource_types[0]
        for path in rrt.iter_path_list(ignore_attribute=True):
            last_node = path.nodes[-1]
            if last_node.id == ANY_ID:
                if len(path.nodes) < 2:
                    continue
                last_node = path.nodes[-2]
            resource_node_set.add(ResourceNodeBean.parse_obj(last_node))
        return list(resource_node_set)
