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
from copy import copy
from itertools import groupby
from typing import List

from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from drf_yasg.openapi import Response as yasg_response
from drf_yasg.utils import swagger_auto_schema
from pydantic.tools import parse_obj_as
from rest_framework import serializers, status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, mixins, views

from backend.account.permissions import RolePermission, role_perm_class
from backend.account.serializers import AccountRoleSLZ
from backend.apps.group.filters import GroupFilter
from backend.apps.group.models import Group
from backend.apps.group.serializers import GroupSLZ, MemberSLZ
from backend.apps.group.views import GroupPermissionMixin
from backend.apps.organization.models import User
from backend.apps.organization.serializers import UserInfoSLZ, UserQuerySLZ
from backend.apps.role.models import Role, RoleCommonAction, RoleRelatedObject, RoleUser
from backend.audit.audit import audit_context_setter, view_audit_decorator
from backend.biz.group import GroupBiz, GroupMemberExpiredAtBean
from backend.biz.policy import PolicyBean, PolicyBeanList
from backend.biz.role import (
    RoleBiz,
    RoleCheckBiz,
    RoleInfoBean,
    RoleListQuery,
    RoleObjectRelationChecker,
    RoleSubjectScopeChecker,
)
from backend.biz.subject import SubjectInfoList
from backend.biz.trans.role import RoleTrans
from backend.common.error_codes import error_codes
from backend.common.serializers import SystemQuerySLZ
from backend.common.swagger import PaginatedResponseSwaggerAutoSchema, ResponseSwaggerAutoSchema
from backend.common.time import get_soon_expire_ts
from backend.service.constants import PermissionCodeEnum, RoleRelatedObjectType, RoleType, SubjectType
from backend.service.models import Subject

from .audit import (
    CommonActionCreateAuditProvider,
    CommonActionDeleteAuditProvider,
    RoleCreateAuditProvider,
    RoleGroupRenewAuditProvider,
    RoleMemberCreateAuditProvider,
    RoleMemberDeleteAuditProvider,
    RoleMemberUpdateAuditProvider,
    RolePolicyAuditProvider,
    RoleUpdateAuditProvider,
    UserRoleDeleteAuditProvider,
)
from .filters import RatingMangerFilter, RoleCommonActionFilter
from .serializers import (
    GradeManagerActionSLZ,
    MemberSystemPermissionUpdateSLZ,
    RatingMangerBaseInfoSZL,
    RatingMangerCreateSLZ,
    RatingMangerDetailSchemaSLZ,
    RatingMangerDetailSLZ,
    RatingMangerListSchemaSLZ,
    RatingMangerListSLZ,
    RoleCommonActionSLZ,
    RoleCommonCreateSLZ,
    RoleGroupMembersRenewSLZ,
    RoleIdSLZ,
    RoleScopeSubjectSLZ,
    SuperManagerMemberDeleteSLZ,
    SuperManagerMemberSLZ,
    SystemManagerMemberUpdateSLZ,
    SystemManagerSLZ,
)


