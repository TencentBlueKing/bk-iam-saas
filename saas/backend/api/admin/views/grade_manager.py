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
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from backend.api.admin.constants import VerifyApiParamLocationEnum, AdminAPIEnum
from backend.api.admin.mixins import SuperManagerAPIPermissionCheckMixin
from backend.api.admin.permissions import AdminAPIPermission
from backend.api.admin.serializers import (
    SuperManagerGradeManagerBasicInfoSLZ,
    SuperManagerSourceSystemSLZ,
    SuperManagerGradeManagerUpdateSLZ,
    SuperManagerGradeManagerCreateSLZ,
)
from backend.api.authentication import ESBAuthentication
from backend.api.admin.filters import GradeManagerFilter

from backend.apps.role.audit import (
    RoleCreateAuditProvider,
    RoleUpdateAuditProvider,
)
from backend.apps.role.models import Role, RoleSource
from backend.apps.role.serializers import RoleIdSLZ
from backend.apps.role.tasks import sync_subset_manager_subject_scope
from backend.audit.audit import audit_context_setter, view_audit_decorator
from backend.biz.role import RoleBiz, RoleCheckBiz

from backend.common.lock import gen_role_upsert_lock
from backend.common.pagination import CustomPageNumberPagination
from backend.service.constants import RoleSourceType, RoleType
from backend.trans.open_management import GradeManagerTrans


class SuperManagerGradeManagerViewSet(SuperManagerAPIPermissionCheckMixin, GenericViewSet):
    """分级管理员"""

    authentication_classes = [ESBAuthentication]
    permission_classes = [AdminAPIPermission]
    admin_api_permission = {
        "create": (VerifyApiParamLocationEnum.SYSTEM_IN_BODY.value, AdminAPIEnum.GRADE_MANAGER_CREATE.value),
        "list": (VerifyApiParamLocationEnum.SYSTEM_IN_QUERY.value, AdminAPIEnum.GRADE_MANAGER_LIST.value),
        "update": (VerifyApiParamLocationEnum.ROLE_IN_PATH.value, AdminAPIEnum.GRADE_MANAGER_UPDATE.value),
    }

    lookup_field = "id"
    queryset = Role.objects.filter(type=RoleType.GRADE_MANAGER.value).order_by("-updated_time")
    pagination_class = CustomPageNumberPagination
    filterset_class = GradeManagerFilter

    biz = RoleBiz()
    role_check_biz = RoleCheckBiz()
    trans = GradeManagerTrans()

    @swagger_auto_schema(
        operation_description="创建分级管理员",
        request_body=SuperManagerGradeManagerCreateSLZ(label="创建分级管理员"),
        responses={status.HTTP_201_CREATED: RoleIdSLZ(label="分级管理员ID")},
        tags=["management.role"],
    )
    @view_audit_decorator(RoleCreateAuditProvider)
    def create(self, request, *args, **kwargs):
        """
        创建分级管理员
        """
        serializer = SuperManagerGradeManagerCreateSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # API里数据鉴权: 不可超过接入系统可管控的授权系统范围
        source_system_id = data["system"]
        auth_system_ids = list({i["system"] for i in data["authorization_scopes"]})
        self.verify_system_scope(source_system_id, auth_system_ids)

        # 检查该系统可创建的分级管理员数量是否超限
        self.role_check_biz.check_grade_manager_of_system_limit(source_system_id)

        # 兼容member格式
        data["members"] = [{"username": username} for username in data["members"]]

        # 转换为RoleInfoBean，用于创建时使用
        role_info = self.trans.to_role_info(data, source_system_id=source_system_id)

        with gen_role_upsert_lock(data["name"]):
            # 名称唯一性检查
            self.role_check_biz.check_grade_manager_unique_name(data["name"])

            with transaction.atomic():
                # 创建角色
                role = self.biz.create_grade_manager(role_info, request.user.username)

                # 记录role创建来源信息
                RoleSource.objects.create(
                    role_id=role.id, source_type=RoleSourceType.API.value, source_system_id=source_system_id
                )

        # 审计
        audit_context_setter(role=role)

        return Response({"id": role.id})

    @swagger_auto_schema(
        operation_description="更新分级管理员",
        request_body=SuperManagerGradeManagerUpdateSLZ(label="更新分级管理员"),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["super_manager.role"],
    )
    @view_audit_decorator(RoleUpdateAuditProvider)
    def update(self, request, *args, **kwargs):
        """
        更新分级管理员
        Note: 这里可授权范围和可授权人员范围均是全覆盖的，只对body里传入的字段进行更新
        """
        role = self.get_object()

        serializer = SuperManagerGradeManagerUpdateSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if "authorization_scopes" in data:
            # API里数据鉴权: 不可超过接入系统可管控的授权系统范围
            role_source = RoleSource.objects.get(source_type=RoleSourceType.API.value, role_id=role.id)
            auth_system_ids = list({i["system"] for i in data["authorization_scopes"]})
            self.verify_system_scope(role_source.source_system_id, auth_system_ids)

        # 转换为RoleInfoBean
        role_info = self.trans.to_role_info_for_update(data)

        # 数据校验
        if "name" in data:
            with gen_role_upsert_lock(data["name"]):
                # 名称唯一性检查
                self.role_check_biz.check_grade_manager_unique_name(data["name"], role.name)

                # 更新
                self.biz.update(role, role_info, request.user.username)
        else:
            # 更新
            self.biz.update(role, role_info, request.user.username)

        if role.type == RoleType.GRADE_MANAGER.value and "subject_scopes" in role_info.get_partial_fields():
            sync_subset_manager_subject_scope.delay(role.id)

        # 审计
        audit_context_setter(role=role)

        return Response({})

    @swagger_auto_schema(
        operation_description="分级管理员列表",
        query_serializer=SuperManagerSourceSystemSLZ(),
        responses={status.HTTP_200_OK: SuperManagerGradeManagerBasicInfoSLZ(many=True)},
        tags=["super_manager.role.member"],
    )
    def list(self, request, *args, **kwargs):
        serializer = SuperManagerSourceSystemSLZ(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        role_ids = list(
            RoleSource.objects.filter(
                source_system_id=data["system"],
                source_type=RoleSourceType.API.value,
            ).values_list("role_id", flat=True)
        )

        queryset = self.queryset.filter(id__in=role_ids)
        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SuperManagerGradeManagerBasicInfoSLZ(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = SuperManagerGradeManagerBasicInfoSLZ(queryset, many=True)
        return Response(serializer.data)
