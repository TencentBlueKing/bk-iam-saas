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
from copy import deepcopy

from drf_yasg.openapi import Response as yasg_response
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, mixins

from backend.account.permissions import RolePermission
from backend.api.admin.models import AdminAPIAllowListConfig
from backend.apps.mgmt.audit import AdminApiWhiteListCreateAuditProvider, AdminApiWhiteListDeleteAuditProvider
from backend.apps.mgmt.constants import WHITE_LIST_API_ENUM_MAP
from backend.apps.mgmt.serializers import AdminApiAddWhiteListSLZ, AdminApiWhiteListSLZ, ApiSLZ, QueryApiSLZ
from backend.audit.audit import audit_context_setter, view_audit_decorator
from backend.common.swagger import ResponseSwaggerAutoSchema
from backend.service.constants import PermissionCodeEnum


class ApiViewSet(mixins.ListModelMixin, GenericViewSet):
    paginator = None  # 去掉swagger中的limit offset参数

    permission_classes = [RolePermission]
    action_permission = {"list": PermissionCodeEnum.MANAGE_API_WHITE_LIST.value}

    @swagger_auto_schema(
        operation_description="API列表",
        query_serializer=QueryApiSLZ(label="api"),
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: ApiSLZ(label="API信息", many=True)},
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
        operation_description="管理类API白名单列表",
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: AdminApiWhiteListSLZ(label="超级管理类API白名单", many=True)},
        tags=["mgmt.white_list"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(self, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="新增-超级管理类API白名单",
        request_body=AdminApiAddWhiteListSLZ(label="管理类API白名单信息"),
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: yasg_response({})},
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
            defaults={"updater": username}, creator=username, app_code=app_code, api=api
        )

        # 写入审计上下文
        audit_context_setter(white_list=conf[0])

        return Response({}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description="删除-超级管理类API白名单",
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: yasg_response({})},
        tags=["mgmt.white_list"],
    )
    @view_audit_decorator(AdminApiWhiteListDeleteAuditProvider)
    def destroy(self, request, *args, **kwargs):
        conf = AdminAPIAllowListConfig.objects.filter(id=self.kwargs.get("id")).first()
        if not conf:
            return Response({})

        copied_conf = deepcopy(conf)  # 生成审计信息来源
        conf.delete()

        # 写入审计上下文
        audit_context_setter(white_list=copied_conf)
        return Response({})
