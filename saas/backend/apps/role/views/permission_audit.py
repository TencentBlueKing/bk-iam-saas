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
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from backend.account.permissions import RolePermission
from backend.apps.role.serializers import AuthorizedSubjectsSLZ, QueryAuthorizedSubjectsSLZ
from backend.biz.permission_audit import QueryAuthorizedSubjects
from backend.service.constants import PermissionCodeEnum
from backend.util.time import format_localtime


class QueryAuthorizedSubjectsViewSet(GenericViewSet):

    permission_classes = [RolePermission]
    method_permission = {
        "post": PermissionCodeEnum.VIEW_AUTHORIZED_SUBJECTS.value,
        "export": PermissionCodeEnum.VIEW_AUTHORIZED_SUBJECTS.value,
    }

    @swagger_auto_schema(
        operation_description="查询-权限所属成员列表",
        request_body=QueryAuthorizedSubjectsSLZ(label="权限信息"),
        responses={status.HTTP_200_OK: AuthorizedSubjectsSLZ(label="拥有权限的对象", many=True)},
        tags=["role"],
    )
    def post(self, request, *args, **kwargs):
        serializer = QueryAuthorizedSubjectsSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        subjects = QueryAuthorizedSubjects(data).query_by_permission_type()
        return Response(subjects)

    @swagger_auto_schema(
        operation_description="导出-权限所属成员列表",
        request_body=QueryAuthorizedSubjectsSLZ(label="权限信息"),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["role"],
    )
    def export(self, request, *args, **kwargs):
        serializer = QueryAuthorizedSubjectsSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        exported_file_name = f'{data["system_id"]}_{format_localtime()}'
        response = QueryAuthorizedSubjects(data).export(exported_file_name)

        return response
