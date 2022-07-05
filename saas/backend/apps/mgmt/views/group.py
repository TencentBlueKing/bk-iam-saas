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
from typing import List

from django.shortcuts import get_object_or_404
from drf_yasg.openapi import Response as yasg_response
from drf_yasg.utils import swagger_auto_schema
from pydantic.tools import parse_obj_as
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from backend.account.permissions import RolePermission, role_perm_class
from backend.apps.group import tasks  # noqa
from backend.apps.group.audit import (
    GroupMemberCreateAuditProvider,
    GroupPolicyUpdateAuditProvider,
    GroupTemplateCreateAuditProvider,
    GroupUpdateAuditProvider,
)
from backend.apps.group.models import Group
from backend.apps.group.serializers import (
    GroupAddMemberSLZ,
    GroupAuthorizationSLZ,
    GroupPolicyUpdateSLZ,
    GroupUpdateSLZ,
    MemberSLZ,
    SearchMemberSLZ,
)
from backend.apps.group.views import (
    GroupMemberUpdateExpiredAtViewSet,
    GroupMemberViewSet,
    GroupPolicyViewSet,
    GroupTemplateViewSet,
    GroupTransferView,
    GroupViewSet,
)
from backend.audit.audit import audit_context_setter, view_audit_decorator
from backend.biz.policy import PolicyBean
from backend.biz.role import RoleBiz
from backend.common.time import PERMANENT_SECONDS
from backend.service.constants import PermissionCodeEnum
from backend.service.models import Subject

permission_logger = logging.getLogger("permission")


class GroupPermissionMixin:
    def check_object_permissions(self, request, obj):
        pass


