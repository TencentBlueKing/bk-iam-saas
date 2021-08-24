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

from backend.biz.policy import PolicyBeanList
from backend.biz.role import RoleInfoBean

from .open import OpenCommonTrans, OpenPolicy


class ManagementCommonTrans(OpenCommonTrans):
    """主要是处理，管理类API一些通用的公共转换逻辑"""

    def to_policy_list_for_batch_action_and_resources(
        self, system_id: str, action_ids: List[str], resources: List[Dict]
    ) -> PolicyBeanList:
        """
        这里是将管理类API对外暴露的策略相关的协议数据，转换为策略数据结构列表
        因为管理类API对外协议一般都是一样的，所以可以通用转换
        resources: [
                {
                    system,
                    type,
                    paths: [
                        [
                            {
                                system,
                                type,
                                id,
                                name,
                            }
                        ]
                    ]
                },
                ...
            ]
        }
        """
        # 将数据转换为OpenPolicy用于后续处理
        actions = [
            {"system_id": system_id, "action_id": action_id, "related_resource_types": resources}
            for action_id in action_ids
        ]
        open_policies = parse_obj_as(List[OpenPolicy], actions)

        # 转换为策略列表(转换时会对action、实例视图等进行校验)
        return self._to_policy_list(system_id, open_policies)


class GradeManagerTrans(ManagementCommonTrans):
    """处理分级管理员数据转换"""

    def to_role_info(self, data: Dict) -> RoleInfoBean:
        """
        将分级管理的信息数据转换为 RoleInfoBean，用于后续分级管理员创建
        data: {
            system,
            name,
            description,
            members: [...],
            subject_scopes: [
                {
                    type,
                    id
                },
                ...
            ],
            authorization_scopes: [
                {
                    system,
                    actions: [
                        {
                            id,
                        },
                        ...
                    ],
                    resources: [
                        {
                            system,
                            type,
                            paths: [
                                [
                                    {
                                        system,
                                        type,
                                        id,
                                        name,
                                    }
                                ]
                            ]
                        },
                        ...
                    ]
                }
            ]
        }
        """
        # 将授权的权限范围数据转换为策略格式的auth_scopes
        authorization_scopes = []
        for auth_scope in data["authorization_scopes"]:
            system_id = auth_scope["system"]
            resources = auth_scope["resources"]
            action_ids = [action["id"] for action in auth_scope["actions"]]
            # 转换为策略列表(转换时会对action、实例视图等进行校验)
            policy_list = self.to_policy_list_for_batch_action_and_resources(system_id, action_ids, resources)
            authorization_scopes.append(
                {
                    "system_id": system_id,
                    # 由于RoleInfoBean需要的action_id是以id表示，而非action_id，所以PolicyBean转为字典时需要用其别名
                    "actions": [p.dict(by_alias=True) for p in policy_list.policies],
                }
            )

        # 替换掉data里原有的authorization_scopes
        data["authorization_scopes"] = authorization_scopes

        return RoleInfoBean.parse_obj(data)
