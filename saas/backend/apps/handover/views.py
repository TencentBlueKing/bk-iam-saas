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

from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, mixins

from backend.apps.application.views import admin_not_need_apply_check
from backend.apps.handover.constants import HandoverObjectType
from backend.apps.handover.models import HandoverRecord, HandoverTask
from backend.apps.handover.serializers import HandoverRecordSLZ, HandoverSLZ, HandoverTaskSLZ
from backend.apps.handover.validation import (
    BaseHandoverValidator,
    CustomPolicyValidator,
    GroupInfoValidator,
    RoleInfoValidator,
    SubjectTemplateValidator,
)
from backend.biz.application import ApplicationBiz, HandoverApplicationDataBean
from backend.biz.handover import HandoverBiz

from .tasks import execute_handover_task

HANDOVER_VALIDATOR_MAP: Dict[str, Type[BaseHandoverValidator]] = {
    HandoverObjectType.GROUP_IDS.value: GroupInfoValidator,
    HandoverObjectType.CUSTOM_POLICIES.value: CustomPolicyValidator,
    HandoverObjectType.ROLE_IDS.value: RoleInfoValidator,
    HandoverObjectType.SUBJECT_TEMPLATE_IDS.value: SubjectTemplateValidator,
}


class HandoverViewSet(GenericViewSet):
    handover_biz = HandoverBiz()
    application_biz = ApplicationBiz()

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

        # 校验 handover_info 合法性
        for key, value in handover_info.items():
            if not value:
                continue
            validator = HANDOVER_VALIDATOR_MAP[key](handover_from, value)
            validator.validate()

        # 审批开关开启时, 走 Application + ITSM 审批流; 否则保持原有立即生效逻辑
        if settings.ENABLE_HANDOVER_APPROVAL:
            data_bean = HandoverApplicationDataBean(
                applicant=handover_from,
                reason=reason,
                handover_to=handover_to,
                handover_info=handover_info,
            )
            result = self.application_biz.create_handover_with_approval(data_bean)
            return Response(result)

        handover_record = self.handover_biz.create_handover_record(handover_from, handover_to, reason, handover_info)
        # 不可在事务里启动异步任务，因为任务启动时可能 DB 查询不到 HandoverTask 数据（事务提交比任务启动慢的情况）
        execute_handover_task.delay(
            handover_from=handover_from, handover_to=handover_to, handover_record_id=handover_record.id
        )

        return Response({"id": handover_record.id})


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
        handover_record_id = kwargs["handover_record_id"]
        handover_tasks = HandoverTask.objects.filter(handover_record_id=handover_record_id)
        serializer = HandoverTaskSLZ(handover_tasks, many=True)
        return Response(serializer.data)
