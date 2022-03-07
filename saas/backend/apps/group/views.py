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
from django.utils.translation import gettext as _
from drf_yasg.openapi import Response as yasg_response
from drf_yasg.utils import swagger_auto_schema
from pydantic.tools import parse_obj_as
from rest_framework import serializers, status, views
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, mixins

from backend.account.permissions import RolePermission, role_perm_class
from backend.apps.application.serializers import ConditionCompareSLZ, ConditionTagSLZ
from backend.apps.group import tasks  # noqa
from backend.apps.group.models import Group
from backend.apps.policy.serializers import PolicyDeleteSLZ, PolicySLZ, PolicySystemSLZ
from backend.apps.template.models import PermTemplatePolicyAuthorized
from backend.audit.audit import audit_context_setter, view_audit_decorator
from backend.biz.group import GroupBiz, GroupCheckBiz, GroupMemberExpiredAtBean
from backend.biz.policy import PolicyBean, PolicyOperationBiz, PolicyQueryBiz
from backend.biz.policy_tag import ConditionTagBean, ConditionTagBiz
from backend.biz.role import RoleBiz, RoleListQuery, RoleObjectRelationChecker
from backend.biz.template import TemplateBiz
from backend.common.error_codes import error_codes
from backend.common.filters import NoCheckModelFilterBackend
from backend.common.serializers import SystemQuerySLZ
from backend.common.swagger import PaginatedResponseSwaggerAutoSchema, ResponseSwaggerAutoSchema
from backend.common.time import PERMANENT_SECONDS
from backend.service.constants import PermissionCodeEnum, RoleType, SubjectType
from backend.service.models import Subject
from backend.trans.group import GroupTrans

from .audit import (
    GroupCreateAuditProvider,
    GroupDeleteAuditProvider,
    GroupMemberCreateAuditProvider,
    GroupMemberDeleteAuditProvider,
    GroupMemberRenewAuditProvider,
    GroupPolicyDeleteAuditProvider,
    GroupPolicyUpdateAuditProvider,
    GroupTemplateCreateAuditProvider,
    GroupTransferAuditProvider,
    GroupUpdateAuditProvider,
)
from .filters import GroupFilter, GroupTemplateSystemFilter
from .serializers import (
    GroupAddMemberSLZ,
    GroupAuthoriedConditionSLZ,
    GroupAuthorizationSLZ,
    GroupCreateSLZ,
    GroupDeleteMemberSLZ,
    GroupIdSLZ,
    GroupMemberUpdateExpiredAtSLZ,
    GroupPolicyUpdateSLZ,
    GroupSLZ,
    GroupTemplateDetailSchemaSLZ,
    GroupTemplateDetailSLZ,
    GroupTemplateSchemaSLZ,
    GroupTemplateSLZ,
    GroupTransferSLZ,
    GroupUpdateSLZ,
    MemberSLZ,
    SearchMemberSLZ,
)

permission_logger = logging.getLogger("permission")


class GroupQueryMixin:
    def get_queryset(self):
        request = self.request
        return RoleListQuery(request.role, request.user).query_group()


class GroupPermissionMixin:
    def check_object_permissions(self, request, obj):
        if not RoleObjectRelationChecker(request.role).check_group(obj):
            self.permission_denied(request, message=f"{request.role.type} role can not access group {obj.id}")


class GroupViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):

    permission_classes = [RolePermission]
    action_permission = {
        "create": PermissionCodeEnum.MANAGE_GROUP.value,
        "update": PermissionCodeEnum.MANAGE_GROUP.value,
        "destroy": PermissionCodeEnum.MANAGE_GROUP.value,
    }

    queryset = Group.objects.all()
    serializer_class = GroupSLZ
    filterset_class = GroupFilter
    lookup_field = "id"

    group_biz = GroupBiz()
    group_check_biz = GroupCheckBiz()
    role_biz = RoleBiz()

    group_trans = GroupTrans()

    @swagger_auto_schema(
        operation_description="创建用户组",
        request_body=GroupCreateSLZ(label="用户组"),
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_201_CREATED: GroupIdSLZ(label="用户组ID")},
        tags=["group"],
    )
    @view_audit_decorator(GroupCreateAuditProvider)
    def create(self, request, *args, **kwargs):
        """
        创建用户组
        """
        serializer = GroupCreateSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = request.user.username
        data = serializer.validated_data

        # 用户组名称在角色内唯一
        self.group_check_biz.check_role_group_name_unique(request.role.id, data["name"])

        # 检测成员是否满足管理的授权范围
        members = parse_obj_as(List[Subject], data["members"])
        self.group_check_biz.check_role_subject_scope(request.role, members)

        group = self.group_biz.create_and_add_members(
            request.role.id, data["name"], data["description"], user_id, members, data["expired_at"]
        )

        # 使用长时任务触发多个模板同时授权
        if data["templates"]:
            templates = self.group_trans.from_group_grant_data(data["templates"])
            self.group_biz.grant(request.role, group, templates)

        # 写入审计上下文
        audit_context_setter(group=group)

        return Response({"id": group.id}, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        request = self.request
        role = request.role
        username = request.user.username
        filter_role_id = request.query_params.get("role_id")

        # 如果当前角色是staff 并且 存在筛选的role_id
        if role.type == RoleType.STAFF.value and filter_role_id:
            # 检查用户是否在角色的授权范围内
            filter_role = self.role_biz.get_role_scope_include_user(filter_role_id, username)
            if not filter_role:
                return Group.objects.none()

            # 返回角色的用户组列表
            return RoleListQuery(filter_role, request.user).query_group()

        return RoleListQuery(role, request.user).query_group()

    @swagger_auto_schema(
        operation_description="用户组列表",
        auto_schema=PaginatedResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: GroupSLZ(label="用户组", many=True)},
        tags=["group"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="用户组详情",
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: GroupSLZ(label="用户组")},
        tags=["group"],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="修改用户组",
        request_body=GroupUpdateSLZ(label="用户组"),
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: GroupUpdateSLZ(label="用户组")},
        tags=["group"],
    )
    @view_audit_decorator(GroupUpdateAuditProvider)
    def update(self, request, *args, **kwargs):
        group = self.get_object()
        serializer = GroupUpdateSLZ(group, data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = request.user.username
        data = serializer.validated_data

        # 用户组名称在角色内唯一
        self.group_check_biz.check_role_group_name_unique(request.role.id, data["name"], group.id)

        group = self.group_biz.update(group, data["name"], data["description"], user_id)

        # 写入审计上下文
        audit_context_setter(group=group)

        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="删除用户组",
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: yasg_response({})},
        tags=["group"],
    )
    @view_audit_decorator(GroupDeleteAuditProvider)
    def destroy(self, request, *args, **kwargs):
        group = self.get_object()

        self.group_biz.delete(group.id)

        # 写入审计上下文
        audit_context_setter(group=group)

        return Response({})


