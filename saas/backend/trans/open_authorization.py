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

from typing import Any, Dict, List

from pydantic.tools import parse_obj_as

from backend.biz.action import ActionBiz
from backend.biz.policy import PolicyBeanList
from backend.common.error_codes import error_codes
from backend.common.time import PERMANENT_SECONDS

from .open import OpenCommonTrans, OpenPolicy


class AuthorizationTrans(OpenCommonTrans):
    """授权 API 的数据转换"""

    def __init__(self, tenant_id: str):
        super().__init__(tenant_id)
        self.tenant_id = tenant_id
        self.action_biz = ActionBiz(tenant_id)

    def to_policy_list_for_instance(
        self, system_id: str, action_id: str, resources: List[Dict], expired_at=0
    ) -> PolicyBeanList:
        """单个实例授权
        resources: [
            {
                system,
                type,
                id,
                name
            }
        ]
        """
        # 将数据转换为 OpenPolicy 用于后续处理
        related_resource_types = [{"system_id": i["system"], "type": i["type"], "paths": [[i]]} for i in resources]
        open_policy = OpenPolicy.parse_obj(
            {"system_id": system_id, "action_id": action_id, "related_resource_types": related_resource_types}
        )

        return self._to_policy_list(system_id, [open_policy], expired_at)

    def to_policy_list_for_instances(
        self, system_id: str, action_ids: List[str], resources: List[Dict], expired_at=0
    ) -> PolicyBeanList:
        """批量实例授权
        resources: [
            {
                system,
                type,
                instances: [
                    {
                        id,
                        name
                    }
                ]
            }
        ]
        """
        # 将数据转换为 OpenPolicy 用于后续处理
        related_resource_types = [
            {
                "system_id": i["system"],
                "type": i["type"],
                "paths": [
                    [{"system_id": i["system"], "type": i["type"], "id": j["id"], "name": j["name"]}]
                    for j in i["instances"]  # 每个实例都是一个路径
                ],
            }
            for i in resources
        ]
        actions = [
            {"system_id": system_id, "action_id": action_id, "related_resource_types": related_resource_types}
            for action_id in action_ids
        ]
        open_policies = parse_obj_as(List[OpenPolicy], actions)

        return self._to_policy_list(system_id, open_policies, expired_at)

    def to_policy_list_for_path(
        self, system_id: str, action_id: str, resources: List[Dict], expired_at=0
    ) -> PolicyBeanList:
        """单一路径授权
        resources: [
            {
                system,
                type,
                path: [
                    {
                        type,  # 缺少对应资源类型的 system_id
                        id,
                        name
                    },
                    ...
                ]
            }
        ]
        """
        # 将数据转换为 OpenPolicy 用于后续处理
        related_resource_types = [
            {"system_id": i["system"], "type": i["type"], "paths": [i["path"]]} for i in resources
        ]
        open_policy = OpenPolicy.parse_obj(
            {"system_id": system_id, "action_id": action_id, "related_resource_types": related_resource_types}
        )
        # 填充路径上资源实例缺少的 system_id
        open_policy.fill_instance_system(self.tenant_id)

        return self._to_policy_list(system_id, [open_policy], expired_at)

    def to_policy_list_for_paths(
        self, system_id: str, action_ids: List[str], resources: List[Dict], expired_at=0
    ) -> PolicyBeanList:
        """批量实例授权
        resources: [
            {
                system,
                type,
                paths: [
                    [
                        {
                            type,  # 缺少对应资源类型的 system_id
                            id,
                            name
                        },
                        ...
                    ],
                    ...
                ]
            }
        ]
        """
        # 将数据转换为 OpenPolicy 用于后续处理
        actions = [
            {"system_id": system_id, "action_id": action_id, "related_resource_types": resources}
            for action_id in action_ids
        ]
        open_policies = parse_obj_as(List[OpenPolicy], actions)
        # 填充路径上资源实例缺少的 system_id
        for open_policy in open_policies:
            open_policy.fill_instance_system(self.tenant_id)

        return self._to_policy_list(system_id, open_policies, expired_at)

    def _gen_action_for_resources_of_creator(
        self, system_id: str, action_ids: List[str], resources: List[Any]
    ) -> List[Dict]:
        """
        生成 Action 结构，用于后续转换为 OpenPolicy
        """
        # 查询 Action 信息，组装出实际 Action 结构
        action_list = self.action_biz.list(system_id)
        actions = []
        for action_id in action_ids:
            action = action_list.get(action_id)
            # 对于新建关联配置里有，但实际 action 不存在，则说明权限模型注册有问题，直接报错
            if not action:
                raise error_codes.VALIDATE_ERROR.format(f"system({system_id}) has not action({action_id})")

            actions.append(
                {
                    "system_id": system_id,
                    "action_id": action_id,
                    # 对于新建关联，是可以连同授予"与资源实例无关"的操作权限
                    "related_resource_types": resources if not action.is_unrelated() else [],
                }
            )
        return actions

    def to_policy_list_for_instances_of_creator(
        self, system_id: str, action_ids: List[str], resource_type_id: str, instances: List[Dict]
    ) -> PolicyBeanList:
        """批量新建关联实例授权
        instances: [
            {
                id,
                name,
                ancestors: [  # 祖先不一定会有
                    {
                        system,
                        type,
                        id,
                    },
                    ...
                ]
            },
            ...
        ]
        """
        # 将 instances 转换为 resources 结构
        paths = []
        for ist in instances:
            # 获取祖先
            path = ist.get("ancestors") or []
            # 将本资源实例添加到路径的最后
            path.append({"system": system_id, "type": resource_type_id, "id": ist["id"], "name": ist["name"]})
            paths.append(path)
        resources = [{"system": system_id, "type": resource_type_id, "paths": paths}]

        # 组装出实际 Action 结构
        actions = self._gen_action_for_resources_of_creator(system_id, action_ids, resources)

        # 将数据转换为 OpenPolicy 用于后续处理
        open_policies = parse_obj_as(List[OpenPolicy], actions)
        # 填充路径上祖先实例缺少的名称
        for open_policy in open_policies:
            open_policy.fill_instance_name(self.tenant_id)

        return self._to_policy_list(system_id, open_policies, expired_at=PERMANENT_SECONDS)

    def to_policy_list_for_attributes_of_creator(
        self, system_id: str, action_ids: List[str], resource_type_id: str, attributes: List[Dict]
    ) -> PolicyBeanList:
        """批量新建关联属性授权
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
        """
        resources = [{"system": system_id, "type": resource_type_id, "attributes": attributes}]

        # 组装出实际 Action 结构
        actions = self._gen_action_for_resources_of_creator(system_id, action_ids, resources)

        # 将数据转换为 OpenPolicy 用于后续处理
        open_policies = parse_obj_as(List[OpenPolicy], actions)

        return self._to_policy_list(system_id, open_policies, expired_at=PERMANENT_SECONDS)
