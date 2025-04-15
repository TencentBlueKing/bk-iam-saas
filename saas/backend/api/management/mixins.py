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

from rest_framework import exceptions

from backend.api.constants import ALLOW_ANY
from backend.api.mixins import SystemClientCheckMixin

from .constants import ManagementAPIEnum
from .models import ManagementAPIAllowListConfig, SystemAllowAuthSystem


class ManagementAPIPermissionCheckMixin(SystemClientCheckMixin):
    """管理类API认证与鉴权
    1. API认证：校验app_code与system
    2. API鉴权: 查询管理类API白名单表
    3. API数据鉴权：查询系统可管控的授权系统表
    """

    def verify_api_allow_list(self, system_id: str, api: ManagementAPIEnum):
        """
        API鉴权: 查询管理类API白名单表，判断是否允许访问API
        """
        allowed = ManagementAPIAllowListConfig.is_allowed(system_id, api)
        if not allowed:
            raise exceptions.PermissionDenied(
                detail=(
                    f"system[{system_id}] is not allowed to call management api[{api}], "
                    "please contact the developer to add a whitelist"
                )
            )

    def verify_system_scope(self, system_id: str, auth_system_ids: List[str]):
        """
        API数据鉴权：查询系统可管控的授权系统表，校验接入系统是否越权提交了其他系统的数据
        主要是针对分级管理员创建和更新时的可授权范围
        """
        # 加速判断：大部分系统都只是管理自身系统的权限，即可授权范围里的每个系统都只能等于自身
        if all(sys_id == system_id for sys_id in auth_system_ids):
            return

        #  接入系统可管控的系统表[system_id/auth_system_id]来实现管控更多接入系统权限
        allowed_auth_system = SystemAllowAuthSystem.list_auth_system_id(system_id)
        allowed_system_ids = set(allowed_auth_system)
        # 任何系统都允许访问自身
        allowed_system_ids.add(system_id)

        # 如果允许管理的系统存在任意，则说明该系统可管理所有系统，鉴权直接通过
        if ALLOW_ANY in allowed_system_ids:
            return

        # 遍历校验
        for sys_id in auth_system_ids:
            if sys_id not in allowed_system_ids:
                raise exceptions.PermissionDenied(
                    detail=(
                        f"system[{system_id}] is not allow to operate system[{sys_id}]'s permission data, "
                        "please contact the developer to add a whitelist"
                    )
                )

    def verify_api(self, app_code: str, system_id: str, api: ManagementAPIEnum):
        """
        该方法为最常用的API认证和鉴权方法，包括：校验app_code与system和校验管理类API权限
        """
        # API认证
        self.verify_system_client(system_id, app_code)
        # API鉴权
        self.verify_api_allow_list(system_id, api)
