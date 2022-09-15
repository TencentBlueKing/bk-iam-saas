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

from pydantic.tools import parse_obj_as

from backend.biz.action import ActionBiz
from backend.biz.group import GroupTemplateGrantBean
from backend.biz.policy import PolicyBean, PolicyBeanList
from backend.biz.role import RoleBiz, RoleInfoBean
from backend.service.constants import ADMIN_USER
from backend.service.models.policy import ResourceGroupList
from backend.service.models.subject import Subject
from backend.service.role import AuthScopeAction, AuthScopeSystem
from backend.util.uuid import gen_uuid

from .constants import ManagementCommonActionNameEnum, ManagementGroupNameSuffixEnum
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

    role_biz = RoleBiz()
    action_biz = ActionBiz()

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
        authorization_scopes = [
            {"system_id": system_id, "actions": policies}
            for system_id, policies in system_authorization_scope_dict.items()
        ]
        return authorization_scopes

    def to_role_info(self, data) -> RoleInfoBean:
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

    def init_role_info(self, data):
        """
        创建初始化分级管理员数据

        1. 遍历各个需要初始化的系统
        2. 查询系统的常用操作与系统的操作信息, 拼装出授权范围
        3. 返回role info
        """
        role_info = RoleInfoBean(
            name=data["biz_name"],
            description="管理员可授予他人{}业务的权限".format(data["biz_name"]),
            members=[ADMIN_USER],
            subject_scopes=[Subject(type="*", id="*")],
            authorization_scopes=[],
        )

        # 默认需要初始化的系统列表
        systems = ["bk_job", "bk_cmdb", "bk_monitorv3", "bk_log_search", "bk_sops", "bk_nodeman", "bk_gsekit"]
        for system_id in systems:
            resource_type = "biz" if system_id != "bk_sops" else "project"
            resource_system = "bk_cmdb" if system_id != "bk_sops" else "bk_sops"
            resource_id = data["biz_id"] if system_id != "bk_sops" else data["project_id"]
            resource_name = data["biz_name"] if system_id != "bk_sops" else data["project_name"]

            auth_scope = AuthScopeSystem(system_id=system_id, actions=[])

            # 1. 查询常用操作
            common_action = self.role_biz.get_common_action_by_name(
                system_id, ManagementCommonActionNameEnum.OPS.value
            )
            if not common_action:
                continue

            # 2. 查询操作信息
            action_list = self.action_biz.list(system_id)

            # 3. 生成授权范围
            for action_id in common_action.action_ids:
                action = action_list.get(action_id)
                if not action:
                    continue

                # 不关联资源类型的操作
                if len(action.related_resource_types) == 0:
                    auth_scope_action = AuthScopeAction(id=action.id, resource_groups=ResourceGroupList(__root__=[]))
                else:
                    policy_data = {
                        "id": action.id,
                        "resource_groups": [
                            {
                                "related_resource_types": [
                                    {
                                        "system_id": rrt.system_id,
                                        "type": rrt.id,
                                        "condition": [
                                            {
                                                "id": gen_uuid(),
                                                "instances": [
                                                    {
                                                        "type": resource_type,
                                                        "path": [
                                                            {
                                                                "id": resource_id,
                                                                "name": resource_name,
                                                                "system_id": resource_system,
                                                                "type": resource_type,
                                                            }
                                                        ],
                                                    }
                                                ],
                                                "attributes": [],
                                            }
                                        ],
                                    }
                                    for rrt in action.related_resource_types
                                ]
                            }
                        ],
                    }
                    auth_scope_action = AuthScopeAction.parse_obj(policy_data)

                auth_scope.actions.append(auth_scope_action)

            # 4. 组合授权范围
            if auth_scope.actions:
                role_info.authorization_scopes.append(auth_scope)

        return role_info

    def init_group_auth_info(self, authorization_scopes, name_suffix: str):
        templates = []
        for auth_scope in authorization_scopes:
            system_id = auth_scope["system_id"]
            actions = auth_scope["actions"]
            if name_suffix == ManagementGroupNameSuffixEnum.READ.value:
                common_action = self.role_biz.get_common_action_by_name(
                    system_id, ManagementCommonActionNameEnum.READ.value
                )
                if not common_action:
                    continue

                actions = [a for a in actions if a["id"] in common_action.action_ids]

            policies = [PolicyBean.parse_obj(action) for action in actions]
            policy_list = PolicyBeanList(
                system_id=system_id,
                policies=policies,
                need_fill_empty_fields=True,  # 填充相关字段
            )

            template = GroupTemplateGrantBean(
                system_id=system_id,
                template_id=0,  # 自定义权限template_id为0
                policies=policy_list.policies,
            )

            templates.append(template)

        return templates
