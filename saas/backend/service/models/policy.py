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
from collections import namedtuple
from typing import Any, Dict, List, Tuple, Union

from pydantic import BaseModel, Field

from backend.apps.policy.models import Policy as PolicyModel
from backend.apps.policy.models import TemporaryPolicy
from backend.service.constants import ANY_ID, DEAULT_RESOURCE_GROUP_ID
from backend.service.utils.translate import ResourceExpressionTranslator
from backend.util.model import ListModel
from backend.util.uuid import gen_uuid

from .action import Action, InstanceSelection
from .instance_selection import PathResourceType
from .subject import Subject


class PathNode(BaseModel):
    id: str
    name: str
    system_id: str = ""  # NOTE 兼容一下, 早期的policy数据中可能没有system_id
    type: str

    def __hash__(self):
        return hash((self.system_id, self.type, self.id))

    def __eq__(self, other):
        return self.system_id == other.system_id and self.type == other.type and self.id == other.id

    def to_path_resource_type(self) -> PathResourceType:
        return PathResourceType(system_id=self.system_id, id=self.type)

    def match_resource_type(self, resource_system_id: str, resource_type_id: str) -> bool:
        """
        是否匹配资源类型
        """
        return self.system_id == resource_system_id and self.type == resource_type_id


class PathNodeList(ListModel):
    __root__: List[PathNode]

    def match_selection(self, resource_system_id: str, resource_type_id: str, selection: InstanceSelection) -> bool:
        """
        检查是否匹配实例视图
        """
        # 链路只有一层, 并且与资源类型匹配
        if len(self.__root__) == 1 and self.__root__[0].match_resource_type(resource_system_id, resource_type_id):
            return True

        return selection.match_path(self._to_path_resource_types())

    def _to_path_resource_types(self) -> List[PathResourceType]:
        return [one.to_path_resource_type() for one in self.__root__]

    def ignore_path(self, selection: InstanceSelection) -> "PathNodeList":
        """
        根据实例视图, 返回忽略路径后的链路
        """
        if (
            selection.ignore_iam_path
            and len(self.__root__) == len(selection.resource_type_chain)
            and self.__root__[-1].id != ANY_ID
        ):
            return PathNodeList(__root__=[self.__root__[-1]])

        return self


class Instance(BaseModel):
    type: str
    path: List[PathNodeList]

    def ignore_path(self, resource_system_id: str, resource_type_id: str, selections: List[InstanceSelection]):
        """
        检查实例视图
        """
        for i in range(len(self.path)):
            node_list = self.path[i]
            for selection in selections:
                if node_list.match_selection(resource_system_id, resource_type_id, selection):
                    self.path[i] = node_list.ignore_path(selection)
                    break


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

    def ignore_path(self, selections: List[InstanceSelection]):
        """
        校验条件中的实例拓扑是否满足实例视图
        """
        for c in self.condition:
            if c.has_no_instances():
                continue

            for instance in c.instances:
                instance.ignore_path(self.system_id, self.type, selections)


class EnvValue(BaseModel):
    name: str = ""
    value: Any


class EnvCondition(BaseModel):
    type: str
    values: List[EnvValue]

    def trim_for_hash(self) -> Tuple[str, Any]:
        return self.type, tuple(sorted([v.value for v in self.values]))


class Environment(BaseModel):
    type: str
    condition: List[EnvCondition]

    def trim_for_hash(self) -> Tuple[str, Any]:
        return self.type, tuple(sorted([c.trim_for_hash() for c in self.condition], key=lambda c: c[0]))


class ResourceGroup(BaseModel):
    id: str = ""
    related_resource_types: List[RelatedResource]
    environments: List[Environment] = []

    def hash_environments(self) -> int:
        """
        计算环境属性hash值
        """
        return hash(tuple(sorted([e.trim_for_hash() for e in self.environments], key=lambda e: e[0])))

    def ignore_path(self, action: Action):
        for rrt in self.related_resource_types:
            resource_type = action.get_related_resource_type(rrt.system_id, rrt.type)
            if not resource_type:
                continue
            rrt.ignore_path(resource_type.instance_selections)


ThinResourceType = namedtuple("ThinResourceType", ["system_id", "type"])


class ResourceGroupList(ListModel):
    __root__: List[ResourceGroup]

    def get_thin_resource_types(self) -> List[ThinResourceType]:
        """
        获取资源类型列表
        """
        if len(self) == 0:
            return []

        return [ThinResourceType(rrt.system_id, rrt.type) for rrt in self[0].related_resource_types]


class Policy(BaseModel):
    action_id: str = Field(alias="id")
    policy_id: int
    expired_at: int
    resource_groups: ResourceGroupList

    class Config:
        allow_population_by_field_name = True  # 支持alias字段同时传 action_id 与 id

    def __init__(self, **data: Any):
        # NOTE 兼容 role, group授权信息的旧版结构
        if "resource_groups" not in data and "related_resource_types" in data:
            if not data["related_resource_types"]:
                data["resource_groups"] = []
            else:
                data["resource_groups"] = [
                    # NOTE: 固定resource_group_id方便删除逻辑
                    {
                        "id": DEAULT_RESOURCE_GROUP_ID,
                        "related_resource_types": data.pop("related_resource_types"),
                    }
                ]

        super().__init__(**data)

    @staticmethod
    def _is_old_structure(resources: List[Dict[str, Any]]) -> bool:
        """
        是否是老的policy结构
        """
        for r in resources:
            if "condition" in r and "system_id" in r and "type" in r:
                return True
        return False

    @classmethod
    def from_db_model(cls, policy: Union[PolicyModel, TemporaryPolicy], expired_at: int) -> "Policy":
        # 兼容新老结构
        resource_groups = policy.resources
        if cls._is_old_structure(policy.resources):
            # NOTE: 固定resource_group_id, 方便删除逻辑
            resource_groups = [ResourceGroup(id=DEAULT_RESOURCE_GROUP_ID, related_resource_types=policy.resources)]

        return cls(
            action_id=policy.action_id,
            policy_id=policy.policy_id,
            expired_at=expired_at,
            resource_groups=ResourceGroupList.parse_obj(resource_groups),
        )

    def to_db_model(self, system_id: str, subject: Subject) -> PolicyModel:
        p = PolicyModel(
            subject_type=subject.type,
            subject_id=subject.id,
            system_id=system_id,
            action_type="",
            action_id=self.action_id,
        )
        p.resources = self.resource_groups.dict()
        return p

    def to_temporary_model(self, system_id: str, subject: Subject) -> TemporaryPolicy:
        p = TemporaryPolicy(
            subject_type=subject.type,
            subject_id=subject.id,
            system_id=system_id,
            action_type="",
            action_id=self.action_id,
            expired_at=self.expired_at,
        )
        p.resources = self.resource_groups.dict()
        return p

    def to_backend_dict(self, system_id: str):
        translator = ResourceExpressionTranslator()
        return {
            "action_id": self.action_id,
            "resource_expression": translator.translate(system_id, self.resource_groups.dict()),
            "environment": "{}",
            "expired_at": self.expired_at,
            "id": self.policy_id,
        }

    def list_thin_resource_type(self) -> List[ThinResourceType]:
        """
        获取权限关联的资源类型列表
        """
        return self.resource_groups.get_thin_resource_types()

    def ignore_path(self, action: Action):
        """
        检查资源的实例视图是否匹配
        """
        for rg in self.resource_groups:
            rg.ignore_path(action)


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
