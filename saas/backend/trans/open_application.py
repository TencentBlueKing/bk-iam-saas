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
from typing import Any, Dict, List, Optional, Tuple

from pydantic.tools import parse_obj_as

from backend.apps.organization.models import User as UserModel
from backend.biz.application import ActionApplicationDataBean
from backend.biz.policy import PolicyBean, PolicyBeanList
from backend.service.constants import SubjectType
from backend.service.models import Applicant
from backend.trans.application import ApplicationDataTrans

from .open import OpenCommonTrans, OpenPolicy


class AccessSystemApplicationTrans(OpenCommonTrans, ApplicationDataTrans):
    """接入系统请求自定义权限的申请链接的请求数据"""

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        OpenCommonTrans.__init__(self, tenant_id)
        ApplicationDataTrans.__init__(self, tenant_id)

    def to_policy_list(self, data: Dict) -> PolicyBeanList:
        """
        组装出申请的策略
        {
            system:
            actions: [
                {
                    id: 操作 ID
                    related_resource_types: [
                        {
                            system,
                            type,
                            instances: [
                                [
                                    {
                                        # system 大部分情况下为空，
                                        # 只有引用了其他系统资源同时与当前系统的资源类型 ID 冲突时才需要
                                        system,
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

        # 1. 将数据转换为 OpenPolicy 用于后续处理
        for action in actions:
            action["system_id"] = system_id
            for rrt in action["related_resource_types"]:
                rrt["paths"] = rrt.pop("instances", [])
        open_policies = parse_obj_as(List[OpenPolicy], actions)

        # 2. 填充资源实例所需数据：（1）system_id（2）name
        for open_policy in open_policies:
            # 填充 system_id
            open_policy.fill_instance_system(self.tenant_id)
            # 将给所有资源实例添加名字
            open_policy.fill_instance_name(self.tenant_id)

        expired_at = data.get("expired_at", 0)
        return self._to_policy_list(system_id, open_policies, expired_at=expired_at)

    def from_grant_policy_application(self, applicant: str, data: Dict) -> ActionApplicationDataBean:
        """来着自定义权限申请的数据转换"""

        # 1. 转换数据结构
        policy_list = self.to_policy_list(data)

        # 2. 只对新增的策略进行申请，所以需要移除掉已有的权限
        application_policy_list = self._gen_need_apply_policy_list(applicant, data["system"], policy_list)

        # 3. 转换为 ApplicationBiz 创建申请单所需数据结构
        user = UserModel.objects.get(username=applicant)

        return ActionApplicationDataBean(
            applicant=applicant,
            policy_list=application_policy_list,
            applicants=[Applicant(type=SubjectType.USER.value, id=user.username, display_name=user.display_name)],
            reason=data["reason"],
        )

    def from_grant_policy_with_custom_ticket_application(
        self, applicant: str, data: Dict
    ) -> Tuple[ActionApplicationDataBean, Optional[List[Tuple[PolicyBean, Any]]]]:
        """来着带自定义审批内容的自定义权限申请的数据转换"""

        # 1. 将多条策略按 Action 合并为标准的策略数据
        policy_list = PolicyBeanList(tenant_id=self.tenant_id, system_id=data["system"], policies=[])
        policy_ticket_contents = []
        for action in data["actions"]:
            one_policy_data = {
                "system": data["system"],
                "actions": [
                    {
                        "id": action["id"],
                        "related_resource_types": [
                            {
                                "system": rrt["system"],
                                "type": rrt["type"],
                                # 实际上是将单个实例转换为标准的多实例结构
                                "instances": [rrt["instance"]] if "instance" in rrt else [],
                                "attributes": rrt.get("attributes", []),
                            }
                            for rrt in action["related_resource_types"]
                        ],
                    }
                ],
            }
            if "expired_at" in data:
                one_policy_data["expired_at"] = data["expired_at"]

            # 转换数据结构
            one_policy_list = self.to_policy_list(one_policy_data)

            # 每条原始策略 (未合并) 对应的审批单据内容
            if data["ticket_content_template"]:
                # Note: 这里必须使用 deepcopy，且需要 one_policy_list 被添加到 policy_list 前，
                # 否则其实 one_policy_list 会跟随着 policy_list 变化，获取的数据就不正确
                policy_ticket_contents.append((deepcopy(one_policy_list.policies[0]), action["ticket_content"]))

            # 添加
            policy_list.add(one_policy_list)

        # 2. 只对新增的策略进行申请，所以需要移除掉已有的权限
        application_policy_list = self._gen_need_apply_policy_list(applicant, data["system"], policy_list)

        # 3. 转换为 ApplicationBiz 创建申请单所需数据结构
        user = UserModel.objects.get(username=applicant)

        application_data = ActionApplicationDataBean(
            applicant=applicant,
            policy_list=application_policy_list,
            applicants=[Applicant(type=SubjectType.USER.value, id=user.username, display_name=user.display_name)],
            reason=data["reason"],
        )

        return application_data, policy_ticket_contents or None
