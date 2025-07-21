# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云 - 权限中心 (BlueKing-IAM) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from typing import Any, Dict, List, Set

from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from drf_yasg.utils import swagger_auto_schema
from pydantic.tools import parse_obj_as
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from backend.account.permissions import RolePermission
from backend.apps.group.models import Group
from backend.apps.template import tasks  # noqa
from backend.apps.template.models import PermTemplate, PermTemplatePolicyAuthorized, PermTemplatePreUpdateLock
from backend.audit.audit import audit_context_setter, view_audit_decorator
from backend.biz.action import ActionResourceGroupForCheck
from backend.biz.policy import PolicyBean
from backend.biz.role import RoleAuthorizationScopeChecker, RoleListQuery, RoleObjectRelationChecker
from backend.biz.subject import SubjectInfoList
from backend.biz.template import (
    TemplateCreateBean,
    TemplateGroupPreCommitBean,
)
from backend.common.error_codes import error_codes
from backend.common.lock import gen_template_upsert_lock
from backend.long_task.constants import TaskType
from backend.long_task.models import TaskDetail
from backend.long_task.tasks import TaskFactory
from backend.mixins import BizMixin
from backend.service.constants import PermissionCodeEnum
from backend.service.models import Subject

from .audit import (
    TemplateCreateAuditProvider,
    TemplateDeleteAuditProvider,
    TemplateMemberDeleteAuditProvider,
    TemplatePreUpdateCreateProvider,
    TemplatePreUpdateDeleteProvider,
    TemplateUpdateAuditProvider,
    TemplateUpdateCommitProvider,
)
from .filters import TemplateFilter, TemplateMemberFilter
from .serializers import (
    GroupCopyActionInstanceSLZ,
    TemplateCreateSLZ,
    TemplateDeleteMemberSLZ,
    TemplateDetailQuerySLZ,
    TemplateGroupAuthorationPreUpdateSLZ,
    TemplateGroupPreViewSchemaSLZ,
    TemplateGroupPreViewSLZ,
    TemplateGroupSLZ,
    TemplateIdSLZ,
    TemplateListSchemaSLZ,
    TemplateListSLZ,
    TemplateMemberListSchemaSLZ,
    TemplateMemberListSLZ,
    TemplatePartialUpdateSLZ,
    TemplatePreUpdateSchemaSLZ,
    TemplatePreUpdateSLZ,
    TemplateRetrieveSchemaSLZ,
)


class TemplateQueryMixin:
    def get_queryset(self):
        request = self.request
        return RoleListQuery(request.role, request.user).query_template()


class TemplatePermissionMixin:
    def get_object(self):
        queryset = PermTemplate.objects.filter(tenant_id=self.request.tenant_id)

        template_id = self.kwargs["id"]
        obj = get_object_or_404(queryset, pk=template_id)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    def check_object_permissions(self, request, obj):
        if not RoleObjectRelationChecker(request.role).check_template(obj):
            self.permission_denied(request, message=f"{request.role.type} role can not access template {obj.id}")