class GroupMemberViewSet(GroupPermissionMixin, GenericViewSet):

    permission_classes = [RolePermission]
    action_permission = {
        "list": PermissionCodeEnum.MANAGE_GROUP.value,
        "create": PermissionCodeEnum.MANAGE_GROUP.value,
        "destroy": PermissionCodeEnum.MANAGE_GROUP.value,
    }

    queryset = Group.objects.all()
    lookup_field = "id"

    biz = GroupBiz()
    group_check_biz = GroupCheckBiz()

    @swagger_auto_schema(
        operation_description="用户组成员列表",
        query_serializer=SearchMemberSLZ(label="keyword"),
        auto_schema=PaginatedResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: MemberSLZ(label="成员")},
        tags=["group"],
    )
    def list(self, request, *args, **kwargs):
        group = get_object_or_404(self.queryset, pk=kwargs["id"])

        # 校验权限
        checker = RoleObjectRelationChecker(request.role)
        if not checker.check_group(group):
            raise error_codes.FORBIDDEN.format(message=_("用户组({})不在当前用户身份可访问的范围内").format(group.id), replace=True)

        if request.query_params.get("keyword"):
            slz = SearchMemberSLZ(data=request.query_params)
            slz.is_valid(raise_exception=True)
            keyword = slz.validated_data["keyword"]

            group_members = self.biz.search_member_by_keyword(group.id, keyword)

            return Response({"results": [one for one in group_members]})

        pagination = LimitOffsetPagination()
        limit = pagination.get_limit(request)
        offset = pagination.get_offset(request)

        count, group_members = self.biz.list_paging_group_member(group.id, limit, offset)
        return Response({"count": count, "results": [one.dict() for one in group_members]})

    @swagger_auto_schema(
        operation_description="用户组添加成员",
        auto_schema=ResponseSwaggerAutoSchema,
        request_body=GroupAddMemberSLZ(label="成员"),
        responses={status.HTTP_200_OK: yasg_response({})},
        tags=["group"],
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
        # 检测成员是否满足管理的授权范围
        self.group_check_biz.check_role_subject_scope(request.role, members)
        self.group_check_biz.check_member_count(group.id, len(members))

        permission_logger.info("group add member by user: %s", request.user.username)

        # 添加成员
        self.biz.add_members(group.id, members, expired_at)

        # 写入审计上下文
        audit_context_setter(group=group, members=[m.dict() for m in members])

        return Response({}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description="用户组删除成员",
        auto_schema=ResponseSwaggerAutoSchema,
        request_body=GroupDeleteMemberSLZ(label="成员"),
        responses={status.HTTP_200_OK: yasg_response({})},
        tags=["group"],
    )
    @view_audit_decorator(GroupMemberDeleteAuditProvider)
    def destroy(self, request, *args, **kwargs):
        serializer = GroupDeleteMemberSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        group = self.get_object()
        data = serializer.validated_data

        permission_logger.info("group delete member by user: %s", request.user.username)

        self.biz.remove_members(str(group.id), parse_obj_as(List[Subject], data["members"]))

        # 写入审计上下文
        audit_context_setter(group=group, members=data["members"])

        return Response({})


class GroupMemberUpdateExpiredAtViewSet(GroupPermissionMixin, GenericViewSet):

    permission_classes = [role_perm_class(PermissionCodeEnum.MANAGE_GROUP.value)]

    queryset = Group.objects.all()
    lookup_field = "id"

    # service
    group_biz = GroupBiz()

    @swagger_auto_schema(
        operation_description="用户组成员续期",
        auto_schema=ResponseSwaggerAutoSchema,
        request_body=GroupMemberUpdateExpiredAtSLZ(label="成员"),
        responses={status.HTTP_200_OK: yasg_response({})},
        tags=["group"],
    )
    @view_audit_decorator(GroupMemberRenewAuditProvider)
    def create(self, request, *args, **kwargs):
        serializer = GroupMemberUpdateExpiredAtSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        group = self.get_object()
        data = serializer.validated_data

        permission_logger.info("group update member expired_at by user: %s", request.user.username)

        for m in data["members"]:
            m["policy_expired_at"] = m.pop("expired_at")

        self.group_biz.update_members_expired_at(
            group.id, parse_obj_as(List[GroupMemberExpiredAtBean], data["members"])
        )

        # 写入审计上下文
        audit_context_setter(group=group, members=data["members"])

        return Response({})


class GroupTemplateViewSet(GroupPermissionMixin, GenericViewSet):

    permission_classes = [RolePermission]
    action_permission = {"create": PermissionCodeEnum.MANAGE_GROUP.value}

    paginator = None  # 去掉swagger中的limit offset参数
    queryset = Group.objects.all()
    filterset_class = GroupTemplateSystemFilter
    filter_backends = [NoCheckModelFilterBackend]
    lookup_field = "id"

    template_biz = TemplateBiz()

    @swagger_auto_schema(
        operation_description="用户组拥有的权限模板列表",
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: GroupTemplateSchemaSLZ(label="权限模板", many=True)},
        tags=["group"],
    )
    def list(self, request, *args, **kwargs):
        group = get_object_or_404(self.queryset, pk=kwargs["id"])
        subject = Subject(type=SubjectType.GROUP.value, id=str(group.id))
        queryset = PermTemplatePolicyAuthorized.objects.filter_by_subject(subject).defer("_data")

        queryset = self.filter_queryset(queryset)
        return Response(GroupTemplateSLZ(queryset, many=True).data)

    @swagger_auto_schema(
        operation_description="用户组权限模板授权信息",
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: GroupTemplateDetailSchemaSLZ(label="授权信息")},
        tags=["group"],
    )
    def retrieve(self, request, *args, **kwargs):
        group = get_object_or_404(self.queryset, pk=kwargs["id"])
        template_id = kwargs["template_id"]

        subject = Subject(type=SubjectType.GROUP.value, id=str(group.id))
        authorized_template = PermTemplatePolicyAuthorized.objects.get_by_subject_template(subject, int(template_id))
        return Response(GroupTemplateDetailSLZ(authorized_template).data)


