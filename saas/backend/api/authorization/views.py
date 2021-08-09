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
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.api.authentication import ESBAuthentication
from backend.api.mixins import ExceptionHandlerMixin, SystemClientCheckMixin
from backend.audit.audit import audit_context_setter, view_audit_decorator
from backend.biz.action import ActionCheckBiz, ActionForCheck
from backend.common.swagger import ResponseSwaggerAutoSchema
from backend.service.action import ActionService
from backend.service.constants import Operate, SubjectType
from backend.service.models import ApplyAction, Attribute, Subject
from backend.service.models.open import ApplyActionList
from backend.service.models.policy import ResourceInstanceList
from backend.service.policy import PolicyService
from backend.service.resource_creator_action import ResourceCreatorActionService

from .audit import SubjectPolicyGrantOrRevokeAuditProvider
from .mixins import AuthorizationAPIAllowListCheckMixin, SubjectCheckMixin
from .serializers import (
    AuthBatchInstanceSLZ,
    AuthBatchPathSLZ,
    AuthInstanceSLZ,
    AuthPathSLZ,
    BatchResourceCreatorActionSLZ,
    ResourceCreatorActionAttributeSLZ,
    ResourceCreatorActionSLZ,
)
from .utils import check_scope, join_ancestors_to_resource_instances


# TODO 提取公共逻辑到biz, 把不同的数据结构转换成统一的结构, 复用相同的授权逻辑, 数据的转换放到biz.trans
# TODO 存在大量的重复逻辑, 需要提取
class AuthInstanceView(
    AuthorizationAPIAllowListCheckMixin, SystemClientCheckMixin, SubjectCheckMixin, ExceptionHandlerMixin, APIView
):
    """
    单个资源授权回收
    """

    authentication_classes = [ESBAuthentication]
    permission_classes = [IsAuthenticated]

    action_svc = ActionService()
    policy_svc = PolicyService()

    action_check_biz = ActionCheckBiz()

    @swagger_auto_schema(
        operation_description="单个资源授权回收",
        auto_schema=ResponseSwaggerAutoSchema,
        request_body=AuthInstanceSLZ,
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["open"],
    )
    @view_audit_decorator(SubjectPolicyGrantOrRevokeAuditProvider)
    def post(self, request, *args, **kwargs):
        serializer = AuthInstanceSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        system_id = data["system"]
        action_id = data["action"]["id"]

        # 检查是否该系统允许调用当前授权API
        self.check_allow_system_action(system_id, action_id)

        # 校验调用方是否能访问该系统
        self.verify_system_client(system_id, request.bk_app_code)

        # 检测被授权的用户是否存在，不存在则尝试同步
        if data["subject"]["type"] == SubjectType.USER.value:
            self.check_or_sync_user(data["subject"]["id"])

        subject = Subject(**data["subject"])

        # 类型转换
        apply_action = ApplyAction.from_instance(data)
        resource_instances = [rrt.to_resource_instance() for rrt in apply_action.related_resource_types]
        # 填充类型名称
        resource_instance_list = ResourceInstanceList(resource_instances)
        resource_instance_list.fill_resource_type_name()

        self.action_check_biz.check(
            system_id,
            [
                ActionForCheck(
                    id=action_id,
                    related_resource_types=[one.dict() for one in resource_instance_list.resource_instances],
                )
            ],
        )

        action = self.action_svc.get(system_id, action_id)
        # 校验授权用户组是否超过其分级管理员范围
        if subject.type == SubjectType.GROUP.value and data["operate"] == Operate.GRANT.value:
            check_scope(system_id, [action], subject, resource_instances)

        # 授权或回收
        result, policies = self.policy_svc.grant_or_revoke_instance(
            data["operate"], system_id, action, subject, resource_instance_list.resource_instances, data["expired_at"]
        )

        audit_context_setter(operate=data["operate"], subject=subject, system_id=system_id, policies=policies)

        return Response(result)


