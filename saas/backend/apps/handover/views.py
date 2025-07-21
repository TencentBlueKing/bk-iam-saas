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

from typing import Dict, Type

from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, mixins

from backend.apps.application.views import admin_not_need_apply_check
from backend.apps.handover.constants import HandoverStatus
from backend.apps.handover.models import HandoverRecord, HandoverTask
from backend.common.error_codes import error_codes
from backend.common.lock import gen_permission_handover_lock
from backend.mixins import TenantMixin
from backend.util.json import json_dumps

from .constants import HandoverObjectType
from .serializers import HandoverRecordSLZ, HandoverSLZ, HandoverTaskSLZ
from .tasks import execute_handover_task
from .validation import (
    BaseHandoverDataProcessor,
    GroupInfoProcessor,
    GustomPolicyProcessor,
    RoleInfoProcessor,
    SubjectTemplateProcessor,
)

HANDOVER_VALIDATOR_MAP: Dict[str, Type[BaseHandoverDataProcessor]] = {
    HandoverObjectType.GROUP_IDS.value: GroupInfoProcessor,
    HandoverObjectType.CUSTOM_POLICIES.value: GustomPolicyProcessor,
    HandoverObjectType.ROLE_IDS.value: RoleInfoProcessor,
    HandoverObjectType.SUBJECT_TEMPLATE_IDS.value: SubjectTemplateProcessor,
}


class HandoverViewSet(TenantMixin, GenericViewSet):
    @swagger_auto_schema(
        operation_description="执行权限交接",
        request_body=HandoverSLZ(label="交接信息"),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["handover"],
    )
    @admin_not_need_apply_check
    def create(self, request, *args, **kwargs):
        serializer = HandoverSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        handover_from = request.user.username
        data = serializer.validated_data

        handover_to = data["handover_to"]
        reason = data["reason"]
        handover_info = data["handover_info"]

        lock = gen_permission_handover_lock(handover_from)
        if not lock.acquire():
            # 拿不到锁，直接返回
            raise error_codes.TASK_EXIST

        try:
            handover_record = HandoverRecord.objects.filter(
                handover_from=handover_from, status=HandoverStatus.RUNNING.value
            ).first()
            if handover_record is not None:
                # 已存在正在运行的任务，不能新建任务
                raise error_codes.TASK_EXIST

            with transaction.atomic():
                # 创建任务
                handover_record = HandoverRecord.objects.create(
                    tenant_id=self.tenant_id, handover_from=handover_from, handover_to=handover_to, reason=reason
                )

                handover_task_details = self._gen_handover_tasks(
                    self.tenant_id, handover_from, handover_info, handover_record
                )

                # 创建子任务信息
                if handover_task_details:
                    HandoverTask.objects.bulk_create(handover_task_details, batch_size=100)

                execute_handover_task.delay(
                    handover_from=handover_from, handover_to=handover_to, handover_record_id=handover_record.id
                )
        finally:
            # 释放锁
            lock.release()

        return Response({"id": handover_record.id})

    def _gen_handover_tasks(self, tenant_id, handover_from, handover_info, handover_record):
        handover_task_details = []
        for key, value in handover_info.items():
            if not value:
                continue
            validator = HANDOVER_VALIDATOR_MAP[key](handover_from, value)
            # 校验任务数据是否合法
            validator.validate()
            info = validator.get_info()
            for one in info:
                handover_task_details.append(
                    HandoverTask(
                        tenant_id=tenant_id,
                        handover_record_id=handover_record.id,
                        object_type=key,
                        object_id=one["id"],
                        object_detail=json_dumps(one),
                    )
                )

        return handover_task_details


class HandoverRecordsViewSet(mixins.ListModelMixin, GenericViewSet):
    serializer_class = HandoverRecordSLZ

    def get_queryset(self):
        request = self.request
        return HandoverRecord.objects.filter(handover_from=request.user.username).order_by("-created_time")

    @swagger_auto_schema(
        operation_description="交接记录 - 查询",
        responses={status.HTTP_200_OK: HandoverRecordSLZ(label="交接记录")},
        tags=["handover"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(self, *args, **kwargs)


class HandoverTasksViewSet(mixins.ListModelMixin, GenericViewSet):
    @swagger_auto_schema(
        operation_description="交接任务 - 查询",
        responses={status.HTTP_200_OK: HandoverTaskSLZ(label="交接任务")},
        tags=["handover"],
    )
    def list(self, request, *args, **kwargs):
        handover_record_id = HandoverRecord.objects.get(
            id=kwargs["handover_record_id"], handover_from=request.user.username
        ).id
        handover_tasks = HandoverTask.objects.filter(handover_record_id=handover_record_id)
        serializer = HandoverTaskSLZ(handover_tasks, many=True)
        return Response(serializer.data)
