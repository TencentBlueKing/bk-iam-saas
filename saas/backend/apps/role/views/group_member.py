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
from typing import List, Optional

from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.viewsets import GenericViewSet, mixins

from backend.account.permissions import RolePermission
from backend.apps.group.serializers import GroupSearchSLZ
from backend.apps.role.filters import RoleGroupSubjectFilter
from backend.apps.role.models import RoleGroupMember
from backend.apps.role.serializers import RoleGroupSubjectSLZ
from backend.apps.subject.serializers import SubjectGroupSLZ
from backend.apps.subject.views import (
    DepartmentSubjectTemplateGroupViewSet,
    SubjectDepartmentGroupSearchViewSet,
    SubjectGroupSearchViewSet,
    SubjectTemplateGroupViewSet,
)
from backend.apps.user.serializers import SubjectTemplateGroupSLZ
from backend.service.constants import PermissionCodeEnum, SubjectType


class RoleGroupMemberViewSet(mixins.ListModelMixin, GenericViewSet):
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
        return (
            RoleGroupMember.objects.filter(role_id=self.request.role.id)
            .values("subject_type", "subject_id")
            .distinct()
            .order_by("subject_type", "subject_id")
        )

    @swagger_auto_schema(
        operation_description="分级管理员查看有权限的用户组成员列表",
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
        super().list(request, *args, **kwargs)

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
        tags=["subject"],
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
        tags=["subject"],
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
    @swagger_auto_schema(
        operation_description="角色用户组成员-部门用户组列表",
        request_body=GroupSearchSLZ(label="用户组搜索"),
        responses={status.HTTP_200_OK: SubjectGroupSLZ(label="用户组", many=True)},
        tags=["subject"],
    )
    def list(self, request, *args, **kwargs):
        return super().search(request, *args, **kwargs)

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
                subject_template_id=0,
            ).values_list("group_id", flat=True)
        )

        search_group_ids = super().search_group_ids(request, kwargs, data)

        if search_group_ids is None:
            return group_ids

        return list(set(group_ids) & set(search_group_ids))
