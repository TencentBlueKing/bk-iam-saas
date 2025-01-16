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
from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Any, List, Optional

from backend.biz.policy import (
    ConditionBean,
    InstanceBean,
    PathNodeBean,
    PathNodeBeanList,
    PolicyBean,
    PolicyBeanList,
    RelatedResourceBean,
    ResourceGroupBean,
    ResourceGroupBeanList,
)
from backend.service.models import Attribute, Value
from backend.service.utils.translate import translate_path

from .constants import ConditionTag


class AbstractTagBean(ABC):
    @abstractmethod
    def set_tag(self, tag: str):
        pass


class TagNoneMixin:
    """
    兼容 tag 为None的情况
    """

    def __init__(self, **data: Any) -> None:
        if "tag" in data and not isinstance(data["tag"], str):
            data.pop("tag")
        super().__init__(**data)  # type: ignore


class PathNodeTagBean(TagNoneMixin, PathNodeBean, AbstractTagBean):
    tag: str = ""

    def set_tag(self, tag: str):
        self.tag = tag


class PathNodeTagBeanList(PathNodeBeanList):
    def __init__(__pydantic_self__, **data: Any) -> None:
        super().__init__(**deepcopy(data))

    def set_tag(self, tag: str):
        for node in self.root:
            node.set_tag(tag)


class InstanceTagBean(TagNoneMixin, InstanceBean, AbstractTagBean):
    path: List[PathNodeTagBeanList]
    tag: str = ""

    def iter_path_node(self):
        for p in self.path:
            for node in p:
                yield node

    def set_tag(self, tag: str):
        self.tag = tag
        for node in self.iter_path_node():
            node.set_tag(tag)

    def _get_path_set(self):
        return {translate_path(p.dict()) for p in self.path}

    def compare_and_tag(self, instance: "InstanceTagBean") -> "InstanceTagBean":
        tag_instance = InstanceTagBean(tag=ConditionTag.UNCHANGED.value, type=self.type, name=self.name, path=[])

        # 生成path hash set
        new_path_set = self._get_path_set()
        old_path_dict = {translate_path(p.dict()): p for p in instance.path}

        for p in self.path:
            copied_p = p.copy()
            # 标记新增的path
            if translate_path(copied_p.dict()) not in old_path_dict:
                copied_p.set_tag(ConditionTag.ADD.value)
            else:
                copied_p.set_tag(ConditionTag.UNCHANGED.value)
            tag_instance.path.append(copied_p)

        # 标记删除的path
        for p in instance.path:
            copied_p = p.copy()
            if translate_path(copied_p.dict()) not in new_path_set:
                copied_p.set_tag(ConditionTag.DELETE.value)
                tag_instance.path.append(copied_p)

        return tag_instance


class ValueTagBean(TagNoneMixin, Value, AbstractTagBean):
    tag: str = ""

    def set_tag(self, tag: str):
        self.tag = tag


class AttributeTagBean(TagNoneMixin, Attribute, AbstractTagBean):
    values: List[ValueTagBean]
    tag: str = ""

    def set_tag(self, tag: str):
        self.tag = tag
        for v in self.values:
            v.set_tag(tag)

    def compare_and_tag(self, attribute: "AttributeTagBean") -> "AttributeTagBean":
        tag_attribute = AttributeTagBean(tag=ConditionTag.UNCHANGED.value, id=self.id, name=self.name, values=[])

        new_id_set = {v.id for v in self.values}
        old_id_set = {v.id for v in attribute.values}

        for v in deepcopy(self.values):
            # 标记新增的属性
            if v.id not in old_id_set:
                v.tag = ConditionTag.ADD.value
            else:
                v.tag = ConditionTag.UNCHANGED.value
            tag_attribute.values.append(v)

        # 标记删除的属性
        if old_id_set - new_id_set:
            for v in deepcopy(attribute.values):
                if v.id not in new_id_set:
                    v.tag = ConditionTag.DELETE.value
                    tag_attribute.values.append(v)

        return tag_attribute


