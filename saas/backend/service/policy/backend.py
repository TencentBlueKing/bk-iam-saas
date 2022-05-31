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
from typing import Dict, List

from backend.component import iam
from backend.service.constants import AbacPolicyChangeType, AuthTypeEnum, SubjectType
from backend.service.models import PathNode, Subject, UniversalPolicyChangedContent


class BackendPolicyOperationService:
    def alter_policies(
        self, subject: Subject, template_id: int, system_id: str, changed_policies: List[UniversalPolicyChangedContent]
    ):
        """
        转换&组装数据并调用后台进行策略变更
        PolicyChangedContent表示单个策略需要变更的所有内容
        """
        # 只允许用户组支持RBAC权限
        assert subject.type == SubjectType.GROUP.value

        # 遍历每条变更的策略，根据rabc和abac拆分
        created_policies, updated_policies, deleted_policy_ids = [], [], []
        resource_actions: Dict[PathNode, Dict[str, List[str]]] = {}
        for p in changed_policies:
            # 对于abac权限，按变更类型分类
            if p.abac is not None:
                if p.abac.change_type == AbacPolicyChangeType.CREATED.value:
                    created_policies.append(
                        p.abac.dict(include={"action_id", "resource_expression", "environment", "expired_at"})
                    )
                elif p.abac.change_type == AbacPolicyChangeType.UPDATED.value:
                    updated_policies.append(
                        p.abac.dict(include={"id", "action_id", "resource_expression", "environment", "expired_at"})
                    )
                elif p.abac.change_type == AbacPolicyChangeType.DELETED.value:
                    deleted_policy_ids.append(p.abac.id)

            # 对于rbac还需要按照resources进行分组聚合
            if p.rbac is not None:
                for r in p.rbac.created:
                    if r not in resource_actions:
                        resource_actions[r] = {"created_action_ids": [], "deleted_action_ids": []}
                    resource_actions[r]["created_action_ids"].append(p.action_id)
                for r in p.rbac.deleted:
                    if r not in resource_actions:
                        resource_actions[r] = {"created_action_ids": [], "deleted_action_ids": []}
                    resource_actions[r]["deleted_action_ids"].append(p.action_id)

        # 将resource_actions转化为调用后台接口所需数据格式
        resource_action_data = [
            {
                "resource": r.dict(include={"system_id", "type", "id"}),
                "created_action_ids": a["created_action_ids"],
                "deleted_action_ids": a["deleted_action_ids"],
            }
            for r, a in resource_actions.items()
        ]

        # 查询并计算用户组类型
        changed_policy_auth_types = {p.action_id: p.auth_type for p in changed_policies}
        auth_type = self._calculate_group_auth_type(int(subject.id), template_id, system_id, changed_policy_auth_types)

        iam.alter_policies_v2(
            subject.type,
            subject.id,
            template_id,
            system_id,
            created_policies,
            updated_policies,
            deleted_policy_ids,
            resource_action_data,
            auth_type,
        )

    def _calculate_group_auth_type(
        self, group_id: int, template_id: int, system_id: str, changed_policy_auth_types: Dict[str, str]
    ) -> str:
        """查询并计算用户组的类型"""
        # 除了本次变更的其他策略的auth_type(需要再查询自定义和模板权限策略)
        abac_count, rbac_count, both_count = 0, 0, 0
        # 1. 先计算即将变更的策略的类型
        for auth_type in changed_policy_auth_types.values():
            abac_count += int(auth_type == AuthTypeEnum.ABAC.value)
            rbac_count += int(auth_type == AuthTypeEnum.RBAC.value)
            both_count += int(auth_type == AuthTypeEnum.BOTH.value)

        # 如果是both，可以提前判断
        if both_count > 0 or (abac_count > 0 and rbac_count > 0):
            return AuthTypeEnum.BOTH.value

        # TODO: 查询group每个模板或自定义权限的策略类型，对于已存在的操作则不需要查询
        #  比较麻烦的点：对于模板的变更，可能只改变一个操作的内容，但是整体得重新计算，但策略的计算是在service层做的，无法同层调用
        #  是否模板授权时可以存储 action_auth_types {action_id: auth_type, ...}的JSON？
        # changed_action_ids = list(changed_policy_auth_types.keys())
        return AuthTypeEnum.BOTH.value
