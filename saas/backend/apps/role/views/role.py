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

from django.db.models import Case, Q, Value, When
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
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
from backend.apps.role.audit import (
    CommonActionCreateAuditProvider,
    CommonActionDeleteAuditProvider,
    RoleCreateAuditProvider,
    RoleGroupRenewAuditProvider,
    RoleMemberCreateAuditProvider,
    RoleMemberDeleteAuditProvider,
    RoleMemberUpdateAuditProvider,
    RolePolicyAuditProvider,
    RoleUpdateAuditProvider,
)
from backend.apps.role.filters import GradeMangerFilter, RoleCommonActionFilter, RoleSearchFilter
from backend.apps.role.models import Role, RoleCommonAction, RoleRelatedObject, RoleRelation, RoleUser
from backend.apps.role.serializers import (
    BaseGradeMangerSchemaSLZ,
    BaseGradeMangerSLZ,
    GradeManagerActionSLZ,
    GradeManagerListSLZ,
    GradeMangerBaseInfoSLZ,
    GradeMangerCreateSLZ,
    GradeMangerDetailSchemaSLZ,
    GradeMangerDetailSLZ,
    GradeMangerListSchemaSLZ,
    MemberSystemPermissionUpdateSLZ,
    RoleCommonActionSLZ,
    RoleCommonCreateSLZ,
    RoleGroupMembersRenewSLZ,
    RoleIdSLZ,
    RoleScopeSubjectSLZ,
    RoleSearchSLZ,
    RoleSubjectCheckSLZ,
    SubsetMangerCreateSLZ,
    SubsetMangerDetailSLZ,
    SuperManagerMemberDeleteSLZ,
    SuperManagerMemberSLZ,
    SystemManagerMemberUpdateSLZ,
    SystemManagerSLZ,
)
from backend.audit.audit import audit_context_setter, view_audit_decorator
from backend.biz.group import GroupBiz, GroupMemberExpiredAtBean
from backend.biz.helper import RoleWithPermGroupBiz
from backend.biz.policy import PolicyBean, PolicyBeanList
from backend.biz.role import (
    RoleBiz,
    RoleCheckBiz,
    RoleInfoBean,
    RoleListQuery,
    RoleObjectRelationChecker,
    RoleSubjectScopeChecker,
    can_user_manage_role,
)
from backend.biz.subject import SubjectInfoList
from backend.common.error_codes import error_codes
from backend.common.lock import gen_role_upsert_lock
from backend.common.serializers import SystemQuerySLZ
from backend.common.time import get_soon_expire_ts
from backend.service.constants import GroupSaaSAttributeEnum, PermissionCodeEnum, RoleRelatedObjectType, RoleType
from backend.service.models import Subject
from backend.trans.role import RoleTrans


