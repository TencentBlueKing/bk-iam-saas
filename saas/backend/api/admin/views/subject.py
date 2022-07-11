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
from django.utils.translation import gettext as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from backend.api.admin.constants import AdminAPIEnum
from backend.api.admin.permissions import AdminAPIPermission
from backend.api.admin.serializers import (
    AdminSubjectGroupSLZ,
    FreezeSubjectResponseSLZ,
    FreezeSubjectSLZ,
    SubjectRoleSLZ,
)
from backend.api.authentication import ESBAuthentication
from backend.biz.group import GroupBiz
from backend.biz.role import RoleBiz
from backend.biz.subject import SubjectBiz
from backend.common.error_codes import error_codes
from backend.common.pagination import CustomPageNumberPagination
from backend.service.models import Subject


class AdminSubjectGroupViewSet(GenericViewSet):
    """Subject的用户组"""

    pagination_class = CustomPageNumberPagination

    authentication_classes = [ESBAuthentication]
    permission_classes = [AdminAPIPermission]

    admin_api_permission = {"list": AdminAPIEnum.SUBJECT_JOINED_GROUP_LIST.value}

    group_biz = GroupBiz()

    @swagger_auto_schema(
        operation_description="Subject加入的用户组列表",
        responses={status.HTTP_200_OK: AdminSubjectGroupSLZ(label="用户组", many=True)},
        tags=["admin.subject.group"],
    )
    def list(self, request, *args, **kwargs):
        subject = Subject(type=kwargs["subject_type"], id=kwargs["subject_id"])
        # 分页参数
        limit, offset = CustomPageNumberPagination().get_limit_offset_pair(request)
        count, relations = self.group_biz.list_paging_subject_group(subject, limit=limit, offset=offset)
        results = [one.dict(include={"id", "name", "expired_at"}) for one in relations]
        return Response({"count": count, "results": results})


class AdminSubjectRoleViewSet(GenericViewSet):
    """Subject的角色列表"""

    authentication_classes = [ESBAuthentication]
    permission_classes = [AdminAPIPermission]

    admin_api_permission = {"list": AdminAPIEnum.SUBJECT_ROLE_LIST.value}

    role_biz = RoleBiz()

    @swagger_auto_schema(
        operation_description="Subject的角色列表",
        responses={status.HTTP_200_OK: SubjectRoleSLZ(label="角色信息", many=True)},
        tags=["admin.subject.group"],
    )
    def list(self, request, *args, **kwargs):
        # 分页参数
        limit, offset = CustomPageNumberPagination().get_limit_offset_pair(request)

        # subject_type should be 'user'
        subject_id = kwargs["subject_id"]

        count, data = self.role_biz.list_paging_user_role(subject_id, limit, offset)
        results = [one.dict() for one in data]
        return Response({"count": count, "results": results})


class AdminSubjectFreezeViewSet(GenericViewSet):
    """用户冻结/解冻接口"""

    authentication_classes = [ESBAuthentication]
    permission_classes = [AdminAPIPermission]
    admin_api_permission = {
        "list": AdminAPIEnum.SUBJECT_FREEZE_UNFREEZE.value,
        "freeze": AdminAPIEnum.SUBJECT_FREEZE_UNFREEZE.value,
        "unfreeze": AdminAPIEnum.SUBJECT_FREEZE_UNFREEZE.value,
    }

    pagination_class = None

    biz = SubjectBiz()

    @swagger_auto_schema(
        operation_description="冻结用户列表",
        responses={status.HTTP_200_OK: FreezeSubjectResponseSLZ(label="冻结用户", many=True)},
        tags=["admin.subject.freeze"],
    )
    def list(self, request, *args, **kwargs):
        data = self.biz.list_freezed_subjects()
        return Response(FreezeSubjectResponseSLZ(data, many=True).data)

    @swagger_auto_schema(
        operation_description="批量冻结用户",
        responses={status.HTTP_201_CREATED: serializers.Serializer()},
        tags=["admin.subject.freeze"],
    )
    def freeze(self, request, *args, **kwargs):
        serializer = FreezeSubjectSLZ(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        if not serializer.validated_data:
            raise error_codes.INVALID_ARGS.format(_("至少传递一个用户"))

        # 特殊逻辑, admin不能被接口冻结, 防止生产事故; 如果确定要冻结admin, 通过后台数据库特殊处理
        for d in serializer.data:
            if d["id"].lower() == "admin":
                raise error_codes.INVALID_ARGS.format(_("admin用户不允许被冻结"))

        self.biz.freeze_users(serializer.data)
        return Response({}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description="冻结用户列表",
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["admin.subject.freeze"],
    )
    def unfreeze(self, request, *args, **kwargs):
        serializer = FreezeSubjectSLZ(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        if not serializer.validated_data:
            raise error_codes.INVALID_ARGS.format(_("至少传递一个用户"))

        self.biz.unfreeze_users(serializer.data)
        return Response({}, status=status.HTTP_200_OK)