class TemplateViewSet(BizMixin, TemplateQueryMixin, GenericViewSet):
    permission_classes = [RolePermission]
    action_permission = {
        "create": PermissionCodeEnum.MANAGE_TEMPLATE.value,
        "update": PermissionCodeEnum.MANAGE_TEMPLATE.value,
        "destroy": PermissionCodeEnum.MANAGE_TEMPLATE.value,
        "partial_update": PermissionCodeEnum.MANAGE_TEMPLATE.value,
    }

    lookup_field = "id"
    serializer_class = TemplateListSLZ
    filterset_class = TemplateFilter

    @swagger_auto_schema(
        operation_description="模板列表",
        responses={status.HTTP_200_OK: TemplateListSchemaSLZ(label="模板", many=True)},
        tags=["template"],
    )
    def list(self, request, *args, **kwargs):
        group_id = request.query_params.get("group_id", "")
        queryset = self.filter_queryset(self.get_queryset())

        # 查询 role 的 system-actions set
        role_system_actions = RoleListQuery(request.role).get_scope_system_actions()
        page = self.paginate_queryset(queryset)
        if page is not None:
            # 查询模板中对 group_id 中有授权的
            exists_template_set = self._query_group_exists_template_set(group_id, page)
            serializer = TemplateListSLZ(
                page, many=True, authorized_template=exists_template_set, role_system_actions=role_system_actions
            )
            return self.get_paginated_response(serializer.data)

        # 查询模板中对 group_id 中有授权的
        exists_template_set = self._query_group_exists_template_set(group_id, queryset)
        serializer = TemplateListSLZ(
            queryset, many=True, authorized_template=exists_template_set, role_system_actions=role_system_actions
        )
        return Response(serializer.data)

    def _query_group_exists_template_set(self, group_id: str, queryset) -> Set[int]:
        """
        查询 group 已授权的模板集合
        """
        if group_id == "":
            return set()

        subject = Subject.from_group_id(group_id)
        exists_template_ids = PermTemplatePolicyAuthorized.objects.query_exists_template_auth(
            subject, [one.id for one in queryset]
        )
        return set(exists_template_ids)

    @swagger_auto_schema(
        operation_description="创建模板",
        request_body=TemplateCreateSLZ(label="模板"),
        responses={status.HTTP_201_CREATED: TemplateIdSLZ(label="模板 ID")},
        tags=["template"],
    )
    @view_audit_decorator(TemplateCreateAuditProvider)
    def create(self, request, *args, **kwargs):
        """
        创建模板
        """
        serializer = TemplateCreateSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = request.user.username
        data = serializer.validated_data

        # 检查模板的授权是否满足管理员的授权范围
        scope_checker = RoleAuthorizationScopeChecker(request.role)
        scope_checker.check_actions(data["system_id"], data["action_ids"])

        with gen_template_upsert_lock(request.role.id, data["name"]):
            # 检查权限模板是否在角色内唯一
            self.template_check_biz.check_role_template_name_exists(request.role.id, data["name"])

            template = self.template_biz.create(request.role.id, TemplateCreateBean.parse_obj(data), user_id)

        audit_context_setter(template=template)

        return Response({"id": template.id}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description="模板详情",
        query_serializer=TemplateDetailQuerySLZ(),
        responses={status.HTTP_200_OK: TemplateRetrieveSchemaSLZ(label="模板详情")},
        tags=["template"],
    )
    def retrieve(self, request, *args, **kwargs):
        slz = TemplateDetailQuerySLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)
        grouping = slz.validated_data["grouping"]

        # 查询 role 的 system-actions set
        role_system_actions = RoleListQuery(request.role).get_scope_system_actions()
        template = self.get_object()
        serializer = TemplateListSLZ(instance=template, role_system_actions=role_system_actions)
        data = serializer.data
        template_action_set = set(template.action_ids)

        actions = self.action_biz.list_template_tagged_action_by_role(
            template.system_id, request.role, template_action_set
        )
        if grouping:
            action_groups = self.action_group_biz.list_by_actions(template.system_id, actions)
            data["actions"] = [one.dict() for one in action_groups]
        else:
            data["actions"] = [one.dict() for one in actions if one.id in template_action_set]

        return Response(data)

    @swagger_auto_schema(
        operation_description="删除模板",
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["template"],
    )
    @view_audit_decorator(TemplateDeleteAuditProvider)
    def destroy(self, request, *args, **kwargs):
        template = self.get_object()
        PermTemplatePreUpdateLock.objects.raise_if_exists(template.id)

        self.template_biz.delete(template.id)

        audit_context_setter(template=template)
        return Response({})

    @swagger_auto_schema(
        operation_description="权限模板基本信息更新",
        request_body=TemplatePartialUpdateSLZ(label="更新权限模板基本信息"),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["template"],
    )
    @view_audit_decorator(TemplateUpdateAuditProvider)
    def partial_update(self, request, *args, **kwargs):
        """仅仅做基本信息更新"""
        template = self.get_object()
        serializer = TemplatePartialUpdateSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = request.user.username
        data = serializer.validated_data

        with gen_template_upsert_lock(request.role.id, data["name"]):
            # 检查权限模板是否在角色内唯一
            self.template_check_biz.check_role_template_name_exists(
                request.role.id, data["name"], template_id=template.id
            )
            PermTemplate.objects.filter(id=template.id).update(updater=user_id, **data)

        audit_context_setter(template=template)

        return Response({})


