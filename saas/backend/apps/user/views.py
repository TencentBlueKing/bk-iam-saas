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
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from backend.account.serializers import AccountRoleSLZ
from backend.apps.role.serializers import RoleCommonActionSLZ
from backend.apps.subject.audit import SubjectGroupDeleteAuditProvider
from backend.apps.subject.serializers import SubjectGroupSLZ, UserRelationSLZ
from backend.apps.user.models import UserProfile
from backend.audit.audit import audit_context_setter, view_audit_decorator
from backend.biz.group import GroupBiz
from backend.biz.role import RoleBiz
from backend.common.pagination import CustomPageNumberPagination
from backend.common.serializers import SystemQuerySLZ
from backend.common.time import get_soon_expire_ts
from backend.service.constants import SubjectRelationType
from backend.service.models import Subject

from .serializers import GroupSLZ, QueryRoleSLZ, UserNewbieSLZ, UserNewbieUpdateSLZ


class UserGroupViewSet(GenericViewSet):

    pagination_class = CustomPageNumberPagination

    biz = GroupBiz()

    @swagger_auto_schema(
        operation_description="我的权限-用户组列表",
        responses={status.HTTP_200_OK: SubjectGroupSLZ(label="用户组", many=True)},
        tags=["user"],
    )
    def list(self, request, *args, **kwargs):
        subject = Subject.from_username(request.user.username)
        limit, offset = CustomPageNumberPagination().get_limit_offset_pair(request)
        count, relations = self.biz.list_paging_subject_group(subject, limit=limit, offset=offset)
        slz = GroupSLZ(instance=relations, many=True)
        return Response({"count": count, "results": slz.data})

    @swagger_auto_schema(
        operation_description="我的权限-退出用户组",
        query_serializer=UserRelationSLZ(),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["user"],
    )
    @view_audit_decorator(SubjectGroupDeleteAuditProvider)
    def destroy(self, request, *args, **kwargs):
        subject = Subject.from_username(request.user.username)

        serializer = UserRelationSLZ(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # 目前只支持移除用户的直接加入的用户组，不支持其通过部门关系加入的用户组
        if data["type"] == SubjectRelationType.GROUP.value:
            self.biz.remove_members(data["id"], [subject])

            # 写入审计上下文
            audit_context_setter(subject=subject, group=Subject.parse_obj(data))

        return Response({})


class UserDepartmentGroupViewSet(GenericViewSet):

    pagination_class = None

    biz = GroupBiz()

    @swagger_auto_schema(
        operation_description="我的权限-继承自部门的用户组列表",
        responses={status.HTTP_200_OK: SubjectGroupSLZ(label="用户组", many=True)},
        tags=["user"],
    )
    def list(self, request, *args, **kwargs):
        subject = Subject.from_username(request.user.username)
        # 目前只能查询所有的, 暂时不支持分页, 如果有性能问题, 需要考虑优化
        relations = self.biz.list_all_user_department_group(subject)
        slz = GroupSLZ(instance=relations, many=True)
        return Response(slz.data)


class UserGroupRenewViewSet(GenericViewSet):

    pagination_class = CustomPageNumberPagination

    # service
    group_biz = GroupBiz()

    @swagger_auto_schema(
        operation_description="用户即将过期用户组列表",
        responses={status.HTTP_200_OK: SubjectGroupSLZ(label="用户组", many=True)},
        tags=["user"],
    )
    def list(self, request, *args, **kwargs):
        subject = Subject.from_username(request.user.username)
        limit, offset = CustomPageNumberPagination().get_limit_offset_pair(request)
        expired_at = get_soon_expire_ts()
        count, relations = self.group_biz.list_paging_subject_group_before_expired_at(
            subject, expired_at=expired_at, limit=limit, offset=offset
        )
        return Response({"count": count, "results": [one.dict() for one in relations]})


class UserProfileNewbieViewSet(GenericViewSet):
    """
    用户配置-新手指引
    """

    pagination_class = None  # 去掉swagger中的limit offset参数

    @swagger_auto_schema(
        operation_description="用户配置-新手指引",
        responses={status.HTTP_200_OK: UserNewbieSLZ(label="新手指引", many=True)},
        tags=["user"],
    )
    def list(self, request, *args, **kwargs):
        data = UserProfile.objects.list_newbie(request.user.username)
        return Response(data)

    @swagger_auto_schema(
        operation_description="用户配置-新手指引设置",
        request_body=UserNewbieUpdateSLZ(label="场景"),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["user"],
    )
    def create(self, request, *args, **kwargs):
        serializer = UserNewbieUpdateSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        UserProfile.objects.update_newbie(request.user.username, data["scene"], True)

        return Response({})


class UserCommonActionViewSet(GenericViewSet):
    """
    常用操作
    """

    pagination_class = None  # 去掉swagger中的limit offset参数

    role_biz = RoleBiz()

    @swagger_auto_schema(
        operation_description="常用操作列表",
        query_serializer=SystemQuerySLZ(),
        responses={status.HTTP_200_OK: RoleCommonActionSLZ(label="常用操作", many=True)},
        tags=["user"],
    )
    def list(self, request, *args, **kwargs):
        data = []

        system_id = request.query_params.get("system_id")
        if system_id:
            data = self.role_biz.list_system_common_actions(system_id)

        return Response([one.dict() for one in data])


class RoleViewSet(GenericViewSet):

    pagination_class = None  # 去掉swagger中的limit offset参数

    biz = RoleBiz()

    @swagger_auto_schema(
        operation_description="用户角色权限",
        query_serializer=QueryRoleSLZ(label="query_role"),
        responses={status.HTTP_200_OK: AccountRoleSLZ(label="角色信息", many=True)},
        tags=["user"],
    )
    def list(self, request, *args, **kwargs):
        slz = QueryRoleSLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)
        with_perm = slz.validated_data["with_perm"]

        user_roles = self.biz.list_user_role(request.user.username, with_perm, with_hidden=False)
        return Response([one.dict() for one in user_roles])