class GradeManagerViewSet(mixins.ListModelMixin, GenericViewSet):
    """
    分级管理员
    """

    permission_classes = [RolePermission]
    action_permission = {
        "create": PermissionCodeEnum.CREATE_GRADE_MANAGER.value,
        "update": PermissionCodeEnum.MANAGE_GRADE_MANAGER.value,
    }

    lookup_field = "id"
    queryset = Role.objects.filter(type=RoleType.GRADE_MANAGER.value).order_by("-updated_time")
    serializer_class = GradeManagerListSLZ
    filterset_class = GradeMangerFilter

    biz = RoleBiz()
    group_biz = GroupBiz()
    role_check_biz = RoleCheckBiz()

    role_trans = RoleTrans()

    def get_queryset(self):
        request = self.request
        return RoleListQuery(request.role, request.user).query_grade_manager(
            with_super=bool(request.query_params.get("with_super", False))
        )

    @swagger_auto_schema(
        operation_description="创建分级管理员",
        request_body=GradeMangerCreateSLZ(label="创建分级管理员"),
        responses={status.HTTP_201_CREATED: RoleIdSLZ(label="分级管理员ID")},
        tags=["role"],
    )
    @view_audit_decorator(RoleCreateAuditProvider)
    def create(self, request, *args, **kwargs):
        """
        创建分级管理员
        """
        serializer = GradeMangerCreateSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = request.user.username
        data = serializer.validated_data

        # 结构转换
        info = self.role_trans.from_role_data(data)

        with gen_role_upsert_lock(data["name"]):
            # 名称唯一性检查
            self.role_check_biz.check_grade_manager_unique_name(data["name"])

            role = self.biz.create_grade_manager(info, user_id)

        # 创建同步权限用户组
        if info.sync_perm:
            self.group_biz.create_sync_perm_group_by_role(
                role,
                user_id,
                attrs={
                    GroupSaaSAttributeEnum.SOURCE_FROM_ROLE.value: True,
                },
            )

        audit_context_setter(role=role)

        return Response({"id": role.id}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description="分级管理员列表",
        responses={status.HTTP_200_OK: GradeMangerListSchemaSLZ(label="分级管理员列表", many=True)},
        tags=["role"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="分级管理员详情",
        responses={status.HTTP_200_OK: GradeMangerDetailSchemaSLZ(label="分级管理员详情")},
        filter_inspectors=[],
        paginator_inspectors=[],
        tags=["role"],
    )
    def retrieve(self, request, *args, **kwargs):
        role = self.get_object()
        serializer = GradeMangerDetailSLZ(instance=role)
        data = serializer.data
        return Response(data)

    @swagger_auto_schema(
        operation_description="分级管理员更新",
        request_body=GradeMangerCreateSLZ(label="更新分级管理员"),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["role"],
    )
    @view_audit_decorator(RoleUpdateAuditProvider)
    def update(self, request, *args, **kwargs):
        role = self.get_object()
        serializer = GradeMangerCreateSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = request.user.username
        data = serializer.validated_data

        # 检查成员数量是否满足限制
        self.role_check_biz.check_member_count(role.id, len(data["members"]))

        # 查询已有的策略范围
        old_scopes = self.biz.list_auth_scope(role.id)
        # 查询旧的数据
        old_system_policy_list = {
            one.system_id: PolicyBeanList(one.system_id, parse_obj_as(List[PolicyBean], one.actions))
            for one in old_scopes
        }

        info = self.role_trans.from_role_data(data, old_system_policy_list=old_system_policy_list)

        with gen_role_upsert_lock(data["name"]):
            # 名称唯一性检查
            self.role_check_biz.check_grade_manager_unique_name(data["name"], role.name)

            self.biz.update(role, info, user_id)

        # 更新同步权限用户组信息
        self.group_biz.update_sync_perm_group_by_role(self.get_object(), user_id, sync_members=True, sync_prem=True)

        audit_context_setter(role=role)

        return Response({})

    @swagger_auto_schema(
        operation_description="分级管理员基本信息更新",
        request_body=GradeMangerBaseInfoSLZ(label="更新分级管理员基本信息"),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["role"],
    )
    @view_audit_decorator(RoleUpdateAuditProvider)
    def partial_update(self, request, *args, **kwargs):
        """仅仅做基本信息更新"""
        role = self.get_object()
        serializer = GradeMangerBaseInfoSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = request.user.username
        data = serializer.validated_data

        # 检查成员数量是否满足限制
        self.role_check_biz.check_member_count(role.id, len(data["members"]))

        # 检查新增成员是否已超所有加入分级管理员的限制
        old_members = set(RoleUser.objects.filter(role_id=role.id).values_list("username", flat=True))
        for member in data["members"]:
            if member["username"] in old_members:
                continue
            # subject加入的分级管理员数量不能超过最大值
            self.role_check_biz.check_subject_grade_manager_limit(Subject.from_username(member["username"]))

        if not can_user_manage_role(user_id, role.id):
            raise error_codes.FORBIDDEN.format(message=_("非分级管理员({})的成员，无权限修改").format(role.name), replace=True)

        with gen_role_upsert_lock(data["name"]):
            # 名称唯一性检查
            self.role_check_biz.check_grade_manager_unique_name(data["name"], role.name)

            self.biz.update(role, RoleInfoBean.from_partial_data(data), user_id)

        # 更新同步权限用户组信息
        self.group_biz.update_sync_perm_group_by_role(self.get_object(), user_id, sync_members=True)

        audit_context_setter(role=role)

        return Response({})


class RoleMemberView(views.APIView):
    """
    角色退出
    """

    role_with_perm_group_biz = RoleWithPermGroupBiz()

    @swagger_auto_schema(
        operation_description="退出角色",
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["role"],
    )
    @view_audit_decorator(RoleMemberDeleteAuditProvider)
    def delete(self, request, *args, **kwargs):
        role_id = kwargs["id"]
        user_id = request.user.username
        role = Role.objects.filter(id=int(role_id)).first()
        if role:
            self.role_with_perm_group_biz.delete_role_member(role, user_id, user_id)

        audit_context_setter(role=role, members=[user_id])
        return Response({})

    @swagger_auto_schema(
        operation_description="角色的成员列表",
        responses={status.HTTP_200_OK: serializers.Serializer()},
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
        query_serializer=SystemQuerySLZ(),
        responses={status.HTTP_200_OK: GradeManagerActionSLZ(label="操作策略", many=True)},
        tags=["role"],
    )
    def get(self, request, *args, **kwargs):
        slz = SystemQuerySLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)

        system_id = slz.validated_data["system_id"]
        # ResourceNameAutoUpdate
        scope_system = self.biz.get_auth_scope_bean_by_system(
            request.role.id, system_id, should_auto_update_resource_name=True
        )
        data = [one.dict() for one in scope_system.actions] if scope_system else []
        return Response(data)