class GradeManagerViewSet(mixins.ListModelMixin, GenericViewSet):
    """
    分级管理员
    """

    permission_classes = [RolePermission]
    action_permission = {
        "create": PermissionCodeEnum.CREATE_RATING_MANAGER.value,
        "update": PermissionCodeEnum.MANAGE_RATING_MANAGER.value,
        "partial_update": PermissionCodeEnum.MANAGE_RATING_MANAGER.value,
    }

    lookup_field = "id"
    queryset = Role.objects.filter(type=RoleType.RATING_MANAGER.value).order_by("-updated_time")
    serializer_class = RatingMangerListSLZ
    filterset_class = RatingMangerFilter

    biz = RoleBiz()
    role_check_biz = RoleCheckBiz()

    role_trans = RoleTrans()

    def get_queryset(self):
        request = self.request
        return RoleListQuery(request.role, request.user).query_grade_manager()

    @swagger_auto_schema(
        operation_description="创建分级管理员",
        request_body=RatingMangerCreateSLZ(label="创建分级管理员"),
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_201_CREATED: RoleIdSLZ(label="分级管理员ID")},
        tags=["role"],
    )
    @view_audit_decorator(RoleCreateAuditProvider)
    def create(self, request, *args, **kwargs):
        """
        创建分级管理员
        """
        serializer = RatingMangerCreateSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = request.user.username
        data = serializer.validated_data

        # 名称唯一性检查
        self.role_check_biz.check_unique_name(data["name"])

        # 结构转换
        info = self.role_trans.from_role_data(data)
        role = self.biz.create(info, user_id)

        audit_context_setter(role=role)

        return Response({"id": role.id}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description="分级管理员列表",
        auto_schema=PaginatedResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: RatingMangerListSchemaSLZ(label="分级管理员列表", many=True)},
        tags=["role"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="分级管理员详情",
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: RatingMangerDetailSchemaSLZ(label="分级管理员详情")},
        filter_inspectors=[],
        paginator_inspectors=[],
        tags=["role"],
    )
    def retrieve(self, request, *args, **kwargs):
        role = self.get_object()
        serializer = RatingMangerDetailSLZ(instance=role)
        data = serializer.data
        return Response(data)

    @swagger_auto_schema(
        operation_description="分级管理员更新",
        request_body=RatingMangerCreateSLZ(label="更新分级管理员"),
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["role"],
    )
    @view_audit_decorator(RoleUpdateAuditProvider)
    def update(self, request, *args, **kwargs):
        role = self.get_object()
        serializer = RatingMangerCreateSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = request.user.username
        data = serializer.validated_data

        # 名称唯一性检查
        self.role_check_biz.check_unique_name(data["name"], role.name)

        # 查询已有的策略范围
        old_scopes = self.biz.list_auth_scope(role.id)
        # 查询旧的数据
        old_system_policy_list = {
            one.system_id: PolicyBeanList(one.system_id, parse_obj_as(List[PolicyBean], one.actions))
            for one in old_scopes
        }

        info = self.role_trans.from_role_data(data, old_system_policy_list=old_system_policy_list)
        self.biz.update(role, info, user_id)

        audit_context_setter(role=role)

        return Response({})

    @swagger_auto_schema(
        operation_description="分级管理员基本信息更新",
        request_body=RatingMangerBaseInfoSZL(label="更新分级管理员基本信息"),
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["role"],
    )
    @view_audit_decorator(RoleUpdateAuditProvider)
    def partial_update(self, request, *args, **kwargs):
        """仅仅做基本信息更新"""
        role = self.get_object()
        serializer = RatingMangerBaseInfoSZL(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = request.user.username
        data = serializer.validated_data

        # 非超级管理员 且 并非分级管理员成员，则无法更新基本信息
        if (
            request.role.type != RoleType.SUPER_MANAGER.value
            and not RoleUser.objects.filter(role_id=role.id, username=user_id).exists()
        ):
            raise error_codes.FORBIDDEN.format(message=_("非分级管理员({})的成员，无权限修改").format(role.name), replace=True)

        self.biz.update(role, RoleInfoBean.parse_obj(data), user_id, partial=True)

        audit_context_setter(role=role)

        return Response({})


class RoleMemberView(views.APIView):
    """
    角色退出
    """

    biz = RoleBiz()

    @swagger_auto_schema(
        operation_description="退出角色",
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: yasg_response({})},
        tags=["role"],
    )
    @view_audit_decorator(UserRoleDeleteAuditProvider)
    def delete(self, request, *args, **kwargs):
        role_id = kwargs["id"]
        user_id = request.user.username
        self.biz.delete_member(int(role_id), user_id)
        audit_context_setter(role_id=role_id)
        return Response({})

    @swagger_auto_schema(
        operation_description="角色的成员列表",
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: {}},
        tags=["role"],
    )
    def get(self, request, *args, **kwargs):
        role_id = kwargs["id"]
        return Response(list(RoleUser.objects.filter(role_id=role_id).values_list("username", flat=True)))


class RoleAuthorizationScopeView(views.APIView):
    """
    角色的授权范围查询
    """

    biz = RoleBiz()

    @swagger_auto_schema(
        operation_description="角色的授权范围",
        auto_schema=ResponseSwaggerAutoSchema,
        query_serializer=SystemQuerySLZ,
        responses={status.HTTP_200_OK: GradeManagerActionSLZ(label="操作策略", many=True)},
        tags=["role"],
    )
    def get(self, request, *args, **kwargs):
        slz = SystemQuerySLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)

        system_id = slz.validated_data["system_id"]
        scope_system = self.biz.get_auth_scope_bean_by_system(request.role.id, system_id)
        data = [one.dict() for one in scope_system.actions] if scope_system else []
        return Response(data)


