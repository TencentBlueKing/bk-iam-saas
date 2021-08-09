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
import logging
from copy import deepcopy
from itertools import chain, groupby
from typing import Any, Dict, List, Optional, Set, Tuple

from pydantic import BaseModel, Extra

from backend.apps.policy.models import Policy as PolicyModel
from backend.common.error_codes import error_codes
from backend.common.time import expired_at_display
from backend.service.models.instance_selection import PathResourceType
from backend.service.models.resource_type import ResourceTypeDict
from backend.util.uuid import gen_uuid

from ..constants import ANY_ID, ConditionTag, PolicyTag
from ..utils.translate import ResourceExpressionTranslator, translate_path
from .action import Action, InstanceSelection, RelatedResourceType
from .resource_type import ResourceNode
from .system import Subject

logger = logging.getLogger("app")

# TODO 需要删除这个文件


class PathHelper:
    """
    path: List[Dict]

    整体封装Instance中Path相关的操作
    """

    def __init__(self, path: List[Dict[str, Any]]):
        self.path = path

    def check_selection_ignore_path(  # TODO 复用selection check逻辑, 只有selection 需要ignore的时候才需要做ignore的逻辑
        self, rrt: "RelatedResource", selection: InstanceSelection
    ) -> Tuple[bool, Optional[List[Dict]]]:
        """
        检查实例拓扑是否匹配实例视图
        """
        if len(self.path) == 1:
            node = self.path[0]
            # 只有一个节点, 节点与关联资源类型相同, 不需要再检查实例视图
            # 可能是从授权接口, 新建关联等等方式授权而来
            if node["system_id"] == rrt.system_id and node["type"] == rrt.type:
                return True, self.path

        path_resource_types = [PathResourceType(system_id=node["system_id"], id=node["type"]) for node in self.path]
        if not selection.match_path(path_resource_types):
            return False, None

        # 完全匹配忽略路径的实例视图, 并且忽略路径, 只取最后一个节点, 并且最后一个节点不是任意
        if (
            selection.ignore_iam_path
            and len(self.path) == len(selection.resource_type_chain)  # noqa
            and self.path[-1]["id"] != ANY_ID  # noqa
        ):
            return True, self.path[-1:]

        return True, self.path


