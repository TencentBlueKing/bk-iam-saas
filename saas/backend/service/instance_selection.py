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

from typing import List

from backend.component import iam

from .models import Action, InstanceSelection, RawInstanceSelection


class InstanceSelectionService:
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id

    def list_raw_by_system(self, system_id: str) -> List[RawInstanceSelection]:
        """
        获取系统所有的实例视图，用于 manager api
        """
        instance_selections = iam.list_instance_selection(system_id)
        if not instance_selections:
            return []
        return [
            RawInstanceSelection(**i)
            for i in instance_selections
            if not i.get("tenant_id") or i.get("tenant_id") == self.tenant_id
        ]

    def list_by_action_resource_type(
        self, system_id: str, action_id: str, resource_type_system_id: str, resource_type_id: str
    ) -> List[InstanceSelection]:
        """
        获取某个操作关联的资源类型的实例视图，前端展示
        """
        action = Action(**iam.get_action(system_id, action_id))
        resource_type = action.get_related_resource_type(resource_type_system_id, resource_type_id)
        if not resource_type:
            return []

        iss = resource_type.instance_selections or []
        # 按租户过滤
        return [i for i in iss if not i.tenant_id or i.tenant_id == self.tenant_id]