class AuthPathView(SystemClientCheckMixin, SubjectCheckMixin, ExceptionHandlerMixin, APIView):
    """
    单个拓扑层级授权/回收
    """

    authentication_classes = [ESBAuthentication]
    permission_classes = [IsAuthenticated]

    action_svc = ActionService()
    policy_svc = PolicyService()

    action_check_biz = ActionCheckBiz()

    @swagger_auto_schema(
        operation_description="单个拓扑层级授权/回收",
        auto_schema=ResponseSwaggerAutoSchema,
        request_body=AuthPathSLZ,
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["open"],
    )
    @view_audit_decorator(SubjectPolicyGrantOrRevokeAuditProvider)
    def post(self, request, *args, **kwargs):
        serializer = AuthPathSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        system_id = data["system"]

        # 校验调用方是否能访问该系统
        self.verify_system_client(system_id, request.bk_app_code)

        # 检测被授权的用户是否存在，不存在则尝试同步
        if data["subject"]["type"] == SubjectType.USER.value:
            self.check_or_sync_user(data["subject"]["id"])

        action_id = data["action"]["id"]
        subject = Subject(**data["subject"])

        apply_action = ApplyAction.from_path(data)

        self.action_check_biz.check(system_id, [ActionForCheck(**apply_action.dict())])

        # 填充拓扑节点的system_id
        apply_action_list = ApplyActionList([apply_action])
        apply_action_list.fill_instance_system(system_id)

        # 类型转换
        resource_instances = [rrt.to_resource_instance() for rrt in apply_action.related_resource_types]

        # 填充类型名称
        resource_instance_list = ResourceInstanceList(resource_instances)
        resource_instance_list.fill_resource_type_name()

        self.action_check_biz.check(
            system_id,
            [
                ActionForCheck(
                    id=action_id,
                    related_resource_types=[one.dict() for one in resource_instance_list.resource_instances],
                )
            ],
        )

        action = self.action_svc.get(system_id, action_id)
        # 校验授权用户组是否超过其分级管理员范围
        if subject.type == SubjectType.GROUP.value and data["operate"] == Operate.GRANT.value:
            check_scope(system_id, [action], subject, resource_instances)

        # 授权或回收
        result, policies = self.policy_svc.grant_or_revoke_instance(
            data["operate"], system_id, action, subject, resource_instance_list.resource_instances, data["expired_at"]
        )

        audit_context_setter(operate=data["operate"], subject=subject, system_id=system_id, policies=policies)

        return Response(result)


class AuthBatchInstanceView(
    AuthorizationAPIAllowListCheckMixin, SystemClientCheckMixin, SubjectCheckMixin, ExceptionHandlerMixin, APIView
):
    """
    批量操作批量资源授权回收
    """

    authentication_classes = [ESBAuthentication]
    permission_classes = [IsAuthenticated]

    action_svc = ActionService()
    policy_svc = PolicyService()

    action_check_biz = ActionCheckBiz()

    @swagger_auto_schema(
        operation_description="批量操作批量资源授权回收",
        auto_schema=ResponseSwaggerAutoSchema,
        request_body=AuthBatchInstanceSLZ,
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["open"],
    )
    @view_audit_decorator(SubjectPolicyGrantOrRevokeAuditProvider)
    def post(self, request, *args, **kwargs):
        serializer = AuthBatchInstanceSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        system_id = data["system"]
        action_ids = [a["id"] for a in data["actions"]]

        # 检查是否该系统允许调用当前授权API
        self.check_allow_system_actions(system_id, action_ids)

        # 校验调用方是否能访问该系统
        self.verify_system_client(system_id, request.bk_app_code)

        # 检测被授权的用户是否存在，不存在则尝试同步
        if data["subject"]["type"] == SubjectType.USER.value:
            self.check_or_sync_user(data["subject"]["id"])

        subject = Subject(**data["subject"])

        # 类型转换
        action = ApplyAction.from_batch_instance(data)
        resource_instances = [rrt.to_resource_instance() for rrt in action.related_resource_types]
        # 填充类型名称
        resource_instance_list = ResourceInstanceList(resource_instances)
        resource_instance_list.fill_resource_type_name()

        related_resource_types = [one.dict() for one in resource_instance_list.resource_instances]
        actions_for_check = [
            ActionForCheck(id=ac["id"], related_resource_types=related_resource_types) for ac in data["actions"]
        ]
        self.action_check_biz.check(system_id, actions_for_check)

        actions = self.action_svc.new_action_list(system_id).filter([ac["id"] for ac in data["actions"]])

        # 校验授权用户组是否超过其分级管理员范围
        if subject.type == SubjectType.GROUP.value and data["operate"] == Operate.GRANT.value:
            check_scope(system_id, actions, subject, resource_instances)

        # 授权或回收
        result, policies = self.policy_svc.grant_or_revoke_batch_instance(
            data["operate"], system_id, actions, subject, resource_instance_list.resource_instances, data["expired_at"]
        )

        audit_context_setter(operate=data["operate"], subject=subject, system_id=system_id, policies=policies)

        return Response(result)


