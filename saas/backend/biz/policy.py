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
import functools
import logging
import time
from collections import defaultdict
from copy import deepcopy
from itertools import chain, groupby
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

from django.conf import settings
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from pydantic.main import BaseModel
from pydantic.tools import parse_obj_as

from backend.common.error_codes import error_codes
from backend.common.lock import gen_policy_alter_lock
from backend.common.time import PERMANENT_SECONDS, expired_at_display, generate_default_expired_at
from backend.service.action import ActionService
from backend.service.constants import ANY_ID, DEFAULT_RESOURCE_GROUP_ID, FETCH_MAX_LIMIT
from backend.service.models import (
    Action,
    BackendThinPolicy,
    Condition,
    Instance,
    InstanceSelection,
    PathNode,
    Policy,
    RelatedResource,
    RelatedResourceType,
    ResourceGroup,
    ResourceGroupList,
    ResourceTypeDict,
    Subject,
    System,
    SystemCounter,
)
from backend.service.models.policy import PathNodeList
from backend.service.policy.operation import PolicyOperationService
from backend.service.policy.query import PolicyQueryService
from backend.service.resource_type import ResourceTypeService
from backend.service.system import SystemService
from backend.service.utils.translate import translate_path
from backend.util.model import ExcludeModel
from backend.util.uuid import gen_uuid

from .resource import ResourceBiz, ResourceNodeBean

logger = logging.getLogger("app")


class PolicyEmptyException(Exception):
    pass


class PathNodeBean(PathNode):
    name: str = ""
    type_name: str = ""
    type_name_en: str = ""

    def fill_empty_fields(self, resource_type_dict: ResourceTypeDict):
        self.type_name, self.type_name_en = resource_type_dict.get_name(self.system_id, self.type)


class PathNodeBeanList(PathNodeList):
    __root__: List[PathNodeBean]

    def to_path_string(self):
        return translate_path(self.dict())

    def display(self) -> str:
        return "/".join(["{}:{}".format(node.type, node.name) for node in self])


class InstanceBean(Instance):
    path: List[PathNodeBeanList]

    name: str = ""
    name_en: str = ""

    def fill_empty_fields(self, resource_type_dict: ResourceTypeDict):
        for node in self.iter_path_node():
            node.fill_empty_fields(resource_type_dict)

            if node.type == self.type:
                self.name, self.name_en = node.type_name, node.type_name_en

    def iter_path_node(self):
        for p in self.path:
            for node in p:
                yield node

    def get_system_id_set(self) -> Set[str]:
        """
        获取所有node相关的system_id集合
        """
        return {node.system_id for node in self.iter_path_node()}

    # For Operation
    def add_paths(self, paths: List[PathNodeBeanList]) -> "InstanceBean":
        """
        合并
        """
        path_set = self._get_path_set()
        for path in paths:
            if path.to_path_string() in path_set:
                continue

            self.path.append(path)

        return self

    def remove_paths(self, paths: List[PathNodeBeanList]) -> "InstanceBean":
        """
        裁剪
        """
        path_set = {path.to_path_string() for path in paths}
        self.path = [path for path in self.path if path.to_path_string() not in path_set]
        return self

    def _get_path_set(self):
        return {path.to_path_string() for path in self.path}

    @property
    def is_empty(self) -> bool:
        return len(self.path) == 0

    def clone_and_filter_by_instance_selections(
        self, resource_system_id: str, resource_type_id: str, selections: List[InstanceSelection]
    ) -> Optional["InstanceBean"]:
        """
        筛选满足实例视图实例, 并clone一个新的instance
        """
        new_paths = []
        for p in self.path:
            for selection in selections:
                if p.match_selection(resource_system_id, resource_type_id, selection):
                    new_paths.append(p)
                    break

        if not new_paths:
            return None

        return InstanceBean(path=new_paths, **self.dict(exclude={"path"}))

    def check_instance_selection(
        self, resource_system_id: str, resource_type_id: str, selections: List[InstanceSelection]
    ):
        """
        检查实例视图
        """
        for p in self.path:
            for selection in selections:
                if p.match_selection(resource_system_id, resource_type_id, selection):
                    break
            else:
                # 所有的实例视图都不匹配
                raise error_codes.VALIDATE_ERROR.format(
                    "{} could not match any instance selection".format(p.display())
                )

    def count(self) -> int:
        """
        实例数量
        """
        return len(self.path)

    def update_resource_name(self, renamed_resources: Dict[PathNodeBean, str]) -> bool:
        is_changed = False
        for p in self.path:
            for node in p:
                new_name = renamed_resources.get(node)
                # 只会更新有重命名的资源
                if new_name is not None and new_name != node.name:
                    node.name = new_name
                    # 记录是否真的修改了数据，便于后续直接修改DB数据
                    is_changed = True
        return is_changed


class InstanceBeanList:
    def __init__(self, instances: List[InstanceBean]) -> None:
        self.instances = instances
        self._instance_dict = {one.type: one for one in instances}

    def get(self, resource_type: str) -> Optional[InstanceBean]:
        return self._instance_dict.get(resource_type, None)

    def add(self, instance_list: "InstanceBeanList") -> "InstanceBeanList":
        for new_instance in instance_list.instances:
            instance = self.get(new_instance.type)
            if not instance:
                self.instances.append(new_instance)
                self._instance_dict[new_instance.type] = new_instance
            else:
                instance.add_paths(new_instance.path)

        return self

    def sub(self, instance_list: "InstanceBeanList") -> "InstanceBeanList":
        for instance in self.instances:
            new_instance = instance_list.get(instance.type)
            if not new_instance:
                continue
            instance.remove_paths(new_instance.path)

        self.instances = [instance for instance in self.instances if not instance.is_empty]
        self._instance_dict = {one.type: one for one in self.instances}
        return self


class ConditionBean(Condition):
    instances: List[InstanceBean]

    def fill_empty_fields(self, resource_type_dict: ResourceTypeDict):
        for instance in self.instances:
            instance.fill_empty_fields(resource_type_dict)

    def get_system_id_set(self) -> Set[str]:
        """
        获取所有node相关的system_id集合
        """
        return set.union(*[instance.get_system_id_set() for instance in self.instances]) if self.instances else set()

    # For Operation
    def add_instances(self, instances: List[InstanceBean]) -> "ConditionBean":
        """
        合并
        """
        self.instances = InstanceBeanList(self.instances).add(InstanceBeanList(instances)).instances
        return self

    def remove_instances(self, instances: List[InstanceBean]) -> "ConditionBean":
        """
        裁剪
        """
        self.instances = InstanceBeanList(self.instances).sub(InstanceBeanList(instances)).instances
        return self

    def count_instance(self, resource_type_id: str) -> int:
        """
        到叶子节点的实例数量, 不包含路径
        """
        return sum([one.count() for one in self.instances if one.type == resource_type_id])


