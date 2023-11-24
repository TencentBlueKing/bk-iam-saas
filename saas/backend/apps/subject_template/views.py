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
from functools import wraps
from typing import List

from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from drf_yasg.utils import swagger_auto_schema
from pydantic import parse_obj_as
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from backend.account.permissions import RolePermission, role_perm_class
from backend.apps.group.models import Group
from backend.apps.group.serializers import SearchMemberSLZ
from backend.apps.subject_template.models import SubjectTemplate, SubjectTemplateGroup, SubjectTemplateRelation
from backend.audit.audit import audit_context_setter, log_api_event, view_audit_decorator
from backend.biz.group import GroupCheckBiz
from backend.biz.role import RoleListQuery
from backend.biz.subject_template import SubjectTemplateBiz, SubjectTemplateCheckBiz
from backend.common.error_codes import error_codes
from backend.common.filters import NoCheckModelFilterBackend
from backend.common.lock import gen_subject_template_upsert_lock
from backend.service.constants import PermissionCodeEnum
from backend.service.models import Subject

from .audit import (
    SubjectTemplateCreateAuditProvider,
    SubjectTemplateDeleteAuditProvider,
    SubjectTemplateGroupDeleteAuditProvider,
    SubjectTemplateMemberCreateAuditProvider,
    SubjectTemplateUpdateAuditProvider,
)
from .filters import SubjectTemplateFilter, SubjectTemplateGroupFilter
from .serializers import (
    BaseSubjectTemplateSLZ,
    SubjectTemplateCreateSLZ,
    SubjectTemplateGroupIdSLZ,
    SubjectTemplateGroupOutputSLZ,
    SubjectTemplateGroupSLZ,
    SubjectTemplateIdSLZ,
    SubjectTemplateListSLZ,
    SubjectTemplateMemberListSLZ,
    SubjectTemplateMemberSLZ,
    SubjectTemplatesAddMemberSLZ,
)

logger = logging.getLogger("app")


def check_readonly_subject_template(func):
    """人员可读检测"""

    @wraps(func)
    def decorate(view, request, *args, **kwargs):
        subject_template = view.get_object()
        if subject_template.readonly:
            raise error_codes.FORBIDDEN.format(message=_("只读人员模版({})禁止变更").format(subject_template.id), replace=True)

        response = func(view, request, *args, **kwargs)
        return response

    return decorate


class SubjectTemplateQueryMixin:
    def get_queryset(self):
        request = self.request
        return RoleListQuery(request.role, request.user).query_subject_template()


class SubjectTemplateViewSet(SubjectTemplateQueryMixin, ModelViewSet):

    permission_classes = [RolePermission]
    action_permission = {
        "create": PermissionCodeEnum.MANAGE_SUBJECT_TEMPLATE.value,
        "update": PermissionCodeEnum.MANAGE_SUBJECT_TEMPLATE.value,
        "destroy": PermissionCodeEnum.MANAGE_SUBJECT_TEMPLATE.value,
    }

    queryset = SubjectTemplate.objects.all()
    lookup_field = "id"
    filterset_class = SubjectTemplateFilter

    check_biz = SubjectTemplateCheckBiz()
    biz = SubjectTemplateBiz()

    @swagger_auto_schema(
        operation_description="创建人员模版",
        request_body=SubjectTemplateCreateSLZ(label="人员模版"),
        responses={status.HTTP_201_CREATED: SubjectTemplateIdSLZ(label="人员模版ID")},
        tags=["subject-template"],
    )
    @view_audit_decorator(SubjectTemplateCreateAuditProvider)
    def create(self, request, *args, **kwargs):
        serializer = SubjectTemplateCreateSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = request.user.username
        data = serializer.validated_data

        # 人员模版数量在角色内是否超限
        self.check_biz.check_role_subject_template_limit(request.role, 1)

        with gen_subject_template_upsert_lock(request.role.id):
            # 人员模版名称在角色内唯一
            self.check_biz.check_role_subject_template_name_unique(request.role.id, data["name"])

            # 创建人员模版
            subject_template = self.biz.create(
                request.role, data["name"], data["description"], user_id, parse_obj_as(List[Subject], data["subjects"])
            )

        # 写入审计上下文
        audit_context_setter(template=subject_template)

        return Response({"id": subject_template.id})

    @swagger_auto_schema(
        operation_description="更新人员模版",
        request_body=BaseSubjectTemplateSLZ(label="人员模版"),
        responses={status.HTTP_200_OK: BaseSubjectTemplateSLZ(label="人员模版ID")},
        tags=["subject-template"],
    )
    @view_audit_decorator(SubjectTemplateUpdateAuditProvider)
    @check_readonly_subject_template
    def update(self, request, *args, **kwargs):
        template = self.get_object()
        serializer = BaseSubjectTemplateSLZ(template, data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = request.user.username
        data = serializer.validated_data

        with gen_subject_template_upsert_lock(request.role.id):
            # 用户组名称在角色内唯一
            self.check_biz.check_role_subject_template_name_unique(request.role.id, data["name"], template.id)

            template.name = data["name"]
            template.description = data["description"]
            template.updater = user_id
            template.save(update_fields=["name", "description", "updater"])

        # 写入审计上下文
        audit_context_setter(template=template)

        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="人员模版列表",
        responses={status.HTTP_200_OK: SubjectTemplateListSLZ(label="用户组", many=True)},
        tags=["subject-template"],
    )
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        serializer = SubjectTemplateListSLZ(
            page, many=True, context={"group_count_dict": self.biz.get_group_count_dict([t.id for t in page])}
        )
        return self.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_description="人员模版详情",
        responses={status.HTTP_200_OK: SubjectTemplateListSLZ(label="用户组")},
        tags=["subject-template"],
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = SubjectTemplateListSLZ(
            instance, context={"group_count_dict": self.biz.get_group_count_dict([instance.id])}
        )
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="删除人员模版",
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["subject-template"],
    )
    @view_audit_decorator(SubjectTemplateDeleteAuditProvider)
    @check_readonly_subject_template
    def destroy(self, request, *args, **kwargs):
        template = self.get_object()

        self.biz.delete(template.id)

        # 写入审计上下文
        audit_context_setter(template=template)

        return Response({})


