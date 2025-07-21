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

from typing import List, Optional

from backend.common.cache import cachedmethod
from backend.component import iam

from .models import System


class SystemList:
    def __init__(self, systems: List[System]) -> None:
        self.systems = systems
        self._system_dict = {one.id: one for one in systems}

    def get(self, system_id: str) -> Optional[System]:
        return self._system_dict.get(system_id, None)


class SystemService:
    def list(self) -> List[System]:
        """获取所有系统"""
        # FIXME(tenant): 仅返回当前租户或全租户的系统列表
        systems = iam.list_system()
        # 组装为返回结构
        return [System(**i) for i in systems]

    def get(self, system_id: str) -> System:
        system = iam.get_system(system_id)
        return System(**system)

    @cachedmethod(timeout=5 * 60)  # 5 分钟过期
    def list_client(self, system_id: str) -> List[str]:
        """
        查询可访问系统的 clients
        """
        system = iam.get_system(system_id, fields="clients")
        return system["clients"].split(",")

    def new_system_list(self) -> SystemList:
        return SystemList(self.list())

    def list_system_manger(self, system_id: str) -> List[str]:
        """
        查询系统的系统管理员配置
        """
        return iam.get_system_managers(system_id)
