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
from typing import List, Optional

from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from backend.account.permissions import RolePermission
from backend.apps.group.audit import GroupMemberDeleteAuditProvider
from backend.apps.group.filters import GroupFilter
from backend.apps.group.models import Group
from backend.apps.group.serializers import GroupsAddMemberSLZ, GroupSearchSLZ
from backend.apps.group.views import GroupsMemberViewSet, split_members_to_subject_and_template
from backend.apps.role.filters import RoleGroupSubjectFilter
from backend.apps.role.models import RoleGroupMember, RoleRelatedObject
from backend.apps.role.serializers import RoleGroupMemberCleanSLZ, RoleGroupMemberSearchSLZ, RoleGroupSubjectSLZ
from backend.apps.subject.serializers import SubjectGroupSLZ
from backend.apps.subject.views import (
    DepartmentSubjectTemplateGroupViewSet,
    SubjectDepartmentGroupSearchViewSet,
    SubjectGroupSearchViewSet,
    SubjectTemplateGroupViewSet,
)
from backend.apps.user.serializers import SubjectTemplateGroupSLZ
from backend.apps.user.views import SubjectGroupSearchMixin
from backend.audit.audit import audit_context_setter, log_api_event
from backend.biz.group import GroupBiz
from backend.biz.role import RoleObjectRelationChecker
from backend.biz.subject_template import SubjectTemplateBiz
from backend.service.constants import PermissionCodeEnum, RoleRelatedObjectType, SubjectType

logger = logging.getLogger("app")


class RoleSubjectGroupSearchMixin(SubjectGroupSearchMixin):
    def search_group_queryset(self, request, *args, **kwargs):
        slz = RoleGroupMemberSearchSLZ(data=request.data)
        slz.is_valid(raise_exception=True)

        data = slz.validated_data

        # 筛选
        f = GroupFilter(
            data={
                k: v
                for k, v in data.items()
                if k in ["id", "name", "description", "hidden"]
                if isinstance(v, bool) or v
            },
            queryset=Group.objects.all(),
        )
        queryset = f.qs

        # 查询role关联的所有用户组
        role_ids = RoleObjectRelationChecker(request.role).list_relation_role_id()
        ids = list(
            RoleRelatedObject.objects.filter(role_id__in=role_ids, object_type=RoleRelatedObjectType.GROUP.value)
            .values_list("object_id", flat=True)
            .distinct()
        )

        search_group_ids = self.search_group_ids(request, kwargs, data)
        if search_group_ids is not None:
            ids = [_id for _id in ids if _id in set(search_group_ids)]

        if not ids:
            return None

        return queryset.filter(id__in=ids)