class RoleSubjectScopView(views.APIView):
    """
    角色的subject授权范围
    """

    biz = RoleBiz()

    @swagger_auto_schema(
        operation_description="角色的subject授权范围",
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: RoleScopeSubjectSLZ(label="操作策略", many=True)},
        tags=["role"],
    )
    def get(self, request, *args, **kwargs):
        scopes = self.biz.list_subject_scope(request.role.id)

        subjects = SubjectInfoList(scopes).subjects if scopes else []
        return Response([one.dict() for one in subjects])


class SystemManagerViewSet(GenericViewSet):

    paginator = None  # 去掉swagger中的limit offset参数

    @swagger_auto_schema(
        operation_description="系统管理员列表",
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: SystemManagerSLZ(label="系统管理员", many=True)},
        tags=["role"],
    )
    def list(self, request, *args, **kwargs):
        query_set = Role.objects.filter(type=RoleType.SYSTEM_MANAGER.value).order_by("-updated_time")
        role = request.role
        if role.type == RoleType.SYSTEM_MANAGER.value:
            query_set = query_set.filter(id=role.id)
        serializer = SystemManagerSLZ(query_set, many=True)
        return Response(serializer.data)


class MemberSystemPermissionView(views.APIView):
    permission_classes = [role_perm_class(PermissionCodeEnum.MANAGE_SYSTEM_MANAGER_MEMBER.value)]

    biz = RoleBiz()

    @swagger_auto_schema(
        operation_description="修改系统管理员成员拥有的权限",
        request_body=MemberSystemPermissionUpdateSLZ(label="修改系统管理员成员拥有的权限"),
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: yasg_response({})},
        tags=["role"],
    )
    @view_audit_decorator(RolePolicyAuditProvider)
    def put(self, request, *args, **kwargs):
        serializer = MemberSystemPermissionUpdateSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        role_id = int(kwargs["id"])

        role = request.role
        if role.type == RoleType.SYSTEM_MANAGER.value and role.id != role_id:
            self.permission_denied(request, message=f"{request.role.id} role can not access role {role_id}")

        enabled = serializer.validated_data["system_permission_global_enabled"]

        self.biz.modify_system_manager_member_system_permission(role_id, enabled)

        audit_context_setter(role=Role.objects.filter(id=role_id).first(), enable=enabled)

        return Response({})


class SystemManagerMemberView(views.APIView):
    permission_classes = [role_perm_class(PermissionCodeEnum.MANAGE_SYSTEM_MANAGER_MEMBER.value)]

    biz = RoleBiz()

    @swagger_auto_schema(
        operation_description="修改系统管理员成员",
        request_body=SystemManagerMemberUpdateSLZ(label="修改系统管理员成员"),
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: yasg_response({})},
        tags=["role"],
    )
    @view_audit_decorator(RoleMemberUpdateAuditProvider)
    def put(self, request, *args, **kwargs):
        serializer = SystemManagerMemberUpdateSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        role_id = int(kwargs["id"])

        role = request.role
        if role.type == RoleType.SYSTEM_MANAGER.value and role.id != role_id:
            self.permission_denied(request, message=f"{request.role.id} role can not access role {role_id}")

        members = serializer.validated_data["members"]
        self.biz.modify_system_manager_members(role_id, members)

        audit_context_setter(role=role)

        return Response({})


