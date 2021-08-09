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
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from backend.account.permissions import role_perm_class
from backend.apps.organization.models import Department, User
from backend.apps.policy.serializers import PolicyDeleteSLZ, PolicyPartDeleteSLZ, PolicySLZ, PolicySystemSLZ
from backend.apps.template.models import PermTemplatePolicyAuthorized
from backend.audit.audit import audit_context_setter, view_audit_decorator
from backend.biz.group import GroupBiz
from backend.biz.policy import ConditionBean, PolicyOperationBiz, PolicyQueryBiz
from backend.common.serializers import SystemQuerySLZ
from backend.common.swagger import ResponseSwaggerAutoSchema
from backend.service.constants import PermissionCodeEnum
from backend.service.models import Subject

from .audit import SubjectGroupDeleteAuditProvider, SubjectPolicyDeleteAuditProvider
from .serializers import SubjectDepartmentSLZ, SubjectGroupSLZ, UserRelationSLZ

permission_logger = logging.getLogger("permission")


class SubjectGroupViewSet(GenericViewSet):

    permission_classes = [role_perm_class(PermissionCodeEnum.MANAGE_ORGANIZATION.value)]

    paginator = None  # 去掉swagger中的limit offset参数

    biz = GroupBiz()

    @swagger_auto_schema(
        operation_description="我的权限-用户组列表",
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: SubjectGroupSLZ(label="用户组", many=True)},
        tags=["subject"],
    )
    def list(self, request, *args, **kwargs):
        _type = kwargs["subject_type"]
        _id = kwargs["subject_id"]
        relations = self.biz.list_subject_group(Subject(type=_type, id=_id), is_recursive=True)
        return Response([one.dict() for one in relations])

    @swagger_auto_schema(
        operation_description="我的权限-退出用户组",
        auto_schema=ResponseSwaggerAutoSchema,
        query_serializer=UserRelationSLZ,
        responses={status.HTTP_200_OK: yasg_response({})},
        tags=["subject"],
    )
    @view_audit_decorator(SubjectGroupDeleteAuditProvider)
    def destroy(self, request, *args, **kwargs):
        serializer = UserRelationSLZ(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        subject = Subject(type=kwargs["subject_type"], id=kwargs["subject_id"])

        permission_logger.info("subject group delete by user: %s", request.user.username)

        if data["type"] == "group":
            group_id = data["id"]
            self.biz.remove_members(group_id, [Subject.parse_obj({"type": subject.type, "id": subject.id})])

            # 写入审计上下文
            audit_context_setter(subject=subject, group=Subject.parse_obj(data))

        return Response({})


class SubjectDepartmentViewSet(GenericViewSet):

    permission_classes = [role_perm_class(PermissionCodeEnum.MANAGE_ORGANIZATION.value)]

    paginator = None  # 去掉swagger中的limit offset参数

    @swagger_auto_schema(
        operation_description="我的权限-部门列表",
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: SubjectDepartmentSLZ(label="部门", many=True)},
        tags=["subject"],
    )
    def list(self, request, *args, **kwargs):
        _type = kwargs["subject_type"]
        _id = kwargs["subject_id"]
        if _type != "user":
            return Response([])
        # 获取userid
        user = User.objects.get(username=_id)
        department_id_set = user.ancestor_department_ids

        if not department_id_set:
            return Response([])

        # TODO: [重构] view 不应该有这么原子调用，而是封装在biz层，迁移到biz.subject
        # 哪些部门被授权过
        authorized_department_ids = PermTemplatePolicyAuthorized.objects.filter(
            subject_type="department", subject_id__in=department_id_set
        ).values_list("subject_id", flat=True)
        authorized_department_ids = list(map(int, authorized_department_ids))  # 转为整型便于查询

        # 查询被授过权的部门信息
        data = [
            {"id": dept.id, "name": dept.name, "full_name": dept.full_name}
            for dept in Department.objects.filter(id__in=authorized_department_ids)
        ]

        return Response(data)


