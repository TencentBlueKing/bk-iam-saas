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

from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Any, Dict, List

from blue_krill.web.std_error import APIError
from django.conf import settings
from django.utils.functional import cached_property
from pydantic import BaseModel

from backend.apps.role.models import Role, RoleResourceRelation, RoleUser
from backend.service.constants import ANY_ID, ProcessorNodeType, RoleType
from backend.service.models.approval import ApprovalProcessWithNodeProcessor
from backend.util.uuid import gen_uuid

from .policy import (
    ConditionBean,
    InstanceBean,
    PolicyBean,
    PolicyEmptyException,
    RelatedResourceBean,
    ResourceGroupBean,
    ResourceGroupBeanList,
)
from .resource import ResourceBiz, ResourceNodeAttributeDictBean, ResourceNodeBean
from .role import RoleAuthorizationScopeChecker


class PolicyProcess(BaseModel):
    """
    策略关联的审批流程对象

    用于自定义申请
    """

    policy: PolicyBean
    process: ApprovalProcessWithNodeProcessor


class PolicyProcessHandler(ABC):
    """
    处理 policy - process 的管道
    """

    def __init__(self, tenant_id: str, system_id: str) -> None:
        self.tenant_id = tenant_id
        self.system_id = system_id

    @abstractmethod
    def handle(self, policy_process_list: List[PolicyProcess]) -> List[PolicyProcess]:
        pass


class InstanceApproverHandler(PolicyProcessHandler):
    """
    实例审批人处理管道
    """

    def __init__(self, tenant_id: str, system_id: str) -> None:
        super().__init__(tenant_id, system_id)
        self.resource_biz = ResourceBiz(self.tenant_id)

    def handle(self, policy_process_list: List[PolicyProcess]) -> List[PolicyProcess]:
        # 返回的结果
        policy_process_results = []
        # 需要处理的有实例审批人节点的 policy_process
        policy_process_with_approver_node = []
        # 需要查询实例审批人的资源实例
        resource_nodes = set()

        for policy_process in policy_process_list:
            # 没有实例审批人节点不需要处理
            if not self.has_instance_approver_node(policy_process.process):
                policy_process_results.append(policy_process)
                continue

            # 设置默认的审批人
            self.set_default_approver(policy_process.process)

            # 保存需要处理实例审批人的 policy_process
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

        # 依据实例审批人信息，拆分 policy, 添加到结果中
        for policy_process in policy_process_with_approver_node:
            policy_process_results.extend(
                self._split_policy_process_by_resource_approver_dict(policy_process, resource_approver_dict)
            )

        return policy_process_results

    def has_instance_approver_node(self, process: ApprovalProcessWithNodeProcessor) -> bool:
        return process.has_instance_approver_node()

    def set_default_approver(self, process: ApprovalProcessWithNodeProcessor):
        # 填充系统管理员，默认为系统管理管理员
        if self.system_manager_approver:
            process.set_node_approver(
                ProcessorNodeType.INSTANCE_APPROVER.value,
                self.system_manager_approver,
            )

    def _split_policy_process_by_resource_approver_dict(  # noqa: C901, PLR0912
        self, policy_process: PolicyProcess, resource_approver_dict: ResourceNodeAttributeDictBean
    ) -> List[PolicyProcess]:
        """
        通过实例审批人信息，分离 policy_process 为独立的实例 policy
        """
        if len(policy_process.policy.list_thin_resource_type()) != 1:
            return [policy_process]

        policy = policy_process.policy
        process = policy_process.process

        policy_process_list: List[PolicyProcess] = []
        for rg in policy.resource_groups:
            rrt: RelatedResourceBean = rg.related_resource_types[0]  # type: ignore
            for condition in rrt.condition:
                # 忽略有属性的 condition
                if not condition.has_no_attributes():
                    continue

                # 遍历所有的实例路径，筛选出有查询有实例审批人的实例
                for instance in condition.instances:
                    for path in instance.path:
                        last_node = path[-1]
                        if last_node.id == ANY_ID:
                            if len(path) < 2:  # noqa: PLR2004
                                continue
                            last_node = path[-2]

                        resource_node = ResourceNodeBean.parse_obj(last_node)
                        instance_approver = resource_approver_dict.get_attribute(resource_node)
                        # NOTE: 去除接入系统可能传入错误的审批人
                        if isinstance(instance_approver, list):
                            instance_approver = [item for item in instance_approver if item]

                        if not instance_approver:
                            continue

                        # 复制出单实例的 policy
                        copied_policy = copy_policy_by_instance_path(policy, rg, rrt, instance, path)

                        # 复制出新的审批流程，并填充实例审批人
                        copied_process = deepcopy(process)
                        copied_process.set_node_approver(
                            ProcessorNodeType.INSTANCE_APPROVER.value,
                            instance_approver,
                        )

                        policy_process_list.append(PolicyProcess(policy=copied_policy, process=copied_process))

        # 如果没有拆分处理部分实例，直接返回原始的 policy_process
        if not policy_process_list:
            return [policy_process]

        # 把原始的策略剔除拆分的部分
        for part_policy_process in policy_process_list:
            try:
                policy_process.policy.remove_resource_group_list(part_policy_process.policy.resource_groups)
            except PolicyEmptyException:
                # 如果原始的策略全部删完了，直接返回拆分的部分
                return policy_process_list

        # 原始拆分后剩余的部分填回来
        policy_process_list.append(policy_process)
        return policy_process_list

    def _list_approver_resource_node_by_policy(self, policy: PolicyBean) -> List[ResourceNodeBean]:
        """列出 policies 中所有资源的节点"""
        # 需要查询资源实例审批人的节点集合
        resource_node_set = set()
        # 只支持关联 1 个资源类型的操作查询资源审批人
        if len(policy.list_thin_resource_type()) != 1:
            return []

        for rg in policy.resource_groups:
            rrt: RelatedResourceBean = rg.related_resource_types[0]  # type: ignore
            for path in rrt.iter_path_list(ignore_attribute=True):
                last_node = path[-1]
                if last_node.id == ANY_ID:
                    if len(path) < 2:  # noqa: PLR2004
                        continue
                    last_node = path[-2]
                resource_node_set.add(ResourceNodeBean.parse_obj(last_node))
        return list(resource_node_set)

    @cached_property
    def system_manager_approver(self) -> List[str]:
        return Role.objects.get(
            type=RoleType.SYSTEM_MANAGER.value, code=self.system_id, tenant_id=self.tenant_id
        ).members


