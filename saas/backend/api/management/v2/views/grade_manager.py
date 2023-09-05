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

from backend.api.authentication import ESBAuthentication
from backend.api.management.constants import ManagementAPIEnum, VerifyApiParamLocationEnum
from backend.api.management.mixins import ManagementAPIPermissionCheckMixin
from backend.api.management.v2.permissions import ManagementAPIPermission
from backend.api.management.v2.serializers import ManagementGradeManagerCreateSLZ, ManagementGradeMangerDetailSLZ
from backend.apps.role.audit import RoleCreateAuditProvider, RoleDeleteAuditProvider, RoleUpdateAuditProvider
from backend.apps.role.models import Role, RoleSource
from backend.apps.role.serializers import RoleIdSLZ
from backend.apps.role.tasks import sync_subset_manager_subject_scope
from backend.audit.audit import audit_context_setter, view_audit_decorator
from backend.audit.constants import AuditSourceType
from backend.biz.group import GroupBiz
from backend.biz.helper import RoleDeleteHelper
from backend.biz.role import RoleBiz, RoleCheckBiz
from backend.common.lock import gen_role_upsert_lock
from backend.service.constants import GroupSaaSAttributeEnum, RoleSourceType, RoleType
from backend.trans.open_management import GradeManagerTrans


class ManagementGradeManagerViewSet(ManagementAPIPermissionCheckMixin, GenericViewSet):
    """分级管理员"""

    authentication_classes = [ESBAuthentication]
    permission_classes = [ManagementAPIPermission]
    management_api_permission = {
        "create": (VerifyApiParamLocationEnum.SYSTEM_IN_BODY.value, ManagementAPIEnum.V2_GRADE_MANAGER_CREATE.value),
        "update": (VerifyApiParamLocationEnum.ROLE_IN_PATH.value, ManagementAPIEnum.V2_GRADE_MANAGER_UPDATE.value),
        "retrieve": (VerifyApiParamLocationEnum.ROLE_IN_PATH.value, ManagementAPIEnum.V2_GRADE_MANAGER_DETAIL.value),
        "destroy": (VerifyApiParamLocationEnum.ROLE_IN_PATH.value, ManagementAPIEnum.V2_GRADE_MANAGER_DELETE.value),
    }

    lookup_field = "id"
    queryset = Role.objects.filter(type=RoleType.GRADE_MANAGER.value).order_by("-updated_time")

    biz = RoleBiz()
    group_biz = GroupBiz()
    role_check_biz = RoleCheckBiz()
    trans = GradeManagerTrans()

    @swagger_auto_schema(
        operation_description="创建分级管理员",
        request_body=ManagementGradeManagerCreateSLZ(label="创建分级管理员"),
        responses={status.HTTP_201_CREATED: RoleIdSLZ(label="分级管理员ID")},
        tags=["management.role"],
    )
    @view_audit_decorator(RoleCreateAuditProvider)
    def create(self, request, *args, **kwargs):
        """
        创建分级管理员
        """
        serializer = ManagementGradeManagerCreateSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # API里数据鉴权: 不可超过接入系统可管控的授权系统范围
        source_system_id = kwargs["system_id"]
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

        # 创建同步权限用户组
        if role_info.sync_perm:
            self.group_biz.create_sync_perm_group_by_role(
                role,
                request.user.username,
                group_name=data["group_name"],
                attrs={
                    GroupSaaSAttributeEnum.SOURCE_TYPE.value: AuditSourceType.OPENAPI.value,
                    GroupSaaSAttributeEnum.SOURCE_FROM_ROLE.value: True,
                },
            )

        # 审计
        audit_context_setter(role=role)

        return Response({"id": role.id})

    @swagger_auto_schema(
        operation_description="更新分级管理员",
        request_body=ManagementGradeManagerCreateSLZ(label="更新分级管理员"),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["management.role"],
    )
    @view_audit_decorator(RoleUpdateAuditProvider)
    def update(self, request, *args, **kwargs):
        """
        更新分级管理员
        """
        role = self.get_object()

        serializer = ManagementGradeManagerCreateSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # 数据校验

        # API里数据鉴权: 不可超过接入系统可管控的授权系统范围
        role_source = RoleSource.objects.get(source_type=RoleSourceType.API.value, role_id=role.id)
        auth_system_ids = list({i["system"] for i in data["authorization_scopes"]})
        self.verify_system_scope(role_source.source_system_id, auth_system_ids)

        # 兼容member格式
        data["members"] = [{"username": username} for username in data["members"]]

        # 转换为RoleInfoBean
        role_info = self.trans.to_role_info(data, source_system_id=kwargs["system_id"])

        with gen_role_upsert_lock(data["name"]):
            # 名称唯一性检查
            self.role_check_biz.check_grade_manager_unique_name(data["name"], role.name)

            # 更新
            self.biz.update(role, role_info, request.user.username)

        if role.type == RoleType.GRADE_MANAGER.value and "subject_scopes" in role_info.get_partial_fields():
            sync_subset_manager_subject_scope.delay(role.id)

        # 更新同步权限用户组信息
        self.group_biz.update_sync_perm_group_by_role(
            self.get_object(), request.user.username, sync_members=True, sync_prem=True, group_name=data["group_name"]
        )

        # 审计
        audit_context_setter(role=role)

        return Response({})

    @swagger_auto_schema(
        operation_description="分级管理员详情",
        responses={status.HTTP_200_OK: ManagementGradeMangerDetailSLZ(label="分级管理员详情")},
        filter_inspectors=[],
        paginator_inspectors=[],
        tags=["management.role"],
    )
    def retrieve(self, request, *args, **kwargs):
        role = self.get_object()
        serializer = ManagementGradeMangerDetailSLZ(instance=role)
        data = serializer.data
        return Response(data)

    @swagger_auto_schema(
        operation_description="删除分级管理员",
        responses={status.HTTP_200_OK: serializers.Serializer()},
        filter_inspectors=[],
        paginator_inspectors=[],
        tags=["management.role"],
    )
    @view_audit_decorator(RoleDeleteAuditProvider)
    def destroy(self, request, *args, **kwargs):
        role = self.get_object()
        RoleDeleteHelper(role.id).delete()

        # 审计
        audit_context_setter(role=role)

        return Response({})
