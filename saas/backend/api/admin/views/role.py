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

from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from backend.api.admin.constants import AdminAPIEnum
from backend.api.admin.permissions import AdminAPIPermission
from backend.api.admin.serializers import SuperManagerMemberSLZ, SystemManagerWithMembersSLZ
from backend.api.authentication import ESBAuthentication
from backend.apps.role.models import Role
from backend.mixins import TenantMixin
from backend.service.constants import RoleType


class AdminSuperManagerMemberViewSet(TenantMixin, GenericViewSet):
    authentication_classes = [ESBAuthentication]
    permission_classes = [AdminAPIPermission]
    admin_api_permission = {"retrieve": AdminAPIEnum.ROLE_SUPER_MANAGER_MEMBER_LIST.value}

    pagination_class = None  # 去掉 swagger 中的 limit offset 参数

    @swagger_auto_schema(
        operation_description="超级管理员成员列表",
        responses={status.HTTP_200_OK: SuperManagerMemberSLZ(label="超级管理员成员", many=True)},
        tags=["admin.role"],
    )
    def retrieve(self, request, *args, **kwargs):
        role = Role.objects.get(type=RoleType.SUPER_MANAGER.value, tenant_id=self.tenant_id)
        enabled_users = set(role.system_permission_enabled_content.enabled_users)
        data = [{"username": i, "has_system_permission": i in enabled_users} for i in role.members]
        return Response(data)


class AdminSystemManagerMemberViewSet(TenantMixin, GenericViewSet):
    authentication_classes = [ESBAuthentication]
    permission_classes = [AdminAPIPermission]
    admin_api_permission = {"retrieve": AdminAPIEnum.ROLE_SYSTEM_MANAGER_MEMBER_LIST.value}

    pagination_class = None  # 去掉 swagger 中的 limit offset 参数

    @swagger_auto_schema(
        operation_description="系统管理员成员列表",
        responses={status.HTTP_200_OK: SystemManagerWithMembersSLZ(label="系统管理员成员")},
        tags=["admin.role"],
    )
    def retrieve(self, request, *args, **kwargs):
        system_id = kwargs["system_id"]

        # TODO: check system_id exists

        role = Role.objects.filter(
            tenant_id=self.tenant_id, type=RoleType.SYSTEM_MANAGER.value, code=system_id
        ).first()

        serializer = SystemManagerWithMembersSLZ(instance=role)
        data = serializer.data
        return Response(data)
