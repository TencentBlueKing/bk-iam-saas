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
import json
from backend.apps.handover.constants import HandoverStatus

from django.core.cache import cache
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, mixins
from drf_yasg.utils import swagger_auto_schema
from drf_yasg.openapi import Response as yasg_response
from backend.common.swagger import ResponseSwaggerAutoSchema
from backend.apps.handover.models import HandOverRecord, HandOverTask

from .serializers import HandOverSLZ, HandOverRecordSLZ, HandOverTaskSLZ, HandOverTaskSLZ
from .tasks import execute_handover_task
from ...biz.handover import create_handover_task

handover_logger = logging.getLogger("handover")


class HandOverViewSet(GenericViewSet):
    paginator = None  # 去掉swagger中的limit offset参数

    @swagger_auto_schema(
        operation_description="执行权限交接",
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: yasg_response({})},
        tags=["handover"],
    )
    def create(self, request, *args, **kwargs):
        serializer = HandOverSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        handover_from = request.user.username
        data = serializer.validated_data

        handover_to = data["handover_to"]
        reason = data["reason"]
        handover_info = data["handover_info"]

        try:
            with cache.lock(handover_from, timeout=10):
                record = HandOverRecord.objects.filter(
                    handover_from=handover_from,
                    status=HandoverStatus.Running.value
                )
                if record is not None:
                    return Response({"id": record.id})

                handover_record = HandOverRecord.objects.create(
                    handover_from=handover_from,
                    handover_to=handover_to,
                    reason=reason
                )
                create_handover_task(handover_record_id=handover_record.id, handover_info=handover_info)

        except Exception:
            exception_msg = "handover cache lock error"
            handover_logger.exception(exception_msg)
            handover_record = HandOverRecord.objects.create(
                handover_from=handover_from,
                handover_to=handover_to,
                reason=reason,
                status=HandoverStatus.Failed.value
            )
            return Response({"id": handover_record.id})

        execute_handover_task.delay(handover_from=handover_from, handover_to=handover_to, record_id=handover_record_id)
        return Response({"id": handover_record.id})


class HandOverRecordsViewSet(mixins.ListModelMixin, GenericViewSet):
    serializer_class = HandOverRecordSLZ

    def get_queryset(self):
        request = self.request
        return HandOverRecord.objects.filter(handover_from=request.user.username)

    @swagger_auto_schema(
        operation_description="交接记录-查询",
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: HandOverRecordSLZ(label="交接记录")},
        tags=["handover"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(self, *args, **kwargs)


class HandOverTasksViewSet(mixins.ListModelMixin, GenericViewSet):

    @swagger_auto_schema(
        operation_description="交接任务-查询",
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: HandOverTaskSLZ(label="交接任务")},
        tags=["handover"],
    )
    def list(self, request, *args, **kwargs):
        handover_record_id = kwargs["handover_record_id"]
        handover_tasks = HandOverTask.objects.filter(handover_record_id=handover_record_id)
        serializer = HandOverTaskSLZ(handover_tasks, many=True)
        return Response(serializer.data)
