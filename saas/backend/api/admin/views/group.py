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
from typing import List

from drf_yasg.utils import swagger_auto_schema
from pydantic.tools import parse_obj_as
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, mixins

from backend.api.admin.constants import AdminAPIEnum, VerifyApiParamLocationEnum
from backend.api.admin.filters import GroupFilter
from backend.api.admin.permissions import AdminAPIPermission
from backend.api.admin.serializers import (
    AdminGroupAuthorizationSLZ,
    AdminGroupBasicSLZ,
    AdminGroupCreateSLZ,
    AdminGroupMemberSLZ,
)
from backend.api.authentication import ESBAuthentication
from backend.api.management.v2.views import ManagementGroupViewSet
from backend.apps.group.audit import GroupCreateAuditProvider, GroupTemplateCreateAuditProvider
from backend.apps.group.constants import OperateEnum
from backend.apps.group.models import Group
from backend.apps.group.views import check_readonly_group
from backend.apps.role.models import Role
from backend.audit.audit import add_audit, audit_context_setter, view_audit_decorator
from backend.audit.constants import AuditSourceType
from backend.biz.group import GroupBiz, GroupCheckBiz, GroupCreationBean
from backend.biz.role import RoleBiz
from backend.common.lock import gen_group_upsert_lock
from backend.common.pagination import CompatiblePagination
from backend.service.constants import GroupSaaSAttributeEnum, RoleType
from backend.trans.group import GroupTrans


class AdminGroupViewSet(mixins.ListModelMixin, GenericViewSet):
    """用户组"""

    authentication_classes = [ESBAuthentication]
    permission_classes = [AdminAPIPermission]

    admin_api_permission = {"list": AdminAPIEnum.GROUP_LIST.value, "create": AdminAPIEnum.GROUP_BATCH_CREATE.value}

    queryset = Group.objects.all()
    serializer_class = AdminGroupBasicSLZ
    filterset_class = GroupFilter
    pagination_class = CompatiblePagination

    group_biz = GroupBiz()
    group_check_biz = GroupCheckBiz()

    @swagger_auto_schema(
        operation_description="用户组列表",
        responses={status.HTTP_200_OK: AdminGroupBasicSLZ(label="用户组信息", many=True)},
        tags=["admin.group"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="批量创建用户组",
        request_body=AdminGroupCreateSLZ(label="用户组"),
        responses={status.HTTP_200_OK: serializers.ListSerializer(child=serializers.IntegerField(label="用户组ID"))},
        tags=["admin.group"],
    )
    def create(self, request, *args, **kwargs):
        role = Role.objects.get(type=RoleType.SUPER_MANAGER.value)

        serializer = AdminGroupCreateSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)
        groups_data = serializer.validated_data["groups"]
        sync_subject_template = serializer.validated_data["sync_subject_template"]

        # 用户组数量在角色内是否超限
        self.group_check_biz.check_role_group_limit(role, len(groups_data))

        infos = parse_obj_as(List[GroupCreationBean], groups_data)

        attrs = None
        if serializer.validated_data["create_attributes"]:
            attrs = {
                GroupSaaSAttributeEnum.SOURCE_TYPE.value: AuditSourceType.OPENAPI.value,
            }

        with gen_group_upsert_lock(role.id):
            # 用户组名称在角色内唯一
            group_names = [g["name"] for g in groups_data]
            self.group_check_biz.batch_check_role_group_names_unique(role.id, group_names)

            groups = self.group_biz.batch_create(
                role,
                infos,
                request.user.username,
                attrs=attrs,
                sync_subject_template=sync_subject_template,
            )

        # 添加审计信息
        # TODO: 后续其他地方也需要批量添加审计时再抽象出一个batch_add_audit方法，将for循环逻辑放到方法里
        for g in groups:
            add_audit(GroupCreateAuditProvider, request, group=g)

        return Response([group.id for group in groups])


class AdminGroupInfoViewSet(ManagementGroupViewSet):
    """用户组"""

    authentication_classes = [ESBAuthentication]
    permission_classes = [AdminAPIPermission]

    admin_api_permission = {
        "update": (VerifyApiParamLocationEnum.GROUP_IN_PATH.value, AdminAPIEnum.GROUP_UPDATE.value),
        "destroy": (VerifyApiParamLocationEnum.GROUP_IN_PATH.value, AdminAPIEnum.GROUP_DELETE.value),
    }


class AdminGroupMemberViewSet(GenericViewSet):
    """用户组成员"""

    authentication_classes = [ESBAuthentication]
    permission_classes = [AdminAPIPermission]

    admin_api_permission = {"list": AdminAPIEnum.GROUP_MEMBER_LIST.value}

    queryset = Group.objects.all()
    lookup_field = "id"
    pagination_class = CompatiblePagination

    biz = GroupBiz()

    @swagger_auto_schema(
        operation_description="用户组成员列表",
        responses={status.HTTP_200_OK: AdminGroupMemberSLZ(label="用户组成员信息", many=True)},
        tags=["admin.group.member"],
    )
    def list(self, request, *args, **kwargs):
        group = self.get_object()

        # 分页参数
        limit, offset = CompatiblePagination().get_limit_offset_pair(request)

        count, group_members = self.biz.list_paging_thin_group_member(group.id, limit, offset)
        results = [one.dict(include={"type", "id", "name", "expired_at"}) for one in group_members]
        return Response({"count": count, "results": results})


class AdminGroupPolicyViewSet(GenericViewSet):
    """用户组授权"""

    authentication_classes = [ESBAuthentication]
    permission_classes = [AdminAPIPermission]

    admin_api_permission = {"create": AdminAPIEnum.GROUP_POLICY_GRANT.value}

    pagination_class = None  # 去掉swagger中的limit offset参数
    queryset = Group.objects.all()
    lookup_field = "id"

    group_biz = GroupBiz()
    role_biz = RoleBiz()

    group_trans = GroupTrans()

    @swagger_auto_schema(
        operation_description="用户组添加权限",
        request_body=AdminGroupAuthorizationSLZ(label="授权信息"),
        responses={status.HTTP_201_CREATED: serializers.Serializer()},
        tags=["admin.group.policy"],
    )
    @view_audit_decorator(GroupTemplateCreateAuditProvider)
    @check_readonly_group(operation=OperateEnum.GROUP_POLICY_CREATE.label)
    def create(self, request, *args, **kwargs):
        serializer = AdminGroupAuthorizationSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        group = self.get_object()
        data = serializer.validated_data

        role = self.role_biz.get_role_by_group_id(group.id)
        templates = self.group_trans.from_group_grant_data(data["templates"])
        self.group_biz.grant(role, group, templates)

        # 写入审计上下文
        audit_context_setter(
            group=group,
            templates=[{"system_id": t["system_id"], "template_id": t["template_id"]} for t in data["templates"]],
        )

        return Response({}, status=status.HTTP_201_CREATED)