class ConditionBeanList:
    def __init__(self, conditions: List[ConditionBean]) -> None:
        self.conditions = self._merge(conditions)
        self.is_any = len(self.conditions) == 0
        self.is_empty = False

    def _merge(self, conditions: List[ConditionBean]) -> List[ConditionBean]:
        """
        合并属性相同的condition
        """
        if len(conditions) == 0:
            return conditions

        # 筛选出只有属性的条件, 并去重
        empty_instance_conditions = {c.hash_attributes(): c for c in conditions if c.has_no_instances()}

        # 合并属性相同的实例
        condition_dict: Dict[Any, ConditionBean] = {}
        # 排序可以使有id的排在前面
        for c in sorted(conditions, key=lambda c: c.id, reverse=True):
            if c.has_no_instances():
                continue

            _hash = c.hash_attributes()
            if _hash in condition_dict:
                condition_dict[_hash].add_instances(c.instances)
            else:
                condition_dict[_hash] = c

        new_conditions: List[ConditionBean] = []
        new_conditions.extend(chain(condition_dict.values(), empty_instance_conditions.values()))
        return new_conditions

    def add(self, condition_list: "ConditionBeanList") -> "ConditionBeanList":
        """
        合并
        """
        if self.is_any and not self.is_empty:
            return self

        if condition_list.is_any:
            self.conditions = condition_list.conditions
            return self

        # 分为不带实例的条件与带实例的条件
        empty_instance_conditions = {c.hash_attributes(): c for c in self.conditions if c.has_no_instances()}
        condition_dict = {c.hash_attributes(): c for c in self.conditions if not c.has_no_instances()}

        for c in condition_list.conditions:
            # 如果申请的条件都为空, 不需要合并
            if c.has_no_instances() and c.has_no_attributes():
                continue

            _hash = c.hash_attributes()
            # 如果不带实例
            if c.has_no_instances():
                # 如果计算的条件的属性hash值不在字典中, 需要新增
                if _hash not in empty_instance_conditions:
                    empty_instance_conditions[_hash] = deepcopy(c)
            else:
                # 带实例的条件如果hash不在字典中, 需要新增, 在字典中, 合并实例
                if _hash not in condition_dict:
                    condition_dict[_hash] = deepcopy(c)
                else:
                    condition_dict[_hash].add_instances(c.instances)

        conditions: List[ConditionBean] = []
        conditions.extend(chain(condition_dict.values(), empty_instance_conditions.values()))
        self.conditions = conditions

        self.is_empty = len(conditions) == 0

        return self

    def sub(self, condition_list: "ConditionBeanList") -> "ConditionBeanList":
        """
        裁剪
        """
        # 如果新旧条件都是任意, 相当于清空
        if self.is_any and condition_list.is_any:
            self.is_empty = True
            return self

        if self.is_any:
            return self

        empty_instance_conditions = {c.hash_attributes(): c for c in self.conditions if c.has_no_instances()}
        condition_dict = {c.hash_attributes(): c for c in self.conditions if not c.has_no_instances()}

        for c in condition_list.conditions:
            _hash = c.hash_attributes()
            if c.has_no_instances():
                if _hash in empty_instance_conditions:
                    empty_instance_conditions.pop(_hash)
            else:
                if _hash not in condition_dict:
                    continue

                # 移除条件中需要删除的部分实例
                condition_dict[_hash].remove_instances(c.instances)

                # 如果条件的所有实例都删空了, 需要移除整组条件
                if condition_dict[_hash].has_no_instances():
                    condition_dict.pop(_hash)

        conditions: List[ConditionBean] = []
        conditions.extend(chain(condition_dict.values(), empty_instance_conditions.values()))
        self.conditions = conditions

        self.is_empty = len(conditions) == 0  # 如果所有的条件都被删完了, 记录状态

        return self

    def remove_by_ids(self, ids: List[str]):
        """
        移除指定id的condition
        """
        if self.is_any:
            return

        self.conditions = [condition for condition in self.conditions if condition.id not in ids]
        self.is_empty = len(self.conditions) == 0


class RelatedResourceBean(RelatedResource):
    condition: List[ConditionBean]

    name: str = ""
    name_en: str = ""
    selection_mode: str = ""  # 方便前端使用

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        # 合并属性相同的实例
        self.condition = ConditionBeanList(self.condition).conditions

    def fill_empty_fields(self, related_resource_type: RelatedResourceType, resource_type_dict: ResourceTypeDict):
        """
        填充默认为空的fields
        """
        self.selection_mode = related_resource_type.selection_mode
        self.name, self.name_en = resource_type_dict.get_name(self.system_id, self.type)

        for c in self.condition:
            c.fill_empty_fields(resource_type_dict)

    def get_system_id_set(self) -> Set[str]:
        """
        获取所有node相关的system_id集合
        """
        system_id_set = (
            set.union(*[condition.get_system_id_set() for condition in self.condition]) if self.condition else set()
        )
        system_id_set.add(self.system_id)
        return system_id_set

    def check_selection(self, selections: List[InstanceSelection]):
        """
        校验条件中的实例拓扑是否满足实例视图
        """
        for c in self.condition:
            if c.has_no_instances():
                continue

            for instance in c.instances:
                instance.check_instance_selection(self.system_id, self.type, selections)

    def count_instance(self) -> int:
        """
        到叶子节点的实例数量, 不包含路径
        """
        return sum([one.count_instance(self.type) for one in self.condition])

    def clone_and_filter_by_instance_selections(
        self, selections: List[InstanceSelection], ignore_attribute: bool = False
    ) -> Optional["RelatedResourceBean"]:
        """
        筛选出满足实例视图的实例, 并clone新的RelatedResourceBean

        ignore_attribute: 是否忽略带属性的condition, 默认不忽略
        """
        new_conditions: List[ConditionBean] = []
        for c in self.condition:
            if not c.has_no_attributes() and ignore_attribute:
                continue

            if c.has_no_instances():
                new_conditions.append(c)
                continue

            new_instances: List[InstanceBean] = []
            for instance in c.instances:
                new_instance = instance.clone_and_filter_by_instance_selections(self.system_id, self.type, selections)
                if new_instance:
                    new_instances.append(new_instance)

            if new_instances:
                new_conditions.append(ConditionBean(instances=new_instances, **c.dict(exclude={"instances"})))

        if not new_conditions:
            return None

        return RelatedResourceBean(condition=new_conditions, **self.dict(exclude={"condition"}))

    def iter_path_list(self, ignore_attribute: bool = False) -> Iterable[PathNodeBeanList]:
        for condition in self.condition:
            # 忽略有属性的condition
            if ignore_attribute and not condition.has_no_attributes():
                continue

            for instance in condition.instances:
                for path in instance.path:
                    yield path

    def update_resource_name(self, renamed_resources: Dict[PathNodeBean, str]) -> bool:
        is_changed = False
        for condition in self.condition:
            for instance in condition.instances:
                # 重命名，并记录是否真的修改了数据，便于后续直接修改DB数据
                if instance.update_resource_name(renamed_resources):
                    is_changed = True

        return is_changed


