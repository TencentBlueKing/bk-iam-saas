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
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from backend.api.authentication import ESBAuthentication
from backend.api.management.constants import ManagementAPIEnum, VerifyAPIParamLocationEnum
from backend.api.management.v2.permissions import ManagementAPIPermission
from backend.api.management.v2.serializers import ManagementGradeManagerBasicSLZ, ManagementSubsetMangerCreateSLZ
from backend.apps.role.audit import RoleCreateAuditProvider
from backend.apps.role.models import Role, RoleSource
from backend.audit.audit import audit_context_setter, view_audit_decorator
from backend.biz.role import RoleBiz, RoleCheckBiz
from backend.service.constants import RoleSourceTypeEnum, RoleType
from backend.trans.role import RoleTrans


class ManagementSubsetManagerViewSet(GenericViewSet):
    """二级管理员"""

    authentication_classes = [ESBAuthentication]
    permission_classes = [ManagementAPIPermission]
    management_api_permission = {
        "create": (
            VerifyAPIParamLocationEnum.ROLE_IN_PATH.value,
            ManagementAPIEnum.V2_SUBSET_MANAGER_CREATE.value,
        ),
    }

    lookup_field = "id"
    biz = RoleBiz()
    role_check_biz = RoleCheckBiz()
    role_trans = RoleTrans()

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
        info = self.role_trans.from_role_data(
            data, _type=RoleType.SUBSET_MANAGER.value, source_system_id=source_system_id
        )

        # 检查授权范围
        self.role_check_biz.check_subset_manager_auth_scope(grade_manager, info.authorization_scopes)

        # 如果配置使用上级的人员选择范围直接使用上级的相关信息覆盖
        if not info.inherit_subject_scope:
            # 检查人员范围
            self.role_check_biz.check_subset_manager_subject_scope(grade_manager, info.subject_scopes)
        else:
            subject_scopes = self.biz.list_subject_scope(grade_manager.id)
            info.subject_scopes = subject_scopes

        # 创建子集管理员, 并创建分级管理员与子集管理员的关系
        role = self.biz.create_subset_manager(grade_manager, info, "admin")

        with transaction.atomic():
            # 创建角色
            role = self.biz.create_subset_manager(grade_manager, info, "admin")

            # 记录role创建来源信息
            RoleSource.objects.create(
                role_id=role.id, source_type=RoleSourceTypeEnum.API.value, source_system_id=source_system_id
            )

        audit_context_setter(role=role)

        return Response({"id": role.id})
