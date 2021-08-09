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
from typing import Dict, List

from pydantic.tools import parse_obj_as

from backend.common.error_codes import error_codes

from ..action import ActionCheckBiz, ActionForCheck
from ..instance_selection import InstanceSelectionBean, InstanceSelectionBiz, PathResourceTypeBean
from ..policy import PolicyBean, PolicyBeanList, group_paths
from ..resource import ResourceBiz, ResourceNodeBean, ResourceNodeNameDictBean


class OpenCommonTrans:
    """主要是处理open api的通用处理，因为所有open api都会保持相同的概念协议，所有很多转换逻辑都是通用"""

    resource_biz = ResourceBiz()

    def _list_instance_name_by_paths(self, paths: List[List[Dict]]) -> ResourceNodeNameDictBean:
        """查询所有路径里的资源实例名称
        paths: [
            [
                {
                    system,
                    type,
                    id,
                },
                ...
            ]
        ]
        """
        resource_nodes = [
            ResourceNodeBean(system_id=node["system"], type=node["type"], id=node["id"])
            for path in paths
            for node in path
        ]
        # 查询资源Name
        return self.resource_biz.fetch_resource_name(resource_nodes, raise_not_found_exception=True)

    @staticmethod
    def _fill_paths_instance_name(paths: List[List[Dict]], name_provider: ResourceNodeNameDictBean):
        """查询所有路径里的资源实例名称
        paths: [
            [
                {
                    system,
                    type,
                    id,
                },
                ...
            ]
        ]
        """
        for path in paths:
            for node in path:
                node["name"] = name_provider.get_name(node["system"], node["type"], node["id"])

    def _fill_paths_instance_name_for_actions(self, actions: List[Dict]):
        """给(多个)路径填充资源实例名称
        actions: [
            {
                id: 操作ID
                related_resource_types: [
                    {
                        system,
                        type,
                        instances: [
                            [
                                {
                                    system,
                                    type,
                                    id,
                                },
                                ...
                            ]
                        ],
                    }
                ]
            }
        ]
        """
        # 1. 遍历所有操作里的所有路径
        paths = []
        for action in actions:
            for rrt in action["related_resource_types"]:
                paths.extend(rrt["instances"])

        # 2. 查询路径里的资源实例
        resource_node_name_dict = self._list_instance_name_by_paths(paths)

        # 3. 填充实例名称
        for action in actions:
            for rrt in action["related_resource_types"]:
                self._fill_paths_instance_name(rrt["instances"], resource_node_name_dict)


