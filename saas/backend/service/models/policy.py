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
from typing import Any, List, Tuple

from pydantic import BaseModel, Field

from backend.apps.policy.models import Policy as PolicyModel
from backend.service.utils.translate import ResourceExpressionTranslator
from backend.util.uuid import gen_uuid

from .subject import Subject


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


class BackendThinPolicy(BaseModel):
    id: int
    system: str
    action_id: str
    expired_at: int


class SystemCounter(BaseModel):
    id: str
    count: int


class PolicyIDExpiredAt(BaseModel):
    id: int
    expired_at: int