class RelatedResourceBeanList:
    def __init__(self, related_resource_types: List[RelatedResourceBean]) -> None:
        self.related_resource_types = related_resource_types
        self.is_empty = False

        self._condition_list_dict = {
            (one.system_id, one.type): ConditionBeanList(one.condition) for one in related_resource_types
        }

    def get_condition_list(self, system_id: str, resource_type_id: str) -> Optional[ConditionBeanList]:
        return self._condition_list_dict.get((system_id, resource_type_id), None)

    def add(self, resource_type_list: "RelatedResourceBeanList") -> "RelatedResourceBeanList":
        for resource_type in self.related_resource_types:
            condition_list = self.get_condition_list(resource_type.system_id, resource_type.type)
            new_condition_list = resource_type_list.get_condition_list(resource_type.system_id, resource_type.type)
            if not condition_list or not new_condition_list:
                continue

            condition_list = condition_list.add(new_condition_list)
            resource_type.condition = condition_list.conditions
            self._condition_list_dict[(resource_type.system_id, resource_type.type)] = condition_list

        return self

    def sub(self, resource_type_list: "RelatedResourceBeanList") -> "RelatedResourceBeanList":
        empty_flags: List[bool] = []  # 记录related resource type 的删空标志
        for resource_type in self.related_resource_types:
            condition_list = deepcopy(self.get_condition_list(resource_type.system_id, resource_type.type))
            new_condition_list = resource_type_list.get_condition_list(resource_type.system_id, resource_type.type)
            if not condition_list or not new_condition_list:
                continue

            condition_list = condition_list.sub(new_condition_list)
            # 如果没有被删空则更新原来的数据, 如果被删空了, 保持原始的数据不变
            # 在有多个关联资源类型的情况下, 只有多个资源类型都删空了, 才会删除整个policy
            # 如果第一个资源类型被删空, 而第二个没有, 则需要, 把第一个的条件保留, 只更新第二个
            if not condition_list.is_empty:
                resource_type.condition = condition_list.conditions
                self._condition_list_dict[(resource_type.system_id, resource_type.type)] = condition_list

            empty_flags.append(condition_list.is_empty)

        self.is_empty = all(empty_flags)  # 多个资源类型情况下, 所有的资源类型都删空了, 才算空

        return self


class ResourceGroupBean(ResourceGroup):
    id: str = ""
    related_resource_types: List[RelatedResourceBean]

    def fill_empty_fields(self, action: Action, resource_type_dict: ResourceTypeDict):
        """
        填充默认为空的fields
        """
        if self.id == "":
            self.id = gen_uuid()

        for related_resource_type in self.related_resource_types:
            action_related_resource_type = action.get_related_resource_type(
                related_resource_type.system_id, related_resource_type.type
            )
            if not action_related_resource_type:
                continue
            related_resource_type.fill_empty_fields(action_related_resource_type, resource_type_dict)

    def get_system_id_set(self) -> Set[str]:
        """
        获取所有node相关的system_id集合
        """
        return (
            set.union(*[one.get_system_id_set() for one in self.related_resource_types])
            if self.related_resource_types
            else set()
        )

    def add_related_resource_types(self, related_resources: List[RelatedResourceBean]) -> "PolicyBean":
        """
        合并
        """
        resource_type_list = RelatedResourceBeanList(self.related_resource_types)
        resource_type_list.add(RelatedResourceBeanList(related_resources))

        self.related_resource_types = resource_type_list.related_resource_types
        return self

    def has_related_resource_types(self, related_resources: List[RelatedResourceBean]) -> bool:
        """
        包含

        新的Policy - 老的Policy = 空, 则老Policy包含新的
        """
        resource_type_list = RelatedResourceBeanList(deepcopy(related_resources))
        resource_type_list.sub(RelatedResourceBeanList(self.related_resource_types))

        return resource_type_list.is_empty

    def remove_related_resource_types(self, related_resources: List[RelatedResourceBean]) -> "PolicyBean":
        """
        裁剪
        """
        resource_type_list = RelatedResourceBeanList(self.related_resource_types)
        resource_type_list.sub(RelatedResourceBeanList(related_resources))

        if resource_type_list.is_empty:
            raise PolicyEmptyException

        self.related_resource_types = resource_type_list.related_resource_types
        return self

    def list_path_node(self) -> List[PathNodeBean]:
        """查询策略包含的资源范围 - 所有路径上的节点，包括叶子节点"""
        nodes = []
        for rrt in self.related_resource_types:
            for path_list in rrt.iter_path_list():
                nodes.extend(list(path_list))
        return nodes

    def count_all_type_instance(self) -> int:
        """
        这里是统计所有实例总数，Action关联多种资源类型是一起计算的
        """
        return sum([rrt.count_instance() for rrt in self.related_resource_types])

    def get_related_resource_type(self, system_id: str, resource_type_id: str) -> Optional[RelatedResourceBean]:
        for rrt in self.related_resource_types:
            if rrt.system_id == system_id and rrt.type == resource_type_id:
                return rrt

        return None

    def set_related_resource_type(self, resource_type: RelatedResourceBean):
        for rrt in self.related_resource_types:
            if rrt.system_id == resource_type.system_id and rrt.type == resource_type.type:
                rrt.condition = resource_type.condition
                break

    def check_instance_selection(self, action: Action):
        for rrt in self.related_resource_types:
            resource_type = action.get_related_resource_type(rrt.system_id, rrt.type)
            if not resource_type:
                continue
            rrt.check_selection(resource_type.instance_selections)

    def update_resource_name(self, renamed_resources: Dict[PathNodeBean, str]) -> bool:
        """
        更新资源实例名称
        """
        is_changed = False
        for rrt in self.related_resource_types:
            # 重命名，并记录是否真的修改了数据，便于后续直接修改DB数据
            if rrt.update_resource_name(renamed_resources):
                is_changed = True

        return is_changed


