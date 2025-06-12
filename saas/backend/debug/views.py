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

from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from backend.common.authentication import BasicAppCodeAuthentication
from backend.common.debug import RedisStorage


class DebugViewSet(GenericViewSet):
    authentication_classes = [BasicAppCodeAuthentication]
    permission_classes = [IsAuthenticated]

    pagination_class = None  # 去掉swagger中的limit offset参数

    lookup_field = "id"

    @swagger_auto_schema(
        operation_description="Celery任务调试信息列表",
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["debug"],
    )
    def list(self, request, *args, **kwargs):
        day = request.query_params.get("day", timezone.now().strftime("%Y%m%d"))
        data = RedisStorage().list_task_debug(day)
        return Response(data)

    @swagger_auto_schema(
        operation_description="调试信息详情",
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["debug"],
    )
    def retrieve(self, request, *args, **kwargs):
        _id = kwargs["id"]
        data = RedisStorage().get(_id)
        return Response(data)