class RoleSubjectScopeView(views.APIView):
    """
    角色的subject授权范围
    """

    biz = RoleBiz()

    @swagger_auto_schema(
        operation_description="角色的subject授权范围",
        responses={status.HTTP_200_OK: RoleScopeSubjectSLZ(label="操作策略", many=True)},
        tags=["role"],
    )
    def get(self, request, *args, **kwargs):
        scopes = self.biz.list_subject_scope(request.role.id)

        subjects = SubjectInfoList(scopes).subjects if scopes else []
        return Response([one.dict() for one in subjects])


class SystemManagerViewSet(GenericViewSet):

    pagination_class = None  # 去掉swagger中的limit offset参数

    @swagger_auto_schema(
        operation_description="系统管理员列表",
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
        responses={status.HTTP_200_OK: serializers.Serializer()},
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
        responses={status.HTTP_200_OK: serializers.Serializer()},
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

        role = Role.objects.filter(id=role_id).first()
        audit_context_setter(role=role)

        return Response({})


class SuperManagerMemberViewSet(GenericViewSet):
    permission_classes = [role_perm_class(PermissionCodeEnum.MANAGE_SUPER_MANAGER_MEMBER.value)]

    pagination_class = None  # 去掉swagger中的limit offset参数

    biz = RoleBiz()

    @swagger_auto_schema(
        operation_description="超级管理员成员列表",
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
        responses={status.HTTP_200_OK: serializers.Serializer()},
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
        responses={status.HTTP_200_OK: serializers.Serializer()},
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
        responses={status.HTTP_200_OK: serializers.Serializer()},
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

    pagination_class = None  # 去掉swagger中的limit offset参数

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

    pagination_class = None  # 去掉swagger中的limit offset参数

    @swagger_auto_schema(
        operation_description="角色 - 根据批量Username查询用户信息",
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
        subjects = scope_checker.check([Subject.from_username(u.username) for u in users], False)

        data = [
            {"username": u.username, "name": u.display_name, "departments": [d.full_name for d in u.departments]}
            for u in users
            if u.username in {s.id for s in subjects}
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
        responses={status.HTTP_200_OK: GroupSLZ(label="成员", many=True)},
        tags=["role"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="角色用户组成员续期",
        request_body=RoleGroupMembersRenewSLZ(label="角色用户组成员"),
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
            raise error_codes.FORBIDDEN.format(message=_("非管理员({})的用户组，无权限续期").format(role.name), replace=True)

        sorted_members = sorted(members, key=lambda m: m["parent_id"])
        for group_id, per_members in groupby(sorted_members, key=lambda m: m["parent_id"]):
            self.group_biz.update_members_expired_at(
                int(group_id),
                [
                    GroupMemberExpiredAtBean(type=m["type"], id=m["id"], expired_at=m["expired_at"])
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
        responses={status.HTTP_200_OK: AccountRoleSLZ(label="角色信息", many=True)},
        tags=["role"],
    )
    def get(self, request):
        q = RoleListQuery(request.role, request.user)
        roles = q.list_role_scope_include_user()
        return Response([one.dict() for one in roles])


class SubsetManagerViewSet(mixins.ListModelMixin, GenericViewSet):
    """
    子集管理员
    """

    permission_classes = [RolePermission]
    action_permission = {
        "create": PermissionCodeEnum.CREATE_SUBSET_MANAGER.value,
        "update": PermissionCodeEnum.MANAGE_SUBSET_MANAGER.value,
    }

    lookup_field = "id"
    queryset = Role.objects.filter(type=RoleType.SUBSET_MANAGER.value).order_by("-updated_time")
    serializer_class = BaseGradeMangerSLZ
    filterset_class = GradeMangerFilter

    biz = RoleBiz()
    group_biz = GroupBiz()
    role_check_biz = RoleCheckBiz()

    role_trans = RoleTrans()

    def get_queryset(self):
        request = self.request
        return RoleListQuery(request.role, request.user).query_subset_manager()

    @swagger_auto_schema(
        operation_description="子集管理员列表",
        responses={status.HTTP_200_OK: BaseGradeMangerSchemaSLZ(label="子集管理员列表", many=True)},
        tags=["role"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="子集管理员详情",
        responses={status.HTTP_200_OK: GradeMangerDetailSchemaSLZ(label="子集管理员详情")},
        filter_inspectors=[],
        paginator_inspectors=[],
        tags=["role"],
    )
    def retrieve(self, request, *args, **kwargs):
        role = self.get_object()
        serializer = SubsetMangerDetailSLZ(instance=role)
        data = serializer.data
        return Response(data)

    def get_object(self):
        queryset = Role.objects.filter(type=RoleType.SUBSET_MANAGER.value)

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
            "Expected view %s to be called with a URL keyword argument "
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            "attribute on the view correctly." % (self.__class__.__name__, lookup_url_kwarg)
        )

        if not can_user_manage_role(self.request.user.username, int(self.kwargs[lookup_url_kwarg])):
            queryset = queryset.none()

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    @swagger_auto_schema(
        operation_description="创建子集管理员",
        request_body=SubsetMangerCreateSLZ(label="创建子集管理员"),
        responses={status.HTTP_201_CREATED: RoleIdSLZ(label="子集管理员ID")},
        tags=["role"],
    )
    @view_audit_decorator(RoleCreateAuditProvider)
    def create(self, request, *args, **kwargs):
        """
        创建子集管理员
        """
        serializer = SubsetMangerCreateSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = request.user.username
        data = serializer.validated_data
        grade_manager = request.role

        # 名称唯一性检查, 检查在分级管理员下唯一
        self.role_check_biz.check_subset_manager_unique_name(grade_manager, data["name"])

        # 结构转换
        info = self.role_trans.from_role_data(data, _type=RoleType.SUBSET_MANAGER.value)

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
        role = self.biz.create_subset_manager(grade_manager, info, user_id)

        # 创建同步权限用户组
        if info.sync_perm:
            self.group_biz.create_sync_perm_group_by_role(
                role,
                user_id,
                attrs={
                    GroupSaaSAttributeEnum.SOURCE_FROM_ROLE.value: True,
                },
            )

        audit_context_setter(role=role)

        return Response({"id": role.id}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description="子集管理员更新",
        request_body=SubsetMangerCreateSLZ(label="子集分级管理员"),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["role"],
    )
    @view_audit_decorator(RoleUpdateAuditProvider)
    def update(self, request, *args, **kwargs):
        role = self.get_object()
        serializer = SubsetMangerCreateSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = request.user.username
        data = serializer.validated_data
        grade_manager = request.role

        # 名称唯一性检查
        self.role_check_biz.check_subset_manager_unique_name(grade_manager, data["name"], role.name)
        # 检查成员数量是否满足限制
        self.role_check_biz.check_member_count(role.id, len(data["members"]))

        # 查询已有的策略范围
        old_scopes = self.biz.list_auth_scope(role.id)
        # 查询旧的数据
        old_system_policy_list = {
            one.system_id: PolicyBeanList(one.system_id, parse_obj_as(List[PolicyBean], one.actions))
            for one in old_scopes
        }

        info = self.role_trans.from_role_data(
            data, old_system_policy_list=old_system_policy_list, _type=RoleType.SUBSET_MANAGER.value
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

        self.biz.update(role, info, user_id)

        # 更新同步权限用户组信息
        self.group_biz.update_sync_perm_group_by_role(self.get_object(), user_id, sync_members=True, sync_prem=True)

        audit_context_setter(role=role)

        return Response({})

    @swagger_auto_schema(
        operation_description="子集管理员基本信息更新",
        request_body=GradeMangerBaseInfoSLZ(label="更新子集管理员基本信息"),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["role"],
    )
    @view_audit_decorator(RoleUpdateAuditProvider)
    def partial_update(self, request, *args, **kwargs):
        """仅仅做基本信息更新"""
        role = self.get_object()
        serializer = GradeMangerBaseInfoSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = request.user.username
        data = serializer.validated_data
        grade_manager = request.role

        # 名称唯一性检查
        self.role_check_biz.check_subset_manager_unique_name(grade_manager, data["name"], role.name)
        # 检查成员数量是否满足限制
        self.role_check_biz.check_member_count(role.id, len(data["members"]))

        # 非分级管理员/子集管理员成员，则无法更新基本信息
        if not can_user_manage_role(user_id, role.id):
            raise error_codes.FORBIDDEN.format(message=_("非管理员({})的成员，无权限修改").format(role.name), replace=True)

        self.biz.update(role, RoleInfoBean.from_partial_data(data), user_id)

        # 更新同步权限用户组信息
        self.group_biz.update_sync_perm_group_by_role(self.get_object(), user_id, sync_members=True)

        audit_context_setter(role=role)

        return Response({})


class UserSubsetManagerViewSet(mixins.ListModelMixin, GenericViewSet):
    """
    用户加入的子集管理员列表
    """

    lookup_field = "id"
    queryset = Role.objects.filter(type=RoleType.SUBSET_MANAGER.value).order_by("-updated_time")
    serializer_class = BaseGradeMangerSLZ

    def get_queryset(self):
        grade_manager_id = self.kwargs["id"]
        subset_manager_ids = list(
            RoleRelation.objects.filter(parent_id=grade_manager_id).values_list("role_id", flat=True)
        )
        if not subset_manager_ids:
            return Role.objects.none()

        # 如果用户是分级管理员成员返回所有的二级管理员
        if RoleUser.objects.user_role_exists(self.request.user.username, grade_manager_id):
            return self.queryset.filter(id__in=subset_manager_ids)

        # 筛选出用户加入的子集管理员id
        role_ids = list(
            RoleUser.objects.filter(role_id__in=subset_manager_ids, username=self.request.user.username).values_list(
                "role_id", flat=True
            )
        )
        if not role_ids:
            return Role.objects.none()

        return self.queryset.filter(id__in=role_ids)

    @swagger_auto_schema(
        operation_description="用户加入的子集管理员列表",
        responses={status.HTTP_200_OK: BaseGradeMangerSchemaSLZ(label="子集管理员列表", many=True)},
        tags=["role"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class RoleSubjectScopCheckView(views.APIView):
    @swagger_auto_schema(
        operation_description="检查角色成员范围是否满足条件",
        request_body=RoleSubjectCheckSLZ(label="授权对象"),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["role"],
    )
    def post(self, request, *args, **kwargs):
        """
        检查角色成员范围是否满足条件
        """
        serializer = RoleSubjectCheckSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        scope_checker = RoleSubjectScopeChecker(request.role)
        exist_subjects = scope_checker.check(
            parse_obj_as(List[Subject], serializer.validated_data["subjects"]), raise_exception=False
        )

        return Response([one.dict() for one in exist_subjects])


class RoleSearchViewSet(mixins.ListModelMixin, GenericViewSet):
    """
    管理员搜索
    """

    queryset = Role.objects.filter(type__in=[RoleType.GRADE_MANAGER.value, RoleType.SUBSET_MANAGER.value]).order_by(
        "-updated_time"
    )
    serializer_class = RoleSearchSLZ
    filterset_class = RoleSearchFilter

    def get_queryset(self):
        queryset = self.queryset
        if bool(self.request.query_params.get("with_super", False)):
            type_order = Case(
                When(type=RoleType.SUPER_MANAGER.value, then=Value(1)),
                When(type=RoleType.SYSTEM_MANAGER.value, then=Value(2)),
                default=Value(3),
            )
            queryset = Role.objects.alias(type_order=type_order).order_by("type_order", "-updated_time")

        # 作为超级管理员时，可以管理所有分级管理员
        if RoleListQuery(self.request.role, self.request.user).is_user_super_manager(self.request.user):
            return queryset

        # 普通用户只能查询到自己加入的管理员
        role_ids = list(RoleUser.objects.filter(username=self.request.user.username).values_list("role_id", flat=True))
        subset_manager_ids = list(
            RoleRelation.objects.filter(parent_id__in=role_ids).values_list("role_id", flat=True)
        )
        return queryset.filter(id__in=set(subset_manager_ids + role_ids))

    @swagger_auto_schema(
        operation_description="管理员搜索",
        responses={status.HTTP_200_OK: RoleSearchSLZ(label="分级管理员列表", many=True)},
        tags=["role"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