class ResourceGroupBeanList(ResourceGroupList):
    __root__: List[ResourceGroupBean]

    def __init__(__pydantic_self__, **data: Any) -> None:
        super().__init__(**data)
        __pydantic_self__._drop_duplicates()

    def _drop_duplicates(self):
        """
        去重
        """
        if len(self) <= 1:
            return self

        # 关联单资源类型的操作, 环境属性相同的情况下, 需要合并资源实例
        if len(self.get_thin_resource_types()) == 1:
            env_hash_rg = {}
            self.__root__ = self._merge_resource_groups_with_same_env(env_hash_rg, self)
            return self

        # 如果resource_group存在包含关系, 移除被包含的resource_group
        for __ in range(len(self)):
            rg = self.pop(0)
            if rg not in self:
                self.append(rg)

        return self

    def get_by_id(self, id: str) -> Optional[ResourceGroupBean]:
        index = self._index_by_id(id)
        return self[index] if index != -1 else None

    def is_super_set(self, resource_groups: "ResourceGroupBeanList") -> bool:
        """
        是否完全包含
        """
        for rg in resource_groups:
            if rg not in self:
                return False

        return True

    def is_unrelated(self) -> bool:
        return len(self) == 0

    def __contains__(self, resource_group: ResourceGroupBean) -> bool:
        for rg in self:
            if resource_group.hash_environments() == rg.hash_environments() and rg.has_related_resource_types(
                resource_group.related_resource_types
            ):
                return True

        return False

    def __add__(self, resource_groups: "ResourceGroupBeanList") -> "ResourceGroupBeanList":
        """
        合并到新的对象
        """
        rg = deepcopy(self)
        rg += resource_groups
        return rg

    def _merge_resource_groups_with_same_env(
        self, env_hash_rg: Dict[int, ResourceGroupBean], resource_groups: "ResourceGroupBeanList"
    ) -> List[ResourceGroupBean]:
        """
        合并相同env的resource_group
        """
        for rg in resource_groups:
            env_hash = rg.hash_environments()
            if env_hash in env_hash_rg:
                env_hash_rg[env_hash].add_related_resource_types(rg.related_resource_types)
                continue

            env_hash_rg[env_hash] = rg
        return list(env_hash_rg.values())

    def __iadd__(self, resource_groups: "ResourceGroupBeanList") -> "ResourceGroupBeanList":
        """
        合并到本身

        如果已有id相同的, 则直接合并id相同的
        如果不存在id相同的, 判断范围是否已包含, 没有包含的合并
        """
        # 处理单个资源类型的合并
        if len(self.get_thin_resource_types()) == 1:
            env_hash_rg = {rg.hash_environments(): rg for rg in self}
            self.__root__ = self._merge_resource_groups_with_same_env(env_hash_rg, resource_groups)
            return self

        for rg in resource_groups:
            original_rg = self.get_by_id(rg.id)
            if original_rg is not None and original_rg.hash_environments() == rg.hash_environments():
                original_rg.add_related_resource_types(rg.related_resource_types)
            elif rg not in self:
                self.__root__.append(rg)
        return self

    def __sub__(self, resource_groups: "ResourceGroupBeanList"):
        """
        移除返回新的对象
        """
        rg = deepcopy(self)
        rg -= resource_groups
        return rg

    def __isub__(self, resource_groups: "ResourceGroupBeanList"):
        """
        移除部分条件

        1. 如果是只关联1个资源类型的操作, 直接移除
        2. 如果关联多个资源类型的操作
           - 完整包含的一组才能移除
        """
        # 只关联1个资源类型的操作
        if len(self.get_thin_resource_types()) == 1:
            new_resource_groups: List[ResourceGroupBean] = []
            for original_rg in self:
                try:
                    for rg in resource_groups:
                        if rg.hash_environments() == original_rg.hash_environments():
                            original_rg.remove_related_resource_types(rg.related_resource_types)
                    new_resource_groups.append(original_rg)
                except PolicyEmptyException:
                    pass

            if not new_resource_groups:
                raise PolicyEmptyException

            self.__root__ = new_resource_groups
            return self

        # 关联多个资源类型的操作
        del_resource_group_ids: Set[str] = set()
        for original_rg in self:
            if original_rg in resource_groups:
                del_resource_group_ids.add(original_rg.id)
                continue

        self.__root__ = [rg for rg in self if rg.id not in del_resource_group_ids]
        if not self.__root__:
            raise PolicyEmptyException

        return self

    def fill_empty_fields(self, action: Action, resource_type_dict: ResourceTypeDict):
        for rg in self:
            rg.fill_empty_fields(action, resource_type_dict)

    def get_system_id_set(self) -> Set[str]:
        """
        获取所有node相关的system_id集合
        """
        return set.union(*[one.get_system_id_set() for one in self]) if self.__root__ else set()

    def list_path_node(self) -> List[PathNodeBean]:
        """查询策略包含的资源范围 - 所有路径上的节点，包括叶子节点"""
        nodes = []
        for rg in self:
            nodes.extend(rg.list_path_node())
        return nodes

    def count_all_type_instance(self) -> int:
        """
        这里是统计所有实例总数，Action关联多种资源类型是一起计算的
        """
        return sum([rg.count_all_type_instance() for rg in self])

    def pop_by_id(self, id: str) -> Optional[ResourceGroupBean]:
        index = self._index_by_id(id)
        if index == -1:
            return None

        return self.pop(index)

    def _index_by_id(self, id: str) -> int:
        for i, rg in enumerate(self):
            if rg.id == id:
                return i

        return -1

    def check_instance_selection(self, action: Action):
        """
        检查资源的实例视图是否匹配
        """
        for rg in self:
            rg.check_instance_selection(action)

    def update_resource_name(self, renamed_resources: Dict[PathNodeBean, str]) -> bool:
        """
        更新资源实例名称
        """
        is_changed = False
        for rg in self:
            # 重命名，并记录是否真的修改了数据，便于后续直接修改DB数据
            if rg.update_resource_name(renamed_resources):
                is_changed = True

        return is_changed


class ResourceTypeInstanceCount(BaseModel):
    type: str
    count: int