class Instance(BaseModel):
    type: str
    name: str = ""
    name_en: str = ""
    path: List[Any]
    tag: Optional[str] = None

    def __init__(self, **data: Any):
        super().__init__(**deepcopy(data))

    def set_tag(self, tag: str, recursive=False):
        self.tag = tag
        if recursive:
            path = self.path
            self.path = []
            for p in path:
                self.path.append({"tag": tag, "chain": p})

    def __add__(self, instance: "Instance") -> "Instance":
        path_set = self._get_path_set()
        for p in instance.path:
            if translate_path(p) not in path_set:
                self.path.append(deepcopy(p))
        return self

    def __contains__(self, instance: "Instance") -> bool:
        path_set = self._get_path_set()
        for p in instance.path:
            if translate_path(p) not in path_set:
                return False
        return True

    def __sub__(self, instance: "Instance") -> "Instance":
        path_set = instance._get_path_set()
        self.path = [p for p in self.path if translate_path(p) not in path_set]
        return self

    def diff(self, instance: "Instance") -> "Instance":
        tag_instance = Instance(tag=ConditionTag.UNCHANGED.value, type=self.type, name=self.name, path=[])

        new_path_set = self._get_path_set()
        old_path_dict = {translate_path(p): p for p in instance.path}

        for p in self.path:
            if translate_path(p) not in old_path_dict:
                tag_instance.path.append({"tag": ConditionTag.ADD.value, "chain": p})
            else:
                tag_instance.path.append({"tag": ConditionTag.UNCHANGED.value, "chain": p})

        if set(old_path_dict.keys()) - new_path_set:
            for p in instance.path:
                if translate_path(p) not in new_path_set:
                    tag_instance.path.append({"tag": ConditionTag.DELETE.value, "chain": p})

        return tag_instance

    def compare(self, instance: "Instance") -> bool:
        return self._get_path_set() == instance._get_path_set()

    def add_instance(self, instance: "Instance") -> bool:
        """
        授权api增加合并实例数据, 返回已有实例是否变更标志
        """
        path_set = self._get_path_set()
        length = len(self.path)

        for p in instance.path:
            if translate_path(p) not in path_set:
                self.path.append(p)

        return length != len(self.path)

    def _get_path_set(self):
        return {translate_path(p) for p in self.path}

    def remove_instance(self, instance: "Instance") -> bool:
        """
        回收实例权限, 返回已有实例是否变更标志
        """
        path_set = instance._get_path_set()
        length = len(self.path)

        self.path = [p for p in self.path if translate_path(p) not in path_set]
        return length != len(self.path)

    def list_resource_node(self) -> List[ResourceNode]:
        """
        通过拆解每个路径里的层级，返回所有拆解出的单一资源实例
        """
        return [ResourceNode(**node) for path in self.path for node in path]

    def check_selection_ignore_path(self, rrt: "RelatedResource", selections: List[InstanceSelection]):
        """
        检查实例拓扑是否匹配实例视图
        """
        for i in range(len(self.path)):
            helper = PathHelper(self.path[i])
            for selection in selections:
                ok, path = helper.check_selection_ignore_path(rrt, selection)
                if ok:
                    self.path[i] = path
                    break
            else:
                raise error_codes.VALIDATE_ERROR.format(
                    "{} could not match any instance selection".format(self._path_display(helper.path))
                )

    def _path_display(self, path: List[Dict]) -> str:
        """
        转换拓扑节点, 返回显示字符串
        """
        return "/".join(["{}:{}".format(node["type_name"], node["name"]) for node in path])

    def get_system_set(self):
        """
        获取所有节点中的system_id
        """
        return {node["system_id"] for path in self.path for node in path}

    def fill_type_name(self, resource_type_dict: ResourceTypeDict):
        """
        填充资源类型名称
        """
        for path in self.path:
            for node in path:
                node["type_name"], node["type_name_en"] = resource_type_dict.get_name(node["system_id"], node["type"])

                if self.type == node["type"]:
                    self.name = node["type_name"]
                    self.name_en = node["type_name_en"]

                if node["id"] == ANY_ID:
                    node["name"] = "{}: 无限制".format(node["type_name"])

    def fill_node_name(self, resource_info_name_dict: Dict[ResourceNode, str]) -> None:
        """
        填充每个节点资源实例名称
        """
        for p in self.path:
            for n in p:
                n["name"] = resource_info_name_dict[ResourceNode(**n)]

    def path_count(self):
        return len(self.path)

    def set_path_node_tag_ADD(self):
        for p in self.path:
            for node in p:
                node["tag"] = ConditionTag.ADD.value


class Attribute(BaseModel):
    id: str
    name: str = ""
    values: List[Dict[str, str]]
    tag: Optional[str] = None

    def __init__(self, **data: Any):
        super().__init__(**deepcopy(data))

    def set_tag(self, tag: str, recursive=False):
        self.tag = tag
        if recursive:
            for v in self.values:
                v["tag"] = tag

    def sort_values(self):
        self.values.sort(key=lambda value: value["id"])

    def trim(self) -> Tuple:
        return self.id, tuple([value["id"] for value in self.values])

    def diff(self, attribute: "Attribute") -> "Attribute":
        tag_attribute = Attribute(tag=ConditionTag.UNCHANGED.value, id=self.id, name=self.name, values=[])

        new_id_set = {v["id"] for v in self.values}
        old_id_set = {v["id"] for v in attribute.values}

        for v in deepcopy(self.values):
            if v["id"] not in old_id_set:
                v["tag"] = ConditionTag.ADD.value
            else:
                v["tag"] = ConditionTag.UNCHANGED.value
            tag_attribute.values.append(v)

        if old_id_set - new_id_set:
            for v in deepcopy(attribute.values):
                if v["id"] not in new_id_set:
                    v["tag"] = ConditionTag.DELETE.value
                    tag_attribute.values.append(v)

        return tag_attribute

    def compare(self, attribute: "Attribute") -> bool:
        return {value["id"] for value in self.values} == {value["id"] for value in attribute.values}


# TODO 一些只负责做类型转换的结构, 提取到biz中
class ResourceInstance(BaseModel):
    """
    实例/路径授权结构, 只用户授权
    """

    system_id: str
    type: str
    instances: List[Instance]
    type_name: str = ""
    type_name_en: str = ""

    def get_system_set(self) -> Set[str]:
        """
        获取所有的system_id
        """
        ids = set.union(*[instance.get_system_set() for instance in self.instances]) if self.instances else set()
        ids.add(self.system_id)
        return ids

    def fill_type_name(self, resource_type_dict: ResourceTypeDict):
        """
        填充资源类型名称
        """
        self.type_name, self.type_name_en = resource_type_dict.get_name(self.system_id, self.type)

        for instance in self.instances:
            instance.fill_type_name(resource_type_dict)


