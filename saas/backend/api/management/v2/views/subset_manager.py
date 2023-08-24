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
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from backend.api.authentication import ESBAuthentication
from backend.api.management.constants import ManagementAPIEnum, VerifyApiParamLocationEnum
from backend.api.management.v2.filters import GradeManagerFilter
from backend.api.management.v2.permissions import ManagementAPIPermission
from backend.api.management.v2.serializers import (
    ManagementGradeManagerBasicInfoSLZ,
    ManagementGradeManagerBasicSLZ,
    ManagementGradeMangerDetailSLZ,
    ManagementSubsetMangerCreateSLZ,
)
from backend.apps.role.audit import RoleCreateAuditProvider, RoleDeleteAuditProvider, RoleUpdateAuditProvider
from backend.apps.role.models import Role, RoleRelation, RoleSource
from backend.audit.audit import audit_context_setter, view_audit_decorator
from backend.audit.constants import AuditSourceType
from backend.biz.group import GroupBiz
from backend.biz.helper import RoleDeleteHelper
from backend.biz.role import RoleBiz, RoleCheckBiz
from backend.service.constants import GroupSaaSAttributeEnum, RoleSourceType, RoleType
from backend.trans.open_management import GradeManagerTrans


class ManagementSubsetManagerCreateListViewSet(GenericViewSet):
    """二级管理员创建"""

    authentication_classes = [ESBAuthentication]
    permission_classes = [ManagementAPIPermission]
    management_api_permission = {
        "create": (
            VerifyApiParamLocationEnum.ROLE_IN_PATH.value,
            ManagementAPIEnum.V2_SUBSET_MANAGER_CREATE.value,
        ),
        "list": (
            VerifyApiParamLocationEnum.ROLE_IN_PATH.value,
            ManagementAPIEnum.V2_SUBSET_MANAGER_LIST.value,
        ),
    }

    lookup_field = "id"
    queryset = Role.objects.filter(type=RoleType.SUBSET_MANAGER.value).order_by("-updated_time")
    filterset_class = GradeManagerFilter

    biz = RoleBiz()
    group_biz = GroupBiz()
    role_check_biz = RoleCheckBiz()
    trans = GradeManagerTrans()

    @swagger_auto_schema(
        operation_description="二级管理员创建",
        request_body=ManagementSubsetMangerCreateSLZ(label="二级管理员创建"),
        responses={status.HTTP_200_OK: ManagementGradeManagerBasicSLZ(label="ID")},
        tags=["management.subset_manager"],
    )
    @view_audit_decorator(RoleCreateAuditProvider)
    def create(self, request, *args, **kwargs):
        """
        二级管理员创建
        """
        serializer = ManagementSubsetMangerCreateSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        grade_manager = get_object_or_404(Role, type=RoleType.GRADE_MANAGER.value, id=kwargs["id"])

        # 名称唯一性检查, 检查在分级管理员下唯一
        self.role_check_biz.check_subset_manager_unique_name(grade_manager, data["name"])

        source_system_id = kwargs["system_id"]

        # 兼容member格式
        data["members"] = [{"username": username} for username in data["members"]]

        # 结构转换
        info = self.trans.to_role_info(data, _type=RoleType.SUBSET_MANAGER.value, source_system_id=source_system_id)

        # 检查授权范围
        self.role_check_biz.check_subset_manager_auth_scope(grade_manager, info.authorization_scopes)

        # 如果配置使用上级的人员选择范围直接使用上级的相关信息覆盖
        if not info.inherit_subject_scope:
            # 检查人员范围
            self.role_check_biz.check_subset_manager_subject_scope(grade_manager, info.subject_scopes)
        else:
            subject_scopes = self.biz.list_subject_scope(grade_manager.id)
            info.subject_scopes = subject_scopes

        with transaction.atomic():
            # 创建子集管理员, 并创建分级管理员与子集管理员的关系
            role = self.biz.create_subset_manager(grade_manager, info, request.user.username)

            # 记录role创建来源信息
            RoleSource.objects.create(
                role_id=role.id, source_type=RoleSourceType.API.value, source_system_id=source_system_id
            )

        # 创建同步权限用户组
        if info.sync_perm:
            self.group_biz.create_sync_perm_group_by_role(
                role,
                request.user.username,
                group_name=data["group_name"],
                attrs={
                    GroupSaaSAttributeEnum.SOURCE_TYPE.value: AuditSourceType.OPENAPI.value,
                    GroupSaaSAttributeEnum.SOURCE_FROM_ROLE.value: True,
                },
            )

        audit_context_setter(role=role)

        return Response({"id": role.id})

    @swagger_auto_schema(
        operation_description="二级管理员列表",
        responses={status.HTTP_200_OK: ManagementGradeManagerBasicInfoSLZ(many=True)},
        tags=["management.subset_manager"],
    )
    def list(self, request, *args, **kwargs):
        role_ids = RoleRelation.objects.list_sub_id(kwargs["id"])

        queryset = self.queryset.filter(id__in=role_ids)
        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ManagementGradeManagerBasicInfoSLZ(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ManagementGradeManagerBasicInfoSLZ(queryset, many=True)
        return Response(serializer.data)


class ManagementSubsetManagerViewSet(GenericViewSet):
    """子集管理员详情"""

    authentication_classes = [ESBAuthentication]
    permission_classes = [ManagementAPIPermission]
    management_api_permission = {
        "retrieve": (VerifyApiParamLocationEnum.ROLE_IN_PATH.value, ManagementAPIEnum.V2_SUBSET_MANAGER_DETAIL.value),
        "update": (VerifyApiParamLocationEnum.ROLE_IN_PATH.value, ManagementAPIEnum.V2_SUBSET_MANAGER_UPDATE.value),
        "destroy": (VerifyApiParamLocationEnum.ROLE_IN_PATH.value, ManagementAPIEnum.V2_SUBSET_MANAGER_DELETE.value),
    }

    lookup_field = "id"
    queryset = Role.objects.filter(type=RoleType.SUBSET_MANAGER.value)

    biz = RoleBiz()
    group_biz = GroupBiz()
    role_check_biz = RoleCheckBiz()
    trans = GradeManagerTrans()

    @swagger_auto_schema(
        operation_description="子集管理员详情",
        responses={status.HTTP_200_OK: ManagementGradeMangerDetailSLZ(label="子集管理员详情")},
        filter_inspectors=[],
        paginator_inspectors=[],
        tags=["management.subset_manager"],
    )
    def retrieve(self, request, *args, **kwargs):
        role = self.get_object()
        serializer = ManagementGradeMangerDetailSLZ(instance=role)
        data = serializer.data
        return Response(data)

    @swagger_auto_schema(
        operation_description="更新二级管理员",
        request_body=ManagementSubsetMangerCreateSLZ(label="更新二级管理员"),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["management.subset_manager"],
    )
    @view_audit_decorator(RoleUpdateAuditProvider)
    def update(self, request, *args, **kwargs):
        """
        更新二级管理员
        """
        role = self.get_object()

        serializer = ManagementSubsetMangerCreateSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # 1. 查询二级管理员的上级分级管理员
        parent_role_id = RoleRelation.objects.get_parent_role_id(role.id)
        grade_manager = Role.objects.get(id=parent_role_id)

        # 名称唯一性检查
        self.role_check_biz.check_subset_manager_unique_name(grade_manager, data["name"], role.name)
        # 检查成员数量是否满足限制
        self.role_check_biz.check_member_count(role.id, len(data["members"]))

        # 兼容member格式
        data["members"] = [{"username": username} for username in data["members"]]

        # 转换为RoleInfoBean
        role_info = self.trans.to_role_info(data, source_system_id=kwargs["system_id"])

        # 检查授权范围
        self.role_check_biz.check_subset_manager_auth_scope(grade_manager, role_info.authorization_scopes)

        # 如果配置使用上级的人员选择范围直接使用上级的相关信息覆盖
        if not role_info.inherit_subject_scope:
            # 检查人员范围
            self.role_check_biz.check_subset_manager_subject_scope(grade_manager, role_info.subject_scopes)
        else:
            subject_scopes = self.biz.list_subject_scope(grade_manager.id)
            role_info.subject_scopes = subject_scopes

        self.biz.update(role, role_info, request.user.username)

        # 更新同步权限用户组信息
        self.group_biz.update_sync_perm_group_by_role(
            self.get_object(), request.user.username, sync_members=True, sync_prem=True, group_name=data["group_name"]
        )

        audit_context_setter(role=role)

        return Response({})

    @swagger_auto_schema(
        operation_description="删除子集管理员",
        responses={status.HTTP_200_OK: serializers.Serializer()},
        filter_inspectors=[],
        paginator_inspectors=[],
        tags=["management.subset_manager"],
    )
    @view_audit_decorator(RoleDeleteAuditProvider)
    def destroy(self, request, *args, **kwargs):
        role = self.get_object()
        RoleDeleteHelper(role.id).delete()

        # 审计
        audit_context_setter(role=role)

        return Response({})