class PolicyBean(Policy):
    policy_id: int = 0
    expired_at: int = 0
    resource_groups: ResourceGroupBeanList

    type: str = ""
    name: str = ""
    name_en: str = ""
    description: str = ""
    description_en: str = ""
    expired_display: str = ""

    def __init__(self, **data: Any):
        if "expired_at" in data and (data["expired_at"] is not None) and ("expired_display" not in data):
            data["expired_display"] = expired_at_display(data["expired_at"])

        # NOTE 兼容数据传None的情况
        if "expired_at" in data and not isinstance(data["expired_at"], int):
            data.pop("expired_at")
        if "expired_display" in data and not isinstance(data["expired_display"], str):
            data.pop("expired_display")
        if "type" in data and not isinstance(data["type"], str):
            data.pop("type")

        # NOTE 兼容 role, group授权信息的旧版结构
        if "resource_groups" not in data and "related_resource_types" in data:
            if not data["related_resource_types"]:
                data["resource_groups"] = []
            else:
                data["resource_groups"] = [
                    # NOTE: 固定resource_group_id方便删除逻辑
                    {
                        "id": DEFAULT_RESOURCE_GROUP_ID,
                        "related_resource_types": data.pop("related_resource_types"),
                    }
                ]

        super().__init__(**data)

    def dict(self, *args, **kwargs):
        kwargs["by_alias"] = True
        return super().dict(*args, **kwargs)

    def fill_empty_fields(self, action: Action, resource_type_dict: ResourceTypeDict):
        """
        填充默认为空的fields
        """
        empty_fields = ["type", "name", "name_en", "description", "description_en"]
        for field in empty_fields:
            setattr(self, field, getattr(action, field))

        self.resource_groups.fill_empty_fields(action, resource_type_dict)

    def get_system_id_set(self) -> Set[str]:
        """
        获取所有node相关的system_id集合
        """
        return self.resource_groups.get_system_id_set()

    def is_expired(self):
        """是否策略已过期"""
        return self.expired_at < int(time.time())

    def set_expired_at(self, expired_at: int):
        self.expired_at = expired_at
        self.expired_display = expired_at_display(expired_at)

    def add_resource_group_list(self, resource_group_list: ResourceGroupBeanList):
        """
        合并
        """
        self.resource_groups += resource_group_list

    def has_resource_group_list(self, resource_group_list: ResourceGroupBeanList) -> bool:
        """
        包含
        """
        if self.resource_groups.is_unrelated():
            return True

        return self.resource_groups.is_super_set(resource_group_list)

    def remove_resource_group_list(self, resource_group_list: ResourceGroupBeanList) -> "PolicyBean":
        """
        裁剪
        """
        if self.resource_groups.is_unrelated():
            raise PolicyEmptyException

        self.resource_groups -= resource_group_list
        return self

    def list_path_node(self) -> List[PathNodeBean]:
        """查询策略包含的资源范围 - 所有路径上的节点，包括叶子节点"""
        return self.resource_groups.list_path_node()

    def count_all_type_instance(self) -> int:
        """
        这里是统计所有实例总数，Action关联多种资源类型是一起计算的
        """
        return self.resource_groups.count_all_type_instance()

    def get_related_resource_type(
        self, resource_group_id: str, system_id: str, resource_type_id: str
    ) -> Optional[RelatedResourceBean]:
        """
        获取指定resource_group_id下指定的资源类型的条件
        """
        resource_group = self.resource_groups.get_by_id(resource_group_id)
        if resource_group is None:
            return None
        return resource_group.get_related_resource_type(system_id, resource_type_id)

    def check_instance_selection(self, action: Action):
        """
        检查资源的实例视图是否匹配
        """
        self.resource_groups.check_instance_selection(action)

    def list_resource_type_instance_count(self) -> List[ResourceTypeInstanceCount]:
        """
        查询资源类型的实例数量
        """
        if len(self.resource_groups) == 0:
            return [ResourceTypeInstanceCount(type="", count=0)]

        counts = []
        for i, resource_type in enumerate(self.list_thin_resource_type()):
            c = ResourceTypeInstanceCount(type=resource_type.type, count=0)

            for rg in self.resource_groups:
                c.count += rg.related_resource_types[i].count_instance()
            counts.append(c)

        return counts

    def update_resource_name(self, renamed_resources: Dict[PathNodeBean, str]) -> bool:
        """
        更新资源实例名称
        """
        return self.resource_groups.update_resource_name(renamed_resources)


class PolicyBeanListMixin:
    action_svc = ActionService()
    resource_type_svc = ResourceTypeService()
    resource_biz = ResourceBiz()

    def __init__(
        self,
        system_id: str,
        policies: List[PolicyBean],
    ) -> None:
        self.system_id = system_id
        self.policies = policies

    def get_system_id_set(self) -> Set[str]:
        """
        获取所有node相关的system_id集合
        """
        return set.union(*[one.get_system_id_set() for one in self.policies]) if self.policies else set()

    def fill_empty_fields(self):
        """
        填充PolicyBean中默认为空的字段
        """
        system_id_set = self.get_system_id_set()
        resource_type_dict = self.resource_type_svc.get_system_resource_type_dict(list(system_id_set))
        action_list = self.action_svc.new_action_list(self.system_id)

        for policy in self.policies:
            action = action_list.get(policy.action_id)
            if not action:
                continue
            policy.fill_empty_fields(action, resource_type_dict)

    def check_instance_selection(self):
        """
        检查实例视图
        如果视图需要忽略路径, 则修改路径
        """
        action_list = self.action_svc.new_action_list(self.system_id)
        for p in self.policies:
            action = action_list.get(p.action_id)
            if not action:
                continue

            p.check_instance_selection(action)

    def _list_path_node(self, is_ignore_big_policy=False) -> List[PathNodeBean]:
        """
        查询策略包含的资源范围 - 所有路径上的节点，包括叶子节点
        is_ignore_big_policy: 是否忽略大的策略，大策略是指策略里的实例数量大于1000，
          主要是用于自动更新策略里的资源实例名称时避免大数量的请求接入系统（1000是权限中心的回调接口协议里规定的）
        """
        nodes = []
        for p in self.policies:
            # 这里是定制逻辑：基于fetch_instance_info限制，避免出现大策略
            if is_ignore_big_policy and p.count_all_type_instance() > FETCH_MAX_LIMIT:
                continue
            nodes.extend(p.list_path_node())
        return nodes

    def check_resource_name(self):
        """
        校验策略里包含资源实例名称与ID是否匹配，主要用于防止前端提交数据的错误
        特别注意：该函数只能用于校验新增的策略，不能校验老策略，因为老的资源实例可能被删除或重命名了
        """
        # 获取策略里的资源的所有节点
        path_nodes = self._list_path_node()
        # 查询资源实例的实际名称
        resource_name_dict = self.resource_biz.fetch_resource_name(parse_obj_as(List[ResourceNodeBean], path_nodes))

        # 校验从接入系统查询的资源实例名称与提交的数据里的名称是否一致
        for node in path_nodes:
            real_name = resource_name_dict.get_attribute(ResourceNodeBean.parse_obj(node))
            # 任意需要特殊判断：只要包含无限制即可
            if node.id == ANY_ID and real_name.lower() in node.name.lower():
                continue

            # NOTE: 如果查不到, 跳过, 避免报错
            if not real_name:
                continue

            # 接入系统查询不到 或者 名称不一致则需要报错提示
            if real_name != node.name:
                raise error_codes.INVALID_ARGS.format(
                    "resource(system_id:{}, type:{}, id:{}, name:{}, real_name: {}) name not match".format(
                        node.system_id, node.type, node.id, node.name, real_name
                    )
                )

    def check_instance_count_limit(self):
        """
        检查策略里的实例数量，避免大规模实例超限
        """
        for p in self.policies:
            for c in p.list_resource_type_instance_count():
                if c.count > settings.SINGLE_POLICY_MAX_INSTANCES_LIMIT:
                    raise error_codes.VALIDATE_ERROR.format(
                        "操作 [{}] 关联的资源类型 [{}] 实例数已达上限{}个，请改用范围或者属性授权。".format(
                            p.action_id, c.type, settings.SINGLE_POLICY_MAX_INSTANCES_LIMIT
                        )
                    )

    def get_renamed_resources(self) -> Dict[PathNodeBean, str]:
        """查询已经被重命名的资源实例"""
        # 获取策略里的资源的所有节点，防御性措施：忽略大策略，避免给接入系统请求压力
        path_nodes = self._list_path_node(is_ignore_big_policy=True)
        # 查询资源实例的实际名称
        resource_name_dict = self.resource_biz.fetch_resource_name(parse_obj_as(List[ResourceNodeBean], path_nodes))

        # 查询出已经名称已变更的资源
        renamed_resources: Dict[PathNodeBean, str] = {}
        for node in path_nodes:
            real_name = resource_name_dict.get_attribute(ResourceNodeBean.parse_obj(node))
            # 任意则无需更新
            if node.id == ANY_ID:
                continue

            # 如果real_name 查询不到，则忽略，Note: 不可删除策略里的资源
            if not real_name:
                continue

            # 名称不一致，说明资源重命名了，需要更新
            if real_name != node.name:
                renamed_resources[node] = real_name

        return renamed_resources

    def auto_update_resource_name(self) -> List[PolicyBean]:
        """
        策略里存储的资源名称可能已经变了，需要进行更新
        Note: 该函数仅用于需要对外展示策略数据时调用，不会自动更新DB里数据
        """
        # 由于自动更新并非核心功能，若接入系统查询有问题，也需要正常显示
        try:
            # 获取策略里被重命名的资源实例
            renamed_resources = self.get_renamed_resources()
        except Exception:  # pylint: disable=broad-except
            logger.exception("biz policy auto_update_resource_name: get_renamed_resources fail")
            return []

        # 没有任何被重命名的资源实例，则无需更新策略
        if len(renamed_resources) == 0:
            return []

        # 修改即将对外展示数据
        changed_policies = []
        for p in self.policies:
            is_changed = p.update_resource_name(renamed_resources)
            # 若策略里有资源实例重名了，则记录起来，用于后续修改DB数据
            if is_changed:
                changed_policies.append(p)

        return changed_policies


