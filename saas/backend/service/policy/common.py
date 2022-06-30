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
from typing import Dict, Iterable, List, Tuple

from backend.apps.policy.models import Policy as PolicyModel
from backend.component import iam

from ..constants import AbacPolicyChangeType, AuthTypeEnum
from ..models import (
    AbacPolicyChangeContent,
    Policy,
    RbacPolicyChangeContent,
    Subject,
    UniversalPolicy,
    UniversalPolicyChangedContent,
)


class PolicyTypeAnalyzer:
    """该类主要用于分析Policy类型，便于后续根据rbac和abac策略执行对应逻辑"""

    action_fields = "id,auth_type"

    def query_action_auth_types(self, system_id: str, action_ids: Iterable[str]) -> Dict[str, str]:
        """查询操作的AuthType"""
        actions = iam.list_action(system_id, fields=self.action_fields)
        # 只返回要查询的操作的Auth，同时对于auth_type为空的，则默认为ABAC
        return {i["id"]: i["auth_type"] or AuthTypeEnum.ABAC.value for i in actions if i["id"] in action_ids}

    def _query_action_id_by_policy_ids(
        self, system_id: str, subject: Subject, policy_ids: List[int]
    ) -> Dict[int, str]:
        """根据PolicyID查询ActionID"""
        if len(policy_ids) == 0:
            return {}

        # 查询PolicyID为Backend Policy的Action
        db_policies = PolicyModel.objects.filter(
            subject_type=subject.type, subject_id=subject.id, system_id=system_id, policy_id__in=policy_ids
        ).only("policy_id", "action_id")

        return {p.policy_id: p.action_id for p in db_policies}

    def split_policy_ids_by_auth_type(
        self, system_id: str, subject: Subject, policy_ids: List[int]
    ) -> Tuple[List[int], List[int]]:
        """用于将PolicyID区分出来，是来着RBAC还是ABAC策略"""
        if len(policy_ids) == 0:
            return [], []

        # 查询PolicyID对应的Action，然后再查询Action的AuthType
        policy_action_ids = self._query_action_id_by_policy_ids(system_id, subject, policy_ids)
        action_auth_types = self.query_action_auth_types(system_id, policy_action_ids.values())

        # 根据AuthType拆分为不同的policy_ids
        abac_policy_ids, universal_policy_ids = [], []
        for policy_id in policy_ids:
            action_id = policy_action_ids[policy_id]
            auth_type = action_auth_types[action_id]
            if auth_type == AuthTypeEnum.ABAC.value:
                abac_policy_ids.append(policy_id)
            else:
                # Note: 若Action类型为RBAC，其产生的策略既有可能是RBAC也有可能是ABAC，也可能是ALL，比如存在任意资源实例化就是ABAC
                universal_policy_ids.append(policy_id)

        return abac_policy_ids, universal_policy_ids

    def split_policies_by_auth_type(self, system_id: str, policies: List[Policy]) -> Tuple[List[Policy], List[Policy]]:
        """将策略列表按照其Action的AuthType进行拆分"""
        if len(policies) == 0:
            return [], []

        # 查询策略Action对应的AuthType
        action_auth_types = self.query_action_auth_types(system_id, [p.action_id for p in policies])

        # 根据AuthType拆分
        abac_policies, universal_policies = [], []
        for p in policies:
            auth_type = action_auth_types[p.action_id]
            if auth_type == AuthTypeEnum.ABAC.value:
                abac_policies.append(p)
            else:
                universal_policies.append(p)

        return abac_policies, universal_policies


class UniversalPolicyChangedContentCalculator:
    """该类主要用于计算Policy被变更的内容，便于后续变更策略"""

    def cal_for_created(self, system_id: str, create_policies: List[Policy]) -> List[UniversalPolicyChangedContent]:
        """根据新增的策略，组装计算出要变更的策略内容"""
        if len(create_policies) == 0:
            return []

        changed_policies = []
        for p in create_policies:
            up = UniversalPolicy.from_policy(p)
            policy_changed_content = UniversalPolicyChangedContent(action_id=p.action_id, auth_type=up.auth_type)
            # 有ABAC策略需要新增
            if up.has_abac():
                policy_changed_content.abac = AbacPolicyChangeContent(
                    change_type=AbacPolicyChangeType.CREATED.value,
                    resource_expression=up.to_resource_expression(system_id),
                )
            # RBAC策略新增
            if up.has_rbac():
                policy_changed_content.rbac = RbacPolicyChangeContent(created=up.instances)

            changed_policies.append(policy_changed_content)

        return changed_policies

    def cal_for_deleted(self, delete_policies: List[Policy]) -> List[UniversalPolicyChangedContent]:
        """根据要删除的策略ID，组装计算出要变更的策略内容"""
        if len(delete_policies) == 0:
            return []

        # 转换为UniversalPolicy结构，然后拆分出rbac和abac权限
        changed_policies = []
        for p in delete_policies:
            up = UniversalPolicy.from_policy(p)
            # Note: 删除策略，默认auth_type为None
            policy_changed_content = UniversalPolicyChangedContent(
                action_id=p.action_id, auth_type=AuthTypeEnum.NONE.value
            )
            # 有ABAC策略需要删除，只需要PolicyID即可
            if up.has_abac():
                policy_changed_content.abac = AbacPolicyChangeContent(
                    change_type=AbacPolicyChangeType.DELETED.value, id=p.policy_id
                )
            # RBAC策略删除，则提供被删除的资源实例
            if up.has_rbac():
                policy_changed_content.rbac = RbacPolicyChangeContent(deleted=up.instances)

            changed_policies.append(policy_changed_content)

        return changed_policies

    def cal_for_updated(
        self, system_id: str, update_policies: List[Tuple[Policy, Policy]]
    ) -> List[UniversalPolicyChangedContent]:
        """根据更新的策略，组装计算出要变更的策略内容"""
        if len(update_policies) == 0:
            return []

        changed_policies = []
        # 遍历每条要新旧对比，进行新旧策略对比，得到需要变更的内容，组装PolicyChangedContent数据
        for p, old_p in update_policies:
            up = UniversalPolicy.from_policy(p)
            old_up = UniversalPolicy.from_policy(old_p)
            policy_changed_content = up.calculate_pre_changed_content(system_id, old_up)
            changed_policies.append(policy_changed_content)

        return changed_policies