class InstanceApproverMergeHandler(InstanceApproverHandler):
    """
    实例审批人合并审批
    """

    def has_instance_approver_node(self, process: ApprovalProcessWithNodeProcessor) -> bool:
        return process.has_instance_approver_merge_node()

    def set_default_approver(self, process: ApprovalProcessWithNodeProcessor):
        # 填充系统管理员，默认为系统管理管理员
        if self.system_manager_approver:
            process.set_node_approver(
                ProcessorNodeType.INSTANCE_APPROVER_MERGE.value,
                [self.system_manager_approver[0]],
            )

    def _split_policy_process_by_resource_approver_dict(  # noqa: C901
        self, policy_process: PolicyProcess, resource_approver_dict: ResourceNodeAttributeDictBean
    ) -> List[PolicyProcess]:
        """
        通过实例审批人信息，分离 policy_process 为独立的实例 policy
        """
        if len(policy_process.policy.list_thin_resource_type()) != 1:
            return [policy_process]

        policy = policy_process.policy
        copied_process = deepcopy(policy_process.process)
        copied_process.set_node_approver(
            ProcessorNodeType.INSTANCE_APPROVER_MERGE.value,
            [],
        )
        instance_approvers: List[str] = []

        policy_process_list: List[PolicyProcess] = []
        for rg in policy.resource_groups:
            rrt: RelatedResourceBean = rg.related_resource_types[0]  # type: ignore
            for condition in rrt.condition:
                # 忽略有属性的 condition
                if not condition.has_no_attributes():
                    continue

                # 遍历所有的实例路径，筛选出有查询有实例审批人的实例
                for instance in condition.instances:
                    for path in instance.path:
                        last_node = path[-1]
                        if last_node.id == ANY_ID:
                            if len(path) < 2:  # noqa: PLR2004
                                continue
                            last_node = path[-2]

                        resource_node = ResourceNodeBean.parse_obj(last_node)
                        if (
                            not resource_approver_dict.get_attribute(resource_node)
                            or not resource_approver_dict.get_attribute(resource_node)[0]
                        ):
                            continue

                        # 由于 ITSM 的限制，合并审批这里只取每个实例的第一个审批人
                        instance_approvers.append(resource_approver_dict.get_attribute(resource_node)[0])

                        # 复制出单实例的 policy
                        copied_policy = copy_policy_by_instance_path(policy, rg, rrt, instance, path)
                        policy_process_list.append(PolicyProcess(policy=copied_policy, process=copied_process))

        # 如果没有拆分处理部分实例，直接返回原始的 policy_process
        if not policy_process_list:
            return [policy_process]

        # 填充实例审批人
        copied_process.set_node_approver(
            ProcessorNodeType.INSTANCE_APPROVER_MERGE.value,
            sorted(set(instance_approvers)),
        )

        # 把原始的策略剔除拆分的部分
        for part_policy_process in policy_process_list:
            try:
                policy_process.policy.remove_resource_group_list(part_policy_process.policy.resource_groups)
            except PolicyEmptyException:
                # 如果原始的策略全部删完了，直接返回拆分的部分
                return policy_process_list

        # 原始拆分后剩余的部分填回来
        policy_process_list.append(policy_process)
        return policy_process_list