class ConditionTagBean(TagNoneMixin, ConditionBean, AbstractTagBean):
    instances: List[InstanceTagBean]
    attributes: List[AttributeTagBean]
    tag: str = ""

    def set_tag(self, tag: str):
        self.tag = tag
        for i in self.instances:
            i.set_tag(tag)
        for a in self.attributes:
            a.set_tag(tag)

    def compare_and_tag(self, condition: "ConditionTagBean") -> "ConditionTagBean":
        """
        对比单个条件
        """
        tag_condition = ConditionTagBean(tag=ConditionTag.UNCHANGED.value, id=self.id, instances=[], attributes=[])

        new_instance_type_set = {i.type for i in self.instances}
        old_instance_type_set = {i.type for i in condition.instances}
        old_instance_type_dict = {i.type: i for i in condition.instances}

        # 比较每一组实例
        for i in self.instances:
            # 如果实例类型在老的实例中不存在, 则属于新增
            if i.type not in old_instance_type_set:
                tag_instance = deepcopy(i)
                tag_instance.set_tag(ConditionTag.ADD.value)
                tag_condition.instances.append(tag_instance)
            # 已存在, 需要继续对比
            else:
                tag_condition.instances.append(i.compare_and_tag(old_instance_type_dict[i.type]))

        # 如果有老的不在新的实例中, 打上删除标签, 加入到实例数据后面
        if old_instance_type_set - new_instance_type_set:
            for i in condition.instances:
                if i.type not in new_instance_type_set:
                    tag_instance = deepcopy(i)
                    tag_instance.set_tag(ConditionTag.DELETE.value)
                    tag_condition.instances.append(tag_instance)

        new_attribute_id_set = {i.id for i in self.attributes}
        old_attribute_id_set = {i.id for i in condition.attributes}
        old_attribute_id_dict = {i.id: i for i in condition.attributes}

        # 比较每一组属性
        for a in self.attributes:
            # 如果属性的key不在老的属性数据中, 则属于新增
            if a.id not in old_attribute_id_set:
                tag_attribute = deepcopy(a)
                tag_attribute.set_tag(ConditionTag.ADD.value)
                tag_condition.attributes.append(tag_attribute)
            # 如果在老的数据中, 则继续对比
            else:
                tag_condition.attributes.append(a.compare_and_tag(old_attribute_id_dict[a.id]))

        # 如果有老的不在新的属性数据中, 打上删除标签, 加入到属性数据后面
        if old_attribute_id_set - new_attribute_id_set:
            for a in condition.attributes:
                if a.id not in new_attribute_id_set:
                    tag_attribute = deepcopy(a)
                    tag_attribute.set_tag(ConditionTag.DELETE.value)
                    tag_condition.attributes.append(tag_attribute)

        return tag_condition


class RelatedResourceTagBean(RelatedResourceBean):
    condition: List[ConditionTagBean]

    def set_tag(self, tag: str):
        for c in self.condition:
            c.set_tag(tag)


class ResourceGroupTagBean(TagNoneMixin, ResourceGroupBean):
    related_resource_types: List[RelatedResourceTagBean]
    tag: str = ""

    def set_tag(self, tag: str):
        self.tag = tag
        for rt in self.related_resource_types:
            rt.set_tag(tag)


class ResourceGroupListTagBean(TagNoneMixin, ResourceGroupBeanList[ResourceGroupTagBean]):
    pass


class PolicyTagBean(TagNoneMixin, PolicyBean):
    resource_groups: ResourceGroupListTagBean
    tag: str = ""

    def set_tag(self, tag: str):
        self.tag = tag
        for rg in self.resource_groups:
            rg.set_tag(tag)


class PolicyTagBeanList(PolicyBeanList):
    def __init__(self, system_id: str, policies: List[PolicyTagBean]) -> None:
        super().__init__(system_id, policies)

    def set_tag(self, tag: str):
        for p in self.policies:
            p.set_tag(tag)

    def get(self, action_id: str) -> Optional[PolicyTagBean]:
        return self._policy_dict.get(action_id, None)


class ConditionTagBiz:
    def compare_and_tag(
        self, new_conditions: List[ConditionTagBean], old_conditions: List[ConditionTagBean], is_template=False
    ) -> List[ConditionTagBean]:
        """
        对比申请条件与已有权限条件的差异

        对比合并条件数据, 并对数据打上标签 新增/不变/删除
        """
        delete_tag = ConditionTag.DELETE.value if is_template else ConditionTag.UNCHANGED.value

        # 生成以属性的hash为key, 并且实例不为空的条件的字典
        new_dict = {c.hash_attributes(): c for c in new_conditions if not c.has_no_instances()}
        old_dict = {c.hash_attributes(): c for c in old_conditions if not c.has_no_instances()}

        # 实例不为空条件的属性hash set
        new_set = set(new_dict.keys())
        old_set = set(old_dict.keys())

        # 生成以属性的hash为key, 并且实例为空的条件的字典
        new_empty_dict = {c.hash_attributes(): c for c in new_conditions if c.has_no_instances()}
        old_empty_dict = {c.hash_attributes(): c for c in old_conditions if c.has_no_instances()}

        # 实例为空的条件的属性hash set
        new_empty_set = set(new_empty_dict.keys())
        old_empty_set = set(old_empty_dict.keys())

        tag_condition = []

        # 标记新增的条件
        for key in new_set - old_set:
            condition = new_dict[key]
            condition.set_tag(ConditionTag.ADD.value)
            tag_condition.append(condition)

        # 标记变更或不变的条件
        for key in new_set & old_set:
            new_condition = new_dict[key]
            old_condition = old_dict[key]
            tag_condition.append(new_condition.compare_and_tag(old_condition))

        # 标记移除的条件
        for key in old_set - new_set:
            condition = old_dict[key]
            condition.set_tag(delete_tag)
            tag_condition.append(condition)

        # 标记新增的只有属性的条件
        for key in new_empty_set - old_empty_set:
            condition = new_empty_dict[key]
            condition.set_tag(ConditionTag.ADD.value)
            tag_condition.append(condition)

        # 标记未变的只有属性的条件
        for key in new_empty_set & old_empty_set:
            condition = new_empty_dict[key]
            condition.set_tag(ConditionTag.UNCHANGED.value)
            tag_condition.append(condition)

        # 标记移除的只有属性的条件
        for key in old_empty_set - new_empty_set:
            condition = old_empty_dict[key]
            condition.set_tag(delete_tag)
            tag_condition.append(condition)

        return sorted(tag_condition, key=lambda c: c.id)
