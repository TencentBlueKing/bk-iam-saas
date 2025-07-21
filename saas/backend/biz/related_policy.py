# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云 - 权限中心 (BlueKing-IAM) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from copy import deepcopy
from typing import List, Optional

from backend.biz.policy import (
    ConditionBean,
    PathNodeBean,
    PathNodeBeanList,
    PolicyBean,
    RelatedResourceBean,
    ResourceGroupBean,
    group_paths,
)
from backend.service.action import ActionList, ActionService
from backend.service.constants import SelectionMode
from backend.service.models import Action, InstanceSelection, RelatedResourceType
from backend.service.models.instance_selection import PathResourceType
from backend.util.uuid import gen_uuid


class RelatedPolicyBiz:
    """
    依赖操作
    """

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.action_svc = ActionService(self.tenant_id)

    def create_related_policies(self, system_id: str, policy: PolicyBean) -> List[PolicyBean]:
        """
        创建权限的依赖权限
        """
        action_list = self.action_svc.new_action_list(system_id)
        action = action_list.get(policy.action_id)
        if not action or not action.related_actions:
            return []

        # 遍历操作依赖的操作，生成依赖操作权限
        related_policies: List[PolicyBean] = []
        for _id in action.related_actions:
            related_action = action_list.get(_id)
            if not related_action:
                continue

            related_policy = self._create_related_policy(policy, related_action)
            if related_policy:
                related_policies.append(related_policy)

        for p in related_policies:
            p.set_expired_at(policy.expired_at)

        return related_policies

    def _create_related_policy(  # noqa: C901, PLR0912
        self, policy: PolicyBean, action: Action, exclude_diff_type_action: bool = False
    ) -> Optional[PolicyBean]:
        """
        创建单个依赖操作的权限

        exclude_diff_type_action: 是否排除资源类型不同的操作

        1. 不支持关联多个资源类型的依赖操作
        2. 依赖操作不关联资源类型，直接创建权限
        3. 申请操作不关联资源类型，依赖操作关联资源类型，不支持
        4. 申请操作与依赖操作存在相同类型的关联资源类型
            1. 申请的操作是任意，创建任意的依赖操作权限
            2. 申请的操作不是任意，使用类型相同规则匹配依赖操作的实例视图，创建出筛选出来的权限
        5. 申请操作与依赖操作不存在相同的关联资源类型
            使用非相同类型的实例视图匹配规则，创建出筛选出来的权限
        """

        # 依赖操作关联的资源类型不能有多个
        if len(action.related_resource_types) > 1:
            return None

        # 依赖操作未关联资源类型，直接创建
        if len(action.related_resource_types) == 0:
            return PolicyBean(action_id=action.id, related_resource_types=[], expired_at=policy.expired_at)

        # 申请的操作不关联资源类型，依赖操作关联了资源类型，不产生依赖操作权限
        if len(policy.resource_groups) == 0:
            return None

        # 申请操作关联的资源类型与依赖操作关联的资源类型相同
        action_rrt = action.related_resource_types[0]

        new_rrt_list = []  # 遍历所有的 resource_group 后生成的用于创建关联操作 policy 的

        for rg in policy.resource_groups:
            # NOTE 有环境属性的资源组不能生成依赖操作
            if len(rg.environments) != 0:
                continue

            if self._has_same_type(policy, action_rrt):
                # 如果有相同的资源类型
                for rrt in rg.related_resource_types:
                    if rrt.type != action_rrt.id or rrt.system_id != action_rrt.system_id:
                        continue

                    # 如果申请操作时任意，创建任意的依赖操作
                    if len(rrt.condition) == 0:
                        new_rrt_list.append(deepcopy(rrt))
                        continue

                    new_rrt = self._filter_condition_of_same_type(rrt, action_rrt)
                    if new_rrt:
                        new_rrt_list.append(new_rrt)
            elif not exclude_diff_type_action:
                new_rrt = self._filter_condition_of_different_type(rg.related_resource_types, action_rrt)
                if new_rrt:
                    new_rrt_list.append(new_rrt)

        if not new_rrt_list:
            return None

        rg = ResourceGroupBean(id=gen_uuid(), related_resource_types=[new_rrt_list[0]])
        for new_rrt in new_rrt_list[1:]:
            rg.add_related_resource_types([new_rrt])

        return PolicyBean(
            action_id=action.id,
            resource_groups=[rg],
            expired_at=policy.expired_at,
        )

    def _has_same_type(self, policy: PolicyBean, action_rrt: RelatedResourceType) -> bool:
        for rt in policy.list_thin_resource_type():
            if rt.system_id == action_rrt.system_id and rt.type == action_rrt.id:
                return True

        return False

    def _filter_condition_of_different_type(
        self, policy_rrts: List[RelatedResourceBean], action_rrt: RelatedResourceType
    ) -> Optional[RelatedResourceBean]:
        """
        不同资源类型，条件筛选

        1. 不支持属性选择
        2. 只支持不带属性的条件 (只有拓扑)
        3. 使用操作类型的实例视图前缀匹配拓扑链路
        4. 如果申请操作关联多个资源类型
            取多个资源类型筛选出来的条件中的并集，即多个资源类型筛选的拓扑需要同时满足依赖操作的实例视图
        """
        # 如果操作的类型选择是 attribute, 不同的资源类型，不支持
        if action_rrt.selection_mode == SelectionMode.ATTRIBUTE.value:
            return None

        rrt_conditions: List[List[ConditionBean]] = []
        for policy_rrt in policy_rrts:
            conditions: List[ConditionBean] = []

            # 筛选出只有实例的条件
            for c in policy_rrt.condition:
                if c.has_no_attributes():
                    conditions.append(deepcopy(c))

            if not conditions:
                return None

            # 使用操作的实例视图筛选合格条件
            conditions = self._filter_condition_of_different_type_by_instance_selection(
                conditions, action_rrt.instance_selections
            )

            if not conditions:
                return None

            rrt_conditions.append(conditions)

        if len(rrt_conditions) == 0:
            return None

        # policy 只关联了一个资源类型
        if len(rrt_conditions) == 1:
            return RelatedResourceBean(system_id=action_rrt.system_id, type=action_rrt.id, condition=rrt_conditions[0])

        # policy 关联了多个资源类型，需要取多个资源类型条件的交集
        conditions = self._merge_multi_conditions(rrt_conditions)
        if conditions:
            return RelatedResourceBean(system_id=action_rrt.system_id, type=action_rrt.id, condition=conditions)

        return None

    def _filter_condition_of_different_type_by_instance_selection(
        self, conditions: List[ConditionBean], instance_selections: List[InstanceSelection]
    ) -> List[ConditionBean]:
        """
        资源类型不相同，筛选依赖操作的条件

        条件中只有实例的条件
        """
        if not instance_selections:
            return []

        checked_path: List[List[PathNodeBean]] = []  # 筛选过的拓扑
        path_set = set()  # 用于去重

        # 对实例视图排序，长的放前面
        sorted_selections = sorted(instance_selections, key=lambda i: len(i.resource_type_chain), reverse=True)
        for c in conditions:
            for i in c.instances:
                # 遍历所有拓扑链路，检查是否满足实例视图
                for p in i.path:
                    new_path = self._check_path_by_instance_selection(p, sorted_selections)
                    if not new_path:
                        continue

                    tp = self._translate_path(new_path)
                    if tp in path_set:  # 判断是否重复
                        continue

                    checked_path.append(new_path)
                    path_set.add(self._translate_path(new_path))

        if not checked_path:
            return []

        # 重新分组
        new_instances = group_paths([PathNodeBeanList.parse_obj(one).dict() for one in checked_path])
        return [ConditionBean(id=gen_uuid(), instances=new_instances, attributes=[])]

    @staticmethod
    def _translate_path(path: List[PathNodeBean]) -> str:
        return "/".join(["{},{},{}".format(node.system_id, node.type, node.id) for node in path])

    def _merge_multi_conditions(self, rrt_conditions: List[List[ConditionBean]]) -> List[ConditionBean]:
        """
        申请的操关联多个资源类型时，产生的依赖操作的条件必须同时产生的条件的交集
        """
        rrt_path_sets: List[set] = []
        for conditions in rrt_conditions:
            path_set = set()
            for c in conditions:
                for i in c.instances:
                    for p in i.path:
                        path_set.add(self._translate_path(p))
            rrt_path_sets.append(path_set)

        # 取并集
        intersection = rrt_path_sets[0].intersection(*rrt_path_sets[1:])
        if not intersection:
            return []

        new_conditions: List[ConditionBean] = []
        for c in rrt_conditions[0]:
            new_instances = []
            for i in c.instances:
                new_paths = []
                for p in i.path:
                    if self._translate_path(p) in intersection:
                        new_paths.append(p)

                # 只保留有 path 的 instance
                if new_paths:
                    new_instance = deepcopy(i)
                    new_instance.path = new_paths
                    new_instances.append(new_instance)

            # 只保留 instance 不为空的条件
            if new_instances:
                new_condition = deepcopy(c)
                new_condition.instances = new_instances
                new_conditions.append(new_condition)

        return new_conditions

    def _filter_condition_of_same_type(
        self, policy_rrt: RelatedResourceBean, action_rrt: RelatedResourceType
    ) -> Optional[RelatedResourceBean]:
        """
        相同的资源类型，条件筛选

        1. 依赖操作只支持属性选择
            筛选只有属性的条件创建依赖操作权限
        2. 依赖操作只支持拓扑
            1. 筛选只有拓扑的条件
            2. 使用依赖操作的实例视图匹配拓扑，筛选出需要创建的的权限
        3. 依赖操作同时支持拓扑与属性
            1. 筛选出有包含拓扑的条件
            2. 使用依赖操作的实例视图匹配拓扑
            3. 补偿回只有属性的条件
        """
        conditions: List[ConditionBean] = []

        # 如果操作的选择类型是 attribute, 则筛选出只有属性的条件，返回所有有属性的条件
        if action_rrt.selection_mode == SelectionMode.ATTRIBUTE.value:
            conditions = [one for one in policy_rrt.condition if one.has_no_instances()]
            if not conditions:
                return None

            return RelatedResourceBean(condition=conditions, **policy_rrt.dict(exclude={"condition"}))

        # 使用实例视图筛选出满足条件的
        new_rrt = policy_rrt.clone_and_filter_by_instance_selections(action_rrt.instance_selections)
        if not new_rrt:
            return None

        # 如果操作的选择类型是 instance, 则筛选出只有实例的条件
        if action_rrt.selection_mode == SelectionMode.INSTANCE.value:
            new_rrt.condition = [one for one in new_rrt.condition if one.has_no_attributes()]
            if len(new_rrt.condition) == 0:
                return None

        return new_rrt

    # 特殊的截断逻辑，不能复用 PathNodeList 的方法
    def _check_path_by_instance_selection(
        self, path: PathNodeBeanList, instance_selections: List[InstanceSelection]
    ) -> Optional[List[PathNodeBean]]:
        """
        校验拓扑链路是否满足实例视图

        不同类型的实例视图匹配使用前缀匹配
        """
        path = list(path.copy())  # type: ignore
        for selection in instance_selections:
            # 资源类型不同时，截取视图长度的拓扑
            if len(path) > len(selection.resource_type_chain):
                path = path[: len(selection.resource_type_chain)]

            path_resource_types = [PathResourceType(system_id=one.system_id, id=one.type) for one in path]
            if not selection.match_path(path_resource_types):
                continue

            return path
        return None

    def create_recommend_policies(
        self, policy: PolicyBean, action_list: ActionList, recommend_action_ids: List[str]
    ) -> List[PolicyBean]:
        """
        创建权限派生的推荐权限
        """
        action = action_list.get(policy.action_id)
        if not action:
            return []

        # 遍历操作推荐的操作，生成推荐操作权限
        recommend_policies: List[PolicyBean] = []
        for _id in recommend_action_ids:
            recommend_action = action_list.get(_id)
            if not recommend_action:
                continue

            recommend_policy = self._create_related_policy(
                policy, recommend_action, exclude_diff_type_action=True
            )  # 只生成有相同资源类型的关联操作
            if recommend_policy:
                recommend_policies.append(recommend_policy)

        for p in recommend_policies:
            p.set_expired_at(policy.expired_at)

        return recommend_policies