class SubjectTemplateMemberViewSet(SubjectTemplateQueryMixin, GenericViewSet):

    permission_classes = [RolePermission]
    action_permission = {
        "create": PermissionCodeEnum.MANAGE_SUBJECT_TEMPLATE.value,
        "destroy": PermissionCodeEnum.MANAGE_SUBJECT_TEMPLATE.value,
    }

    queryset = SubjectTemplate.objects.all()
    lookup_field = "id"

    check_biz = SubjectTemplateCheckBiz()
    biz = SubjectTemplateBiz()
    group_check_biz = GroupCheckBiz()

    @swagger_auto_schema(
        operation_description="添加人员模版成员",
        request_body=SubjectTemplateMemberSLZ(label="人员模版"),
        responses={status.HTTP_201_CREATED: serializers.Serializer()},
        tags=["subject-template"],
    )
    @view_audit_decorator(SubjectTemplateMemberCreateAuditProvider)
    @check_readonly_subject_template
    def create(self, request, *args, **kwargs):
        template = self.get_object()
        serializer = SubjectTemplateMemberSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        subjects = parse_obj_as(List[Subject], serializer.validated_data["subjects"])

        # 检查人员在管理员的范围内
        self.group_check_biz.check_role_subject_scope(request.role, subjects)

        self.check_biz.check_member_count(template.id, len(subjects))

        self.biz.add_members(template.id, subjects)

        # 写入审计上下文
        audit_context_setter(template=template, subjects=[m.dict() for m in subjects])

        return Response({})

    @swagger_auto_schema(
        operation_description="删除人员模版成员",
        request_body=SubjectTemplateMemberSLZ(label="人员模版"),
        responses={status.HTTP_201_CREATED: serializers.Serializer()},
        tags=["subject-template"],
    )
    @view_audit_decorator(SubjectTemplateMemberCreateAuditProvider)
    @check_readonly_subject_template
    def destroy(self, request, *args, **kwargs):
        template = self.get_object()
        serializer = SubjectTemplateMemberSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        subjects = parse_obj_as(List[Subject], serializer.validated_data["subjects"])
        self.biz.delete_members(template.id, subjects)

        # 写入审计上下文
        audit_context_setter(template=template, subjects=[m.dict() for m in subjects])

        return Response({})

    @swagger_auto_schema(
        operation_description="人员模版成员列表",
        responses={status.HTTP_200_OK: SubjectTemplateMemberListSLZ(label="成员", many=True)},
        tags=["subject-template"],
    )
    def list(self, request, *args, **kwargs):
        template = self.get_object()

        if request.query_params.get("keyword"):
            slz = SearchMemberSLZ(data=request.query_params)
            slz.is_valid(raise_exception=True)
            keyword = slz.validated_data["keyword"].lower()

            group_members = self.biz.search_member_by_keyword(template.id, keyword)

            return Response({"results": SubjectTemplateMemberListSLZ(group_members, many=True).data})

        queryset = SubjectTemplateRelation.objects.filter(template_id=template.id)
        page = self.paginate_queryset(queryset)

        # 填充数据
        group_members = self.biz.convert_to_subject_template_members(page)
        return self.get_paginated_response(SubjectTemplateMemberListSLZ(group_members, many=True).data)


