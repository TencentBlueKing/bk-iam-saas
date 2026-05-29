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

from backend.biz.system import SystemBiz


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


def _extract_value(container, key):
    """支持点号嵌套的字段提取，如 'action.system_id'"""
    if container is None:
        return None
    cur = container
    for part in key.split("."):
        if isinstance(cur, dict):
            cur = cur.get(part)
        else:
            return None
        if cur is None:
            return None
    return cur


def system_access_perm_class(source: str = "url", key: str = "system_id"):
    """
    生成系统访问校验权限类的工厂函数

    功能：
        校验请求中携带的 system_id：
          1. 系统在数据库中存在
          2. 调用方租户有权访问该系统（系统属于本租户 或 系统为全租户系统）
        校验逻辑底层复用 SystemBiz.get（其内部已包含租户匹配性校验）

    适用范围：用户调用的接口

    参数：
        source: system_id 的来源
            - "url"       : URL kwargs（路径参数）
            - "query"     : query string（GET 参数）
            - "body"      : request body（POST/PUT 请求体）
            - "body_list" : request body 是 system_id 字符串列表（批量场景）
        key: 字段名，支持点号嵌套（如 "resource_type.system_id"）；source="body_list" 时该参数无意义

    用法：
        permission_classes = [system_access_perm_class()]                              # URL 中 system_id
        permission_classes = [system_access_perm_class("query", "system_id")]          # query 中 system_id
        permission_classes = [system_access_perm_class("body", "source_system_id")]    # body 中 source_system_id
        permission_classes = [system_access_perm_class("body_list")]                   # body 是 system_id 列表

        # 与 role_perm_class 组合使用
        permission_classes = [
            role_perm_class(PermissionCodeEnum.MANAGE_GROUP.value),
            system_access_perm_class("body", "system_id"),
        ]
    """

    class Permission(permissions.BasePermission):
        def has_permission(self, request, view):
            if not bool(request.user and request.user.is_authenticated):
                return False

            # 提取 system_id
            if source == "url":
                system_ids = [request.parser_context["kwargs"].get(key)]
            elif source == "query":
                system_ids = [request.query_params.get(key)]
            elif source == "body":
                system_ids = [_extract_value(request.data, key)]
            elif source == "body_list":
                system_ids = request.data if isinstance(request.data, list) else []
            else:
                raise ValueError(f"unsupported source: {source}")

            # 过滤掉空值（不传 system_id 表示查询所有，此时跳过校验）
            system_ids = [s for s in system_ids if s]
            if not system_ids:
                return True

            # 逐个校验，SystemBiz.get 在系统不存在或租户不匹配时会抛异常
            biz = SystemBiz(request.tenant_id)
            for system_id in system_ids:
                biz.get(system_id)

            return True

    return Permission
