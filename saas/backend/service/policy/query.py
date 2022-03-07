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
from typing import List, Optional, Tuple

from django.db.models import Count
from django.shortcuts import get_object_or_404

from backend.apps.policy.models import Policy as PolicyModel
from backend.apps.policy.models import TemporaryPolicy
from backend.common.error_codes import error_codes
from backend.component import iam

from ..models import BackendThinPolicy, Policy, Subject, SystemCounter


class PolicyList:
    def __init__(self, policies: List[Policy]) -> None:
        self.policies = policies
        self._policy_dict = {p.action_id: p for p in policies}

    def get(self, action_id: str) -> Optional[Policy]:
        return self._policy_dict.get(action_id, None)

    @property
    def ids(self) -> List[int]:
        return [policy.policy_id for policy in self.policies]

    def remove_by_action_ids(self, action_ids: List[str]):
        self.policies = [p for p in self.policies if p.action_id not in set(action_ids)]
        for action_id in action_ids:
            self._policy_dict.pop(action_id)

    def extend_without_repeated(self, policies: List[Policy]):
        """
        只新增不在已有列表中的策略
        """
        for p in policies:
            if p.action_id in self._policy_dict:
                continue
            self._policy_dict[p.action_id] = p
            self.policies.append(p)

    def update(self, policy: Policy):
        """
        更新数据
        """
        old_policy = self.get(policy.action_id)
        if not old_policy:
            self.extend_without_repeated([policy])
            return

        old_policy.resource_groups = policy.resource_groups
        old_policy.expired_at = policy.expired_at
        old_policy.policy_id = policy.policy_id


class BackendThinPolicyList:
    def __init__(self, policies: List[BackendThinPolicy]) -> None:
        self.policies = policies
        self._policy_dict = {policy.action_id: policy for policy in policies}

    def get(self, action_id: str) -> Optional[BackendThinPolicy]:
        return self._policy_dict.get(action_id, None)

    @property
    def ids(self) -> List[int]:
        return [one.id for one in self.policies]


class PolicyQueryService:
    """Policy Query Service"""

    def list_by_subject(
        self, system_id: str, subject: Subject, action_ids: Optional[List[str]] = None
    ) -> List[Policy]:
        """
        查询subject指定系统下的所有Policy
        """
        qs = PolicyModel.objects.filter(system_id=system_id, subject_type=subject.type, subject_id=subject.id)

        if action_ids is not None and len(action_ids) > 0:
            qs.filter(action_id__in=action_ids)

        return self._trans_from_queryset(system_id, subject, qs)

    def list_temporary_by_subject(self, system_id: str, subject: Subject) -> List[Policy]:
        """
        查询subject指定系统下的临时权限
        """
        qs = TemporaryPolicy.objects.filter(system_id=system_id, subject_type=subject.type)
        return [Policy.from_db_model(one, one.expired_at) for one in qs]

    def _trans_from_queryset(self, system_id: str, subject: Subject, queryset) -> List[Policy]:
        """
        db policy queryset 转换为List[Policy]
        """
        backend_policy_list = new_backend_policy_list_by_subject(system_id, subject)

        policies = [
            Policy.from_db_model(one, backend_policy_list.get(one.action_id).expired_at)  # type: ignore
            for one in queryset
            if backend_policy_list.get(one.action_id)
        ]
        return policies

    def list_by_policy_ids(self, system_id: str, subject: Subject, policy_ids: List[int]) -> List[Policy]:
        """
        查询指定policy_ids的策略
        """
        qs = PolicyModel.objects.filter(
            system_id=system_id, subject_type=subject.type, subject_id=subject.id, policy_id__in=policy_ids
        )
        return self._trans_from_queryset(system_id, subject, qs)

    def list_temporary_by_policy_ids(self, system_id: str, subject: Subject, policy_ids: List[int]) -> List[Policy]:
        """
        查询指定policy_ids的临时策略
        """
        qs = TemporaryPolicy.objects.filter(
            system_id=system_id, subject_type=subject.type, subject_id=subject.id, policy_id__in=policy_ids
        )
        return [Policy.from_db_model(one, one.expired_at) for one in qs]

    def list_system_counter_by_subject(self, subject: Subject) -> List[SystemCounter]:
        """
        查询subject有权限的系统-policy数量信息
        """
        qs = (
            PolicyModel.objects.filter(subject_type=subject.type, subject_id=subject.id)
            .values("system_id")
            .annotate(count=Count("system_id"))
        )

        return [SystemCounter(id=one["system_id"], count=one["count"]) for one in qs]

    def get_system_policy(self, policy_id: int, subject: Subject) -> Tuple[str, Policy]:
        """
        获取指定的Policy
        """
        db_policy = get_object_or_404(
            PolicyModel, policy_id=policy_id, subject_type=subject.type, subject_id=subject.id
        )

        backend_policy_list = new_backend_policy_list_by_subject(db_policy.system_id, subject)

        if not backend_policy_list.get(db_policy.action_id):
            raise error_codes.NOT_FOUND_ERROR

        policy = Policy.from_db_model(
            db_policy, backend_policy_list.get(db_policy.action_id).expired_at  # type: ignore
        )
        return db_policy.system_id, policy

    def list_backend_policy_before_expired_at(self, expired_at: int, subject: Subject) -> List[BackendThinPolicy]:
        """
        查询指定过期事件之前的Policy
        """
        backend_policies = iam.list_policy(subject.type, subject.id, expired_at)
        return [BackendThinPolicy(**policy) for policy in backend_policies]

    def new_policy_list_by_subject(self, system_id: str, subject: Subject) -> PolicyList:
        return PolicyList(self.list_by_subject(system_id, subject))


def new_backend_policy_list_by_subject(
    system_id: str, subject: Subject, template_id: int = 0
) -> BackendThinPolicyList:
    """
    获取后端的Policy List
    """
    backend_policies = iam.list_system_policy(system_id, subject.type, subject.id, template_id)
    return BackendThinPolicyList([BackendThinPolicy(**policy) for policy in backend_policies])
