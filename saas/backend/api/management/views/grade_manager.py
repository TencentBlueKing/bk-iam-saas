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
from collections import defaultdict
from typing import Dict, List

from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from backend.api.authentication import ESBAuthentication
from backend.api.management.constants import ManagementAPIEnum, VerifyAPIParamLocationEnum
from backend.api.management.mixins import ManagementAPIPermissionCheckMixin
from backend.api.management.permissions import ManagementAPIPermission
from backend.api.management.serializers import (
    ManagementGradeManagerCreateSLZ,
    ManagementGradeManagerMembersDeleteSLZ,
    ManagementGradeManagerMembersSLZ,
)
from backend.api.mixins import ExceptionHandlerMixin
from backend.apps.role.audit import (
    RoleCreateAuditProvider,
    RoleMemberCreateAuditProvider,
    RoleMemberDeleteAuditProvider,
)
from backend.apps.role.models import Role, RoleSource, RoleUser
from backend.apps.role.serializers import RoleIdSLZ
from backend.audit.audit import audit_context_setter, view_audit_decorator
from backend.biz.action import ActionCheckBiz, ActionForCheck
from backend.biz.policy import PolicyBean, PolicyBeanList
from backend.biz.role import RoleBiz, RoleCheckBiz, RoleInfoBean
from backend.biz.trans import ToPolicyRelatedResources
from backend.common.swagger import ResponseSwaggerAutoSchema
from backend.service.constants import RoleSourceTypeEnum, RoleType


class ManagementGradeManagerViewSet(ManagementAPIPermissionCheckMixin, ExceptionHandlerMixin, GenericViewSet):
    """分级管理员"""

    authentication_classes = [ESBAuthentication]
    permission_classes = [ManagementAPIPermission]
    management_api_permission = {
        "create": (VerifyAPIParamLocationEnum.SYSTEM_IN_BODY.value, ManagementAPIEnum.GRADE_MANAGER_CREATE.value),
    }

    biz = RoleBiz()
    role_check_biz = RoleCheckBiz()
    action_check_biz = ActionCheckBiz()

    @swagger_auto_schema(
        operation_description="创建分级管理员",
        request_body=ManagementGradeManagerCreateSLZ(label="创建分级管理员"),
        auto_schema=ResponseSwaggerAutoSchema,
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
        source_system_id = data["system"]
        auth_system_ids = list({i["system"] for i in data["authorization_scopes"]})
        self.verify_system_scope(source_system_id, auth_system_ids)

        # 名称唯一性检查
        self.role_check_biz.check_unique_name(data["name"])

        # 将授权的权限范围数据转为List[Policy]，并按照系统分组
        system_policies: Dict[str, List[PolicyBean]] = defaultdict(list)
        for auth_scope in data["authorization_scopes"]:
            # Resources转换为Policy的RelatedResourceTypes结构
            related_resources = ToPolicyRelatedResources().from_resource_paths(auth_scope["resources"])

            # 将Actions展开并给每个Action添加对应的Resources得到Policies
            for ac in auth_scope["actions"]:
                system_policies[auth_scope["system"]].append(
                    PolicyBean(action_id=ac["id"], related_resource_types=related_resources)
                )

        # 校验Policy，并填充资源类型等相关字段数据，最终组装出authorization_scopes
        authorization_scopes = []
        for system_id, policies in system_policies.items():
            # 检查Resources与Action RelatedResourceTypes是否匹配
            self.action_check_biz.check(system_id, [ActionForCheck.parse_obj(p.dict()) for p in policies])
            policy_list = PolicyBeanList(system_id, policies, need_check_instance_selection=True)
            # 组装出，create role的authorization_scope数据
            authorization_scopes.append({"system_id": system_id, "actions": [p.dict() for p in policy_list.policies]})
        # 使用创建角色所需的authorization_scopes替换掉参数里
        data["authorization_scopes"] = authorization_scopes

        # 创建角色
        role = self.biz.create(RoleInfoBean.parse_obj(data), request.user.username)

        # 记录role创建来源信息
        RoleSource.objects.create(
            role_id=role.id, source_type=RoleSourceTypeEnum.API.value, source_system_id=source_system_id
        )

        # 审计
        audit_context_setter(role=role)

        return Response({"id": role.id})


class ManagementGradeManagerMemberViewSet(ExceptionHandlerMixin, GenericViewSet):
    """分级管理员成员"""

    paginator = None  # 去掉swagger中的limit offset参数

    authentication_classes = [ESBAuthentication]
    permission_classes = [ManagementAPIPermission]
    management_api_permission = {
        "create": (VerifyAPIParamLocationEnum.ROLE_IN_PATH.value, ManagementAPIEnum.GRADE_MANAGER_MEMBER_ADD.value),
        "list": (VerifyAPIParamLocationEnum.ROLE_IN_PATH.value, ManagementAPIEnum.GRADE_MANAGER_MEMBER_LIST.value),
        "destroy": (
            VerifyAPIParamLocationEnum.ROLE_IN_PATH.value,
            ManagementAPIEnum.GRADE_MANAGER_MEMBER_DELETE.value,
        ),
    }

    lookup_field = "id"
    queryset = Role.objects.filter(type=RoleType.RATING_MANAGER.value).order_by("-updated_time")

    biz = RoleBiz()

    @swagger_auto_schema(
        operation_description="分级管理员成员列表",
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: serializers.ListSerializer(child=serializers.CharField(label="成员"))},
        tags=["management.role.member"],
    )
    def list(self, request, *args, **kwargs):
        role = self.get_object()
        # 成员
        return Response(role.members)

    @swagger_auto_schema(
        operation_description="批量添加分级管理员成员",
        request_body=ManagementGradeManagerMembersSLZ(label="分级管理员成员"),
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["management.role.member"],
    )
    @view_audit_decorator(RoleMemberCreateAuditProvider)
    def create(self, request, *args, **kwargs):
        role = self.get_object()

        serializer = ManagementGradeManagerMembersSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        members = list(set(serializer.validated_data["members"]))
        # 批量添加成员(添加时去重)
        self.biz.add_grade_manager_members(role.id, members)

        # 审计
        audit_context_setter(role=role, members=members)

        return Response({})

    @swagger_auto_schema(
        operation_description="批量删除分级管理员成员",
        query_serializer=ManagementGradeManagerMembersDeleteSLZ(label="分级管理员成员"),
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["management.role.member"],
    )
    @view_audit_decorator(RoleMemberDeleteAuditProvider)
    def destroy(self, request, *args, **kwargs):
        role = self.get_object()

        serializer = ManagementGradeManagerMembersDeleteSLZ(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        members = list(set(serializer.validated_data["members"]))
        RoleUser.objects.delete_grade_manager_member(role.id, members)

        # 审计
        audit_context_setter(role=role, members=members)

        return Response({})