class AccessSystemApplicationTrans(OpenCommonTrans):
    """接入系统请求自定义权限的申请链接的请求数据"""

    action_check_biz = ActionCheckBiz()
    instance_selection_biz = InstanceSelectionBiz()

    def _raise_match_selection_fail_exception(self, path):
        raise error_codes.VALIDATE_ERROR.format(f"resource({path}) not satisfy instance selection")

    def _fill_instance_path_system(self, path: List[Dict], selections: List[InstanceSelectionBean]):
        """使用实例视图，对资源实例路径进行system填充
        path: [
            {
                system,  # 大部分情况下为空，只有引用了其他系统资源同时与当前系统的资源类型ID冲突时才需要
                type,
                id,
            },
            ...
        ]
        """
        # 遍历每个实例视图，查询哪些实例视图与path是匹配
        path_resource_types = [
            PathResourceTypeBean(system_id=node.get("system", ""), id=node["type"]) for node in path
        ]
        match_selections = [selection for selection in selections if selection.match_path(path_resource_types)]

        # 若没有任何一个实例视图匹配，说明数据有问题，直接异常
        if not match_selections:
            self._raise_match_selection_fail_exception(path)

        # 判断是否路径上每个节点都有system，有的话不需要使用实例视图填充
        if all([node.get("system") != "" for node in path]):
            return

        # 取匹配的实例视图的第一个来做填充
        first_match_selection = match_selections[0]

        # 获取到实例视图提供的系统列表, 填充到现有的path中
        system_ids = first_match_selection.list_match_path_system_id(path_resource_types)
        for node, system_id in zip(path, system_ids):
            node["system"] = system_id

        # 如果有多个实例视图可以匹配, 所有实例视图返回的system_ids必须一致
        for selection in match_selections[1:]:
            if system_ids != selection.list_match_path_system_id(path_resource_types):
                self._raise_match_selection_fail_exception(path)

    def _fill_instance_system(self, system_id: str, action: Dict):
        """填充system，由于申请数据里的资源实例只有type和id，不知道该资源是哪个系统的，所以需要根据权限模型的进行填充
        action: {
            id: 操作ID
            related_resource_types: [
                {
                    system,
                    type,
                    instances: [
                        [
                            {
                                system,  # 大部分情况下为空，只有引用了其他系统资源同时与当前系统的资源类型ID冲突时才需要
                                type,
                                id,
                            },
                            ...
                        ]
                    ]
                }
            ]
        }
        """
        # 使用模型里的实例视图进行填充
        for rrt in action["related_resource_types"]:
            # 查询实例视图
            selections = self.instance_selection_biz.list_by_action_resource_type(
                system_id, action["id"], rrt["system"], rrt["type"]
            )

            # 对于只支持属性配置的操作，不需要填充
            if not selections:
                # 没有实例视图，但是在授权时配置里实例，则不允许
                if rrt["instances"]:
                    raise error_codes.VALIDATE_ERROR.format(f"action({action['id']}) not support to grant instance")
                continue

            # 填充instance的system_id
            for path in rrt["instances"]:
                self._fill_instance_path_system(path, selections)

    @staticmethod
    def _to_policy(action: Dict) -> PolicyBean:
        """申请的数据转换为策略数据结构
        action: {
            id: 操作ID
            related_resource_types: [
                {
                    system,
                    type,
                    instances: [
                        [
                            {
                                system,
                                type,
                                id,
                                name,
                            },
                            ...
                        ]
                    ],
                    attributes: [
                        {
                            id,
                            name,
                            values: [
                                {
                                    id,
                                    name
                                },
                                ...
                            ]
                        },
                        ...
                    ]
                }
            ]
        }
        """
        related_resource_types = []
        for rt in action["related_resource_types"]:
            # 将path里system转为system_id
            for path in rt["instances"]:
                for node in path:
                    node["system_id"] = node.pop("system")

            # 将多个以path方式表示的实例进行分组
            instances = group_paths(rt["instances"])

            related_resource_types.append(
                {
                    "system_id": rt["system"],
                    "type": rt["type"],
                    "condition": [{"instances": instances, "attributes": rt["attributes"]}],
                }
            )

        return PolicyBean.parse_obj({"action_id": action["id"], "related_resource_types": related_resource_types})

    def to_policies(self, data: Dict) -> PolicyBeanList:
        """
        组装出申请的策略
        {
            system:
            actions: [
                {
                    id: 操作ID
                    related_resource_types: [
                        {
                            system,
                            type,
                            instances: [
                                [
                                    {
                                        system,  # 大部分情况下为空，只有引用了其他系统资源同时与当前系统的资源类型ID冲突时才需要
                                        type,
                                        id,
                                    },
                                    ...
                                ]
                            ],
                            attributes: [
                                {
                                    id,
                                    name,
                                    values: [
                                        {
                                            id,
                                            name
                                        },
                                        ...
                                    ]
                                },
                                ...
                            ]
                        }
                    ]
                }
            ]
        }
        """
        system_id = data["system"]
        actions = data["actions"]

        # 1. 初步检查是否合法数据，与权限模型是否一致
        self.action_check_biz.check(system_id, parse_obj_as(List[ActionForCheck], actions))

        # 2. 遍历每个授权操作的策略，对实例的system_id进行填充
        for action in actions:
            self._fill_instance_system(system_id, action)

        # 3. 将给所有资源实例添加名字
        self._fill_paths_instance_name_for_actions(actions)

        # 4. 转换为策略数据结构
        policies = [self._to_policy(action) for action in actions]
        policy_list = PolicyBeanList(
            system_id=system_id,
            policies=policies,
            need_fill_empty_fields=True,
            need_check_instance_selection=False,
            need_ignore_path=False,
        )

        return policy_list