class SuperManagerMemberViewSet(GenericViewSet):
    permission_classes = [role_perm_class(PermissionCodeEnum.MANAGE_SUPER_MANAGER_MEMBER.value)]

    paginator = None  # 去掉swagger中的limit offset参数

    biz = RoleBiz()

    @swagger_auto_schema(
        operation_description="超级管理员成员列表",
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: SuperManagerMemberSLZ(label="超级管理员成员", many=True)},
        tags=["role"],
    )
    def list(self, request, *args, **kwargs):
        role = Role.objects.get(type=RoleType.SUPER_MANAGER.value)
        enabled_users = set(role.system_permission_enabled_content.enabled_users)
        data = [{"username": i, "system_permission_enabled": i in enabled_users} for i in role.members]
        return Response(data)

    @swagger_auto_schema(
        operation_description="添加超级管理员成员",
        request_body=SuperManagerMemberSLZ(label="超级管理员成员"),
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: yasg_response({})},
        tags=["role"],
    )
    @view_audit_decorator(RoleMemberCreateAuditProvider)
    def create(self, request, *args, **kwargs):
        serializer = SuperManagerMemberSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data["username"]
        enabled = serializer.validated_data["system_permission_enabled"]
        self.biz.add_super_manager_member(username, enabled)

        audit_context_setter(role=request.role, members=[username])

        return Response({})

    @swagger_auto_schema(
        operation_description="删除超级管理员成员",
        request_body=SuperManagerMemberDeleteSLZ(label="超级管理员成员"),
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: yasg_response({})},
        tags=["role"],
    )
    @view_audit_decorator(RoleMemberDeleteAuditProvider)
    def destroy(self, request, *args, **kwargs):
        serializer = SuperManagerMemberDeleteSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data["username"]
        self.biz.delete_super_manager_member(username)

        audit_context_setter(role=request.role, members=[username])

        return Response({})

    @swagger_auto_schema(
        operation_description="修改超级管理员成员拥有的权限",
        request_body=SuperManagerMemberSLZ(label="超级管理员成员"),
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: yasg_response({})},
        tags=["role"],
    )
    @view_audit_decorator(RolePolicyAuditProvider)
    def update(self, request, *args, **kwargs):
        serializer = SuperManagerMemberSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data["username"]
        enabled = serializer.validated_data["system_permission_enabled"]
        self.biz.update_super_manager_member_system_permission(username, enabled)

        audit_context_setter(role=request.role, enable=enabled, username=username)

        return Response({})


class RoleCommonActionViewSet(GenericViewSet):
    """
    常用操作
    """

    permission_classes = [role_perm_class(PermissionCodeEnum.MANAGE_COMMON_ACTION.value)]

    paginator = None  # 去掉swagger中的limit offset参数

    queryset = RoleCommonAction.objects.all()
    serializer_class = RoleCommonActionSLZ
    filterset_class = RoleCommonActionFilter
    lookup_field = "id"

    biz = RoleBiz()

    def get_queryset(self):
        role_id = self.request.role.id
        return super().get_queryset().filter(role_id=role_id)

    @swagger_auto_schema(
        operation_description="常用操作列表",
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: RoleCommonActionSLZ(label="常用操作", many=True)},
        tags=["role"],
    )
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data

        system_id = request.query_params.get("system_id")
        if system_id:
            system_common_actions = self.biz.list_system_common_actions(system_id)
            data = [one.dict() for one in system_common_actions] + data

        return Response(data)

    @swagger_auto_schema(
        operation_description="创建常用操作",
        request_body=RoleCommonCreateSLZ(label="常用操作"),
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["role"],
    )
    @view_audit_decorator(CommonActionCreateAuditProvider)
    def create(self, request, *args, **kwargs):
        serializer = RoleCommonCreateSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        system_id = serializer.validated_data["system_id"]

        max_common_action = 20  # 常用操作最大值
        if self.queryset.filter(system_id=system_id).count() >= max_common_action:
            raise error_codes.INVALID_ARGS.format(_("系统{}的常用操作不能超过{}个").format(system_id, max_common_action))

        name = serializer.validated_data["name"]
        if RoleCommonAction.objects.filter(role_id=request.role.id).filter(Q(name=name) | Q(name_en=name)).exists():
            raise error_codes.INVALID_ARGS.format(_("名称: {} 已存在").format(name))

        instance = serializer.save(role_id=request.role.id)

        audit_context_setter(role=request.role, commonaction=instance)

        return Response({"id": instance.id}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description="删除常用操作",
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["role"],
    )
    @view_audit_decorator(CommonActionDeleteAuditProvider)
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        audit_context_setter(role=request.role, commonaction=copy(instance))

        instance.delete()

        return Response({})


