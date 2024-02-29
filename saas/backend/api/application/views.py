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
from rest_framework.viewsets import GenericViewSet, views

from backend.api.authentication import ESBAuthentication
from backend.apps.application.models import Application
from backend.apps.application.serializers import ApplicationDetailSchemaSLZ, ApplicationDetailSLZ
from backend.biz.application import ApplicationBiz
from backend.biz.open import ApplicationPolicyListCache
from backend.service.constants import ApplicationType
from backend.trans.open_application import AccessSystemApplicationTrans
from backend.util.url import url_join

from .serializers import (
    AccessSystemApplicationCustomPolicyResultSLZ,
    AccessSystemApplicationCustomPolicySLZ,
    AccessSystemApplicationSLZ,
    AccessSystemApplicationUrlSLZ,
)


class ApplicationView(views.APIView):
    """
    接入系统申请
    """

    authentication_classes = [ESBAuthentication]
    permission_classes = [IsAuthenticated]

    access_system_application_trans = AccessSystemApplicationTrans()
    application_policy_list_cache = ApplicationPolicyListCache()

    @swagger_auto_schema(
        operation_description="接入系统权限申请",
        request_body=AccessSystemApplicationSLZ(label="接入系统申请数据"),
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
        policy_list = self.access_system_application_trans.to_policy_list(data)

        # 保存到cache中
        cache_id = self.application_policy_list_cache.set(policy_list)

        # 返回重定向地址
        url = url_join(settings.APP_URL, "/apply-custom-perm")
        params = {"system_id": system_id, "cache_id": cache_id}
        url = url + "?" + urlencode(params)

        return Response({"url": url})


class ApplicationDetailView(GenericViewSet):
    """
    接入系统申请详情
    """

    authentication_classes = [ESBAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Application.objects.all()
    lookup_field = "sn"

    @swagger_auto_schema(
        operation_description="权限申请详情",
        responses={status.HTTP_200_OK: ApplicationDetailSchemaSLZ(label="申请详情")},
        tags=["open"],
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ApplicationDetailSLZ(instance)
        return Response(serializer.data)


class ApplicationCustomPolicyView(views.APIView):
    """
    创建自定义权限申请单
    """

    authentication_classes = [ESBAuthentication]
    permission_classes = [IsAuthenticated]

    access_system_application_trans = AccessSystemApplicationTrans()
    application_biz = ApplicationBiz()

    @swagger_auto_schema(
        operation_description="创建自定义权限申请单",
        request_body=AccessSystemApplicationCustomPolicySLZ(label="创建自定义权限申请单"),
        responses={status.HTTP_200_OK: AccessSystemApplicationCustomPolicyResultSLZ(label="申请单信息")},
        tags=["open"],
    )
    def post(self, request):
        # 校验数据
        serializer = AccessSystemApplicationCustomPolicySLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        username = data["applicant"]

        # 将Dict数据转换为创建单据所需的数据结构
        application_data = self.access_system_application_trans.from_grant_policy_application(username, data)
        # 创建单据
        applications = self.application_biz.create_for_policy(ApplicationType.GRANT_ACTION.value, application_data)

        return Response({"id": applications[0].id, "sn": applications[0].sn})
