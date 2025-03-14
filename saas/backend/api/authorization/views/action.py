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
from rest_framework.views import APIView

from backend.api.authentication import ESBAuthentication
from backend.audit.audit import audit_context_setter, view_audit_decorator
from backend.biz.resource_creator_action import ResourceCreatorActionBiz
from backend.service.models import Subject
from backend.trans.open_authorization import AuthorizationTrans

from ..audit import SubjectPolicyGrantOrRevokeAuditProvider
from ..constants import AuthorizationAPIEnum, OperateEnum, VerifyApiParamLocationEnum
from ..mixins import AuthViewMixin
from ..permissions import AuthorizationAPIPermission
from ..serializers import ActionAttributeSLZ


class ActionAttributeView(AuthViewMixin, APIView):
    """属性授权"""

    authentication_classes = [ESBAuthentication]
    permission_classes = [AuthorizationAPIPermission]
    authorization_api_permission = {
        "post": (
            VerifyApiParamLocationEnum.SYSTEM_IN_BODY.value,
            AuthorizationAPIEnum.CREATOR_AUTHORIZATION_INSTANCE.value,
        ),
    }

    biz = ResourceCreatorActionBiz()
    trans = AuthorizationTrans()

    @swagger_auto_schema(
        operation_description="属性授权",
        request_body=ActionAttributeSLZ,
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["open"],
    )
    @view_audit_decorator(SubjectPolicyGrantOrRevokeAuditProvider)
    def create(self, request, *args, **kwargs):
        serializer = ActionAttributeSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        subject = Subject.from_username(data["creator"])
        system_id = data["system"]
        action_id = data["action_id"]
        resource_type_id = data["type"]
        attributes = data["attributes"]

        # 转换为策略列表
        policy_list = self.trans.to_policy_list_for_attributes_of_creator(
            system_id,
            [
                action_id,
            ],
            resource_type_id,
            attributes,
        )

        # 授权
        policies = self.grant_or_revoke(OperateEnum.GRANT.value, subject, policy_list)

        audit_context_setter(operate=OperateEnum.GRANT.value, subject=subject, system_id=system_id, policies=policies)

        return self.batch_policy_response(policies)
