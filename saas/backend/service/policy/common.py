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

from backend.component import iam
from backend.service.constants import AbacPolicyChangeType, AuthType
from backend.service.models import (
    AbacPolicyChangeContent,
    Policy,
    RbacPolicyChangeContent,
    UniversalPolicy,
    UniversalPolicyChangedContent,
)


class UniversalPolicyChangedContentAnalyzer:
    """该类主要用于计算Policy被变更的内容，便于后续变更策略"""

    action_fields = "id,auth_type"

    def _query_action_auth_types(self, system_id: str, action_ids: Iterable[str]) -> Dict[str, str]:
        """查询操作的AuthType"""
        actions = iam.list_action(system_id, fields=self.action_fields)
        # 只返回要查询的操作的Auth，同时对于auth_type为空的，则默认为ABAC
        return {i["id"]: i["auth_type"] or AuthType.ABAC.value for i in actions if i["id"] in action_ids}

    def cal_for_created(self, system_id: str, create_policies: List[Policy]) -> List[UniversalPolicyChangedContent]:
        """根据新增的策略，组装计算出要变更的策略内容"""
        if len(create_policies) == 0:
            return []

        action_auth_types = self._query_action_auth_types(system_id, [p.action_id for p in create_policies])

        changed_policies = []
        for p in create_policies:
            up = UniversalPolicy.from_policy(p, action_auth_types[p.action_id])
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

    def cal_for_deleted(self, system_id: str, delete_policies: List[Policy]) -> List[UniversalPolicyChangedContent]:
        """根据要删除的策略ID，组装计算出要变更的策略内容"""
        if len(delete_policies) == 0:
            return []

        action_auth_types = self._query_action_auth_types(system_id, [p.action_id for p in delete_policies])

        # 转换为UniversalPolicy结构，然后拆分出rbac和abac权限
        changed_policies = []
        for p in delete_policies:
            up = UniversalPolicy.from_policy(p, action_auth_types[p.action_id])
            # Note: 删除策略，默认auth_type为None
            policy_changed_content = UniversalPolicyChangedContent(
                action_id=p.action_id, auth_type=AuthType.NONE.value
            )
            # 有ABAC策略需要删除，只需要PolicyID即可
            if up.has_abac():
                policy_changed_content.abac = AbacPolicyChangeContent(
                    change_type=AbacPolicyChangeType.DELETED.value, id=p.backend_policy_id
                )
            # RBAC策略删除，则提供被删除的资源实例
            if up.has_rbac():
                policy_changed_content.rbac = RbacPolicyChangeContent(deleted=up.instances)

            changed_policies.append(policy_changed_content)

        return changed_policies

    def cal_for_updated(
        self,
        system_id: str,
        update_policies: List[Tuple[Policy, Policy]],  # List[(new, old)]
    ) -> List[UniversalPolicyChangedContent]:
        """根据更新的策略，组装计算出要变更的策略内容"""
        if len(update_policies) == 0:
            return []

        action_auth_types = self._query_action_auth_types(system_id, [p.action_id for p, _ in update_policies])

        changed_policies = []
        # 遍历每条要新旧对比，进行新旧策略对比，得到需要变更的内容，组装PolicyChangedContent数据
        for p, old_p in update_policies:
            auth_type = action_auth_types[p.action_id]
            up = UniversalPolicy.from_policy(p, auth_type)
            old_up = UniversalPolicy.from_policy(old_p, auth_type)
            policy_changed_content = up.calculate_pre_changed_content(system_id, old_up)
            changed_policies.append(policy_changed_content)

        return changed_policies