def copy_policy_by_instance_path(policy, resource_group, rrt, instance, path):
    # 复制出单实例的 policy
    return PolicyBean(
        resource_groups=ResourceGroupBeanList.parse_obj(
            [
                ResourceGroupBean(
                    id=gen_uuid(),
                    related_resource_types=[
                        RelatedResourceBean(
                            condition=[
                                ConditionBean(
                                    attributes=[],
                                    instances=[
                                        InstanceBean(
                                            path=[path],
                                            type=instance.type,
                                            name=instance.name,
                                            name_en=instance.name_en,
                                        )
                                    ],
                                )
                            ],
                            name=rrt.name,
                            name_en=rrt.name_en,
                            selection_mode=rrt.selection_mode,
                            system_id=rrt.system_id,
                            type=rrt.type,
                        )
                    ],
                    environments=resource_group.environments,
                )
            ]
        ),
        **policy.dict(exclude={"resource_groups"}),
    )


class GradeManagerApproverHandler(PolicyProcessHandler):
    """分级管理员审批人"""

    def __init__(self, tenant_id: str, system_id: str) -> None:
        super().__init__(tenant_id, system_id)

        # for cache
        self._resource_role_ids: Dict[ResourceNodeBean, List[int]] = {}
        self._role_id_checker: Dict[int, RoleAuthorizationScopeChecker] = {}

    def handle(self, policy_process_list: List[PolicyProcess]) -> List[PolicyProcess]:
        # 返回的结果
        policy_process_results = []

        for policy_process in policy_process_list:
            # 没有实例审批人节点不需要处理
            if not policy_process.process.has_grade_manager_node():
                policy_process_results.append(policy_process)
                continue

            # 查找策略中需要查询分级管理员的资源实例
            label_resource_policy = self._split_label_resource_policy(policy_process.policy)

            if not label_resource_policy:
                # 填充系统管理员
                policy_process.process.set_node_approver(
                    ProcessorNodeType.GRADE_MANAGER.value,
                    self.system_manager_approver,
                )

                policy_process_results.append(policy_process)
                continue

            origin_policy_empty = False
            for resource_node, part_policy in label_resource_policy.items():
                # 查询资源实例范围的分级管理员
                role_ids = self._query_grade_manager_role_ids(self.system_id, resource_node, part_policy)
                if not role_ids:
                    continue

                # 查询分级管理员的成员作为审批人
                approvers = list(set(RoleUser.objects.filter(role_id__in=role_ids).values_list("username", flat=True)))
                copied_process = deepcopy(policy_process.process)
                copied_process.set_node_approver(
                    ProcessorNodeType.GRADE_MANAGER.value,
                    approvers,
                )
                policy_process_results.append(PolicyProcess(policy=part_policy, process=copied_process))

                # 原始的 policy 移除已经处理的部份
                try:
                    policy_process.policy.remove_resource_group_list(part_policy.resource_groups)
                except PolicyEmptyException:
                    origin_policy_empty = True

            if origin_policy_empty:
                continue

            # 原始拆分后剩余的部分填充系统管理员
            policy_process.process.set_node_approver(
                ProcessorNodeType.GRADE_MANAGER.value,
                self.system_manager_approver,
            )
            policy_process_results.append(policy_process)

        return policy_process_results

    @cached_property
    def system_manager_approver(self) -> List[str]:
        return Role.objects.get(
            type=RoleType.SYSTEM_MANAGER.value, code=self.system_id, tenant_id=self.tenant_id
        ).members

    def _query_grade_manager_role_ids(
        self, system_id: str, resource_node: ResourceNodeBean, part_policy: PolicyBean
    ) -> List[int]:
        """查询满足授权范围的分级管理员"""
        role_ids = self._list_related_resource_role_ids(resource_node)

        if not role_ids:
            return role_ids

        role_result = []
        # 交验满足授权范围的分级管理员
        for checker in self._list_role_scope_checker(role_ids):
            try:
                checker.check_policies(system_id, [part_policy])
                role_result.append(checker.role.id)
            except APIError:
                pass

        return role_result

    def _list_role_scope_checker(self, role_ids: List[int]) -> List[RoleAuthorizationScopeChecker]:
        miss_role_ids = []
        for role_id in role_ids:
            if role_id not in self._role_id_checker:
                miss_role_ids.append(role_id)

        if miss_role_ids:
            for role in Role.objects.filter(id__in=miss_role_ids):
                self._role_id_checker[role.id] = RoleAuthorizationScopeChecker(role)

        return [self._role_id_checker[_id] for _id in role_ids if _id in self._role_id_checker]

    def _list_related_resource_role_ids(self, resource_node: ResourceNodeBean):
        if resource_node not in self._resource_role_ids:
            role_ids = list(
                RoleResourceRelation.objects.filter(
                    system_id=resource_node.system_id,
                    resource_type_id=resource_node.type,
                    resource_id=resource_node.id,
                ).values_list("role_id", flat=True)
            )

            self._resource_role_ids[resource_node] = role_ids

        return self._resource_role_ids[resource_node]

    def _split_label_resource_policy(self, policy: PolicyBean) -> Dict[Any, PolicyBean]:
        """分离出需要查询分级管理员的节点与部分策略"""
        # label resource -> part policy
        resource_node_policy: Dict[ResourceNodeBean, PolicyBean] = {}
        # 只支持关联 1 个资源类型的操作查询资源审批人
        if len(policy.list_thin_resource_type()) != 1:
            return resource_node_policy

        for rg in policy.resource_groups:
            rrt: RelatedResourceBean = rg.related_resource_types[0]  # type: ignore
            for condition in rrt.condition:
                # 忽略有属性的 condition
                if not condition.has_no_attributes():
                    continue

                # 遍历所有的实例路径，筛选出有查询有实例审批人的实例
                for instance in condition.instances:
                    for path in instance.path:
                        first_node = path[0]
                        if (first_node.system_id, first_node.type) not in settings.ROLE_RESOURCE_RELATION_TYPE_SET:
                            continue

                        node = ResourceNodeBean.parse_obj(first_node)
                        if node not in resource_node_policy:
                            # copy part policy
                            resource_node_policy[node] = copy_policy_by_instance_path(policy, rg, rrt, instance, path)
                        else:
                            # 合并到已有的 policy 中
                            resource_node_policy[node].resource_groups[0].related_resource_types[0].condition[
                                0
                            ].add_instances(
                                [
                                    InstanceBean(
                                        path=[path],
                                        type=instance.type,
                                        name=instance.name,
                                        name_en=instance.name_en,
                                    )
                                ]
                            )

        return resource_node_policy
