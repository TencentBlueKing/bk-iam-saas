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
import logging

from django.http import StreamingHttpResponse
from drf_yasg.openapi import Response as yasg_response
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from backend.biz.permission_audit import SubjectsWithPermissionBiz
from backend.common.swagger import ResponseSwaggerAutoSchema

from ..serializers import PermissionManageSLZ, SubjectsWithPermissionSLZ

logger = logging.getLogger("app")


class SubjectsWithPermissionViewSet(GenericViewSet):
    biz = SubjectsWithPermissionBiz

    @swagger_auto_schema(
        operation_description="查询-权限所属成员列表",
        request_body=PermissionManageSLZ(label="权限信息"),
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: SubjectsWithPermissionSLZ(label="拥有权限的对象", many=True)},
        tags=["role"],
    )
    def list(self, request, *args, **kwargs):

        serializer = PermissionManageSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        subjects = self.biz(data).query_subjects_by_resource()
        return Response(subjects)

    @swagger_auto_schema(
        operation_description="导出-权限所属成员列表",
        request_body=PermissionManageSLZ(label="权限信息"),
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: yasg_response({})},
        tags=["role"],
    )
    def export(self, request, *args, **kwargs):

        serializer = PermissionManageSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        exported_file_name = "permission_members"
        output = self.biz(data).export()

        response = StreamingHttpResponse(output)
        response["Content-Type"] = "application/octet-stream"
        response["Content-Disposition"] = f'attachment;filename="{exported_file_name}.xlsx"'

        return response
