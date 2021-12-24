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
from drf_yasg.openapi import Response as yasg_response
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, mixins

from backend.account.permissions import RolePermission
from backend.api.management.models import ManagementAPIAllowListConfig
from backend.apps.mgmt.serializers import ManagementApiAddWhiteListSLZ, ManagementApiSLZ, ManagementApiWhiteListSLZ
from backend.common.swagger import ResponseSwaggerAutoSchema
from backend.service.constants import PermissionCodeEnum
from backend.service.mgmt import WhiteListService


class ManagementApiViewSet(mixins.ListModelMixin, GenericViewSet):

    paginator = None  # 去掉swagger中的limit offset参数

    permission_classes = [RolePermission]
    action_permission = {"list": PermissionCodeEnum.MANAGE_API_WHITE_LIST.value}
    white_list_svc = WhiteListService()

    @swagger_auto_schema(
        operation_description="管理类API列表",
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: ManagementApiSLZ(label="管理类API", many=True)},
        tags=["mgmt.white_list"],
    )
    def list(self, request, *args, **kwargs):
        data = self.white_list_svc.list_management_api()
        return Response(data)


class ManagementApiWhiteListViewSet(mixins.ListModelMixin, GenericViewSet):

    permission_classes = [RolePermission]
    action_permission = {
        "list": PermissionCodeEnum.MANAGE_API_WHITE_LIST.value,
        "create": PermissionCodeEnum.MANAGE_API_WHITE_LIST.value,
        "destroy": PermissionCodeEnum.MANAGE_API_WHITE_LIST.value,
    }

    white_list_svc = WhiteListService()
    queryset = ManagementAPIAllowListConfig.objects.all()
    serializer_class = ManagementApiWhiteListSLZ

    @swagger_auto_schema(
        operation_description="管理类API白名单列表",
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: ManagementApiWhiteListSLZ(label="管理类API白名单", many=True)},
        tags=["mgmt.white_list"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(self, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="新增-管理类API白名单",
        request_body=ManagementApiAddWhiteListSLZ(label="管理类API白名单信息"),
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: yasg_response({})},
        tags=["mgmt.white_list"],
    )
    def create(self, request, *args, **kwargs):
        serializer = ManagementApiAddWhiteListSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        username = request.user.username
        system_id = data["system_id"]
        api = data["api"]

        self.white_list_svc.add_management_api(username=username, system_id=system_id, api=api)

        return Response({}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description="删除-管理类API白名单",
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: yasg_response({})},
        tags=["mgmt.white_list"],
    )
    def destroy(self, request, *args, **kwargs):
        self.white_list_svc.delete_management_api_by_id(kwargs["id"])

        return Response({})
