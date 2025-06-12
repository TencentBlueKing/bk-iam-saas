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

from typing import Any, Dict, List, Optional

from django.conf import settings
from pydantic import parse_obj_as

from backend.biz.group import GroupTemplateGrantBean
from backend.biz.policy import PolicyBeanList
from backend.biz.role import RoleInfoBean
from backend.service.constants import RoleType
from backend.service.role import AuthScopeAction, AuthScopeSystem

from .policy import PolicyTrans


class RoleTrans:
    """
    转换Role的创建/更新信息
    """

    policy_trans = PolicyTrans()

    def from_role_data(
        self,
        data: Dict[str, Any],
        old_system_policy_list: Optional[Dict[str, PolicyBeanList]] = None,
        _type: str = RoleType.GRADE_MANAGER.value,
        source_system_id: str = "",
    ) -> RoleInfoBean:
        """
        data: {
            "name": str,
            "description": str,
            "members": List[
                {
                    "username": str
                }
            ],
            "subject_scopes": [
                {
                    "type": str,
                    "id": str
                }
            ],
            "authorization_scopes": [
                {
                    "system_id": str,
                    "actions": [],
                    "aggregations": []
                }
            ]
        }

        old_system_policy_list: 更新的数据提供
        """
        data.update(
            {
                "type": _type,
                "source_system_id": source_system_id,
                "hidden": source_system_id in settings.HIDDEN_SYSTEM_LIST if source_system_id else False,
            }
        )

        for system in data["authorization_scopes"]:
            system_id = system["system_id"]

            policy_list = self.policy_trans.from_aggregate_actions_and_actions(system_id, system)

            if old_system_policy_list and system_id in old_system_policy_list:
                # 更新范围信息时只需检查新增部分的实例名称
                added_policy_list = policy_list.sub(old_system_policy_list[system_id])
                added_policy_list.check_resource_name()
            else:
                policy_list.check_resource_name()

            system["actions"] = [p.dict() for p in policy_list.policies]

        return RoleInfoBean.parse_obj(data)


class RoleAuthScopeTrans:
    def from_policy_list(self, policy_list: PolicyBeanList):
        return AuthScopeSystem(
            system_id=policy_list.system_id, actions=parse_obj_as(List[AuthScopeAction], policy_list.policies)
        )

    def from_group_auth_templates(self, templates: List[GroupTemplateGrantBean]):
        return [
            AuthScopeSystem(
                system_id=template.system_id, actions=parse_obj_as(List[AuthScopeAction], template.policies)
            )
            for template in templates
        ]