class GroupPolicyViewSet(GroupPermissionMixin, GenericViewSet):

    permission_classes = [RolePermission]
    action_permission = {
        "create": PermissionCodeEnum.MANAGE_GROUP.value,
        "destroy": PermissionCodeEnum.MANAGE_GROUP.value,
        "update": PermissionCodeEnum.MANAGE_GROUP.value,
    }

    paginator = None  # 去掉swagger中的limit offset参数
    queryset = Group.objects.all()
    lookup_field = "id"

    policy_query_biz = PolicyQueryBiz()
    policy_operation_biz = PolicyOperationBiz()
    group_biz = GroupBiz()

    group_trans = GroupTrans()

    @swagger_auto_schema(
        operation_description="用户组添加权限",
        auto_schema=ResponseSwaggerAutoSchema,
        request_body=GroupAuthorizationSLZ(label="授权信息"),
        responses={status.HTTP_201_CREATED: yasg_response({})},
        tags=["group"],
    )
    @view_audit_decorator(GroupTemplateCreateAuditProvider)
    def create(self, request, *args, **kwargs):
        serializer = GroupAuthorizationSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        group = self.get_object()
        data = serializer.validated_data

        templates = self.group_trans.from_group_grant_data(data["templates"])
        self.group_biz.grant(request.role, group, templates)

        # 写入审计上下文
        audit_context_setter(
            group=group,
            templates=[{"system_id": t["system_id"], "template_id": t["template_id"]} for t in data["templates"]],
        )

        return Response({}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description="用户组自定义权限列表",
        auto_schema=ResponseSwaggerAutoSchema,
        query_serializer=SystemQuerySLZ,
        responses={status.HTTP_200_OK: PolicySLZ(label="策略", many=True)},
        tags=["group"],
    )
    def list(self, request, *args, **kwargs):
        slz = SystemQuerySLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)

        system_id = slz.validated_data["system_id"]
        group = get_object_or_404(self.queryset, pk=kwargs["id"])

        subject = Subject(type=SubjectType.GROUP.value, id=str(group.id))

        policies = self.policy_query_biz.list_by_subject(system_id, subject)

        # ResourceNameAutoUpdate
        updated_policies = self.policy_operation_biz.update_due_to_renamed_resource(system_id, subject, policies)

        return Response([p.dict() for p in updated_policies])

    @swagger_auto_schema(
        operation_description="用户组删除自定义权限",
        auto_schema=ResponseSwaggerAutoSchema,
        request_body=PolicyDeleteSLZ(label="ids"),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["group"],
    )
    @view_audit_decorator(GroupPolicyDeleteAuditProvider)
    def destroy(self, request, *args, **kwargs):
        slz = PolicyDeleteSLZ(data=request.data)
        slz.is_valid(raise_exception=True)

        system_id = slz.validated_data["system_id"]
        ids = slz.validated_data["ids"]
        group = self.get_object()
        subject = Subject(type=SubjectType.GROUP.value, id=str(group.id))

        permission_logger.info("subject policy delete by user: %s", request.user.username)

        policy_list = self.policy_query_biz.query_policy_list_by_policy_ids(system_id, subject, ids)

        # 删除权限
        self.policy_operation_biz.delete_by_ids(system_id, subject, ids)

        # 写入审计上下文
        audit_context_setter(group=group, system_id=system_id, policies=policy_list.policies)

        return Response()

    @swagger_auto_schema(
        operation_description="用户组权限修改",
        auto_schema=ResponseSwaggerAutoSchema,
        request_body=GroupPolicyUpdateSLZ(label="修改策略"),
        responses={status.HTTP_200_OK: yasg_response({})},
        tags=["group"],
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
        self.group_biz.update_policies(request.role, group.id, system_id, template_id, policies)

        # 写入审计上下文
        audit_context_setter(group=group, system_id=system_id, template_id=template_id, policies=policies)

        return Response({})


class GroupSystemViewSet(GenericViewSet):

    paginator = None  # 去掉swagger中的limit offset参数
    queryset = Group.objects.all()
    lookup_field = "id"

    biz = GroupBiz()

    @swagger_auto_schema(
        operation_description="用户组有权限的所有系统列表",
        auto_schema=ResponseSwaggerAutoSchema,
        query_serializer=None,
        responses={status.HTTP_200_OK: PolicySystemSLZ(label="系统", many=True)},
        tags=["group"],
    )
    def list(self, request, *args, **kwargs):
        group = self.get_object()
        data = self.biz.list_system_counter(group.id)
        return Response([one.dict() for one in data])


class GroupTransferView(views.APIView):
    """
    用户组转出
    """

    permission_classes = [role_perm_class(PermissionCodeEnum.TRANSFER_GROUP.value)]

    role_biz = RoleBiz()

    @swagger_auto_schema(
        operation_description="用户组批量转出",
        auto_schema=ResponseSwaggerAutoSchema,
        request_body=GroupTransferSLZ(label="用户转移"),
        responses={status.HTTP_200_OK: {}},
        tags=["group"],
    )
    @view_audit_decorator(GroupTransferAuditProvider)
    def post(self, request, *args, **kwargs):
        slz = GroupTransferSLZ(data=request.data, context={"role": request.role})
        slz.is_valid(raise_exception=True)

        group_ids = slz.validated_data["group_ids"]
        role_id = slz.validated_data["role_id"]

        self.role_biz.transfer_groups_role(group_ids, role_id)

        audit_context_setter(group_ids=group_ids, role_id=role_id)

        return Response({})


class GroupTemplateConditionCompareView(GroupPermissionMixin, GenericViewSet):
    condition_biz = ConditionTagBiz()
    template_biz = TemplateBiz()

    queryset = Group.objects.all()
    lookup_field = "id"

    @swagger_auto_schema(
        operation_description="权限模板操作条件对比",
        auto_schema=ResponseSwaggerAutoSchema,
        request_body=GroupAuthoriedConditionSLZ(label="操作条件"),
        responses={status.HTTP_200_OK: ConditionTagSLZ(label="条件差异", many=True)},
        tags=["group"],
    )
    def create(self, request, *args, **kwargs):
        serializer = GroupAuthoriedConditionSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        group = self.get_object()

        action_id = data["action_id"]
        related_resource_type = data["related_resource_type"]

        new_condition = parse_obj_as(List[ConditionTagBean], related_resource_type["condition"])
        # 从模板数据中查找匹配的操作, 资源类型的条件
        template_id = kwargs["template_id"]

        subject = Subject(type=SubjectType.GROUP.value, id=str(group.id))
        authorized_template = PermTemplatePolicyAuthorized.objects.get_by_subject_template(subject, int(template_id))
        for action in authorized_template.data["actions"]:
            policy = PolicyBean.parse_obj(action)
            # 查询对应的操作
            if policy.action_id == action_id:
                # 操作操作中对应于资源类型的操作
                related_resource_type = policy.get_related_resource_type(
                    related_resource_type["system_id"], related_resource_type["type"]
                )
                old_condition = related_resource_type.condition if related_resource_type else []

                # 对比用户组已有的条件与用户提交的条件
                conditions = self.condition_biz.compare_and_tag(
                    new_condition, parse_obj_as(List[ConditionTagBean], old_condition), is_template=True
                )

                return Response([c.dict() for c in conditions])

        raise error_codes.VALIDATE_ERROR.format(_("模板: {} 没有操作: {} 的权限").format(template_id, action_id))


class GroupCustomPolicyConditionCompareView(GroupPermissionMixin, GenericViewSet):
    policy_biz = PolicyQueryBiz()
    condition_biz = ConditionTagBiz()

    queryset = Group.objects.all()
    lookup_field = "id"

    @swagger_auto_schema(
        operation_description="条件差异对比",
        request_body=ConditionCompareSLZ(label="资源条件"),
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: ConditionTagSLZ(label="条件差异", many=True)},
        tags=["group"],
    )
    def create(self, request, *args, **kwargs):
        serializer = ConditionCompareSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        group = self.get_object()
        subject = Subject(type=SubjectType.GROUP.value, id=str(group.id))

        # 1. 查询policy的condition
        related_resource_type = data["related_resource_type"]
        old_condition = self.policy_biz.get_policy_resource_type_conditions(
            subject,
            data["policy_id"],
            related_resource_type["system_id"],
            related_resource_type["type"],
        )

        # 2. 对比合并差异
        conditions = self.condition_biz.compare_and_tag(
            parse_obj_as(List[ConditionTagBean], related_resource_type["condition"]),
            parse_obj_as(List[ConditionTagBean], old_condition),
            is_template=True,
        )

        return Response([c.dict() for c in conditions])