class PolicyBeanList(PolicyBeanListMixin):
    def __init__(
        self,
        system_id: str,
        policies: List[PolicyBean],
        need_fill_empty_fields: bool = False,
        need_check_instance_selection: bool = False,
    ) -> None:
        """
        system_id: policies的系统id
        policies: 策略列表
        need_fill_empty_fields: 是否需要填充空白字段, 默认否
        need_check_instance_selection: 是否需要检查实例视图, 默认否
        """
        self.system_id = system_id
        self.policies = policies

        self._policy_dict = {policy.action_id: policy for policy in policies}

        if need_fill_empty_fields:
            self.fill_empty_fields()

        if need_check_instance_selection:
            self.check_instance_selection()

    def get(self, action_id: str) -> Optional[PolicyBean]:
        return self._policy_dict.get(action_id, None)

    @staticmethod
    def _generate_expired_at(expired_at: int) -> int:
        """生成一个新策略的默认过期时间"""
        # 如果传入设置的过期时间, 大于当前时间，且小于或等于永久，则使用它
        if time.time() < expired_at <= PERMANENT_SECONDS:
            return expired_at

        return generate_default_expired_at()

    # For Operation
    def split_to_creation_and_update_for_grant(
        self, new_policy_list: "PolicyBeanList"
    ) -> Tuple["PolicyBeanList", "PolicyBeanList"]:
        """
        授权时, 分离需要新增与更新的策略

        self: 原来已有的policy list
        new_policy_list: 新增授权的policy list
        """
        create_policies, update_policies = [], []
        for p in new_policy_list.policies:
            # 已有的权限不存在, 则创建
            old_policy = self.get(p.action_id)
            if not old_policy:
                # 对于新策略，需要校验策略的过期时间是否合理，不合理则生成一个默认的过期时间
                p.set_expired_at(self._generate_expired_at(p.expired_at))
                create_policies.append(p)
                continue

            # 已有的权限包含新的权限
            if old_policy.has_resource_group_list(p.resource_groups):
                # 只有过期时间变更, 也需要更新
                if p.expired_at > old_policy.expired_at:
                    old_policy.set_expired_at(p.expired_at)
                    update_policies.append(old_policy)
                continue

            # 已有的权限合并新的权限并更新
            old_policy.add_resource_group_list(p.resource_groups)
            if p.expired_at > old_policy.expired_at:
                old_policy.set_expired_at(p.expired_at)
            update_policies.append(old_policy)

        return PolicyBeanList(self.system_id, create_policies), PolicyBeanList(self.system_id, update_policies)

    def split_to_update_and_delete_for_revoke(
        self, delete_policy_list: "PolicyBeanList"
    ) -> Tuple["PolicyBeanList", "PolicyBeanList"]:
        """
        回收权限时, 分离出需要更新的策略与删除的策略

        self: 原来已有的policy list
        delete_policy_list: 需要回收的policy list
        """
        update_policies, delete_policies = [], []
        for p in self.policies:
            delete_policy = delete_policy_list.get(p.action_id)
            if not delete_policy:
                continue

            if p.resource_groups.is_unrelated():
                delete_policies.append(p)
                continue

            try:
                update_policies.append(p.remove_resource_group_list(delete_policy.resource_groups))
            except PolicyEmptyException:
                delete_policies.append(p)

        return PolicyBeanList(self.system_id, update_policies), PolicyBeanList(self.system_id, delete_policies)

    def add(self, policy_list: "PolicyBeanList") -> "PolicyBeanList":
        """
        合并权限
        """
        for p in policy_list.policies:
            old_policy = self.get(p.action_id)
            if not old_policy:
                self.policies.append(p)
                self._policy_dict[p.action_id] = p
                continue

            old_policy.add_resource_group_list(p.resource_groups)

        return self

    def sub(self, policy_list: "PolicyBeanList") -> "PolicyBeanList":
        """
        裁剪
        筛选出差集
        """
        subtraction = []
        for p in self.policies:
            old_policy = policy_list.get(p.action_id)
            if not old_policy:
                subtraction.append(p)
                continue

            try:
                subtraction.append(deepcopy(p).remove_resource_group_list(old_policy.resource_groups))
            except PolicyEmptyException:
                pass
        return PolicyBeanList(self.system_id, subtraction)

    def to_svc_policies(self):
        return parse_obj_as(List[Policy], self.policies)


class TemporaryPolicyBeanList(PolicyBeanListMixin):
    def __init__(
        self,
        system_id: str,
        policies: List[PolicyBean],
        need_fill_empty_fields: bool = False,
    ) -> None:
        self.system_id = system_id
        self.policies = policies

        if need_fill_empty_fields:
            self.fill_empty_fields()


class SystemCounterBean(SystemCounter):
    name: str = ""
    name_en: str = ""

    def fill_empty_fields(self, system: System):
        self.name, self.name_en = system.name, system.name_en


class ThinSystem(System, ExcludeModel):
    __exclude__ = ["description", "description_en"]


class ThinAction(Action, ExcludeModel):
    __exclude__ = ["description", "description_en", "type", "related_resource_types", "related_actions"]


class ExpiredPolicy(BackendThinPolicy, ExcludeModel):
    __exclude__ = ["action_id"]

    system: ThinSystem
    action: ThinAction
    expired_display: str
    policy: Optional[PolicyBean] = None

    def __init__(self, **data: Any):
        if "expired_at" in data and (data["expired_at"] is not None) and ("expired_display" not in data):
            data["expired_display"] = expired_at_display(data["expired_at"])
        super().__init__(**data)


