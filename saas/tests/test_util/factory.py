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
from typing import Dict, List, Optional

from backend.biz.policy import ConditionBean, InstanceBean, PolicyBean, RelatedResourceBean
from backend.service.models import (
    Action,
    Attribute,
    Condition,
    Instance,
    InstanceSelection,
    Policy,
    RelatedResource,
    RelatedResourceType,
    ResourceInstance,
)


class AttributeFactory:
    """属性数据生成"""

    def new_dict(self, _id: str, name: str, values: Optional[List[Dict]] = None) -> Dict:
        return {"id": _id, "name": name, "values": values or []}

    def example(self) -> Attribute:
        return self.new("os", "os", [{"id": "linux", "name": "linux"}])

    def new(self, _id: str, name: str, values: Optional[List[Dict]] = None) -> Attribute:
        return Attribute(**self.new_dict(_id, name, values))


class InstanceFactory:
    def new_dict(self, _type: str, name: str, paths: Optional[List[List[Dict]]] = None) -> Dict:
        return {
            "name": name,
            "type": _type,
            "path": paths or [],
        }

    def example(self) -> Instance:
        return self.new(
            "host", "主机", [[{"system_id": "bk_cmdb", "type": "host", "type_name": "主机", "id": "host1", "name": "主机1"}]]
        )

    def new(self, _type: str, name: str, paths: Optional[List[List[Dict]]] = None) -> Instance:
        return Instance(**self.new_dict(_type, name, paths))


class InstanceBeanFactory:
    def new_dict(self, _type: str, name: str, paths: Optional[List[List[Dict]]] = None) -> Dict:
        return {
            "name": name,
            "type": _type,
            "path": paths or [],
        }

    def example(self) -> InstanceBean:
        return self.new(
            "host", "主机", [[{"system_id": "bk_cmdb", "type": "host", "type_name": "主机", "id": "host1", "name": "主机1"}]]
        )

    def new(self, _type: str, name: str, paths: Optional[List[List[Dict]]] = None) -> InstanceBean:
        return InstanceBean(**self.new_dict(_type, name, paths))


class ConditionFactory:
    """条件数据生成"""

    def __init__(self):
        self.attribute_factory = AttributeFactory()
        self.instance_factory = InstanceFactory()

    def new_dict(self, instances: Optional[List[Dict]] = None, attributes: Optional[List[Dict]] = None) -> Dict:
        return {"instances": instances or [], "attributes": attributes or []}

    def example(self) -> Condition:
        return self.new([self.instance_factory.example()], [self.attribute_factory.example()])

    def new(
        self, instances: Optional[List[Instance]] = None, attributes: Optional[List[Attribute]] = None
    ) -> Condition:
        return Condition(**self.new_dict([i.dict() for i in instances or []], [a.dict() for a in attributes or []]))


class ConditionBeanFactory:
    """条件数据生成"""

    def __init__(self):
        self.attribute_factory = AttributeFactory()
        self.instance_factory = InstanceBeanFactory()

    def new_dict(self, instances: Optional[List[Dict]] = None, attributes: Optional[List[Dict]] = None) -> Dict:
        return {"instances": instances or [], "attributes": attributes or []}

    def example(self) -> ConditionBean:
        return self.new([self.instance_factory.example()], [self.attribute_factory.example()])

    def new(
        self, instances: Optional[List[InstanceBean]] = None, attributes: Optional[List[Attribute]] = None
    ) -> ConditionBean:
        return ConditionBean(
            **self.new_dict([i.dict() for i in instances or []], [a.dict() for a in attributes or []])
        )


