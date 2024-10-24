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
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from backend.api.admin.serializers import AdminSystemProviderConfigSLZ
from backend.api.authentication import ESBAuthentication
from backend.api.management.constants import ManagementAPIEnum, VerifyApiParamLocationEnum
from backend.api.management.v2.permissions import ManagementAPIPermission
from backend.apps.system.views import SystemViewSet
from backend.service.resource import SystemProviderConfigService


class ManagementSystemViewSet(SystemViewSet):
    authentication_classes = [ESBAuthentication]
    permission_classes = [ManagementAPIPermission]
    management_api_permission = {
        "list": (VerifyApiParamLocationEnum.SYSTEM_IN_PATH.value, ManagementAPIEnum.SYSTEM_PROVIDER_CONFIG_LIST.value)
    }

    pagination_class = None  # 去掉swagger中的limit offset参数

    translate_exempt = True

    def list(self, request, *args, **kwargs):
        request.query_params._mutable = True
        request.query_params["all"] = True
        request.query_params["hidden"] = False

        return super().list(request, *args, **kwargs)


class ManagementSystemProviderConfigViewSet(GenericViewSet):
    authentication_classes = [ESBAuthentication]
    permission_classes = [ManagementAPIPermission]
    management_api_permission = {
        "list": (VerifyApiParamLocationEnum.SYSTEM_IN_PATH.value, ManagementAPIEnum.SYSTEM_PROVIDER_CONFIG_LIST.value)
    }

    @swagger_auto_schema(
        operation_description="系统回调信息",
        responses={status.HTTP_200_OK: AdminSystemProviderConfigSLZ(label="系统回调信息")},
        tags=["admin.system.provider_config"],
    )
    def list(self, request, *args, **kwargs):
        system_id = kwargs["system_id"]
        system_provider_config = SystemProviderConfigService().get_provider_config(system_id=system_id)

        return Response(AdminSystemProviderConfigSLZ(system_provider_config).data)
