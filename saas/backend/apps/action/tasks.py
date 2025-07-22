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

from collections import defaultdict
from typing import Dict, List, Optional

from celery import shared_task
from django.conf import settings
from pydantic import parse_obj_as

from backend.apps.action.models import AggregateAction
from backend.biz.system import SystemBiz
from backend.service.action import ActionService
from backend.service.models.action import Action
from backend.service.models.instance_selection import ChainNode


@shared_task(ignore_result=True)
def generate_action_aggregate():
    # 生成操作聚合配置
    systems = SystemBiz().list()
    action_svc = ActionService(settings.BK_APP_TENANT_ID)

    # 遍历每个系统
    for system in systems:
        system_id = system.id
        actions = action_svc.list(system_id)
        # 使用操作的实例视图生成聚合操作的结构
        resource_type_actions = aggregate_actions_group_by_selection_node(actions)

        # 查询系统已存在的聚合操作
        exists_agg_actions = query_exists_aggregate_actions(system_id)

        # 分离处理需要删除的聚合操作
        delete_agg_actions = [
            agg_action
            for resource_type, agg_action in exists_agg_actions.items()
            if resource_type not in resource_type_actions
        ]

        # 分离出需要创建与需要更新的聚合操作
        create_agg_actions, update_agg_actions = [], []
        for resource_type, action_ids in resource_type_actions.items():
            if resource_type in exists_agg_actions:
                agg_action = exists_agg_actions[resource_type]
                if len(action_ids) == 1:
                    delete_agg_actions.append(agg_action)
                    continue

                if set(agg_action.action_ids) != set(action_ids):
                    agg_action.action_ids = action_ids
                    update_agg_actions.append(agg_action)

                continue

            if len(action_ids) == 1:
                continue

            agg_action = AggregateAction(system_id=system_id)
            agg_action.action_ids = action_ids
            agg_action.aggregate_resource_type = resource_type.to_resource_type_list()
            create_agg_actions.append(agg_action)

        # 执行 CURD
        if create_agg_actions:
            AggregateAction.objects.bulk_create(create_agg_actions)

        if update_agg_actions:
            AggregateAction.objects.bulk_update(update_agg_actions, ["_action_ids"])

        if delete_agg_actions:
            AggregateAction.objects.filter(id__in=[agg_action.id for agg_action in delete_agg_actions]).delete()


class FirstNodeList:
    def __init__(self, nodes: List[ChainNode]) -> None:
        self.nodes = sorted(nodes, key=lambda node: hash(node))  # 保持节点顺序

    def __hash__(self):
        return hash(tuple(self.nodes))

    def __eq__(self, other) -> bool:
        return self.nodes == other.nodes

    def to_resource_type_list(self):
        return [node.dict() for node in self.nodes]


def query_exists_aggregate_actions(system_id) -> Dict[FirstNodeList, AggregateAction]:
    """
    查询已存在的聚合操作配置
    """
    agg_actions = AggregateAction.objects.filter(system_id=system_id)
    resource_type_agg_action = {}
    for aa in agg_actions:
        resource_type = aa.aggregate_resource_type
        node_list = parse_obj_as(List[ChainNode], resource_type)
        resource_type_agg_action[FirstNodeList(node_list)] = aa
    return resource_type_agg_action


def aggregate_actions_group_by_selection_node(actions) -> Dict[FirstNodeList, List[str]]:
    """
    使用实例视图的节点聚合操作
    """
    resource_type_actions = defaultdict(list)
    for action in actions:
        # 操作关联多个资源，或者不关联资源不能聚合
        if len(action.related_resource_types) != 1:
            continue

        first_node_list = get_action_selection_first_node_list(action)
        if first_node_list is None:
            continue

        resource_type_actions[first_node_list].append(action.id)

    return resource_type_actions


def get_action_selection_first_node_list(action: Action) -> Optional[FirstNodeList]:
    """
    获取操作的关联的资源类型的实例视图的第一个节点
    如果有多个实例视图，返回多个实例视图的第一个节点，并且去重
    !!! 只能用于只关联了 1 个资源类型的操作
    """
    resource_type = action.related_resource_types[0]
    if not resource_type.instance_selections:
        return None

    first_node_set = set()
    # 遍历余下的所有实例视图，如果第一个节点与第一个视图的第一个节点不一致，返回 None
    for instance_selection in resource_type.instance_selections:
        first_node = instance_selection.resource_type_chain[0]
        if first_node not in first_node_set:
            first_node_set.add(first_node)

    return FirstNodeList(list(first_node_set))
