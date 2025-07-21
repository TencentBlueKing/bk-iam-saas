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

from rest_framework import exceptions

from backend.biz.system import SystemBiz


class SystemClientCheckMixin:
    def verify_system_client(self, system_id: str, app_code: str):
        """
        验证 app_code 是否能访问系统
        """
        clients = SystemBiz().list_client(system_id)

        if app_code not in clients:
            raise exceptions.PermissionDenied(
                detail="app_code {} can not access system {}".format(app_code, system_id)
            )
