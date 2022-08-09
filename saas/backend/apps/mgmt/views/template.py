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
import logging

from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.response import Response

from backend.account.permissions import RolePermission
from backend.apps.role.models import AnonymousRole
from backend.apps.template import tasks  # noqa
from backend.apps.template.audit import TemplateUpdateAuditProvider
from backend.apps.template.models import PermTemplate
from backend.apps.template.serializers import (
    TemplateDetailQuerySLZ,
    TemplateListSchemaSLZ,
    TemplateListSLZ,
    TemplatePartialUpdateSLZ,
    TemplateRetrieveSchemaSLZ,
)
from backend.apps.template.views import (
    TemplateGroupSyncPreviewViewSet,
    TemplateMemberViewSet,
    TemplatePreGroupSyncViewSet,
    TemplatePreUpdateViewSet,
    TemplateUpdateCommitViewSet,
    TemplateViewSet,
)
from backend.audit.audit import audit_context_setter, view_audit_decorator
from backend.biz.role import RoleBiz, RoleListQuery
from backend.biz.template import TemplateBiz
from backend.service.constants import PermissionCodeEnum

permission_logger = logging.getLogger("permission")


class TemplateQueryMixin:
    def get_queryset(self):
        pass


class TemplatePermissionNoneCheckMixin:
    def get_object(self):
        queryset = PermTemplate.objects.all()

        template_id = self.kwargs["id"]
        obj = get_object_or_404(queryset, pk=template_id)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    def check_object_permissions(self, request, obj):
        pass


class MgmtTemplateViewSet(TemplateQueryMixin, TemplateViewSet):
    permission_classes = [RolePermission]
    action_permission = {
        "update": PermissionCodeEnum.MGMT_TEMPLATE.value,
        "destroy": PermissionCodeEnum.MGMT_TEMPLATE.value,
        "partial_update": PermissionCodeEnum.MGMT_TEMPLATE.value,
    }

    role_biz = RoleBiz()
    temp_biz = TemplateBiz()

    @swagger_auto_schema(
        operation_description="模板列表",
        responses={status.HTTP_200_OK: TemplateListSchemaSLZ(label="模板", many=True)},
        tags=["mgmt.template"],
    )
    def list(self, request, *args, **kwargs):
        group_id = request.query_params.get("group_id", "")

        # 根据用户组ID获取对应的角色ID
        role = self.role_biz.get_role_by_group_id(group_id=group_id) if group_id else AnonymousRole
        queryset = self.filter_queryset(RoleListQuery(role, request.user).query_template())

        # 查询role的system-actions set
        role_system_actions = RoleListQuery(role).get_scope_system_actions()
        page = self.paginate_queryset(queryset)
        if page is not None:
            # 查询模板中对group_id中有授权的
            exists_template_set = self._query_group_exists_template_set(group_id, page)
            serializer = TemplateListSLZ(
                page, many=True, authorized_template=exists_template_set, role_system_actions=role_system_actions
            )

            return self.get_paginated_response(serializer.data)

        # 查询模板中对group_id中有授权的
        exists_template_set = self._query_group_exists_template_set(group_id, queryset)
        serializer = TemplateListSLZ(
            queryset, many=True, authorized_template=exists_template_set, role_system_actions=role_system_actions
        )
        return Response(serializer.data)


    @swagger_auto_schema(
        operation_description="模板详情",
        query_serializer=TemplateDetailQuerySLZ(),
        responses={status.HTTP_200_OK: TemplateRetrieveSchemaSLZ(label="模板详情")},
        tags=["mgmt.template"],
    )
    def retrieve(self, request, *args, **kwargs):
        slz = TemplateDetailQuerySLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)
        grouping = slz.validated_data["grouping"]

        template_id = kwargs["id"]
        # 根据所操作的模板获取关联角色信息
        role = self.temp_biz.get_role_by_template_id(template_id)
        # 查询role的system-actions set
        role_system_actions = RoleListQuery(role).get_scope_system_actions()
        template = get_object_or_404(self.queryset, pk=template_id)
        serializer = TemplateListSLZ(instance=template, role_system_actions=role_system_actions)
        data = serializer.data
        template_action_set = set(template.action_ids)

        actions = self.action_biz.list_template_tagged_action_by_role(
            template.system_id, role, template_action_set
        )
        if grouping:
            action_groups = self.action_group_biz.list_by_actions(template.system_id, actions)
            data["actions"] = [one.dict() for one in action_groups]
        else:
            data["actions"] = [one.dict() for one in actions if one.id in template_action_set]

        return Response(data)

    @swagger_auto_schema(
        operation_description="权限模板基本信息更新",
        request_body=TemplatePartialUpdateSLZ(label="更新权限模板基本信息"),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["mgmt.template"],
    )
    @view_audit_decorator(TemplateUpdateAuditProvider)
    def partial_update(self, request, *args, **kwargs):
        """仅仅做基本信息更新"""
        template = self.get_object()
        serializer = TemplatePartialUpdateSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        template_id = kwargs["id"]
        user_id = request.user.username
        data = serializer.validated_data

        # 根据所操作的模板获取关联角色信息
        role_id = self.temp_biz.get_role_by_template_id(template_id).id
        # 检查权限模板是否在角色内唯一
        self.template_check_biz.check_role_template_name_exists(role_id, data["name"], template_id=template.id)
        PermTemplate.objects.filter(id=template.id).update(updater=user_id, **data)

        audit_context_setter(template=template)

        return Response({})


class MgmtTemplateMemberViewSet(TemplatePermissionNoneCheckMixin, TemplateMemberViewSet):

    permission_classes = [RolePermission]


class MgmtTemplatePreUpdateViewSet(TemplatePermissionNoneCheckMixin, TemplatePreUpdateViewSet):
    """
    预更新
    """
    permission_classes = [RolePermission]
    action_permission = {
        "create": PermissionCodeEnum.MGMT_TEMPLATE.value,
        "destroy": PermissionCodeEnum.MGMT_TEMPLATE.value,
    }


class MgmtTemplatePreGroupSyncViewSet(TemplatePermissionNoneCheckMixin, TemplatePreGroupSyncViewSet):
    """
    用户组预提交同步
    """
    permission_classes = [RolePermission]
    action_permission = {
        "create": PermissionCodeEnum.MGMT_TEMPLATE.value
    }


class MgmtTemplateGroupSyncPreviewViewSet(TemplatePermissionNoneCheckMixin, TemplateGroupSyncPreviewViewSet):
    permission_classes = [RolePermission]


class MgmtTemplateUpdateCommitViewSet(TemplatePermissionNoneCheckMixin, TemplateUpdateCommitViewSet):
    """
    权限模板更新提交
    """
    permission_classes = [RolePermission]
    action_permission = {
        "create": PermissionCodeEnum.MGMT_TEMPLATE.value
    }