class UserView(views.APIView):

    paginator = None  # 去掉swagger中的limit offset参数

    @swagger_auto_schema(
        operation_description="角色 - 根据批量Username查询用户信息",
        auto_schema=ResponseSwaggerAutoSchema,
        request_body=UserQuerySLZ(label="查询条件"),
        responses={status.HTTP_200_OK: UserInfoSLZ(label="用户信息列表", many=True)},
        tags=["role"],
    )
    def post(self, request, *args, **kwargs):
        serializer = UserQuerySLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        usernames = serializer.validated_data["usernames"]

        users = User.objects.filter(username__in=usernames)

        scope_checker = RoleSubjectScopeChecker(request.role)
        subjects = scope_checker.check([Subject(type=SubjectType.USER.value, id=u.username) for u in users], False)

        data = [
            {"username": u.username, "name": u.display_name} for u in users if u.username in {s.id for s in subjects}
        ]

        return Response(data)


class RoleGroupRenewViewSet(mixins.ListModelMixin, GenericViewSet):
    group_biz = GroupBiz()

    queryset = Group.objects.all()
    serializer_class = GroupSLZ
    filterset_class = GroupFilter

    def get_queryset(self):
        request = self.request
        group_ids = list(
            RoleRelatedObject.objects.filter(
                role_id=request.role.id, object_type=RoleRelatedObjectType.GROUP.value
            ).values_list("object_id", flat=True)
        )
        if not group_ids:
            return Group.objects.none()

        expired_at = get_soon_expire_ts()
        exist_group_ids = self.group_biz.list_exist_groups_before_expired_at(group_ids, expired_at)
        if not exist_group_ids:
            return Group.objects.none()

        return Group.objects.filter(id__in=exist_group_ids)

    @swagger_auto_schema(
        operation_description="查询角色即将过期的用户组",
        auto_schema=PaginatedResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: GroupSLZ(label="成员", many=True)},
        tags=["role"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="角色用户组成员续期",
        request_body=RoleGroupMembersRenewSLZ(label="角色用户组成员"),
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["role"],
    )
    @view_audit_decorator(RoleGroupRenewAuditProvider)
    def create(self, request, *args, **kwargs):
        serializer = RoleGroupMembersRenewSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        members = serializer.validated_data["members"]
        role = request.role

        group_ids = list({m["parent_id"] for m in members})

        checker = RoleObjectRelationChecker(role)
        if not checker.check_group_ids(group_ids):
            raise error_codes.FORBIDDEN.format(message=_("非分级管理员({})的用户组，无权限续期").format(role.name), replace=True)

        sorted_members = sorted(members, key=lambda m: m["parent_id"])
        for group_id, per_members in groupby(sorted_members, key=lambda m: m["parent_id"]):
            self.group_biz.update_members_expired_at(
                int(group_id),
                [
                    GroupMemberExpiredAtBean(type=m["type"], id=m["id"], policy_expired_at=m["expired_at"])
                    for m in per_members
                ],
            )

        audit_context_setter(role=request.role, members=members)

        return Response({})


class RoleGroupMembersRenewViewSet(GroupPermissionMixin, GenericViewSet):

    queryset = Group.objects.all()
    lookup_field = "id"

    group_biz = GroupBiz()

    @swagger_auto_schema(
        operation_description="用户组即将过期成员列表",
        auto_schema=PaginatedResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: MemberSLZ(label="成员")},
        tags=["role"],
    )
    def list(self, request, *args, **kwargs):
        group = get_object_or_404(self.queryset, pk=kwargs["id"])

        pagination = LimitOffsetPagination()
        limit = pagination.get_limit(request)
        offset = pagination.get_offset(request)

        expired_at = get_soon_expire_ts()
        count, group_members = self.group_biz.list_paging_members_before_expired_at(
            group.id, expired_at, limit, offset
        )
        return Response({"count": count, "results": [one.dict() for one in group_members]})


class AuthScopeIncludeUserRoleView(views.APIView):
    """
    授权范围包含用户的角色列表
    """

    @swagger_auto_schema(
        operation_description="授权范围包含用户的角色列表",
        auto_schema=PaginatedResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: AccountRoleSLZ(label="角色信息", many=True)},
        tags=["role"],
    )
    def get(self, request):
        q = RoleListQuery(request.role, request.user)
        roles = q.list_role_scope_include_user()
        return Response([one.dict() for one in roles])