class RoleGroupMemberViewSet(RoleSubjectGroupSearchMixin):
    """
    分级管理员查看有权限的用户组成员列表
    """

    permission_classes = [RolePermission]
    action_permission = {
        "list": PermissionCodeEnum.MANAGE_ROLE_GROUP_MEMBER.value,
    }

    queryset = RoleGroupMember.objects.all()
    serializer_class = RoleGroupSubjectSLZ
    filterset_class = RoleGroupSubjectFilter

    def get_queryset(self):
        group_qs = self.search_group_queryset(self.request, *self.args, **self.kwargs)
        if group_qs is None:
            return RoleGroupMember.objects.none()

        group_ids = list(group_qs.values_list("id", flat=True))
        if not group_ids:
            return RoleGroupMember.objects.none()

        qs = (
            RoleGroupMember.objects.filter(role_id=self.request.role.id, group_id__in=group_ids)
            .values("subject_type", "subject_id")
            .distinct()
            .order_by("subject_type", "subject_id")
        )

        slz = RoleGroupMemberSearchSLZ(data=self.request.data)
        slz.is_valid(raise_exception=True)

        data = slz.validated_data

        # 筛选
        f = RoleGroupSubjectFilter(
            data=data,
            queryset=qs,
        )
        return f.qs

    @swagger_auto_schema(
        operation_description="分级管理员查看有权限的用户组成员列表",
        request_body=RoleGroupMemberSearchSLZ(label="用户组搜索"),
        responses={status.HTTP_200_OK: RoleGroupSubjectSLZ(label="分级管理员用户组成员列表", many=True)},
        tags=["role"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class RoleGroupMemberTemplateGroupViewSet(SubjectTemplateGroupViewSet):
    permission_classes = [RolePermission]
    action_permission = {
        "list": PermissionCodeEnum.MANAGE_ROLE_GROUP_MEMBER.value,
    }

    @swagger_auto_schema(
        operation_description="角色用户组成员-人员模版用户组列表",
        request_body=GroupSearchSLZ(label="用户组搜索"),
        responses={status.HTTP_200_OK: SubjectTemplateGroupSLZ(label="用户组", many=True)},
        tags=["role"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def search_group_ids(self, request, kwargs, data) -> Optional[List[int]]:
        search_group_ids = super().search_group_ids(request, kwargs, data)

        # 查询subject 在角色下关联的用户组
        subject = self.get_subject(request, kwargs)
        group_ids = list(
            RoleGroupMember.objects.filter(
                role_id=self.request.role.id, subject_type=subject.type, subject_id=subject.id
            )
            .exclude(subject_template_id=0)
            .values_list("group_id", flat=True)
        )

        if search_group_ids is None:
            return group_ids

        return list(set(group_ids) & set(search_group_ids))


class RoleGroupMemberDepartmentTemplateGroupViewSet(DepartmentSubjectTemplateGroupViewSet):
    permission_classes = [RolePermission]
    action_permission = {
        "list": PermissionCodeEnum.MANAGE_ROLE_GROUP_MEMBER.value,
    }

    @swagger_auto_schema(
        operation_description="角色用户组成员-部门人员模版用户组列表",
        request_body=GroupSearchSLZ(label="用户组搜索"),
        responses={status.HTTP_200_OK: SubjectTemplateGroupSLZ(label="用户组", many=True)},
        tags=["role"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def search_group_ids(self, request, kwargs, data) -> Optional[List[int]]:
        # 查询subject 在角色下关联的用户组
        subject = self.get_subject(request, kwargs)
        if subject.type != SubjectType.USER.value:
            return []

        departments = self.biz.get_user_departments(subject.id)
        if not departments:
            return []

        group_ids = list(
            RoleGroupMember.objects.filter(
                role_id=self.request.role.id,
                subject_type=SubjectType.DEPARTMENT.value,
                subject_id__in=[str(d.id) for d in departments],
            )
            .exclude(subject_template_id=0)
            .values_list("group_id", flat=True)
        )

        search_group_ids = super().search_group_ids(request, kwargs, data)

        if search_group_ids is None:
            return group_ids

        return list(set(group_ids) & set(search_group_ids))


class RoleGroupMemberGroupViewSet(SubjectGroupSearchViewSet):
    permission_classes = [RolePermission]
    action_permission = {
        "list": PermissionCodeEnum.MANAGE_ROLE_GROUP_MEMBER.value,
    }

    @swagger_auto_schema(
        operation_description="角色用户组成员-用户组列表",
        request_body=GroupSearchSLZ(label="用户组搜索"),
        responses={status.HTTP_200_OK: SubjectGroupSLZ(label="用户组", many=True)},
        tags=["role"],
    )
    def list(self, request, *args, **kwargs):
        return super().search(request, *args, **kwargs)

    def search_group_ids(self, request, kwargs, data) -> Optional[List[int]]:
        search_group_ids = super().search_group_ids(request, kwargs, data)

        # 查询subject 在角色下关联的用户组
        subject = self.get_subject(request, kwargs)
        group_ids = list(
            RoleGroupMember.objects.filter(
                role_id=self.request.role.id, subject_type=subject.type, subject_id=subject.id, subject_template_id=0
            ).values_list("group_id", flat=True)
        )

        if search_group_ids is None:
            return group_ids

        return list(set(group_ids) & set(search_group_ids))


class RoleGroupMemberDepartmentGroupViewSet(SubjectDepartmentGroupSearchViewSet):

    subject_template_biz = SubjectTemplateBiz()

    @swagger_auto_schema(
        operation_description="角色用户组成员-部门用户组列表",
        request_body=GroupSearchSLZ(label="用户组搜索"),
        responses={status.HTTP_200_OK: SubjectGroupSLZ(label="用户组", many=True)},
        tags=["role"],
    )
    def list(self, request, *args, **kwargs):
        return super().search(request, *args, **kwargs)

    def search_group_ids(self, request, kwargs, data) -> Optional[List[int]]:
        # 查询subject 在角色下关联的用户组
        subject = self.get_subject(request, kwargs)
        if subject.type != SubjectType.USER.value:
            return []

        departments = self.subject_template_biz.get_user_departments(subject.id)
        if not departments:
            return []

        group_ids = list(
            RoleGroupMember.objects.filter(
                role_id=self.request.role.id,
                subject_type=SubjectType.DEPARTMENT.value,
                subject_id__in=[str(d.id) for d in departments],
                subject_template_id=0,
            ).values_list("group_id", flat=True)
        )

        search_group_ids = super().search_group_ids(request, kwargs, data)

        if search_group_ids is None:
            return group_ids

        return list(set(group_ids) & set(search_group_ids))


class RoleGroupMemberCleanViewSet(GenericViewSet):
    permission_classes = [RolePermission]
    action_permission = {
        "create": PermissionCodeEnum.MANAGE_ROLE_GROUP_MEMBER.value,
    }

    group_biz = GroupBiz()

    @swagger_auto_schema(
        operation_description="批量清理用户组成员",
        request_body=RoleGroupMemberCleanSLZ(label="成员"),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["role"],
    )
    def create(self, request, *args, **kwargs):
        serializer = RoleGroupMemberCleanSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        members_data = data["members"]

        # 成员Dict结构转换为Subject结构，并去重
        members, _ = split_members_to_subject_and_template(members_data)

        # 查询出role以及所有的子集管理员id
        role_ids = RoleObjectRelationChecker(request.role).list_relation_role_id()

        group_id_set = set()
        for subject in members:
            group_ids = list(
                RoleGroupMember.objects.filter(
                    subject_type=subject.type, subject_id=subject.id, role_id__in=role_ids, subject_template_id=0
                ).values_list("group_id", flat=True)
            )
            group_id_set = group_id_set | set(group_ids)

        for group_id in group_id_set:
            self.group_biz.remove_members(str(group_id), members)

            try:
                # 写入审计上下文
                group = Group.objects.filter(id=group_id).first()
                if not group:
                    continue

                audit_context_setter(group=group, members=[m.dict() for m in members])
                provider = GroupMemberDeleteAuditProvider(request)
                log_api_event(request, provider)
            except Exception:  # pylint: disable=broad-except
                logger.exception("save audit event fail")

        return Response({})


class RoleGroupMemberResetViewSet(RoleGroupMemberCleanViewSet, GroupsMemberViewSet):
    @swagger_auto_schema(
        operation_description="批量重置用户组成员",
        request_body=GroupsAddMemberSLZ(label="成员"),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["role"],
    )
    def create(self, request, *args, **kwargs):
        RoleGroupMemberCleanViewSet.create(self, request, *args, **kwargs)
        return GroupsMemberViewSet.create(self, request, *args, **kwargs)