class PolicyQueryBiz:
    system_svc = SystemService()
    action_svc = ActionService()
    resource_type_svc = ResourceTypeService()

    svc = PolicyQueryService()

    def list_by_subject(
        self, system_id: str, subject: Subject, action_ids: Optional[List[str]] = None
    ) -> List[PolicyBean]:
        """
        查询subject指定系统的策略
        """
        policy_list = self.new_policy_list(system_id, subject, action_ids)
        return policy_list.policies

    def list_temporary_by_subject(self, system_id: str, subject: Subject) -> List[PolicyBean]:
        """查询subject指定系统的临时权限策略"""
        policies = self.svc.list_temporary_by_subject(system_id, subject)
        pl = TemporaryPolicyBeanList(system_id, parse_obj_as(List[PolicyBean], policies), need_fill_empty_fields=True)
        return pl.policies

    def new_policy_list(
        self, system_id: str, subject: Subject, action_ids: Optional[List[str]] = None
    ) -> PolicyBeanList:
        policies = self.svc.list_by_subject(system_id, subject, action_ids)
        policy_list = PolicyBeanList(system_id, parse_obj_as(List[PolicyBean], policies), need_fill_empty_fields=True)
        return policy_list

    def query_policy_list_by_policy_ids(
        self, system_id: str, subject: Subject, policy_ids: List[int]
    ) -> PolicyBeanList:
        """
        通过policy_ids查询policy list
        """
        policies = self.svc.list_by_policy_ids(system_id, subject, policy_ids)
        policy_list = PolicyBeanList(system_id, parse_obj_as(List[PolicyBean], policies), need_fill_empty_fields=True)
        return policy_list

    def list_temporary_by_policy_ids(
        self, system_id: str, subject: Subject, policy_ids: List[int]
    ) -> List[PolicyBean]:
        """
        通过policy_ids查询临时权限
        """
        policies = self.svc.list_temporary_by_policy_ids(system_id, subject, policy_ids)
        pl = TemporaryPolicyBeanList(system_id, parse_obj_as(List[PolicyBean], policies), need_fill_empty_fields=True)
        return pl.policies

    def list_system_counter_by_subject(self, subject: Subject, hidden: bool = True) -> List[SystemCounterBean]:
        """
        查询subject有权限的系统-policy数量信息
        """
        system_counts = self.svc.list_system_counter_by_subject(subject, hidden)
        return self._system_counter_to_system_counter_bean(system_counts)

    def _system_counter_to_system_counter_bean(self, system_counts: List[SystemCounter]) -> List[SystemCounterBean]:
        system_list = self.system_svc.new_system_list()
        system_count_beans = parse_obj_as(List[SystemCounterBean], system_counts)

        for scb in system_count_beans:
            system = system_list.get(scb.id)
            if not system:
                continue
            scb.fill_empty_fields(system)

        return system_count_beans

    def list_temporary_system_counter_by_subject(self, subject: Subject) -> List[SystemCounterBean]:
        """
        查询subject有权限的系统-临时policy数量信息
        """
        system_counts = self.svc.list_temporary_system_counter_by_subject(subject)
        return self._system_counter_to_system_counter_bean(system_counts)

    def get_policy_resource_type_conditions(
        self, subject: Subject, policy_id: int, resource_group_id: str, resource_system: str, resource_type: str
    ):
        """
        查询指定Policy的资源类型的condition
        """
        policy = self.get_policy_by_id(subject, policy_id)
        related_resource_type = policy.get_related_resource_type(resource_group_id, resource_system, resource_type)
        if not related_resource_type:
            return []
        return related_resource_type.condition

    def list_expired(self, subject: Subject, expired_at: int) -> List[ExpiredPolicy]:
        """
        查询以过期的权限列表
        """
        backend_policies = self.svc.list_backend_policy_before_expired_at(expired_at, subject)

        # 查询system, action的信息
        system_id_set = {one.system for one in backend_policies}
        action_list_dict = {system_id: self.action_svc.new_action_list(system_id) for system_id in system_id_set}
        system_list = self.system_svc.new_system_list()

        # 查询saas policy id
        all_action_id = {p.action_id for p in backend_policies}
        action_id_dict = self.svc.get_action_id_dict(subject, all_action_id)

        # 取策略详情
        system_ids = defaultdict(list)
        for k, v in action_id_dict.items():
            system_ids[k[0]].append(v)

        system_policy_list = {}
        for system_id, ids in system_ids.items():
            policy_list = self.query_policy_list_by_policy_ids(system_id, subject, ids)
            system_policy_list[system_id] = policy_list

        # 填充action, system
        expired_policies = []
        for p in backend_policies:
            action = (
                action_list_dict[p.system].get(p.action_id) if p.system in action_list_dict else None
            ) or ThinAction(id="", name="", name_en="")
            system = system_list.get(p.system) or ThinSystem(id="", name="", name_en="")

            id = action_id_dict.get((p.system, p.action_id), 0)
            if not id:
                continue

            policy = system_policy_list.get(p.system, {p.action_id: None}).get(p.action_id)

            expired_policies.append(
                ExpiredPolicy(
                    id=id,
                    system=system.dict(),
                    action=action.dict(),
                    policy=policy,
                    **p.dict(exclude={"id", "system"}),
                )
            )

        return expired_policies

    def get_policy_by_id(self, subject: Subject, policy_id: int) -> PolicyBean:
        """
        获取指定的Policy
        """
        system_id, policy = self.svc.get_policy_by_id(policy_id, subject)
        policy_list = PolicyBeanList(system_id, [PolicyBean.parse_obj(policy)], need_fill_empty_fields=True)
        return policy_list.policies[0]

    def get_policy_system_by_id(self, subject: Subject, policy_id: int) -> str:
        """
        获取指定策略的system
        """
        return self.svc.get_policy_system_by_id(policy_id, subject)


