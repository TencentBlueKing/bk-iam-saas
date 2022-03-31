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
from urllib.parse import urlencode

from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import views

from backend.api.authentication import ESBAuthentication
from backend.biz.open import ApplicationPolicyListCache
from backend.common.swagger import ResponseSwaggerAutoSchema
from backend.trans.open_application import AccessSystemApplicationTrans
from backend.util.url import url_join

from .serializers import AccessSystemApplicationSLZ, AccessSystemApplicationUrlSLZ


class ApplicationView(views.APIView):
    """
    接入系统申请
    """

    authentication_classes = [ESBAuthentication]
    permission_classes = [IsAuthenticated]

    access_system_application_biz = AccessSystemApplicationTrans()
    application_policy_list_cache = ApplicationPolicyListCache()

    @swagger_auto_schema(
        operation_description="接入系统权限申请",
        request_body=AccessSystemApplicationSLZ(label="接入系统申请数据"),
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: AccessSystemApplicationUrlSLZ(label="重定向URL")},
        tags=["open"],
    )
    def post(self, request):
        # 校验数据
        serializer = AccessSystemApplicationSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        system_id = data["system"]

        # 将申请的数据转换为PolicyBeanList数据结构，同时需要进行数据检查
        policy_list = self.access_system_application_biz.to_policy_list(data)

        # 保存到cache中
        cache_id = self.application_policy_list_cache.set(policy_list)

        # 返回重定向地址
        url = url_join(settings.APP_URL, "/apply-custom-perm")
        params = {"system_id": system_id, "cache_id": cache_id}
        url = url + "?" + urlencode(params)

        return Response({"url": url})
