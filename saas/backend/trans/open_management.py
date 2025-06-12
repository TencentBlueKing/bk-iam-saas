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

from collections import defaultdict
from typing import Dict, List

from django.conf import settings
from pydantic.tools import parse_obj_as

from backend.biz.policy import PolicyBeanList
from backend.biz.role import RoleInfoBean
from backend.common.time import PERMANENT_SECONDS
from backend.service.constants import RoleType

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
        return self._to_policy_list(
            system_id, open_policies, expired_at=PERMANENT_SECONDS
        )  # 用户组授权默认过期时间为永久


class GradeManagerTrans(ManagementCommonTrans):
    """处理分级管理员数据转换"""

    def _preprocess_authorization_scopes(self, data_authorization_scopes):
        """
        预处理authorization_scopes，保证可用于RoleInfoBean的转换
        data_authorization_scopes: [
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
        """
        # 授权可范围数据转换为策略格式的auth_scopes
        system_authorization_scope_dict = defaultdict(list)
        for auth_scope in data_authorization_scopes:
            system_id = auth_scope["system"]
            resources = auth_scope["resources"]
            action_ids = [action["id"] for action in auth_scope["actions"]]
            # 转换为策略列表(转换时会对action、实例视图等进行校验)
            policy_list = self.to_policy_list_for_batch_action_and_resources(system_id, action_ids, resources)
            # 由于RoleInfoBean需要的action_id是以id表示，而非action_id，所以PolicyBean转为字典时需要用其别名
            policies = [p.dict(by_alias=True) for p in policy_list.policies]
            system_authorization_scope_dict[system_id].extend(policies)

        # 将按system分组的数据转为authorization_scopes
        return [
            {"system_id": system_id, "actions": policies}
            for system_id, policies in system_authorization_scope_dict.items()
        ]

    def to_role_info(
        self, data, _type: str = RoleType.GRADE_MANAGER.value, source_system_id: str = ""
    ) -> RoleInfoBean:
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
        data.update(
            {
                "type": _type,
                "source_system_id": source_system_id,
                "hidden": source_system_id in settings.HIDDEN_SYSTEM_LIST if source_system_id else False,
            }
        )

        # 替换掉data里原有的authorization_scopes
        data["authorization_scopes"] = self._preprocess_authorization_scopes(data["authorization_scopes"])

        return RoleInfoBean.parse_obj(data)

    def to_role_info_for_update(self, data):
        """
        将分级管理的信息数据转换为 RoleInfoBean，用于后续分级管理员更新
        data结构与to_role_info的data一致，但可能只有部分字段
        """
        if "authorization_scopes" in data:
            # 替换掉data里原有的authorization_scopes
            data["authorization_scopes"] = self._preprocess_authorization_scopes(data["authorization_scopes"])
        return RoleInfoBean.from_partial_data(data)
