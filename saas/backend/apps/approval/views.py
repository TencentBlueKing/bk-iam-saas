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
from collections import Counter

from django.db.models import Q
from django.utils.translation import gettext as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, mixins

from backend.account.permissions import role_perm_class
from backend.audit.audit import audit_context_setter, view_audit_decorator
from backend.biz.action import ActionBiz, ActionSearchCondition
from backend.biz.approval import ApprovalProcessBiz
from backend.biz.role import RoleAuthorizationScopeChecker, RoleListQuery, RoleObjectRelationChecker
from backend.common.error_codes import error_codes
from backend.common.serializers import SystemQuerySLZ
from backend.service.action import ActionService
from backend.service.constants import PermissionCodeEnum, RoleType

from .audit import (
    ActionSensitivityLevelAuditProvider,
    ApprovalProcessActionAuditProvider,
    ApprovalProcessGlobalConfigAuditProvider,
    ApprovalProcessGroupAuditProvider,
)
from .serializers import (
    ActionApprovalProcessModifySLZ,
    ActionApprovalProcessQuerySLZ,
    ActionApprovalProcessSLZ,
    ActionSensitivityLevelSLZ,
    ApporvalProcessQuerySLZ,
    ApprovalProcessGlobalConfigModifySLZ,
    ApprovalProcessGlobalConfigSLZ,
    ApprovalProcessSLZ,
    GroupApprovalProcessModifySLZ,
    GroupApprovalProcessQuerySLZ,
    GroupApprovalProcessSLZ,
    SensitivityLevelCountSLZ,
)


class ApprovalProcessViewSet(GenericViewSet):
    permission_classes = [role_perm_class(PermissionCodeEnum.CONFIGURE_APPROVAL_PROCESS.value)]

    pagination_class = None  # 去掉swagger中的limit offset参数

    biz = ApprovalProcessBiz()

    @swagger_auto_schema(
        operation_description="审批流程列表",
        query_serializer=ApporvalProcessQuerySLZ(),
        responses={status.HTTP_200_OK: ApprovalProcessSLZ(label="审批流程列表")},
        tags=["approval"],
    )
    def list(self, request, *args, **kwargs):
        slz = ApporvalProcessQuerySLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)

        processes = self.biz.list_with_node_names(slz.validated_data["type"])

        return Response([p.dict() for p in processes])


class ApprovalProcessGlobalConfigViewSet(mixins.ListModelMixin, GenericViewSet):

    permission_classes = [role_perm_class(PermissionCodeEnum.MANAGE_GLOBAL_SETTING.value)]

    pagination_class = None  # 去掉swagger中的limit offset参数

    biz = ApprovalProcessBiz()

    @swagger_auto_schema(
        operation_description="默认审批流程",
        responses={status.HTTP_200_OK: ApprovalProcessGlobalConfigSLZ(label="审批流程列表", many=True)},
        tags=["approval"],
    )
    def list(self, request, *args, **kwargs):
        # 查询所有默认审批流程
        default_processes = self.biz.list_default_process()
        return Response([dp.dict() for dp in default_processes])

    @swagger_auto_schema(
        operation_description="批量设置操作的审批流程",
        request_body=ApprovalProcessGlobalConfigModifySLZ(),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["approval"],
    )
    @view_audit_decorator(ApprovalProcessGlobalConfigAuditProvider)
    def create(self, request, *args, **kwargs):
        slz = ApprovalProcessGlobalConfigModifySLZ(data=request.data)
        slz.is_valid(raise_exception=True)

        application_type = slz.validated_data["type"]
        process_id = int(slz.validated_data["process_id"])

        self.biz.create_or_update_default_process(application_type, process_id, request.user.username)

        audit_context_setter(role=request.role, type=application_type, process_id=process_id)

        return Response({})