class GroupViewSet(GroupViewSet):
    permission_classes = [RolePermission]
    action_permission = {
        "update": PermissionCodeEnum.MGMT_GROUP.value,
        "destroy": PermissionCodeEnum.MGMT_GROUP.value
    }

    def get_queryset(self):
        return Group.objects.all()

    @swagger_auto_schema(
        operation_description="修改用户组",
        request_body=GroupUpdateSLZ(label="用户组"),
        responses={status.HTTP_200_OK: GroupUpdateSLZ(label="用户组")},
        tags=["mgmt.group"],
    )
    @view_audit_decorator(GroupUpdateAuditProvider)
    def update(self, request, *args, **kwargs):
        group = self.get_object()
        serializer = GroupUpdateSLZ(group, data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = request.user.username
        data = serializer.validated_data

        # 根据所操作的用户组获取关联角色信息
        role = self.role_biz.get_role_by_group_id(group_id=group.id)
        # 用户组名称在角色内唯一
        self.group_check_biz.check_role_group_name_unique(role.id, data["name"], group.id)

        group = self.group_biz.update(group, data["name"], data["description"], user_id)

        # 写入审计上下文
        audit_context_setter(group=group)

        return Response(serializer.data)


class GroupMemberViewSet(GroupPermissionMixin, GroupMemberViewSet):

    permission_classes = [RolePermission]
    action_permission = {
        "list": PermissionCodeEnum.MGMT_GROUP.value,
        "create": PermissionCodeEnum.MGMT_GROUP.value,
        "destroy": PermissionCodeEnum.MGMT_GROUP.value,
    }

    role_biz = RoleBiz()

    @swagger_auto_schema(
        operation_description="用户组成员列表",
        query_serializer=SearchMemberSLZ(label="keyword"),
        responses={status.HTTP_200_OK: MemberSLZ(label="成员")},
        tags=["mgmt.group"],
    )
    def list(self, request, *args, **kwargs):
        group = get_object_or_404(self.queryset, pk=kwargs["id"])
        if request.query_params.get("keyword"):
            slz = SearchMemberSLZ(data=request.query_params)
            slz.is_valid(raise_exception=True)
            keyword = slz.validated_data["keyword"].lower()

            group_members = self.biz.search_member_by_keyword(group.id, keyword)

            return Response({"results": [one.dict() for one in group_members]})

        pagination = LimitOffsetPagination()
        limit = pagination.get_limit(request)
        offset = pagination.get_offset(request)

        count, group_members = self.biz.list_paging_group_member(group.id, limit, offset)
        return Response({"count": count, "results": [one.dict() for one in group_members]})

    @swagger_auto_schema(
        operation_description="用户组添加成员",
        request_body=GroupAddMemberSLZ(label="成员"),
        responses={status.HTTP_200_OK: yasg_response({})},
        tags=["mgmt.group"],
    )
    @view_audit_decorator(GroupMemberCreateAuditProvider)
    def create(self, request, *args, **kwargs):
        serializer = GroupAddMemberSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        group = self.get_object()
        data = serializer.validated_data

        members_data = data["members"]
        expired_at = data["expired_at"]

        # 成员Dict结构转换为Subject结构，并去重
        members = list(set(parse_obj_as(List[Subject], members_data)))

        # 根据所操作的用户组获取关联角色信息
        role = self.role_biz.get_role_by_group_id(group_id=group.id)
        # 检测成员是否满足管理的授权范围
        self.group_check_biz.check_role_subject_scope(role, members)
        # 检测用户组成员数量是否超限
        self.group_check_biz.check_member_count(group.id, len(members))

        permission_logger.info("group %s add members %s by user %s", group.id, members, request.user.username)

        # 添加成员
        self.biz.add_members(group.id, members, expired_at)

        # 写入审计上下文
        audit_context_setter(group=group, members=[m.dict() for m in members])

        return Response({}, status=status.HTTP_201_CREATED)


class GroupMemberUpdateExpiredAtViewSet(GroupPermissionMixin, GroupMemberUpdateExpiredAtViewSet):

    permission_classes = [role_perm_class(PermissionCodeEnum.MGMT_GROUP.value)]


class GroupTemplateViewSet(GroupPermissionMixin, GroupTemplateViewSet):

    permission_classes = [RolePermission]
    action_permission = {"create": PermissionCodeEnum.MGMT_GROUP.value}


class GroupPolicyViewSet(GroupPermissionMixin, GroupPolicyViewSet):

    permission_classes = [RolePermission]
    action_permission = {
        "create": PermissionCodeEnum.MGMT_GROUP.value,
        "destroy": PermissionCodeEnum.MGMT_GROUP.value,
        "update": PermissionCodeEnum.MGMT_GROUP.value,
    }

    role_biz = RoleBiz()

    @swagger_auto_schema(
        operation_description="用户组添加权限",
        request_body=GroupAuthorizationSLZ(label="授权信息"),
        responses={status.HTTP_201_CREATED: yasg_response({})},
        tags=["mgmt.group"],
    )
    @view_audit_decorator(GroupTemplateCreateAuditProvider)
    def create(self, request, *args, **kwargs):
        serializer = GroupAuthorizationSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        group = self.get_object()
        data = serializer.validated_data

        templates = self.group_trans.from_group_grant_data(data["templates"])

        # 根据所操作的用户组获取关联角色信息
        role = self.role_biz.get_role_by_group_id(group_id=group.id)
        self.group_biz.grant(role, group, templates)

        # 写入审计上下文
        audit_context_setter(
            group=group,
            templates=[{"system_id": t["system_id"], "template_id": t["template_id"]} for t in data["templates"]],
        )

        return Response({}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description="用户组权限修改",
        request_body=GroupPolicyUpdateSLZ(label="修改策略"),
        responses={status.HTTP_200_OK: yasg_response({})},
        tags=["mgmt.group"],
    )
    @view_audit_decorator(GroupPolicyUpdateAuditProvider)
    def update(self, request, *args, **kwargs):
        group = self.get_object()

        slz = GroupPolicyUpdateSLZ(data=request.data)
        slz.is_valid(raise_exception=True)

        data = slz.validated_data
        system_id = data["system_id"]
        template_id = data["template_id"]

        policies = [PolicyBean(expired_at=PERMANENT_SECONDS, **action) for action in data["actions"]]
        # 根据所操作的用户组获取关联角色信息
        role = self.role_biz.get_role_by_group_id(group_id=group.id)
        self.group_biz.update_policies(role, group.id, system_id, template_id, policies)

        # 写入审计上下文
        audit_context_setter(group=group, system_id=system_id, template_id=template_id, policies=policies)

        return Response({})


class GroupTransferView(GroupTransferView):
    """
    用户组转出
    """

    permission_classes = [role_perm_class(PermissionCodeEnum.MGMT_GROUP.value)]