# TODO 提到biz中
class ResourceInstanceList:
    def __init__(self, resource_instances: List[ResourceInstance]) -> None:
        self.resource_instances = resource_instances

    def fill_resource_type_name(self):
        """
        填充资源类型的名称
        """
        # TODO 提取到biz后, 解除循环依赖
        from backend.service.resource_type import ResourceTypeService

        system_ids = list(set.union(*[r.get_system_set() for r in self.resource_instances]))
        resource_type_dict = ResourceTypeService().get_resource_type_dict(system_ids)
        for resource_instance in self.resource_instances:
            resource_instance.fill_type_name(resource_type_dict)


class Condition(BaseModel):
    instances: List[Instance]
    attributes: List[Attribute]
    id: str = ""
    tag: Optional[str] = None

    def set_tag(self, tag: str, recursive=False):
        self.tag = tag
        if recursive:
            for i in self.instances:
                i.set_tag(tag, recursive)
            for a in self.attributes:
                a.set_tag(tag, recursive)

    def sort_attributes(self):
        for a in self.attributes:
            a.sort_values()
        self.attributes.sort(key=lambda attribute: attribute.id)

    def hash_attributes(self) -> Tuple:
        self.sort_attributes()
        return tuple([attribute.trim() for attribute in self.attributes])

    def is_attributes_empty(self) -> bool:
        return len(self.attributes) == 0

    def is_instances_empty(self) -> bool:
        return len(self.instances) == 0

    def merge_instances(self, instances: List[Instance]):
        """
        合并传入的实例, 去重
        """
        instances_dict = {instance.type: instance for instance in self.instances}
        for instance in instances:
            _type = instance.type
            if _type in instances_dict:
                instances_dict[_type] + instance
            else:
                self.instances.append(deepcopy(instance))

    def has_instances(self, instances: List[Instance]) -> bool:
        """
        判断是否包含传入的实例
        """
        instances_dict = {instance.type: instance for instance in self.instances}
        for instance in instances:
            _type = instance.type
            if _type in instances_dict:
                if instance not in instances_dict[_type]:
                    return False
            else:
                return False
        return True

    def remove_instances(self, instances: List[Instance]):
        """
        移除传入的实例
        """
        instances_dict = {instance.type: instance for instance in self.instances}
        for instance in instances:
            _type = instance.type
            if _type in instances_dict:
                instances_dict[_type] - instance
        self.instances = [instance for instance in self.instances if len(instance.path)]

    def diff(self, condition: "Condition") -> "Condition":
        """
        对比单个条件
        """
        tag_condition = Condition(tag=ConditionTag.UNCHANGED.value, id=self.id, instances=[], attributes=[])

        new_instance_type_set = {i.type for i in self.instances}
        old_instance_type_set = {i.type for i in condition.instances}
        old_instance_type_dict = {i.type: i for i in condition.instances}

        # 比较每一组实例
        for i in self.instances:
            # 如果实例类型在老的实例中不存在, 则属于新增
            if i.type not in old_instance_type_set:
                tag_instance = deepcopy(i)
                tag_instance.set_tag(ConditionTag.ADD.value, True)
                tag_condition.instances.append(tag_instance)
            # 已存在, 需要继续对比
            else:
                tag_condition.instances.append(i.diff(old_instance_type_dict[i.type]))

        # 如果有老的不在新的实例中, 打上删除标签, 加入到实例数据后面
        if old_instance_type_set - new_instance_type_set:
            for i in condition.instances:
                if i.type not in new_instance_type_set:
                    tag_instance = deepcopy(i)
                    tag_instance.set_tag(ConditionTag.DELETE.value, True)
                    tag_condition.instances.append(tag_instance)

        new_attribute_id_set = {i.id for i in self.attributes}
        old_attribute_id_set = {i.id for i in condition.attributes}
        old_attribute_id_dict = {i.id: i for i in condition.attributes}

        # 比较每一组属性
        for a in self.attributes:
            # 如果属性的key不在老的属性数据中, 则属于新增
            if a.id not in old_attribute_id_set:
                tag_attribute = deepcopy(a)
                tag_attribute.set_tag(ConditionTag.ADD.value, True)
                tag_condition.attributes.append(tag_attribute)
            # 如果在老的数据中, 则继续对比
            else:
                tag_condition.attributes.append(a.diff(old_attribute_id_dict[a.id]))

        # 如果有老的不在新的属性数据中, 打上删除标签, 加入到属性数据后面
        if old_attribute_id_set - new_attribute_id_set:
            for a in condition.attributes:
                if a.id not in new_attribute_id_set:
                    tag_attribute = deepcopy(a)
                    tag_attribute.set_tag(ConditionTag.DELETE.value, True)
                    tag_condition.attributes.append(tag_attribute)

        return tag_condition

    def compare(self, condition: "Condition") -> bool:
        """
        比较条件
        """
        new_instance_dict = {instance.type: instance for instance in self.instances}
        old_instance_dict = {instance.type: instance for instance in condition.instances}

        if set(new_instance_dict.keys()) != set(old_instance_dict.keys()):
            return False

        for key in new_instance_dict.keys():
            if not new_instance_dict[key].compare(old_instance_dict[key]):
                return False

        # 比较属性选择
        new_attribute_dict = {attribute.id: attribute for attribute in self.attributes}
        old_attribute_dict = {attribute.id: attribute for attribute in condition.attributes}

        if set(new_attribute_dict.keys()) != set(old_attribute_dict.keys()):
            return False

        for key in new_attribute_dict.keys():
            if not new_attribute_dict[key].compare(old_attribute_dict[key]):
                return False

        return True

    def add_instance(self, instance: Instance) -> bool:
        """
        实例授权, 合并到已有的条件中, 返回是否变更标志
        """
        for i in self.instances:
            if i.type == instance.type:
                return i.add_instance(instance)

        self.instances.append(instance)
        return True

    def remove_instance(self, instance: Instance) -> bool:
        """
        回收实例权限, 返回是否变更条件
        """
        is_modified = False
        for i in self.instances:
            if i.type == instance.type:
                if i.remove_instance(instance):
                    is_modified = True

        if is_modified:
            self.instances = [i for i in self.instances if len(i.path) != 0]
        return is_modified

    def list_resource_node(self) -> List[ResourceNode]:
        """
        通过拆解每个路径里的层级，返回所有拆解出的单一资源实例
        """
        nodes = []
        # 遍历每一组实例分组
        for instance in self.instances:
            nodes.extend(instance.list_resource_node())
        return nodes

    def get_system_set(self) -> Set[str]:
        """
        获取所有的system_id
        """
        if self.is_instances_empty():
            return set()
        return set.union(*[instance.get_system_set() for instance in self.instances])

    def instances_count(self, _type: str):
        return sum([i.path_count() for i in self.instances if i.type == _type])

    def iter_path(self):
        for instance in self.instances:
            for path in instance.path:
                yield path

    def set_instance_path_node_tag_ADD(self):
        for instance in self.instances:
            instance.set_path_node_tag_ADD()