class SubjectTemplatesMemberCreateViewSet(SubjectTemplateQueryMixin, GenericViewSet):

    permission_classes = [
        role_perm_class(
            PermissionCodeEnum.MANAGE_SUBJECT_TEMPLATE.value,
        )
    ]

    queryset = SubjectTemplate.objects.all()

    check_biz = SubjectTemplateCheckBiz()
    biz = SubjectTemplateBiz()
    group_check_biz = GroupCheckBiz()

    # 批量添加成员
    @swagger_auto_schema(
        operation_description="批量人员模版添加成员",
        request_body=SubjectTemplatesAddMemberSLZ(label="成员"),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["subject-template"],
    )
    def create(self, request, *args, **kwargs):
        serializer = SubjectTemplatesAddMemberSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        template_ids = data["template_ids"]

        # 添加成员 异常信息记录
        failed_info = {}
        # 成员Dict结构转换为Subject结构，并去重
        members = list(set(parse_obj_as(List[Subject], data["subjects"])))

        # 检查人员在管理员的范围内
        self.group_check_biz.check_role_subject_scope(request.role, members)

        templates = self.get_queryset().filter(id__in=template_ids)
        for template in templates:
            if template.readonly:
                raise error_codes.FORBIDDEN.format(message=_("只读人员模版({})禁止变更").format(template.id), replace=True)

            try:
                # 校验用户组数量是否超限
                self.check_biz.check_member_count(template.id, len(members))

                self.biz.add_members(template.id, members)

            except Exception as e:  # pylint: disable=broad-except noqa
                failed_info.update({template.name: "{}".format(e)})

            else:
                try:
                    # 写入审计上下文
                    audit_context_setter(template=template, subjects=[m.dict() for m in members])
                    provider = SubjectTemplateMemberCreateAuditProvider(request)
                    log_api_event(request, provider)
                except Exception:  # pylint: disable=broad-except
                    logger.exception("save audit event fail")

        if not failed_info:
            return Response({}, status=status.HTTP_201_CREATED)

        raise error_codes.ACTIONS_PARTIAL_FAILED.format(failed_info)


class SubjectTemplateGroupViewSet(SubjectTemplateQueryMixin, GenericViewSet):

    permission_classes = [RolePermission]
    action_permission = {
        "destroy": PermissionCodeEnum.MANAGE_SUBJECT_TEMPLATE.value,
    }

    queryset = SubjectTemplate.objects.all()
    lookup_field = "id"

    filterset_class = SubjectTemplateGroupFilter
    filter_backends = [NoCheckModelFilterBackend]

    biz = SubjectTemplateBiz()

    @swagger_auto_schema(
        operation_description="人员模版关联用户组列表",
        responses={status.HTTP_200_OK: SubjectTemplateGroupSLZ(label="用户组", many=True)},
        tags=["subject-template"],
    )
    def list(self, request, *args, **kwargs):
        template = get_object_or_404(self.queryset, pk=kwargs["id"])

        subject_template_groups = list(
            SubjectTemplateGroup.objects.filter(template_id=template.id).values(
                "group_id", "expired_at", "created_time"
            )
        )
        queryset = Group.objects.filter(id__in=[one["group_id"] for one in subject_template_groups])
        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)

        serializer = SubjectTemplateGroupOutputSLZ(
            page,
            many=True,
            context={"template_dict": {one["group_id"]: one for one in subject_template_groups}},
        )
        return self.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_description="删除人员模版用户关联",
        request_body=SubjectTemplateGroupIdSLZ(label="人员模版"),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["subject-template"],
    )
    @view_audit_decorator(SubjectTemplateGroupDeleteAuditProvider)
    def destroy(self, request, *args, **kwargs):
        template = self.get_object()

        serializer = SubjectTemplateGroupIdSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        group_id = serializer.validated_data["group_id"]
        self.biz.delete_group(template.id, group_id)

        # 写入审计上下文
        audit_context_setter(template=template, group=Group.objects.filter(id=group_id).first())

        return Response({})
