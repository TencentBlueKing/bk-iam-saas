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

from backend.biz.group import GroupTemplateGrantBean

from .policy import PolicyTrans


class GroupTrans:
    """
    转换 Group 授权信息
    """

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.policy_trans = PolicyTrans(self.tenant_id)

    def from_group_grant_data(self, data: List[Dict[str, Any]]) -> List[GroupTemplateGrantBean]:
        """
        转换 Group 授权数据结构

        data: [
            {
                "system_id": str
                "template_id": str
                "actions": []
                "aggregations": []
            }
        ]
        """
        return [
            GroupTemplateGrantBean(
                system_id=one["system_id"],
                template_id=one["template_id"],
                policies=self.policy_trans.from_aggregate_actions_and_actions(one["system_id"], one).policies,
            )
            for one in data
        ]
