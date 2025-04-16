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

from backend.apps.policy.serializers import PolicyDeleteSLZ, PolicySLZ, PolicySystemSLZ
from backend.apps.subject.audit import SubjectTemporaryPolicyDeleteAuditProvider
from backend.audit.audit import audit_context_setter, view_audit_decorator
from backend.biz.open import ApplicationPolicyListCache
from backend.biz.policy import PolicyOperationBiz, PolicyQueryBiz
from backend.common.serializers import SystemQuerySLZ
from backend.service.models import Subject


class TemporaryPolicyViewSet(GenericViewSet):
    pagination_class = None  # 去掉swagger中的limit offset参数

    policy_query_biz = PolicyQueryBiz()
    policy_operation_biz = PolicyOperationBiz()

    application_policy_list_cache = ApplicationPolicyListCache()

    @swagger_auto_schema(
        operation_description="用户的所有临时权限列表",
        query_serializer=SystemQuerySLZ(),
        responses={status.HTTP_200_OK: PolicySLZ(label="策略", many=True)},
        tags=["temporary_policy"],
    )
    def list(self, request, *args, **kwargs):
        slz = SystemQuerySLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)

        system_id = slz.validated_data["system_id"]

        subject = Subject.from_username(request.user.username)
        policies = self.policy_query_biz.list_temporary_by_subject(system_id, subject)

        return Response([p.dict() for p in policies])

    @swagger_auto_schema(
        operation_description="删除权限",
        query_serializer=PolicyDeleteSLZ(),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["temporary_policy"],
    )
    @view_audit_decorator(SubjectTemporaryPolicyDeleteAuditProvider)
    def destroy(self, request, *args, **kwargs):
        slz = PolicyDeleteSLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)

        system_id = slz.validated_data["system_id"]
        ids = slz.validated_data["ids"]
        subject = Subject.from_username(request.user.username)

        policies = self.policy_query_biz.list_temporary_by_policy_ids(system_id, subject, ids)

        # 删除权限
        self.policy_operation_biz.delete_temporary_policies_by_ids(system_id, subject, ids)

        # 写入审计上下文
        audit_context_setter(subject=subject, system_id=system_id, policies=policies)

        return Response()


class TemporaryPolicySystemViewSet(GenericViewSet):
    pagination_class = None  # 去掉swagger中的limit offset参数

    biz = PolicyQueryBiz()

    @swagger_auto_schema(
        operation_description="用户的有临时权限的所有系统列表",
        responses={status.HTTP_200_OK: PolicySystemSLZ(label="系统", many=True)},
        tags=["temporary_policy"],
    )
    def list(self, request, *args, **kwargs):
        subject = Subject.from_username(request.user.username)

        data = self.biz.list_temporary_system_counter_by_subject(subject)

        return Response([one.dict() for one in data])