class ActionApprovalProcessViewSet(GenericViewSet):

    permission_classes = [role_perm_class(PermissionCodeEnum.MANAGE_SYSTEM_SETTING.value)]

    biz = ApprovalProcessBiz()
    action_svc = ActionService()

    action_biz = ActionBiz()

    @swagger_auto_schema(
        operation_description="操作-审批流程列表",
        query_serializer=ActionApprovalProcessQuerySLZ(),
        responses={status.HTTP_200_OK: ActionApprovalProcessSLZ(label="操作-审批流程列表", many=True)},
        tags=["approval"],
    )
    def list(self, request, *args, **kwargs):
        slz = ActionApprovalProcessQuerySLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)

        system_id = slz.validated_data["system_id"]
        action_group_id = slz.validated_data.get("action_group_id")
        keyword = slz.validated_data.get("keyword")
        sensitivity_level = slz.validated_data.get("sensitivity_level")

        # 分页参数
        paginator = LimitOffsetPagination()
        offset, limit = paginator.get_offset(request), paginator.get_limit(request)

        # 校验角色管理范围
        checker = RoleAuthorizationScopeChecker(request.role)
        checker.check_systems([system_id])

        # 执行搜索操作
        actions = self.action_biz.search(
            system_id,
            ActionSearchCondition(
                keyword=keyword, action_group_id=action_group_id, sensitivity_level=sensitivity_level
            ),
        )

        # 分页数据
        count = len(actions)
        actions = actions[offset : offset + limit]

        # 获取操作与审批流程关系
        action_process_relation_dict = self.biz.get_action_process_relation_dict(system_id, [a.id for a in actions])

        data = []
        for action in actions:
            process = action_process_relation_dict.get_process(action.id)
            data.append(
                {
                    "system_id": system_id,
                    "action_id": action.id,
                    "action_name": action.name,
                    "action_name_en": action.name_en,
                    "process_id": process.id,
                    "process_name": process.name,
                    "sensitivity_level": action.sensitivity_level,
                }
            )

        return Response({"count": count, "results": data})

    @swagger_auto_schema(
        operation_description="批量设置操作的审批流程",
        request_body=ActionApprovalProcessModifySLZ(),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["approval"],
    )
    @view_audit_decorator(ApprovalProcessActionAuditProvider)
    def create(self, request, *args, **kwargs):
        slz = ActionApprovalProcessModifySLZ(data=request.data)
        slz.is_valid(raise_exception=True)

        actions = slz.validated_data["actions"]
        process_id = int(slz.validated_data["process_id"])

        # 目前只支持同一系统的批量Action设置审批流程
        system_id = actions[0]["system_id"]
        action_ids = [a["id"] for a in actions]

        # 校验角色管理范围
        checker = RoleAuthorizationScopeChecker(request.role)
        checker.check_systems([system_id])

        self.biz.batch_create_or_update_action_process(system_id, action_ids, process_id, request.user.username)

        audit_context_setter(role=request.role, system_id=system_id, action_ids=action_ids, process_id=process_id)

        return Response({})


class SystemActionSensitivityLevelCountViewSet(GenericViewSet):
    permission_classes = [role_perm_class(PermissionCodeEnum.MANAGE_SYSTEM_SETTING.value)]

    biz = ActionBiz()

    @swagger_auto_schema(
        operation_description="获取系统的操作与敏感等级数量",
        query_serializer=SystemQuerySLZ(),
        responses={status.HTTP_200_OK: SensitivityLevelCountSLZ()},
        tags=["approval"],
    )
    def list(self, request, *args, **kwargs):
        slz = SystemQuerySLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)

        system_id = slz.validated_data["system_id"]

        action_list = self.biz.list_without_cache_sensitivity_level(system_id)
        level_count = Counter(obj.sensitivity_level for obj in action_list.actions)

        data = dict(level_count.items())
        data["all"] = len(action_list.actions)

        return Response(data)