class RelatedResource(BaseModel):
    system_id: str
    type: str
    condition: List[Condition]
    name: str = ""
    name_en: str = ""
    tag: Optional[str] = None
    selection_mode: str = ""  # 方便前端使用
    _is_empty: bool = False

    class Config:
        extra = Extra.allow  # 允许Model在初始化时不传部分field

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.merge_self_conditions()

    def merge_self_conditions(self):
        """
        合并条件
        """
        if self.is_any():
            return

        # 筛选出只有属性的条件, 并去重
        empty_instance_contions = {c.hash_attributes(): c for c in self.condition if c.is_instances_empty()}

        # 合并属性相同的实例
        condition_dict: Dict[Any, Condition] = {}
        # 排序可以使有id的排在前面
        for c in sorted(self.condition, key=lambda c: c.id, reverse=True):
            # 如果条件是有实例的
            if not c.is_instances_empty():
                _hash = c.hash_attributes()
                if _hash in condition_dict:
                    condition_dict[_hash].merge_instances(c.instances)
                else:
                    condition_dict[_hash] = c

        conditions = []
        conditions.extend(chain(condition_dict.values(), empty_instance_contions.values()))
        self.condition = conditions

    def merge_conditions(self, conditions: List[Condition], maximize=False):
        """
        合并输入的条件
        """
        if self.is_any() and not self.is_empty():
            return

        if maximize and len(conditions) == 0:
            self.condition = []
            return

        # 分为不带实例的条件与带实例的条件
        empty_instance_contions = {c.hash_attributes(): c for c in self.condition if c.is_instances_empty()}
        condition_dict = {c.hash_attributes(): c for c in self.condition if not c.is_instances_empty()}

        for c in conditions:
            # 如果申请的条件都为空, 不需要合并
            if c.is_instances_empty() and c.is_attributes_empty():
                continue

            _hash = c.hash_attributes()
            # 如果不带实例
            if c.is_instances_empty():
                # 如果计算的条件的属性hash值不在字典中, 需要新增
                if _hash not in empty_instance_contions:
                    empty_instance_contions[_hash] = deepcopy(c)
            else:
                # 带实例的条件如果hash不在字典中, 需要新增, 在字典中, 合并实例
                if _hash not in condition_dict:
                    condition_dict[_hash] = deepcopy(c)
                else:
                    condition_dict[_hash].merge_instances(c.instances)

        conditions = []
        conditions.extend(chain(condition_dict.values(), empty_instance_contions.values()))
        self.condition = conditions
        self._is_empty = len(conditions) == 0

    def remove_conditions(self, conditions: List[Condition]):
        """
        删除已有的条件
        """
        # 如果新旧条件都是任意, 相当于清空
        if self.is_any() and len(conditions) == 0:
            self._is_empty = True
            return

        if self.is_any():
            return

        empty_instance_contions = {c.hash_attributes(): c for c in self.condition if c.is_instances_empty()}
        condition_dict = {c.hash_attributes(): c for c in self.condition if not c.is_instances_empty()}

        for c in conditions:
            _hash = c.hash_attributes()
            if c.is_instances_empty():
                if _hash in empty_instance_contions:
                    empty_instance_contions.pop(_hash)
            else:
                if _hash in condition_dict:
                    # 移除条件中需要删除的部分实例
                    condition_dict[_hash].remove_instances(c.instances)
                    # 如果条件的所有实例都删空了, 需要移除整组条件
                    if condition_dict[_hash].is_instances_empty():
                        condition_dict.pop(_hash)

        conditions = []
        conditions.extend(chain(condition_dict.values(), empty_instance_contions.values()))
        self.condition = conditions
        self._is_empty = len(conditions) == 0  # 如果所有的条件都被删完了, 记录状态

    def has_conditions(self, conditions: List[Condition]) -> bool:
        """
        是否包含所有的条件
        """
        # 如果已有权限是任意, 新的权限不是任意, 则不包含
        if len(conditions) == 0 and not self.is_any():
            return False

        # 如果是任意, 包含所有
        if self.is_any():
            return True

        empty_instance_contions = {c.hash_attributes() for c in self.condition if c.is_instances_empty()}
        condition_dict = {c.hash_attributes(): c for c in self.condition if not c.is_instances_empty()}

        # 三种可能为False
        # 1. 不带实例的条件不在空实例集合中
        # 2. 带实例的条件不在带实例的条件字典中
        # 3. 带实例的条件包含的实例数据超出了现有的数据
        for c in conditions:
            _hash = c.hash_attributes()
            if c.is_instances_empty() and _hash not in empty_instance_contions:
                return False
            elif not c.is_instances_empty() and _hash not in condition_dict:
                return False
            elif (
                not c.is_instances_empty()
                and _hash in condition_dict  # noqa
                and not condition_dict[_hash].has_instances(c.instances)  # noqa
            ):
                return False

        return True

    def is_any(self) -> bool:
        """
        是否是任意
        """
        return len(self.condition) == 0

    def is_empty(self):
        """
        条件是否被删空
        """
        return self._is_empty

    def set_empty(self):
        self.condition = []
        self._is_empty = True

    def compare(self, rt: "RelatedResource") -> bool:
        """
        对比资源类型
        """
        if len(self.condition) != len(rt.condition):
            return False

        # 比较无实例操作是否一致
        if {c.hash_attributes() for c in self.condition if c.is_instances_empty()} != {
            c.hash_attributes() for c in rt.condition if c.is_instances_empty()
        }:
            return False

        new_conditions = {c.hash_attributes(): c for c in self.condition if not c.is_instances_empty()}
        old_conditions = {c.hash_attributes(): c for c in rt.condition if not c.is_instances_empty()}

        if set(new_conditions.keys()) != set(old_conditions.keys()):
            return False

        for key in new_conditions.keys():
            if not new_conditions[key].compare(old_conditions[key]):
                return False

        return True

    def set_tag_update(self):
        self.tag = PolicyTag.UPDATE.value

    def set_tag_unchanged(self):
        self.tag = PolicyTag.UNCHANGED.value

    def set_tag_delete(self):
        self.tag = PolicyTag.DELETE.value

    def get_tag(self) -> Optional[str]:
        return self.tag

    def fill_type_name(self, rrt: RelatedResourceType, resource_type_dict: ResourceTypeDict) -> None:
        """
        填充名称
        """
        self.selection_mode = rrt.selection_mode

        self.name, self.name_en = resource_type_dict.get_name(self.system_id, self.type)

        for c in self.condition:
            for i in c.instances:
                i.fill_type_name(resource_type_dict)

    def fill_resource_node_name(self, resource_info_name_dict: Dict[ResourceNode, str]) -> None:
        """
        填充每个节点资源实例名称
        """
        for c in self.condition:
            for i in c.instances:
                i.fill_node_name(resource_info_name_dict)

    def add_instance(self, instance: Instance) -> bool:
        """
        实例授权, 合并到已有的条件中, 返回是否变更标志
        """
        if self.is_any():
            return False

        for c in self.condition:
            if c.is_attributes_empty():
                return c.add_instance(instance)

        self.condition.append(Condition(id=gen_uuid(), instances=[instance], attributes=[]))
        return True

    def remove_instance(self, instance: Instance) -> bool:
        """
        回收实例权限, 返回是否变更标志
        """
        if self.is_any():
            return False

        is_modified = False
        for c in self.condition:
            if c.is_attributes_empty():
                if c.remove_instance(instance):
                    is_modified = True

        if is_modified:
            self.condition = [c for c in self.condition if not (c.is_attributes_empty() and len(c.instances) == 0)]
            self._is_empty = len(self.condition) == 0
        return is_modified

    def list_resource_node(self) -> List[ResourceNode]:
        """
        通过拆解每个路径里的层级，返回所有拆解出的单一资源实例
        """
        nodes = []
        # 遍历每一组权限配置
        for condition in self.condition:
            nodes.extend(condition.list_resource_node())
        return nodes

    @classmethod
    def from_resource_instance(cls, resource_instance: ResourceInstance):
        condition = [Condition(id=gen_uuid(), instances=resource_instance.instances, attributes=[])]
        # 若实例为空列表，表示无限制
        if len(resource_instance.instances) == 0:
            condition = []

        return cls(
            system_id=resource_instance.system_id,
            type=resource_instance.type,
            condition=condition,
            name=resource_instance.type_name,
            name_en=resource_instance.type_name_en,
        )

    @classmethod
    def from_attributes(cls, system_id: str, _type: str, name: str, name_en: str, attributes: List[Attribute]):
        return cls(
            system_id=system_id,
            type=_type,
            condition=[Condition(id=gen_uuid(), instances=[], attributes=attributes)],
            name=name,
            name_en=name_en,
        )

    def check_selection_ignore_path(self, selections: List[InstanceSelection]):
        """
        校验条件中的实例拓扑是否满足实例视图
        """
        for c in self.condition:
            if c.is_instances_empty():
                continue

            for instance in c.instances:
                instance.check_selection_ignore_path(self, selections)

    def get_system_set(self) -> Set[str]:
        """
        获取所有的system_id
        """
        if self.is_any() or self.is_empty():
            return {self.system_id}
        ids = set.union(*[condition.get_system_set() for condition in self.condition])
        ids.add(self.system_id)
        return ids

    def instances_count(self):
        return sum([c.instances_count(self.type) for c in self.condition])

    def set_instance_path_node_tag_ADD(self):
        for c in self.condition:
            c.set_instance_path_node_tag_ADD()


