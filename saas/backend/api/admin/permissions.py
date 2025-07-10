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

from rest_framework import exceptions, permissions

from .models import AdminAPIAllowListConfig


class AdminAPIPermission(permissions.IsAuthenticated):
    """
    Admin API权限校验
    需要配合 admin_api_permission
    admin_api_permission = {
        "请求函数名称": 鉴权API名称
    }
    鉴权API名称对应是：AdminAPIEnum枚举值
    """

    def has_permission(self, request, view):
        # ESB认证必须通过
        if not super().has_permission(request, view):
            return False

        # 若配置了当前鉴权Class，但是没有配套的admin_api_permission，则直接不通过
        if not hasattr(view, "admin_api_permission"):
            return False

        # 默认值即为请求method，因为继承于APIView（即使是ViewSet，ViewSet也是继承了APIView的）
        handler_name = request.method.lower()
        # ViewSet.as_view({...}) 设置了method的映射，则进行更新为映射的值
        if hasattr(view, "action"):
            handler_name = view.action

        # 判断要处理的函数, 即handler是否配置了权限
        # 若没有配置权限控制，则直接不通过
        if handler_name not in view.admin_api_permission:
            return False

        # API认证与鉴权
        api = view.admin_api_permission[handler_name]
        # 若校验不通过，则会直接抛出exceptions.PermissionDenied异常
        self._verify_api(request, api)

        return True

    def _verify_api(self, request, api):
        """
        对API进行校验
        """
        # 所有API认证鉴权所需
        app_code = request.bk_app_code

        # TODO: 添加缓存，避免每次请求都进行DB查询，同时对于managment和authorization也需要添加
        is_allowed = AdminAPIAllowListConfig.is_allowed(app_code, api)
        if not is_allowed:
            raise exceptions.PermissionDenied(detail=f"app_code({app_code}) do not be allowed to call api({api})")
