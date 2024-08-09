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

from backend.api.admin.constants import AdminAPIEnum
from backend.api.admin.permissions import AdminAPIPermission
from backend.api.admin.serializers import (
    AdminTemplateCreateSLZ,
    AdminTemplateIdSLZ,
    AdminTemplateListSchemaSLZ,
    AdminTemplateListSLZ,
)
from backend.api.authentication import ESBAuthentication
from backend.apps.role.models import Role
from backend.apps.template.audit import TemplateCreateAuditProvider
from backend.apps.template.views import TemplateQueryMixin
from backend.audit.audit import audit_context_setter, view_audit_decorator
from backend.biz.role import RoleAuthorizationScopeChecker, RoleListQuery
from backend.biz.template import TemplateBiz, TemplateCheckBiz, TemplateCreateBean
from backend.common.lock import gen_template_upsert_lock
from backend.service.constants import RoleType


class AdminTemplateViewSet(TemplateQueryMixin, GenericViewSet):
    """模板"""

    authentication_classes = [ESBAuthentication]
    permission_classes = [AdminAPIPermission]

    admin_api_permission = {
        "list": AdminAPIEnum.TEMPLATE_LIST.value,
        "create": AdminAPIEnum.TEMPLATE_CREATE.value,
    }

    template_biz = TemplateBiz()
    template_check_biz = TemplateCheckBiz()

    @swagger_auto_schema(
        operation_description="模板列表",
        responses={status.HTTP_200_OK: AdminTemplateListSchemaSLZ(label="模板", many=True)},
        tags=["admin.template"],
    )
    def list(self, request, *args, **kwargs):
        role = Role.objects.get(type=RoleType.SUPER_MANAGER.value)
        queryset = RoleListQuery(role, request.user).query_template()

        # 查询 role 的 system-actions set
        role_system_actions = RoleListQuery(role).get_scope_system_actions()

        # 强制分页
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)

        if page is None:
            return Response(
                {
                    "detail": "Pagination is required, but no valid page parameters were provided."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = AdminTemplateListSLZ(page, many=True,
                                          role_system_actions=role_system_actions)
        return paginator.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_description="创建模板",
        request_body=AdminTemplateCreateSLZ(label="模板"),
        responses={status.HTTP_201_CREATED: AdminTemplateIdSLZ(label="模板ID")},
        tags=["admin.template"],
    )
    @view_audit_decorator(TemplateCreateAuditProvider)
    def create(self, request, *args, **kwargs):
        """
        创建模板
        """
        serializer = AdminTemplateCreateSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = request.user.username
        data = serializer.validated_data
        role = Role.objects.get(type=RoleType.SUPER_MANAGER.value)

        # 检查模板的授权是否满足管理员的授权范围
        scope_checker = RoleAuthorizationScopeChecker(role)
        scope_checker.check_actions(data["system_id"], data["action_ids"])

        with gen_template_upsert_lock(role.id, data["name"]):
            # 检查权限模板是否在角色内唯一
            self.template_check_biz.check_role_template_name_exists(role.id, data["name"])

            template = self.template_biz.create(role.id, TemplateCreateBean.parse_obj(data), user_id)

        audit_context_setter(template=template)

        return Response({"id": template.id}, status=status.HTTP_201_CREATED)
