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
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from backend.api.authentication import ESBAuthentication
from backend.api.management.constants import ManagementAPIEnum, VerifyApiParamLocationEnum
from backend.api.management.v1.permissions import ManagementAPIPermission
from backend.api.management.v1.serializers import (
    ManagementGradeManagerBasicSLZ,
    ManagementGroupBasicSLZ,
    ManagementUserGradeManagerQuerySLZ,
    ManagementUserQuerySLZ,
)
from backend.apps.group.models import Group
from backend.apps.role.models import Role, RoleRelatedObject
from backend.biz.group import GroupBiz
from backend.biz.role import RoleBiz
from backend.service.constants import RoleRelatedObjectType, RoleType
from backend.service.models import Subject


class ManagementUserGradeManagerViewSet(GenericViewSet):
    """用户加入的分级管理员"""

    pagination_class = None  # 去掉swagger中的limit offset参数

    authentication_classes = [ESBAuthentication]
    permission_classes = [ManagementAPIPermission]
    management_api_permission = {
        "list": (VerifyApiParamLocationEnum.SYSTEM_IN_QUERY.value, ManagementAPIEnum.USER_ROLE_LIST.value),
    }

    role_biz = RoleBiz()

    @swagger_auto_schema(
        operation_description="用户加入的分级管理员列表",
        query_serializer=ManagementUserGradeManagerQuerySLZ(),
        responses={status.HTTP_200_OK: ManagementGradeManagerBasicSLZ(label="分级管理员", many=True)},
        tags=["management.user.role"],
    )
    def list(self, request, *args, **kwargs):
        serializer = ManagementUserGradeManagerQuerySLZ(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        roles = self.role_biz.list_user_role_for_system(data["user_id"], data["system"])

        resp_slz = ManagementGradeManagerBasicSLZ(roles, many=True)
        return Response(resp_slz.data)


class ManagementUserGradeManagerGroupViewSet(GenericViewSet):
    """用户在某个分级管理员下的用户组"""

    pagination_class = None  # 去掉swagger中的limit offset参数

    authentication_classes = [ESBAuthentication]
    permission_classes = [ManagementAPIPermission]
    management_api_permission = {
        "list": (VerifyApiParamLocationEnum.ROLE_IN_PATH.value, ManagementAPIEnum.USER_ROLE_GROUP_LIST.value),
    }

    lookup_field = "id"
    queryset = Role.objects.filter(type=RoleType.GRADE_MANAGER.value).order_by("-updated_time")

    group_biz = GroupBiz()

    @swagger_auto_schema(
        operation_description="用户在某个分级管理员下加入的用户组列表",
        query_serializer=ManagementUserQuerySLZ(),
        responses={status.HTTP_200_OK: ManagementGroupBasicSLZ(label="用户组", many=True)},
        tags=["management.user.role.group"],
    )
    def list(self, request, *args, **kwargs):
        serializer = ManagementUserQuerySLZ(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        role = self.get_object()

        # 查询用户加入的用户组
        # NOTE: 可能会有性能问题, 用户的组过多
        relations = self.group_biz.list_all_subject_group(Subject.from_username(data["user_id"]))

        user_group_ids = [one.id for one in relations]
        # 查询分级管理员下的用户组列表
        role_group_ids = RoleRelatedObject.objects.list_role_object_ids(role.id, RoleRelatedObjectType.GROUP.value)
        # 取交集，即为用户在某个分级管理员下的用户组ID列表
        group_ids = set(user_group_ids) & set(role_group_ids)
        groups = Group.objects.filter(id__in=group_ids)

        resp_slz = ManagementGroupBasicSLZ(groups, many=True)
        return Response(resp_slz.data)
