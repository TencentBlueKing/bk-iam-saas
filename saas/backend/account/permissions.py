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

from rest_framework import permissions


def role_perm_class(perm_code):
    """A factory function which generates a Permission class for DRF permission check"""

    class Permission(permissions.BasePermission):
        def has_permission(self, request, view):
            """
            Return `True` if permission is granted, `False` otherwise.
            """
            if not bool(request.user and request.user.is_authenticated):
                return False

            return perm_code in set(request.role.permissions)

    return Permission


class RolePermission(permissions.BasePermission):
    """
    ViewSet 需要配置 action_permission
    APIView 需要配置 method_permission
    """

    def has_permission(self, request, view):
        if not bool(request.user and request.user.is_authenticated):
            return False

        if hasattr(view, "action_permission") and hasattr(view, "action"):
            # 没有在 action_permission 中配置的的 action 不需要鉴权，直接通过
            if view.action not in view.action_permission:
                return True

            return view.action_permission[view.action] in set(request.role.permissions)

        if hasattr(view, "method_permission"):
            method = request.method.lower()
            # 没有在 method_permission 中配置的的 method 不需要鉴权，直接通过
            if method not in view.method_permission:
                return True

            return view.method_permission[method] in set(request.role.permissions)

        return False
