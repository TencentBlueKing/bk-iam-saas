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

from backend.common.cache import cachedmethod
from backend.service.system import SystemService


class SystemBiz:
    svc = SystemService()

    get = SystemService.__dict__["get"]
    list = SystemService.__dict__["list"]
    new_system_list = SystemService.__dict__["new_system_list"]
    list_system_manger = SystemService.__dict__["list_system_manger"]

    @cachedmethod(timeout=5 * 60)  # 缓存5分钟
    def list_client(self, system_id: str) -> List[str]:
        """查询可访问系统的clients"""
        return self.svc.list_client(system_id)