class ActionSensitivityLevelViewSet(GenericViewSet):
    permission_classes = [role_perm_class(PermissionCodeEnum.MANAGE_SENSITIVITY_LEVEL.value)]

    biz = ApprovalProcessBiz()

    @swagger_auto_schema(
        operation_description="批量设置操作的敏感等级",
        request_body=ActionSensitivityLevelSLZ(),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["approval"],
    )
    @view_audit_decorator(ActionSensitivityLevelAuditProvider)
    def create(self, request, *args, **kwargs):
        slz = ActionSensitivityLevelSLZ(data=request.data)
        slz.is_valid(raise_exception=True)

        actions = slz.validated_data["actions"]
        sensitivity_level = slz.validated_data["sensitivity_level"]

        # 目前只支持同一系统的批量Action设置审批流程
        system_id = actions[0]["system_id"]
        action_ids = [a["id"] for a in actions]

        # 校验系统管理员权限
        if request.role.type == RoleType.SYSTEM_MANAGER.value and request.role.code != system_id:
            raise error_codes.FORBIDDEN

        self.biz.batch_create_or_update_action_sensitivity_level(
            system_id, action_ids, sensitivity_level, request.user.username
        )

        audit_context_setter(
            role=request.role, system_id=system_id, action_ids=action_ids, sensitivity_level=sensitivity_level
        )

        return Response({})


class GroupApprovalProcessViewSet(GenericViewSet):

    permission_classes = [role_perm_class(PermissionCodeEnum.MANAGE_GROUP.value)]

    biz = ApprovalProcessBiz()

    @swagger_auto_schema(
        operation_description="用户组-审批流程列表",
        query_serializer=GroupApprovalProcessQuerySLZ(),
        responses={status.HTTP_200_OK: GroupApprovalProcessSLZ(label="用户组-审批流程列表", many=True)},
        tags=["approval"],
    )
    def list(self, request, *args, **kwargs):
        slz = GroupApprovalProcessQuerySLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)

        keyword = slz.validated_data.get("keyword")

        # 分页
        paginator = LimitOffsetPagination()
        offset, limit = paginator.get_offset(request), paginator.get_limit(request)

        # 查询当前分级管理员可以管理的用户组
        group_queryset = RoleListQuery(request.role, request.user).query_group()
        if keyword:
            group_queryset = group_queryset.filter(Q(name__icontains=keyword) | Q(description__icontains=keyword))

        # 分页数据
        count = group_queryset.count()
        groups = group_queryset[offset : offset + limit]

        # 获取操作与审批流程关系
        group_process_relation_dict = self.biz.get_group_process_relation_dict([g.id for g in groups])

        data = []
        for group in groups:
            process = group_process_relation_dict.get_process(group.id)
            data.append(
                {
                    "group_id": group.id,
                    "group_name": group.name,
                    "group_desc": group.description,
                    "process_id": process.id,
                    "process_name": process.name,
                }
            )

        return Response({"count": count, "results": data})

    @swagger_auto_schema(
        operation_description="批量设置用户组的审批流程",
        request_body=GroupApprovalProcessModifySLZ(),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["approval"],
    )
    @view_audit_decorator(ApprovalProcessGroupAuditProvider)
    def create(self, request, *args, **kwargs):
        slz = GroupApprovalProcessModifySLZ(data=request.data)
        slz.is_valid(raise_exception=True)

        group_ids = slz.validated_data["group_ids"]
        process_id = int(slz.validated_data["process_id"])

        # 校验角色是否能管理对应的用户组
        if not RoleObjectRelationChecker(request.role).check_group_ids(group_ids):
            raise error_codes.FORBIDDEN.format(
                message=_("非分级管理员({})的用户组，无权限续期").format(request.role.name), replace=True
            )

        self.biz.batch_create_or_update_group_process(group_ids, process_id, request.user.username)

        audit_context_setter(role=request.role, group_ids=group_ids, process_id=process_id)

        return Response({})
