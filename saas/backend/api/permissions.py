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

from rest_framework import permissions


class ApprovalBotPermission(permissions.BasePermission):
    """
    审批机器人回调鉴权
    """

    APP_CODE = "approvalbot"

    def has_permission(self, request, view):
        if not bool(request.user and request.user.is_authenticated):
            return False

        # 只有app_code为审批助手才能访问
        return request.bk_app_code == self.APP_CODE
