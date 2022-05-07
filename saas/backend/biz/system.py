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
from typing import List

from pydantic import BaseModel

from backend.apps.role.models import Role
from backend.service.constants import RoleType
from backend.service.system import SystemService


class SystemShareInfo(BaseModel):
    id: str
    managers: List[str] = []


class SystemBiz:
    svc = SystemService()

    get = SystemService.__dict__["get"]
    list = SystemService.__dict__["list"]
    new_system_list = SystemService.__dict__["new_system_list"]

    def list_client(self, system_id: str) -> List[str]:
        """查询可访问系统的clients"""
        return self.svc.list_client(system_id)

    def get_share_info(self, system_id: str) -> SystemShareInfo:
        """获取系统共享信息"""
        share_info = SystemShareInfo(id=system_id, managers=[])
        try:
            role = Role.objects.get(type=RoleType.SYSTEM_MANAGER.value, code=system_id)
            share_info.managers = role.members
        except Role.DoesNotExist:
            # 对于无系统管理员，可能是系统不存在或SaaS未同步到，直接忽略即可
            pass

        return share_info
