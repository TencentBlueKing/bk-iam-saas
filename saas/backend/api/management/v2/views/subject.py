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

from backend.api.authentication import ESBAuthentication
from backend.api.management.constants import ManagementAPIEnum, VerifyAPIParamLocationEnum
from backend.api.management.v2.permissions import ManagementAPIPermission
from backend.api.management.v2.serializers import ManagementSubjectGroupBelongSLZ
from backend.biz.group import GroupBiz
from backend.common.error_codes import error_codes
from backend.service.models import Subject


class ManagementUserGroupBelongViewSet(GenericViewSet):
    """用户与用户组归属"""

    authentication_classes = [ESBAuthentication]
    permission_classes = [ManagementAPIPermission]
    management_api_permission = {
        "check": (
            VerifyAPIParamLocationEnum.GROUP_IDS_IN_QUERY.value,
            ManagementAPIEnum.V2_USER_GROUPS_BELONG_CHECK.value,
        ),
    }

    pagination_class = None

    group_biz = GroupBiz()

    @swagger_auto_schema(
        operation_description="用户与用户组归属判断",
        query_serializer=ManagementSubjectGroupBelongSLZ("用户组所属判断"),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["management.user.group.belong"],
    )
    def check(self, request, *args, **kwargs):
        serializer = ManagementSubjectGroupBelongSLZ(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            group_ids_str = data["group_ids"]
            group_ids = list(map(int, group_ids_str.split(",")))
        except ValueError:
            raise error_codes.INVALID_ARGS.format(f"group_ids: {group_ids_str} valid error")

        username = kwargs["user_id"]

        group_belongs = self.group_biz.check_subject_groups_belong(
            Subject.from_username(username),
            group_ids,
        )

        return Response(group_belongs)


class ManagementDepartmentGroupBelongViewSet(GenericViewSet):
    """部门与用户组归属"""

    authentication_classes = [ESBAuthentication]
    permission_classes = [ManagementAPIPermission]
    management_api_permission = {
        "check": (
            VerifyAPIParamLocationEnum.GROUP_IDS_IN_QUERY.value,
            ManagementAPIEnum.V2_DEPARTMENT_GROUPS_BELONG_CHECK.value,
        ),
    }

    pagination_class = None

    group_biz = GroupBiz()

    @swagger_auto_schema(
        operation_description="部门与用户组归属判断",
        query_serializer=ManagementSubjectGroupBelongSLZ("用户组所属判断"),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["management.department.group.belong"],
    )
    def check(self, request, *args, **kwargs):
        serializer = ManagementSubjectGroupBelongSLZ(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        group_ids = list(map(int, data["group_ids"].split(",")))
        department_id = kwargs["id"]

        group_belongs = self.group_biz.check_subject_groups_belong(
            Subject.from_department_id(department_id),
            group_ids,
        )

        return Response(group_belongs)