def custom_policy_change_lock(func):
    """装饰器：策略变更的分布式全局锁，避免并发导致数据错误
    Note: 若被添加于类的方法上，需要使用method_decorator，主要是为了不关注类的self/cls参数
    from django.utils.decorators import method_decorator
    method_decorator(policy_change_lock)
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Note: 必须保证被装饰的函数有参数system_id和subject
        system_id = kwargs["system_id"] if "system_id" in kwargs else args[0]
        subject = kwargs["subject"] if "subject" in kwargs else args[1]

        # 加 template_id + system + subject 锁
        template_id = 0  # 自定义权限，TemplateID默认为0
        with gen_policy_alter_lock(template_id, system_id, subject.type, subject.id):
            return func(*args, **kwargs)

    return wrapper


class PolicyOperationBiz:
    query_biz = PolicyQueryBiz()

    svc = PolicyOperationService()
    action_svc = ActionService()

    @method_decorator(custom_policy_change_lock)
    def delete_by_ids(self, system_id: str, subject: Subject, policy_ids: List[int]):
        """
        删除policies
        """
        self.svc.delete_by_ids(system_id, subject, policy_ids)

    def delete_temporary_policies_by_ids(self, system_id: str, subject: Subject, policy_ids: List[int]):
        """
        删除临时权限
        """
        self.svc.delete_temporary_policies_by_ids(system_id, subject, policy_ids)

    @method_decorator(custom_policy_change_lock)
    def delete_by_resource_group_id(
        self, system_id: str, subject: Subject, policy_id: int, resource_group_id: str
    ) -> PolicyBean:
        """
        删除policy中指定resource_group_id的部分
        """
        policy = self.query_biz.get_policy_by_id(subject, policy_id)
        # 任意的policy不能删除
        if len(policy.resource_groups) == 0:
            raise error_codes.INVALID_ARGS.format(_("资源组不存在"))

        # resource_group不存在不能删除
        resource_group = policy.resource_groups.pop_by_id(resource_group_id)
        if resource_group is None:
            raise error_codes.INVALID_ARGS.format(_("资源组不存在"))

        # 删空的情况直接整体删除
        if len(policy.resource_groups) == 0:
            self.svc.delete_by_ids(system_id, subject, [policy_id])
        else:
            self.svc.alter(system_id, subject, update_policies=[Policy.parse_obj(policy)])

        return policy

    @method_decorator(custom_policy_change_lock)
    def delete_partial(
        self,
        system_id: str,
        subject: Subject,
        policy_id: int,
        resource_group_id: str,
        resource_system_id: str,
        resource_type_id: str,
        condition_ids: List[str],
        conditions: List[ConditionBean],
    ) -> PolicyBean:
        """
        Policy条件部分删除
        返回更新后的Policy
        """
        policy = self.query_biz.get_policy_by_id(subject, policy_id)
        resource_type = policy.get_related_resource_type(resource_group_id, resource_system_id, resource_type_id)
        if not resource_type:
            raise error_codes.VALIDATE_ERROR.format(_("{}: {} 资源类型不存在").format(resource_system_id, resource_type_id))

        condition_list = ConditionBeanList(resource_type.condition)
        # 删除condition id对应的condition
        condition_list.remove_by_ids(condition_ids)
        # 删除条件
        condition_list.sub(ConditionBeanList(conditions))

        if condition_list.is_empty:
            raise error_codes.INVALID_ARGS.format(_("批量删除实例不能清空所有条件"))

        # 更新修改后的条件
        resource_type.condition = condition_list.conditions
        resource_group = policy.resource_groups.pop_by_id(resource_group_id)
        resource_group.set_related_resource_type(resource_type)  # type: ignore

        # 如果policy中其它的resource_group能包含删减后的resource_group, 则整体删除
        policy.add_resource_group_list(ResourceGroupBeanList.parse_obj([resource_group]))

        self.svc.alter(system_id, subject, update_policies=[Policy.parse_obj(policy)])

        return policy

    @method_decorator(custom_policy_change_lock)
    def update(self, system_id: str, subject: Subject, policies: List[PolicyBean]) -> List[PolicyBean]:
        """
        更新subject的权限策略

        覆盖更新, 返回更新后的策略
        """
        old_policy_list = self.query_biz.new_policy_list(system_id, subject, [p.action_id for p in policies])
        update_policy_list = PolicyBeanList(system_id, policies, need_fill_empty_fields=True)
        for policy in update_policy_list.policies:
            old_policy = old_policy_list.get(policy.action_id)
            if not old_policy:
                raise error_codes.VALIDATE_ERROR.format(_("用户组没有{}操作的权限").format(policy.action_id))
            policy.expired_at = old_policy.expired_at
            policy.policy_id = old_policy.policy_id

        # 检查策略里的实例数量，避免大规模实例超限
        update_policy_list.check_instance_count_limit()

        self.svc.alter(
            system_id,
            subject,
            update_policies=update_policy_list.to_svc_policies(),
            action_list=self.action_svc.new_action_list(system_id),
        )

        return update_policy_list.policies

    @method_decorator(custom_policy_change_lock)
    def alter(self, system_id: str, subject: Subject, policies: List[PolicyBean]):
        """
        变更subject权限策略
        """
        old_policy_list = self.query_biz.new_policy_list(system_id, subject, [p.action_id for p in policies])
        new_policy_list = PolicyBeanList(system_id, policies)

        create_policy_list, update_policy_list = old_policy_list.split_to_creation_and_update_for_grant(
            new_policy_list
        )

        # 检查策略里的实例数量，避免大规模实例超限
        create_policy_list.check_instance_count_limit()
        update_policy_list.check_instance_count_limit()

        self.svc.alter(
            system_id,
            subject,
            create_policies=create_policy_list.to_svc_policies(),
            update_policies=update_policy_list.to_svc_policies(),
            action_list=self.action_svc.new_action_list(system_id),
        )

    @method_decorator(custom_policy_change_lock)
    def revoke(self, system_id: str, subject: Subject, delete_policies: List[PolicyBean]) -> List[PolicyBean]:
        """
        删除策略，这里diff可能进行部分删除，若完全一样，则整条策略删除
        返回受影响的策略
        """
        old_policy_list = self.query_biz.new_policy_list(system_id, subject, [p.action_id for p in delete_policies])
        deleted_policy_list = PolicyBeanList(system_id, delete_policies)

        # 获取需要更新和整条删除的策略
        update_policy_list, whole_delete_policy_list = old_policy_list.split_to_update_and_delete_for_revoke(
            deleted_policy_list
        )
        # 变更策略
        self.svc.alter(
            system_id=system_id,
            subject=subject,
            create_policies=[],
            update_policies=update_policy_list.to_svc_policies(),
            delete_policy_ids=[p.policy_id for p in whole_delete_policy_list.policies],
        )

        return update_policy_list.policies + whole_delete_policy_list.policies

    @method_decorator(custom_policy_change_lock)
    def update_due_to_renamed_resource(
        self, system_id: str, subject: Subject, policies: List[PolicyBean]
    ) -> List[PolicyBean]:
        """
        更新策略，这里只是更新策略里的资源实例名称，并不会影响策略本身鉴权相关的
        返回的是所有策略，包括未被更新的
        """
        policy_list = PolicyBeanList(system_id, parse_obj_as(List[PolicyBean], policies))
        updated_policies = policy_list.auto_update_resource_name()
        if len(updated_policies) > 0:
            # 只需要修改DB，且只修改有更新的策略
            self.svc.only_update_db_policies(system_id, subject, updated_policies)

        # 返回的是所有策略，包括未被更新的
        return policy_list.policies

    def create_temporary_policies(self, system_id: str, subject: Subject, policies: List[PolicyBean]):
        """
        创建临时权限
        """
        self.svc.create_temporary_policies(
            system_id,
            subject,
            policies=parse_obj_as(List[Policy], policies),
            action_list=self.action_svc.new_action_list(system_id),
        )


def group_paths(paths: List[List[Dict]]) -> List[InstanceBean]:
    """
    对拓扑分组
    """
    instances: List[InstanceBean] = []

    # 对拓扑路径分组, 如果拓扑最后的节点是任意, 则使用倒数第二个节点分组
    def key_func(path: List[Dict]):
        node = path[-1]
        if node["id"] == ANY_ID and len(path) > 1:
            node = path[-2]
        return node["system_id"], node["type"]

    sorted_paths = sorted(paths, key=key_func)
    # 按链路的最后一个资源的类型分组
    for k, group in groupby(sorted_paths, key=key_func):
        instances.append(InstanceBean(type=k[1], path=list(group)))

    return instances
