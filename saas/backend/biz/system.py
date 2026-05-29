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

from django.utils.translation import gettext as _

from backend.common.cache import cachedmethod
from backend.common.error_codes import error_codes
from backend.service.system import SystemService


class SystemBiz:
    def __init__(self, tenant_id: str) -> None:
        self.tenant_id = tenant_id
        self.svc = SystemService(self.tenant_id)

    get = SystemService.__dict__["get"]
    list = SystemService.__dict__["list"]
    new_system_list = SystemService.__dict__["new_system_list"]
    list_system_manger = SystemService.__dict__["list_system_manger"]

    def validate_system_access(self, system_id: str) -> None:
        """校验单个系统访问权限"""
        system = self.svc.get(system_id)
        if system.tenant_id not in (self.tenant_id, ""):
            raise error_codes.FORBIDDEN.format(_("租户不匹配，无权访问该系统"), True)

    def validate_systems_access(self, system_ids: List[str]) -> None:
        """批量校验系统访问权限"""
        for system_id in system_ids:
            self.validate_system_access(system_id)

    @cachedmethod(timeout=5 * 60)  # 缓存5分钟
    def list_client(self, system_id: str) -> List[str]:
        """查询可访问系统的clients"""
        return self.svc.list_client(system_id)
