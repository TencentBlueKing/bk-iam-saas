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

import json
from collections import Counter
from typing import Any, Dict, Iterable, List, Tuple

from pydantic import BaseModel

from backend.apps.policy.models import Policy as PolicyModel
from backend.apps.template.models import PermTemplatePolicyAuthorized
from backend.component import iam
from backend.service.constants import AbacPolicyChangeType, AuthType, SubjectType
from backend.service.models import PathNode, Subject, UniversalPolicyChangedContent


class AuthTypeStatistics(BaseModel):
    """统计分析AuthType"""

    abac_count: int = 0
    rbac_count: int = 0
    all_count: int = 0

    def accumulate(self, auth_types: Iterable[str]):
        """累加"""
        counter = Counter(auth_types)
        self.abac_count += counter.get(AuthType.ABAC.value, 0)
        self.rbac_count += counter.get(AuthType.RBAC.value, 0)
        self.all_count += counter.get(AuthType.ALL.value, 0)

    def is_all_auth_type(self) -> bool:
        return self.all_count > 0 or (self.abac_count > 0 and self.rbac_count > 0)

    def auth_type(self) -> str:
        """根据统计结果，分析出最终auth_type"""
        if self.is_all_auth_type():
            return AuthType.ALL.value

        if self.rbac_count > 0:
            return AuthType.RBAC.value

        if self.abac_count > 0:
            return AuthType.ABAC.value

        return AuthType.NONE.value


class BackendPolicyOperationService:
    def alter_backend_policies(
        self, subject: Subject, template_id: int, system_id: str, changed_policies: List[UniversalPolicyChangedContent]
    ):
        """
        转换&组装数据并调用后台进行策略变更
        PolicyChangedContent表示单个策略需要变更的所有内容
        """
        # 只允许用户组支持RBAC权限
        assert subject.type == SubjectType.GROUP.value

        # 生成要变更的ABAC数据
        created_policies, updated_policies, deleted_policy_ids = self.generate_abac_data(changed_policies)

        # 生成要变更的RBAC数据
        resource_action_data = self.generate_rbac_data(changed_policies)

        # 查询并计算用户组类型
        changed_policy_auth_types = {p.action_id: p.auth_type for p in changed_policies}
        auth_type = self._calculate_auth_type(subject, template_id, system_id, changed_policy_auth_types)

        iam.alter_group_policies_v2(
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

    def generate_rbac_data(self, changed_policies: List[UniversalPolicyChangedContent]) -> List[Dict[str, Any]]:
        """从批量变更策略的内容里提取生成要变更的RBAC策略数据"""
        resource_actions: Dict[PathNode, Dict[str, List[str]]] = {}
        for p in changed_policies:
            # 无需RBAC变更，则忽略
            if p.rbac is None:
                continue

            # 对于rbac 需要按照resources进行分组聚合
            for r in p.rbac.created:
                if r not in resource_actions:
                    resource_actions[r] = {"created_action_ids": [], "deleted_action_ids": []}
                resource_actions[r]["created_action_ids"].append(p.action_id)

            for r in p.rbac.deleted:
                if r not in resource_actions:
                    resource_actions[r] = {"created_action_ids": [], "deleted_action_ids": []}
                resource_actions[r]["deleted_action_ids"].append(p.action_id)

        # 将resource_actions转化为调用后台接口所需数据格式
        return [
            {
                "resource": r.dict(include={"system_id", "type", "id"}),
                "created_action_ids": a["created_action_ids"],
                "deleted_action_ids": a["deleted_action_ids"],
            }
            for r, a in resource_actions.items()
        ]

    def generate_abac_data(
        self, changed_policies: List[UniversalPolicyChangedContent]
    ) -> Tuple[List[Dict], List[Dict], List[int]]:
        """从批量变更策略的内容里提取生成要变更的ABAC策略数据"""
        created_policies, updated_policies, deleted_policy_ids = [], [], []
        for p in changed_policies:
            # 无需RBAC变更，则忽略
            if p.abac is None:
                continue

            # 对于abac权限，按变更类型分类
            if p.abac.change_type == AbacPolicyChangeType.CREATED.value:
                created_policy = p.abac.dict(include={"resource_expression", "environment", "expired_at"})
                created_policy["action_id"] = p.action_id
                created_policies.append(created_policy)
            elif p.abac.change_type == AbacPolicyChangeType.UPDATED.value:
                updated_policy = p.abac.dict(include={"id", "resource_expression", "environment", "expired_at"})
                updated_policy["action_id"] = p.action_id
                updated_policies.append(updated_policy)
            elif p.abac.change_type == AbacPolicyChangeType.DELETED.value:
                deleted_policy_ids.append(p.abac.id)

        return created_policies, updated_policies, deleted_policy_ids

    def _calculate_auth_type(
        self, subject: Subject, template_id: int, system_id: str, changed_policy_auth_types: Dict[str, str]
    ) -> str:
        """查询并计算用户组的类型"""
        # 除了本次变更的其他策略的auth_type(需要再查询自定义和模板权限策略)
        auth_type_statistics = AuthTypeStatistics()

        # 1. 先统计即将变更的策略的类型
        auth_type_statistics.accumulate(changed_policy_auth_types.values())

        # 如果是all，可以提前判断
        if auth_type_statistics.is_all_auth_type():
            return AuthType.ALL.value

        # 2. 查询用户组自定义权限里每条策略类型
        custom_perm_auth_types = PolicyModel.objects.filter(
            subject_type=subject.type, subject_id=subject.id, system_id=system_id
        ).values("action_id", "auth_type")
        # 剔除本次变更的策略
        auth_types = [
            i["auth_type"]
            for i in custom_perm_auth_types
            # 变更的非自定义权限或非变更Action
            if template_id != 0 or i["action_id"] not in changed_policy_auth_types
        ]
        # 统计累加
        auth_type_statistics.accumulate(auth_types)

        # 如果是all，可以提前判断
        if auth_type_statistics.is_all_auth_type():
            return AuthType.ALL.value

        # 3. 查询用户组每个权限模板的策略类型
        template_auth_types = PermTemplatePolicyAuthorized.objects.filter(
            subject_type=subject.type, subject_id=subject.id, system_id=system_id
        ).values("template_id", "_auth_types")
        # 统计累加
        for i in template_auth_types:
            auth_template_id = i["template_id"]
            # _auth_types 存储为 {action_id: auth_type, ...}的JSON
            _auth_types = json.loads(i["_auth_types"])
            # 剔除本次变更的策略
            auth_types = [
                auth_type
                for action_id, auth_type in _auth_types.items()
                # 非本次变更的模板 或 非变更的Action
                if auth_template_id != template_id or action_id not in changed_policy_auth_types
            ]
            auth_type_statistics.accumulate(auth_types)

            # 如果是all，可以提前判断
            if auth_type_statistics.is_all_auth_type():
                return AuthType.ALL.value

        return auth_type_statistics.auth_type()