class ResourceFactory:
    def __init__(self):
        self.condition_factory = ConditionFactory()

    def new_dict(self, system_id: str, _type: str, name: str, condition: Optional[List[Dict]] = None) -> Dict:
        return {"system_id": system_id, "type": _type, "name": name, "condition": condition or []}

    def example(self) -> RelatedResource:
        return self.new("bk_cmdb", "host", "主机", [self.condition_factory.example()])

    def new(
        self, system_id: str, _type: str, name: str, condition: Optional[List[Condition]] = None
    ) -> RelatedResource:
        return RelatedResource(**self.new_dict(system_id, _type, name, [c.dict() for c in condition or []]))


class RelatedResourceBeanFactory:
    def __init__(self):
        self.condition_factory = ConditionBeanFactory()

    def new_dict(self, system_id: str, _type: str, name: str, condition: Optional[List[Dict]] = None) -> Dict:
        return {"system_id": system_id, "type": _type, "name": name, "condition": condition or []}

    def example(self) -> RelatedResourceBean:
        return self.new("bk_cmdb", "host", "主机", [self.condition_factory.example()])

    def new(
        self, system_id: str, _type: str, name: str, condition: Optional[List[Condition]] = None
    ) -> RelatedResourceBean:
        return RelatedResourceBean(**self.new_dict(system_id, _type, name, [c.dict() for c in condition or []]))


class InstanceSelectionFactory:
    def new(
        self, _id: str, system_id: str, ignore_iam_path: bool, resource_type_chain: List[Dict]
    ) -> InstanceSelection:
        return InstanceSelection(
            id=_id,
            system_id=system_id,
            name=_id,
            name_en=_id,
            ignore_iam_path=ignore_iam_path,
            resource_type_chain=resource_type_chain,
        )

    def example(self) -> InstanceSelection:
        return self.new(
            "test",
            "bk_cmdb",
            False,
            [
                {"system_id": "bk_cmdb", "id": "biz"},
                {"system_id": "bk_cmdb", "id": "set"},
                {"system_id": "bk_cmdb", "id": "module"},
                {"system_id": "bk_cmdb", "id": "host"},
            ],
        )


class RelatedResourceTypeFactory:
    def __init__(self):
        self.instance_selection_factory = InstanceSelectionFactory()

    def new(self, _id: str, system_id: str, instance_selections: List[InstanceSelection]) -> RelatedResourceType:
        return RelatedResourceType(
            id=_id, system_id=system_id, name=_id, name_en=_id, instance_selections=instance_selections
        )

    def example(self) -> RelatedResourceType:
        return self.new("host", "bk_cmdb", [self.instance_selection_factory.example()])


class ActionFactory:
    def __init__(self):
        self.related_resource_type_factory = RelatedResourceTypeFactory()

    def new(self, _id: str, _type: str, related_resource_types: List[RelatedResourceType]) -> Action:
        return Action(
            id=_id,
            type=_type,
            name=_id,
            name_en=_id,
            description=_id,
            description_en=_id,
            related_resource_types=related_resource_types,
        )

    def example(self):
        return self.new("view_host", "host", [self.related_resource_type_factory.example()])


class ResourceInstanceFactory:
    def __init__(self):
        self.instance_factory = InstanceFactory()

    def new(self, system_id: str, _type: str, instances: List[Instance]) -> ResourceInstance:
        return ResourceInstance(system_id=system_id, type=_type, instances=instances)

    def example(self):
        return self.new("bk_cmdb", "host", [self.instance_factory.example()])


class PolicyFactory:
    def __init__(self):
        self.resource_factory = ResourceFactory()

    def new(self, _id: str, related_resource_types: List[RelatedResource]):
        return Policy(id=_id, related_resource_types=related_resource_types, environment={})

    def example(self):
        return self.new("view_host", [self.resource_factory.example()])


class PolicyBeanFactory:
    def __init__(self):
        self.resource_factory = RelatedResourceBeanFactory()

    def new(self, _id: str, related_resource_types: List[RelatedResourceBean]):
        return PolicyBean(id=_id, related_resource_types=related_resource_types, environment={})

    def example(self):
        return self.new("view_host", [self.resource_factory.example()])