class SubjectSystemViewSet(GenericViewSet):

    permission_classes = [role_perm_class(PermissionCodeEnum.MANAGE_ORGANIZATION.value)]

    paginator = None  # 去掉swagger中的limit offset参数

    biz = PolicyQueryBiz()

    @swagger_auto_schema(
        operation_description="Subject有权限的所有系统列表",
        auto_schema=ResponseSwaggerAutoSchema,
        query_serializer=None,
        responses={status.HTTP_200_OK: PolicySystemSLZ(label="系统", many=True)},
        tags=["subject"],
    )
    def list(self, request, *args, **kwargs):
        subject = Subject(type=kwargs["subject_type"], id=kwargs["subject_id"])

        data = self.biz.list_system_counter_by_subject(subject)

        return Response([one.dict() for one in data])


class SubjectPolicyViewSet(GenericViewSet):

    permission_classes = [role_perm_class(PermissionCodeEnum.MANAGE_ORGANIZATION.value)]

    paginator = None  # 去掉swagger中的limit offset参数

    policy_query_biz = PolicyQueryBiz()
    policy_operation_biz = PolicyOperationBiz()

    @swagger_auto_schema(
        operation_description="Subject权限列表",
        auto_schema=ResponseSwaggerAutoSchema,
        query_serializer=SystemQuerySLZ,
        responses={status.HTTP_200_OK: PolicySLZ(label="策略", many=True)},
        tags=["subject"],
    )
    def list(self, request, *args, **kwargs):
        slz = SystemQuerySLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)

        system_id = slz.validated_data["system_id"]

        subject = Subject(type=kwargs["subject_type"], id=kwargs["subject_id"])

        policies = self.policy_query_biz.list_by_subject(system_id, subject)

        return Response([p.dict() for p in policies])

    @swagger_auto_schema(
        operation_description="删除权限",
        auto_schema=ResponseSwaggerAutoSchema,
        query_serializer=PolicyDeleteSLZ,
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["subject"],
    )
    @view_audit_decorator(SubjectPolicyDeleteAuditProvider)
    def destroy(self, request, *args, **kwargs):
        slz = PolicyDeleteSLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)

        system_id = slz.validated_data["system_id"]
        ids = slz.validated_data["ids"]
        subject = Subject(type=kwargs["subject_type"], id=kwargs["subject_id"])

        permission_logger.info("subject policy delete by user: %s", request.user.username)

        policy_list = self.policy_query_biz.query_policy_list_by_policy_ids(system_id, subject, ids)

        # 删除权限
        self.policy_operation_biz.delete_by_ids(system_id, subject, ids)

        # 写入审计上下文
        audit_context_setter(subject=subject, system_id=system_id, policies=policy_list.policies)

        return Response()

    @swagger_auto_schema(
        operation_description="权限更新",
        auto_schema=ResponseSwaggerAutoSchema,
        request_body=PolicyPartDeleteSLZ(label="条件删除"),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["subject"],
    )
    @view_audit_decorator(SubjectPolicyDeleteAuditProvider)
    def update(self, request, *args, **kwargs):
        slz = PolicyPartDeleteSLZ(data=request.data)
        slz.is_valid(raise_exception=True)

        data = slz.validated_data

        policy_id = kwargs["pk"]
        system_id = data["system_id"]
        resource_type = data["type"]
        condition_ids = data["ids"]
        condition = data["condition"]

        subject = Subject(type=kwargs["subject_type"], id=kwargs["subject_id"])

        permission_logger.info("subject policy delete partial by user: %s", request.user.username)

        delete_policy = self.policy_operation_biz.delete_partial(
            subject,
            policy_id,
            system_id,
            resource_type,
            condition_ids,
            [ConditionBean(attributes=[], **c) for c in condition],
        )

        # 写入审计上下文
        audit_context_setter(subject=subject, system_id=system_id, policies=[delete_policy])

        return Response({})
