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

from drf_yasg.openapi import Response as yasg_response
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from backend.apps.role.serializers import RoleCommonActionSLZ
from backend.apps.subject.audit import SubjectGroupDeleteAuditProvider
from backend.apps.subject.serializers import SubjectGroupSLZ, UserRelationSLZ
from backend.apps.user.models import UserProfile
from backend.audit.audit import audit_context_setter, view_audit_decorator
from backend.biz.group import GroupBiz
from backend.biz.role import RoleBiz
from backend.common.serializers import SystemQuerySLZ
from backend.common.swagger import ResponseSwaggerAutoSchema
from backend.common.time import get_soon_expire_ts
from backend.service.constants import SubjectType
from backend.service.models import Subject

from .serializers import GroupSLZ, UserNewbieSLZ, UserNewbieUpdateSLZ

permission_logger = logging.getLogger("permission")


class UserGroupViewSet(GenericViewSet):

    paginator = None  # 去掉swagger中的limit offset参数

    biz = GroupBiz()

    @swagger_auto_schema(
        operation_description="我的权限-用户组列表",
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: SubjectGroupSLZ(label="用户组", many=True)},
        tags=["user"],
    )
    def list(self, request, *args, **kwargs):
        subject = Subject(type=SubjectType.USER.value, id=request.user.username)
        relations = self.biz.list_subject_group(subject, is_recursive=True)
        slz = GroupSLZ(instance=relations, many=True)
        return Response(slz.data)

    @swagger_auto_schema(
        operation_description="我的权限-退出用户组",
        auto_schema=ResponseSwaggerAutoSchema,
        query_serializer=UserRelationSLZ,
        responses={status.HTTP_200_OK: yasg_response({})},
        tags=["user"],
    )
    @view_audit_decorator(SubjectGroupDeleteAuditProvider)
    def destroy(self, request, *args, **kwargs):
        serializer = UserRelationSLZ(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        subject = Subject(type=SubjectType.USER.value, id=request.user.username)

        permission_logger.info("subject group delete by user: %s", request.user.username)

        if data["type"] == "group":
            group_id = data["id"]
            self.biz.remove_members(group_id, [Subject.parse_obj({"type": subject.type, "id": subject.id})])

            # 写入审计上下文
            audit_context_setter(subject=subject, group=Subject.parse_obj(data))

        return Response({})


class UserGroupRenewViewSet(GenericViewSet):

    paginator = None  # 去掉swagger中的limit offset参数

    # service
    group_biz = GroupBiz()

    @swagger_auto_schema(
        operation_description="用户即将过期用户组列表",
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: SubjectGroupSLZ(label="用户组", many=True)},
        tags=["user"],
    )
    def list(self, request, *args, **kwargs):
        subject = Subject(type=SubjectType.USER.value, id=request.user.username)
        expired_at = get_soon_expire_ts()
        relations = self.group_biz.list_subject_group_before_expired_at(subject, expired_at)
        return Response([one.dict() for one in relations])


class UserProfileNewbieViewSet(GenericViewSet):
    """
    用户配置-新手指引
    """

    paginator = None  # 去掉swagger中的limit offset参数

    @swagger_auto_schema(
        operation_description="用户配置-新手指引",
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: UserNewbieSLZ(label="新手指引", many=True)},
        tags=["user"],
    )
    def list(self, request, *args, **kwargs):
        data = UserProfile.objects.list_newbie(request.user.username)
        return Response(data)

    @swagger_auto_schema(
        operation_description="用户配置-新手指引设置",
        request_body=UserNewbieUpdateSLZ(label="场景"),
        responses={status.HTTP_200_OK: yasg_response({})},
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

    paginator = None  # 去掉swagger中的limit offset参数

    role_biz = RoleBiz()

    @swagger_auto_schema(
        operation_description="常用操作列表",
        query_serializer=SystemQuerySLZ,
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: RoleCommonActionSLZ(label="常用操作", many=True)},
        tags=["user"],
    )
    def list(self, request, *args, **kwargs):
        data = []

        system_id = request.query_params.get("system_id")
        if system_id:
            data = self.role_biz.list_system_common_actions(system_id)

        return Response([one.dict() for one in data])