class AuthBatchPathView(SystemClientCheckMixin, SubjectCheckMixin, ExceptionHandlerMixin, APIView):
    """
    批量操作批量拓扑层级授权/回收
    """

    authentication_classes = [ESBAuthentication]
    permission_classes = [IsAuthenticated]

    action_svc = ActionService()
    policy_svc = PolicyService()

    action_check_biz = ActionCheckBiz()

    @swagger_auto_schema(
        operation_description="批量操作批量拓扑层级授权/回收",
        auto_schema=ResponseSwaggerAutoSchema,
        request_body=AuthBatchPathSLZ,
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["open"],
    )
    @view_audit_decorator(SubjectPolicyGrantOrRevokeAuditProvider)
    def post(self, request, *args, **kwargs):
        serializer = AuthBatchPathSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        system_id = data["system"]

        # 校验调用方是否能访问该系统
        self.verify_system_client(system_id, request.bk_app_code)

        # 检测被授权的用户是否存在，不存在则尝试同步
        if data["subject"]["type"] == SubjectType.USER.value:
            self.check_or_sync_user(data["subject"]["id"])

        subject = Subject(**data["subject"])

        apply_action = ApplyAction.from_batch_path(data)

        # 检查操作数据
        self.action_check_biz.check(system_id, [ActionForCheck(**apply_action.dict())])

        # 填充拓扑节点的system_id
        apply_action_list = ApplyActionList([apply_action])
        apply_action_list.fill_instance_system(system_id)

        # 类型转换
        resource_instances = [rrt.to_resource_instance() for rrt in apply_action.related_resource_types]
        # 填充类型名称
        resource_instance_list = ResourceInstanceList(resource_instances)
        resource_instance_list.fill_resource_type_name()

        related_resource_types = [one.dict() for one in resource_instance_list.resource_instances]
        actions_for_check = [
            ActionForCheck(id=ac["id"], related_resource_types=related_resource_types) for ac in data["actions"]
        ]
        self.action_check_biz.check(system_id, actions_for_check)

        actions = self.action_svc.new_action_list(system_id).filter([ac["id"] for ac in data["actions"]])

        # 校验授权用户组是否超过其分级管理员范围
        if subject.type == SubjectType.GROUP.value and data["operate"] == Operate.GRANT.value:
            check_scope(system_id, actions, subject, resource_instances)

        # 授权或回收
        result, policies = self.policy_svc.grant_or_revoke_batch_instance(
            data["operate"], system_id, actions, subject, resource_instance_list.resource_instances, data["expired_at"]
        )

        audit_context_setter(operate=data["operate"], subject=subject, system_id=system_id, policies=policies)

        return Response(result)


# TODO: [重构]新建关联单独拆分views/ResourceCreatorAction.py
class ResourceCreatorActionView(
    AuthorizationAPIAllowListCheckMixin, SystemClientCheckMixin, SubjectCheckMixin, ExceptionHandlerMixin, APIView
):
    """
    新建关联授权
    """

    authentication_classes = [ESBAuthentication]
    permission_classes = [IsAuthenticated]

    action_svc = ActionService()
    policy_svc = PolicyService()
    rca_svc = ResourceCreatorActionService()

    @swagger_auto_schema(
        operation_description="新建关联授权",
        auto_schema=ResponseSwaggerAutoSchema,
        request_body=ResourceCreatorActionSLZ,
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["open"],
    )
    @view_audit_decorator(SubjectPolicyGrantOrRevokeAuditProvider)
    def post(self, request, *args, **kwargs):
        serializer = ResourceCreatorActionSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        system_id = data["system"]
        resource_type = data["type"]

        # 检查是否该系统允许调用当前授权API
        self.check_allow_resource_type(system_id, resource_type)

        # 校验调用方是否能访问该系统
        self.verify_system_client(system_id, request.bk_app_code)

        # 检测被授权的用户是否存在，不存在则尝试同步
        self.check_or_sync_user(data["creator"])

        subject = Subject(type=SubjectType.USER.value, id=data["creator"])

        # 查询出对应资源类型需要授予哪些ActionID
        action_ids = set(self.rca_svc.get_actions(system_id, resource_type))
        # 转换为Action结构
        actions = self.action_svc.new_action_list(system_id).filter(list(action_ids))

        # 转换出资源对象
        resource_instances = join_ancestors_to_resource_instances(
            system_id, resource_type, [{"id": data["id"], "name": data["name"], "ancestors": data.get("ancestors")}]
        )

        # TODO: 可能需要校验实例视图，多个Action，具体是单实例符合实例视图还是层级符合实例视图？

        # 授权或回收
        result, policies = self.policy_svc.grant_or_revoke_batch_instance(
            Operate.GRANT.value, system_id, actions, subject, resource_instances
        )

        audit_context_setter(operate=Operate.GRANT.value, subject=subject, system_id=system_id, policies=policies)

        return Response(result)