class TemplateMemberViewSet(BizMixin, TemplatePermissionMixin, GenericViewSet):
    permission_classes = [RolePermission]
    action_permission = {
        "create": PermissionCodeEnum.MANAGE_TEMPLATE.value,
        "destroy": PermissionCodeEnum.MANAGE_TEMPLATE.value,
    }

    lookup_field = "id"
    filterset_class = TemplateMemberFilter

    def get_queryset(self):
        return PermTemplatePolicyAuthorized.objects.filter(tenant_id=self.tenant_id).defer("_data")

    @swagger_auto_schema(
        operation_description="模板成员",
        responses={status.HTTP_200_OK: TemplateMemberListSchemaSLZ(label="模板成员", many=True)},
        tags=["template"],
    )
    def list(self, request, *args, **kwargs):
        template = self.get_object()
        queryset = self.filter_queryset(self.get_queryset()).filter(template_id=template.id)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = TemplateMemberListSLZ(page, many=True)
            data = self._fill_template_member_info(serializer.data)
            return self.get_paginated_response(data)

        serializer = TemplateMemberListSLZ(queryset, many=True)

        data = self._fill_template_member_info(serializer.data)
        return Response(data)

    def _fill_template_member_info(self, data: List[Dict[str, Any]]):
        """
        填充模板成员信息
        """
        subject_list = SubjectInfoList(parse_obj_as(List[Subject], data))
        for d, subject in zip(data, subject_list.subjects, strict=False):
            d.update(subject.dict())
        return data

    @swagger_auto_schema(
        operation_description="删除模板成员",
        request_body=TemplateDeleteMemberSLZ(label="成员"),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["template"],
    )
    @view_audit_decorator(TemplateMemberDeleteAuditProvider)
    def destroy(self, request, *args, **kwargs):
        template = self.get_object()
        PermTemplatePreUpdateLock.objects.raise_if_exists(template.id)

        serializer = TemplateDeleteMemberSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)
        members = serializer.validated_data["members"]

        self.template_biz.revoke_subjects(template.system_id, template.id, parse_obj_as(List[Subject], members))

        audit_context_setter(template=template, members=members)

        return Response({})


class TemplatePreUpdateViewSet(BizMixin, TemplatePermissionMixin, GenericViewSet):
    """
    预更新
    """

    lookup_field = "id"
    queryset = PermTemplate.objects.all()

    pagination_class = None  # 去掉 swagger 中的 limit offset 参数

    @swagger_auto_schema(
        operation_description="预更新",
        request_body=TemplatePreUpdateSLZ(label="新增操作"),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["template"],
    )
    @view_audit_decorator(TemplatePreUpdateCreateProvider)
    def create(self, request, *args, **kwargs):
        template = self.get_object()

        slz = TemplatePreUpdateSLZ(data=request.data)
        slz.is_valid(raise_exception=True)

        lock = self.template_biz.create_template_update_lock(template, slz.validated_data["action_ids"])

        audit_context_setter(template=template)

        add_action_ids = list(set(lock.action_ids) - set(template.action_ids))
        if not add_action_ids:
            return Response([])

        clone_config = self.template_policy_clone_biz.gen_system_action_clone_config(
            template.system_id, add_action_ids, template.action_ids
        )
        return Response([one.dict(by_alias=True) for one in clone_config])

    @swagger_auto_schema(
        operation_description="获取已有的预提交信息",
        responses={status.HTTP_200_OK: TemplatePreUpdateSchemaSLZ(label="预提交信息")},
        tags=["template"],
    )
    def list(self, request, *args, **kwargs):
        template = self.get_object()

        # 判断模板是否存在已存在的预提交信息
        lock = PermTemplatePreUpdateLock.objects.acquire_lock_not_running_or_raise(template_id=template.id)
        if not lock:
            return Response({})

        return Response({"action_ids": lock.action_ids})

    @swagger_auto_schema(
        operation_description="删除已提交的预更新信息",
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["template"],
    )
    @view_audit_decorator(TemplatePreUpdateDeleteProvider)
    def destroy(self, request, *args, **kwargs):
        template = self.get_object()
        self.template_biz.delete_pre_update_lock(template.id)

        audit_context_setter(template=template)
        return Response({})


class TemplatePreGroupSyncViewSet(BizMixin, TemplatePermissionMixin, GenericViewSet):
    """
    用户组预提交同步
    """

    lookup_field = "id"

    @swagger_auto_schema(
        operation_description="用户组同步预提交",
        request_body=TemplateGroupAuthorationPreUpdateSLZ(label="用户组同步预提交"),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["template"],
    )
    def create(self, request, *args, **kwargs):
        template = self.get_object()

        add_action_ids = self.template_biz.list_template_update_add_action_id(template)

        slz = TemplateGroupAuthorationPreUpdateSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        for group in data["groups"]:
            self.action_check_biz.check_action_resource_group(
                template.system_id, parse_obj_as(List[ActionResourceGroupForCheck], group["actions"])
            )

        # 检查数据
        pre_commits = parse_obj_as(List[TemplateGroupPreCommitBean], data["groups"])
        self.template_check_biz.check_group_update_pre_commit(template.id, pre_commits, add_action_ids)

        # 新增获取更新
        self.template_biz.create_or_update_group_pre_commit(template.id, pre_commits)

        return Response({})


