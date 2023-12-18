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
from rest_framework.viewsets import GenericViewSet, mixins

from backend.account.permissions import RolePermission
from backend.apps.role.filters import RoleGroupSubjectFilter
from backend.apps.role.models import RoleGroupMember
from backend.apps.role.serializers import RoleGroupSubjectSLZ
from backend.service.constants import PermissionCodeEnum


class RoleGroupMemberViewSet(mixins.ListModelMixin, GenericViewSet):
    """
    分级管理员查看有权限的用户组成员列表
    """

    permission_classes = [RolePermission]
    action_permission = {
        "list": PermissionCodeEnum.MANAGE_ROLE_GROUP_MEMBER.value,
    }

    queryset = RoleGroupMember.objects.all()
    serializer_class = RoleGroupSubjectSLZ
    filterset_class = RoleGroupSubjectFilter

    def get_queryset(self):
        return (
            RoleGroupMember.objects.filter(role_id=self.request.role.id)
            .values("subject_type", "subject_id")
            .distinct()
            .order_by("subject_type", "subject_id")
        )

    @swagger_auto_schema(
        operation_description="分级管理员查看有权限的用户组成员列表",
        responses={status.HTTP_200_OK: RoleGroupSubjectSLZ(label="分级管理员用户组成员列表", many=True)},
        tags=["role"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