# TODO: [重构]新建关联单独拆分views/ResourceCreatorAction.py
class BatchResourceCreatorActionView(
    AuthorizationAPIAllowListCheckMixin, SystemClientCheckMixin, SubjectCheckMixin, ExceptionHandlerMixin, APIView
):
    """
    新建关联授权 - 批量资源实例
    """

    authentication_classes = [ESBAuthentication]
    permission_classes = [IsAuthenticated]

    action_svc = ActionService()
    policy_svc = PolicyService()
    rca_svc = ResourceCreatorActionService()

    @swagger_auto_schema(
        operation_description="新建关联授权",
        auto_schema=ResponseSwaggerAutoSchema,
        request_body=BatchResourceCreatorActionSLZ,
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["open"],
    )
    @view_audit_decorator(SubjectPolicyGrantOrRevokeAuditProvider)
    def post(self, request, *args, **kwargs):
        serializer = BatchResourceCreatorActionSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        system_id = data["system"]
        resource_type = data["type"]

        # 检查是否该系统允许调用当前授权API
        self.check_allow_resource_type(system_id, resource_type)

        # 校验调用方是否能访问该系统
        self.verify_system_client(system_id, request.bk_app_code)

        # 检测被授权的用户是否存在，不存在则尝试同步
        self.check_or_sync_user(data["creator"])

        subject = Subject(type=SubjectType.USER.value, id=data["creator"])

        # 查询出对应资源类型需要授予哪些ActionID
        action_ids = set(self.rca_svc.get_actions(system_id, resource_type))
        # 转换为Action结构
        actions = self.action_svc.new_action_list(system_id).filter(list(action_ids))

        # 转换出资源对象
        resource_instances = join_ancestors_to_resource_instances(system_id, resource_type, data["instances"])
        # 填充类型名称
        resource_instance_list = ResourceInstanceList(resource_instances)
        resource_instance_list.fill_resource_type_name()

        # TODO: 可能需要校验实例视图，多个Action，具体是单实例符合实例视图还是层级符合实例视图？

        # 授权或回收
        result, policies = self.policy_svc.grant_or_revoke_batch_instance(
            Operate.GRANT.value, system_id, actions, subject, resource_instance_list.resource_instances
        )

        audit_context_setter(operate=Operate.GRANT.value, subject=subject, system_id=system_id, policies=policies)

        return Response(result)


# TODO: [重构]新建关联单独拆分views/ResourceCreatorAction.py
class ResourceCreatorActionAttributeView(SystemClientCheckMixin, SubjectCheckMixin, ExceptionHandlerMixin, APIView):
    """
    新建关联授权 - 属性授权
    """

    authentication_classes = [ESBAuthentication]
    permission_classes = [IsAuthenticated]

    policy_svc = PolicyService()
    rca_svc = ResourceCreatorActionService()

    @swagger_auto_schema(
        operation_description="新建关联授权-属性授权",
        auto_schema=ResponseSwaggerAutoSchema,
        request_body=ResourceCreatorActionAttributeSLZ,
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["open"],
    )
    @view_audit_decorator(SubjectPolicyGrantOrRevokeAuditProvider)
    def post(self, request, *args, **kwargs):
        serializer = ResourceCreatorActionAttributeSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        system_id = data["system"]
        resource_type = data["type"]
        attributes_data = data["attributes"]

        # 校验调用方是否能访问该系统
        self.verify_system_client(system_id, request.bk_app_code)

        # 检测被授权的用户是否存在，不存在则尝试同步
        self.check_or_sync_user(data["creator"])

        subject = Subject(type=SubjectType.USER.value, id=data["creator"])

        # 查询出对应资源类型需要授予哪些ActionID
        action_ids = self.rca_svc.get_actions(system_id, resource_type)

        # 转换成资源属性
        attributes = [Attribute(**a) for a in attributes_data]

        # 授权
        result, policies = self.policy_svc.grant_attribute(system_id, action_ids, subject, attributes)

        audit_context_setter(operate=Operate.GRANT.value, subject=subject, system_id=system_id, policies=policies)

        return Response(result)