class Policy(BaseModel):
    id: str
    related_resource_types: List[RelatedResource]
    environment: Optional[Dict] = None
    policy_id: int = 0
    expired_at: Optional[int] = None

    type: Optional[str] = None
    name: str = ""
    name_en: str = ""
    description: str = ""
    description_en: str = ""
    expired_display: Optional[str] = None
    tag: Optional[str] = None

    # 用于新老策略对比差异时，记录是否仅仅只是过期时间不一样
    is_diff_only_expired_at: bool = False

    def __init__(self, **data: Any):
        if "expired_at" in data and (data["expired_at"] is not None) and ("expired_display" not in data):
            data["expired_display"] = expired_at_display(data["expired_at"])
        super().__init__(**data)

    def set_expired_at(self, expired_at: int):
        self.expired_at = expired_at
        self.expired_display = expired_at_display(self.expired_at)

    def set_tag_add(self):
        self.tag = PolicyTag.ADD.value

    def set_tag_update(self):
        self.tag = PolicyTag.UPDATE.value

    def set_tag_unchanged(self):
        self.tag = PolicyTag.UNCHANGED.value

    def set_tag_delete(self):
        self.tag = PolicyTag.DELETE.value

    def to_backend_dict(self):
        translator = ResourceExpressionTranslator()
        return {
            "action_id": self.id,
            "resource_expression": translator.translate([rt.dict() for rt in self.related_resource_types]),
            "environment": "{}",
            "expired_at": self.expired_at,
            "id": self.policy_id,
        }

    @classmethod
    def from_db_model(cls, policy: PolicyModel) -> "Policy":
        return cls(
            id=policy.action_id,
            related_resource_types=policy.resources,
            environment=policy.environment,
            policy_id=policy.policy_id,
            type=policy.action_type,
        )

    def to_db_model(self, system_id: str, subject: Subject) -> PolicyModel:
        p = PolicyModel(
            subject_type=subject.type,
            subject_id=subject.id,
            system_id=system_id,
            action_type=self.type,
            action_id=self.id,
        )
        p.resources = [rt.dict() for rt in self.related_resource_types]
        p.environment = self.environment
        return p

    def is_unrelated(self) -> bool:
        """
        是否是非关联
        """
        return len(self.related_resource_types) == 0

    def merge(self, policy: "Policy", maximize=False):
        """
        合并

        maximize 是否最大化合并, 如果老的policy是任意, 则不合并
        """
        if self.is_unrelated() and policy.is_unrelated():
            return

        rt_dict = {(rt.system_id, rt.type): rt for rt in policy.related_resource_types}
        for rt in self.related_resource_types:
            key = (rt.system_id, rt.type)
            if key in rt_dict:
                rt.merge_conditions(rt_dict[key].condition, maximize)

    def has(self, policy: "Policy") -> bool:
        """
        包含
        """
        if self.is_unrelated() and policy.is_unrelated():
            return True

        rt_dict = {(rt.system_id, rt.type): rt for rt in policy.related_resource_types}
        for rt in self.related_resource_types:
            key = (rt.system_id, rt.type)
            if key in rt_dict:
                if not rt.has_conditions(rt_dict[key].condition):
                    return False
        return True

    def diff(self, policy: "Policy") -> bool:
        """
        求差集

        返回值, 是否完全一致

        处理多个资源类型依赖关系, 如果只有一个资源类型修改了, 那么另外一个资源类型的条件要保持不变

        is_related: 是否是依赖操作, 如果是, 在已有的权限是任意时, 不能变更
        """
        if self.is_unrelated() and policy.is_unrelated():
            is_diff = self.compare_expired_at(policy)
            self.is_diff_only_expired_at = is_diff  # 需要有一个是否变更的标志
            return is_diff

        related_resource_types = deepcopy(self.related_resource_types)
        rt_dict = {(rt.system_id, rt.type): rt for rt in policy.related_resource_types}
        for rt in related_resource_types:
            key = (rt.system_id, rt.type)
            if key in rt_dict:
                # 如果从有限权限变更成任意, 可以确定有变更
                if rt.is_any() and not rt_dict[key].is_any():
                    return False

                rt.remove_conditions(rt_dict[key].condition)

        # 如果所有的资源类型都被删空, 返回True
        is_empty = all([rt.is_empty() for rt in related_resource_types])
        # 如果完全没变, 但是申请的时间变了
        if is_empty and not self.compare_expired_at(policy):
            self.is_diff_only_expired_at = True
            return False

        # 如果有部分资源没有被删空, 返回False, 并对删空的部分补偿回来
        if not is_empty:
            original_rt_dict = {(rt.system_id, rt.type): rt for rt in self.related_resource_types}
            for rt in related_resource_types:
                key = (rt.system_id, rt.type)
                if rt.is_empty():
                    rt.merge_conditions(original_rt_dict[key].condition)

        # 更新
        self.related_resource_types = related_resource_types

        return is_empty

    def compare_expired_at(self, policy: "Policy") -> bool:
        return self.expired_at == policy.expired_at

    def compare(self, policy: "Policy") -> bool:
        """
        对比条件
        """
        if not self._compare_types(policy):
            return False

        rt_dict = {(rt.system_id, rt.type): rt for rt in policy.related_resource_types}
        for rt in self.related_resource_types:
            key = (rt.system_id, rt.type)
            if key in rt_dict:
                if not rt_dict[key].compare(rt):
                    return False
        return True

    def _compare_types(self, policy: "Policy") -> bool:
        """
        比较依赖资源是否一致
        """
        return {(rt.system_id, rt.type) for rt in policy.related_resource_types} == {
            (rt.system_id, rt.type) for rt in self.related_resource_types
        }

    def fill_action_base_info(self, action: Action):
        """填充Action的基本信息"""
        self.name = action.name
        self.name_en = action.name_en
        self.description = action.description
        self.description_en = action.description_en
        self.type = action.type

    def fill_name(self, action: Action, system_resource_types: ResourceTypeDict) -> None:
        """
        填充名称
        """
        self.fill_action_base_info(action)

        for rt in self.related_resource_types:
            action_rrt = action.get_related_resource_type(rt.system_id, rt.type)
            if not action_rrt:
                continue

            rt.fill_type_name(action_rrt, system_resource_types)

    def fill_resource_node_name(self, resource_info_name_dict: Dict[ResourceNode, str]) -> None:
        """
        填充每个节点资源实例的Name
        """
        for rt in self.related_resource_types:
            rt.fill_resource_node_name(resource_info_name_dict)

    def add_resources_instance(self, resources: List[ResourceInstance]) -> bool:
        """
        实例授权, 返回是否变更标志
        """
        is_modified = False

        rt_dict = {(rt.system_id, rt.type): rt for rt in self.related_resource_types}
        for r in resources:
            rt = rt_dict[(r.system_id, r.type)]
            if r.instances:
                for instance in r.instances:
                    # NOTE 这个里的and顺序不能弄反, 一定要先add
                    if rt.add_instance(instance) and (not is_modified):
                        is_modified = True
            else:
                # 若资源实例为空列表，说明授权无限制资源实例
                # 若原有策略为无限制，则不修改，否则修改为无限制
                if not rt.is_any():
                    rt.merge_conditions([], True)
                    is_modified = True

        return is_modified

    def remove_resources_instance(self, resources: List[ResourceInstance]) -> bool:
        """
        回收实例权限, 返回是否便功能标志
        只有关联的资源类型的条件都有变更, 才真正的改变策略
        """
        result = []

        rt_dict = {(rt.system_id, rt.type): rt for rt in self.related_resource_types}
        for r in resources:
            rt = rt_dict[(r.system_id, r.type)]
            is_modified = False
            for instance in r.instances:
                # NOTE 这个里的and顺序不能弄反, 一定要先add
                if rt.remove_instance(instance) and (not is_modified):
                    is_modified = True
            result.append(is_modified)
        return all(result)

    def get_system_set(self) -> Set[str]:
        """
        获取所有的system_id
        """
        if self.is_unrelated():
            return set()
        return set.union(*[rrt.get_system_set() for rrt in self.related_resource_types])

    def set_instance_path_node_tag_ADD(self):
        for rrt in self.related_resource_types:
            rrt.set_instance_path_node_tag_ADD()


def group_paths(paths: List[List[Dict]]) -> List[Instance]:
    """
    对拓扑分组
    """
    instances: List[Instance] = []

    # 对拓扑路径分组, 如果拓扑最后的节点是任意, 则使用倒数第二个节点分组
    def key_func(path: List[Dict]):
        node = path[-1]
        if node["id"] == ANY_ID and len(path) > 1:
            node = path[-2]
        return node["system_id"], node["type"]

    sorted_paths = sorted(paths, key=key_func)
    # 按链路的最后一个资源的类型分组
    for k, group in groupby(sorted_paths, key=key_func):
        instances.append(Instance(type=k[1], path=list(group)))

    return instances
