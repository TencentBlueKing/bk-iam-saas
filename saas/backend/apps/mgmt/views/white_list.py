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

from copy import deepcopy

from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, mixins

from backend.account.permissions import RolePermission
from backend.api.admin.models import AdminAPIAllowListConfig
from backend.api.authorization.models import AuthAPIAllowListConfig
from backend.api.management.models import ManagementAPIAllowListConfig
from backend.apps.mgmt.audit import (
    AdminApiWhiteListCreateAuditProvider,
    AdminApiWhiteListDeleteAuditProvider,
    AuthorizationApiWhiteListCreateAuditProvider,
    AuthorizationApiWhiteListDeleteAuditProvider,
    ManagementApiWhiteListCreateAuditProvider,
    ManagementApiWhiteListDeleteAuditProvider,
)
from backend.apps.mgmt.constants import WHITE_LIST_API_ENUM_MAP
from backend.apps.mgmt.filters import AuthorizationApiWhiteListFilter
from backend.apps.mgmt.serializers import (
    AdminApiAddWhiteListSLZ,
    AdminApiWhiteListSLZ,
    ApiSLZ,
    AuthorizationApiAddWhiteListSLZ,
    AuthorizationApiWhiteListSchemaSLZ,
    AuthorizationApiWhiteListSLZ,
    ManagementApiAddWhiteListSLZ,
    ManagementApiWhiteListSchemaSLZ,
    ManagementApiWhiteListSLZ,
    QueryApiSLZ,
)
from backend.audit.audit import audit_context_setter, view_audit_decorator
from backend.service.constants import PermissionCodeEnum


# FIXME(tenant): 应该调整为仅仅运营租户的管理员可操作
class ApiViewSet(mixins.ListModelMixin, GenericViewSet):
    pagination_class = None  # 去掉 swagger 中的 limit offset 参数

    permission_classes = [RolePermission]
    action_permission = {"list": PermissionCodeEnum.MANAGE_API_WHITE_LIST.value}

    @swagger_auto_schema(
        operation_description="API 列表",
        query_serializer=QueryApiSLZ(label="api"),
        responses={status.HTTP_200_OK: ApiSLZ(label="API 信息", many=True)},
        tags=["mgmt.api"],
    )
    def list(self, request, *args, **kwargs):
        slz = QueryApiSLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)
        api_type = slz.validated_data["api_type"]
        data = WHITE_LIST_API_ENUM_MAP[api_type].info()
        return Response(data)