class TemplateGenerateCloneGroupPolicyViewSet(BizMixin, TemplatePermissionMixin, GenericViewSet):
    """
    生成克隆的用户组策略
    """

    lookup_field = "id"

    @swagger_auto_schema(
        operation_description="生成克隆的用户组策略",
        request_body=GroupCopyActionInstanceSLZ(label="新增操作"),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["template"],
    )
    def create(self, request, *args, **kwargs):
        template = self.get_object()

        slz = GroupCopyActionInstanceSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        # 生成每个用户组对应的策略
        group_policies = self.template_policy_clone_biz.generate_template_groups_clone_policy(
            template, data["group_ids"], data["action_id"], data["clone_from_action_id"], request.role
        )
        return Response([one.dict() for one in group_policies])


class TemplateGroupSyncPreviewViewSet(BizMixin, TemplatePermissionMixin, GenericViewSet):
    lookup_field = "id"

    @swagger_auto_schema(
        operation_description="权限模板用户组更新预览",
        responses={status.HTTP_200_OK: TemplateGroupPreViewSchemaSLZ(label="预览", many=True)},
        tags=["template"],
    )
    def list(self, request, *args, **kwargs):
        template = self.get_object()
        lock = PermTemplatePreUpdateLock.objects.acquire_lock_waiting_or_raise(template_id=template.id)

        delete_action_set = set(template.action_ids) - set(lock.action_ids)

        # 查询模板授权到用户组的授权信息
        queryset = PermTemplatePolicyAuthorized.objects.filter(template_id=template.id)
        page = self.paginate_queryset(queryset)
        if page is not None:
            # 查询用户组的信息
            group_ids = [one.subject_id for one in page]
            groups = Group.objects.filter(id__in=group_ids)

            # 组合生成 response 信息
            serializer = TemplateGroupPreViewSLZ(
                groups,
                many=True,
                context={"tenant_id": self.tenant_id},
                authorized_templates=page,
                delete_action_ids=delete_action_set,
            )
            return self.get_paginated_response(serializer.data)

        group_ids = [one.subject_id for one in queryset]
        groups = Group.objects.filter(id__in=group_ids)
        serializer = TemplateGroupPreViewSLZ(
            groups,
            many=True,
            context={"tenant_id": self.tenant_id},
            authorized_templates=queryset,
            delete_action_ids=delete_action_set,
        )
        return Response(serializer.data)


class TemplateUpdateCommitViewSet(BizMixin, TemplatePermissionMixin, GenericViewSet):
    """
    权限模板更新提交
    """

    lookup_field = "id"

    @swagger_auto_schema(
        operation_description="权限模板更新提交",
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["template"],
    )
    @view_audit_decorator(TemplateUpdateCommitProvider)
    def create(self, request, *args, **kwargs):
        template = self.get_object()
        add_action_ids = self.template_biz.list_template_update_add_action_id(template)
        # 只有有新增的操作的时候需要校验
        if add_action_ids:
            self.template_check_biz.check_group_pre_commit_complete(template.id)

        if not PermTemplatePreUpdateLock.objects.update_waiting_to_running(template.id):
            # 任务已经开始运行了
            raise error_codes.VALIDATE_ERROR.format(_("预提交的任务不存在，禁止提交！"))

        # 使用长时任务实现用户组授权更新
        task = TaskDetail.create(self.tenant_id, TaskType.TEMPLATE_UPDATE.value, [template.id])
        TaskFactory().run(task.id)

        audit_context_setter(template=template)

        return Response({})


class TemplateConvertToCustomPolicyViewSet(BizMixin, TemplatePermissionMixin, GenericViewSet):
    """
    转换成自定义权限
    """

    lookup_field = "id"

    @swagger_auto_schema(
        operation_description="模版权限转换成自定义权限",
        responses={status.HTTP_200_OK: TemplateGroupSLZ()},
        tags=["template"],
    )
    @view_audit_decorator(TemplateMemberDeleteAuditProvider)
    def create(self, request, *args, **kwargs):
        template = self.get_object()

        slz = TemplateGroupSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        group_id = slz.validated_data["group_id"]

        # 查询用户组关联的模版权限
        subject = Subject.from_group_id(group_id)
        authorized_template = PermTemplatePolicyAuthorized.objects.get_by_subject_template(subject, template.id)
        template_policies = parse_obj_as(List[PolicyBean], authorized_template.data["actions"])

        # 合并权限，重新授权自定义权限
        self.policy_operation_biz.alter(template.system_id, subject, template_policies)

        # 解除用户组与模版直接的关系
        self.template_biz.revoke_subjects(template.system_id, template.id, [subject])

        audit_context_setter(template=template, members=[subject.dict()])

        return Response({})
