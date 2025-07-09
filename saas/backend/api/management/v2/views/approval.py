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

from functools import cached_property

from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import views

from backend.api.authentication import ESBAuthentication
from backend.api.management.constants import ManagementAPIEnum, VerifyApiParamLocationEnum
from backend.api.management.v2.permissions import ManagementAPIPermission
from backend.apps.application.models import Application
from backend.apps.role.models import Role
from backend.biz.application import ApplicationBiz


class ManagementApplicationApprovalView(views.APIView):
    """
    审批后回调权限中心
    """

    authentication_classes = [ESBAuthentication]
    permission_classes = [ManagementAPIPermission]
    management_api_permission = {
        "post": (
            VerifyApiParamLocationEnum.SYSTEM_IN_PATH.value,
            ManagementAPIEnum.V2_APPLICATION_APPROVAL.value,
        ),
    }

    @cached_property
    def biz(self):
        return ApplicationBiz(self.request.tenant_id)

    # Note: 这里会回调第三方处理，所以不定义参数
    def post(self, request, *args, **kwargs):
        source_system_id = kwargs["system_id"]
        callback_id = kwargs["callback_id"]

        # 校验系统与 callback_id 对应的审批存在
        application = get_object_or_404(Application, source_system_id=source_system_id, callback_id=callback_id)

        obj = self.biz.handle_approval_callback_request(callback_id, request)

        if isinstance(obj, Role):
            return Response({"id": application.id, "role_id": obj.id})

        return Response({"id": application.id})