class AdminApiWhiteListViewSet(mixins.ListModelMixin, GenericViewSet):
    permission_classes = [RolePermission]
    action_permission = {
        "list": PermissionCodeEnum.MANAGE_API_WHITE_LIST.value,
        "create": PermissionCodeEnum.MANAGE_API_WHITE_LIST.value,
        "destroy": PermissionCodeEnum.MANAGE_API_WHITE_LIST.value,
    }

    queryset = AdminAPIAllowListConfig.objects.all()
    serializer_class = AdminApiWhiteListSLZ

    @swagger_auto_schema(
        operation_description="超级管理类 API 白名单列表",
        responses={status.HTTP_200_OK: AdminApiWhiteListSLZ(label="超级管理类 API 白名单", many=True)},
        tags=["mgmt.white_list"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(self, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="新增 - 超级管理类 API 白名单",
        request_body=AdminApiAddWhiteListSLZ(label="超级管理类 API 白名单信息"),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["mgmt.white_list"],
    )
    @view_audit_decorator(AdminApiWhiteListCreateAuditProvider)
    def create(self, request, *args, **kwargs):
        serializer = AdminApiAddWhiteListSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        username = request.user.username
        app_code = data["app_code"]
        api = data["api"]

        conf = AdminAPIAllowListConfig.objects.update_or_create(
            defaults={"updater": username}, app_code=app_code, api=api
        )

        # 写入审计上下文
        audit_context_setter(white_list=conf[0])

        return Response({}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description="删除 - 超级管理类 API 白名单",
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["mgmt.white_list"],
    )
    @view_audit_decorator(AdminApiWhiteListDeleteAuditProvider)
    def destroy(self, request, *args, **kwargs):
        conf = AdminAPIAllowListConfig.objects.filter(id=self.kwargs.get("id")).first()
        if not conf:
            return Response({})
        # delete 操作会导致 conf.id 的值被修改为 0，
        # 那么记录审计信息时就无法确定被删除的具体对象 ID，所以需要提前将 conf 的内容进行 deepcopy
        copied_conf = deepcopy(conf)
        conf.delete()

        # 写入审计上下文
        audit_context_setter(white_list=copied_conf)
        return Response({})


class AuthorizationApiWhiteListViewSet(mixins.ListModelMixin, GenericViewSet):
    permission_classes = [RolePermission]
    action_permission = {
        "list": PermissionCodeEnum.MANAGE_API_WHITE_LIST.value,
        "create": PermissionCodeEnum.MANAGE_API_WHITE_LIST.value,
        "destroy": PermissionCodeEnum.MANAGE_API_WHITE_LIST.value,
    }

    queryset = AuthAPIAllowListConfig.objects.all()
    serializer_class = AuthorizationApiWhiteListSLZ
    filterset_class = AuthorizationApiWhiteListFilter

    @swagger_auto_schema(
        operation_description="授权类 API 白名单列表",
        responses={status.HTTP_200_OK: AuthorizationApiWhiteListSchemaSLZ(label="授权类 API 白名单", many=True)},
        tags=["mgmt.white_list"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(self, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="新增 - 授权类 API 白名单",
        request_body=AuthorizationApiAddWhiteListSLZ(label="授权类 API 白名单信息"),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["mgmt.white_list"],
    )
    @view_audit_decorator(AuthorizationApiWhiteListCreateAuditProvider)
    def create(self, request, *args, **kwargs):
        serializer = AuthorizationApiAddWhiteListSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        username = request.user.username
        system_id = data["system_id"]
        object_id = data["object_id"]
        api = data["api"]

        conf = AuthAPIAllowListConfig.objects.update_or_create(
            defaults={"updater": username}, system_id=system_id, object_id=object_id, type=api
        )

        # 写入审计上下文
        audit_context_setter(white_list=conf[0])

        return Response({}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description="删除 - 授权类 API 白名单",
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["mgmt.white_list"],
    )
    @view_audit_decorator(AuthorizationApiWhiteListDeleteAuditProvider)
    def destroy(self, request, *args, **kwargs):
        conf = AuthAPIAllowListConfig.objects.filter(id=self.kwargs.get("id")).first()
        if not conf:
            return Response({})

        # delete 操作会导致 conf.id 的值被修改为 0，
        # 那么记录审计信息时就无法确定被删除的具体对象 ID，所以需要提前将 conf 的内容进行 deepcopy
        copied_conf = deepcopy(conf)
        conf.delete()

        # 写入审计上下文
        audit_context_setter(white_list=copied_conf)

        return Response({})


class ManagementApiWhiteListViewSet(mixins.ListModelMixin, GenericViewSet):
    permission_classes = [RolePermission]
    action_permission = {
        "list": PermissionCodeEnum.MANAGE_API_WHITE_LIST.value,
        "create": PermissionCodeEnum.MANAGE_API_WHITE_LIST.value,
        "destroy": PermissionCodeEnum.MANAGE_API_WHITE_LIST.value,
    }

    queryset = ManagementAPIAllowListConfig.objects.all()
    serializer_class = ManagementApiWhiteListSLZ

    @swagger_auto_schema(
        operation_description="管理类 API 白名单列表",
        responses={status.HTTP_200_OK: ManagementApiWhiteListSchemaSLZ(label="管理类 API 白名单", many=True)},
        tags=["mgmt.white_list"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(self, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="新增 - 管理类 API 白名单",
        request_body=ManagementApiAddWhiteListSLZ(label="管理类 API 白名单信息"),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["mgmt.white_list"],
    )
    @view_audit_decorator(ManagementApiWhiteListCreateAuditProvider)
    def create(self, request, *args, **kwargs):
        serializer = ManagementApiAddWhiteListSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        username = request.user.username
        system_id = data["system_id"]
        api = data["api"]

        conf = ManagementAPIAllowListConfig.objects.update_or_create(
            defaults={"updater": username}, system_id=system_id, api=api
        )

        # 写入审计上下文
        audit_context_setter(white_list=conf[0])

        return Response({}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description="删除 - 管理类 API 白名单",
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["mgmt.white_list"],
    )
    @view_audit_decorator(ManagementApiWhiteListDeleteAuditProvider)
    def destroy(self, request, *args, **kwargs):
        conf = ManagementAPIAllowListConfig.objects.filter(id=self.kwargs.get("id")).first()
        if not conf:
            return Response({})

        # delete 操作会导致 conf.id 的值被修改为 0，
        # 那么记录审计信息时就无法确定被删除的具体对象 ID，所以需要提前将 conf 的内容进行 deepcopy
        copied_conf = deepcopy(conf)
        conf.delete()

        # 写入审计上下文
        audit_context_setter(white_list=copied_conf)

        return Response({})
