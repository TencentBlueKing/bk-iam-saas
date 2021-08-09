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
from typing import Any, Dict, List, Optional, Tuple

from django.db.models import Count
from pydantic import BaseModel
from pydantic.fields import Field

from backend.apps.policy.models import Policy as PolicyModel
from backend.common.error_codes import error_codes
from backend.component import iam
from backend.service.models import Subject
from backend.service.utils.translate import ResourceExpressionTranslator
from backend.util.uuid import gen_uuid


# TODO Policy重构完成后, 迁移模型到models下
class PathNode(BaseModel):
    id: str
    name: str
    system_id: str = ""  # NOTE 兼容一下, 早期的policy数据中可能没有system_id
    type: str


class Instance(BaseModel):
    type: str
    path: List[List[PathNode]]


class Value(BaseModel):
    id: Any
    name: str


class Attribute(BaseModel):
    id: str
    name: str
    values: List[Value]

    def sort_values(self):
        self.values.sort(key=lambda value: value.id)

    def trim(self) -> Tuple:
        return self.id, tuple([value.id for value in self.values])


class Condition(BaseModel):
    instances: List[Instance]
    attributes: List[Attribute]
    id: str

    def __init__(self, **data: Any) -> None:
        if "id" not in data:
            data["id"] = gen_uuid()
        super().__init__(**data)

    def sort_attributes(self):
        for a in self.attributes:
            a.sort_values()
        self.attributes.sort(key=lambda attribute: attribute.id)

    def hash_attributes(self):
        self.sort_attributes()
        return hash(tuple([attribute.trim() for attribute in self.attributes]))

    def has_no_attributes(self) -> bool:
        return len(self.attributes) == 0

    def has_no_instances(self) -> bool:
        return len(self.instances) == 0


class RelatedResource(BaseModel):
    system_id: str
    type: str
    condition: List[Condition]


class Policy(BaseModel):
    action_id: str = Field(alias="id")
    related_resource_types: List[RelatedResource]
    policy_id: int
    expired_at: int

    class Config:
        allow_population_by_field_name = True  # 支持alias字段同时传 action_id 与 id

    @classmethod
    def from_db_model(cls, policy: PolicyModel, expired_at: int) -> "Policy":
        return cls(
            action_id=policy.action_id,
            related_resource_types=policy.resources,
            policy_id=policy.policy_id,
            expired_at=expired_at,
        )

    def to_db_model(self, system_id: str, subject: Subject) -> PolicyModel:
        p = PolicyModel(
            subject_type=subject.type,
            subject_id=subject.id,
            system_id=system_id,
            action_type="",
            action_id=self.action_id,
        )
        p.resources = [rt.dict() for rt in self.related_resource_types]
        p.environment = {}
        return p

    def to_backend_dict(self):
        translator = ResourceExpressionTranslator()
        return {
            "action_id": self.action_id,
            "resource_expression": translator.translate([rt.dict() for rt in self.related_resource_types]),
            "environment": "{}",
            "expired_at": self.expired_at,
            "id": self.policy_id,
        }


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

        old_policy.related_resource_types = policy.related_resource_types
        old_policy.expired_at = policy.expired_at
        old_policy.policy_id = policy.policy_id


class BackendThinPolicy(BaseModel):
    id: int
    system: str
    action_id: str
    expired_at: int


class SystemCounter(BaseModel):
    id: str
    count: int


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

    def list_by_subject(self, system_id: str, subject: Subject) -> List[Policy]:
        """
        查询subject指定系统下的所有Policy
        """
        qs = PolicyModel.objects.filter(system_id=system_id, subject_type=subject.type, subject_id=subject.id)

        return self._trans_from_queryset(system_id, subject, qs)

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
        db_policy = PolicyModel.objects.get(policy_id=policy_id, subject_type=subject.type, subject_id=subject.id)

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

    def get_backend_expression_by_subject_action(
        self, system_id: str, action_id: str, subject: Subject
    ) -> Dict[str, Any]:
        """
        获取subject指定action的后端表达式
        """
        return iam.get_backend_expression(system_id, subject.dict(), action_id)

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
