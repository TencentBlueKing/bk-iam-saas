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


class HandoverViewSet(GenericViewSet):
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

        handover_record = self._create_handover_record(handover_from, handover_to, reason, handover_info)
        # 不可在事务里启动异步任务，因为任务启动时可能 DB 查询不到 HandoverTask 数据（事务提交比任务启动慢的情况）
        execute_handover_task.delay(
            handover_from=handover_from, handover_to=handover_to, handover_record_id=handover_record.id
        )

        return Response({"id": handover_record.id})

    def _create_handover_record(self, handover_from, handover_to, reason, handover_info):
        """创建交接记录及子任务，包含对象粒度的分布式锁和重复任务校验"""
        handover_task_details = self._gen_handover_tasks(handover_from, handover_info)
        # 按对象粒度加锁，防止并发创建相同对象的交接任务
        locks = self._acquire_handover_task_locks(handover_from, handover_task_details)

        try:
            if self._has_running_handover_tasks(handover_from, handover_task_details):
                # 已存在相同交接对象正在运行的任务，不能新建重复任务
                raise error_codes.TASK_EXIST

            with transaction.atomic():
                handover_record = HandoverRecord.objects.create(
                    handover_from=handover_from, handover_to=handover_to, reason=reason
                )

                # 子任务在生成时未关联 record，此处回填关联关系
                for task in handover_task_details:
                    task.handover_record_id = handover_record.id

                if handover_task_details:
                    HandoverTask.objects.bulk_create(handover_task_details, batch_size=100)

            return handover_record
        finally:
            for lock in locks:
                lock.release()

    def _acquire_handover_task_locks(self, handover_from, handover_task_details):
        """逐个获取对象粒度的分布式锁，任一锁获取失败时回滚已持有的锁并抛出异常"""
        locks = []

        for key in self._gen_handover_task_lock_keys(handover_from, handover_task_details):
            lock = gen_permission_handover_lock(key)
            if not lock.acquire():
                for acquired_lock in locks:
                    acquired_lock.release()
                raise error_codes.TASK_EXIST
            locks.append(lock)

        return locks

    def _gen_handover_task_lock_keys(self, handover_from, handover_task_details):
        """生成排序后的锁 key 集合，格式为 handover_from:object_type:object_id，排序以避免死锁"""
        return sorted(
            {"{}:{}:{}".format(handover_from, task.object_type, task.object_id) for task in handover_task_details}
        )

    def _has_running_handover_tasks(self, handover_from, handover_task_details):
        """检查是否已存在相同交接对象的运行中任务，通过 (object_type, object_id) 集合交集判断"""
        new_task_keys = {(task.object_type, str(task.object_id)) for task in handover_task_details}
        if not new_task_keys:
            return False

        running_record_ids = list(
            HandoverRecord.objects.filter(
                handover_from=handover_from, status=HandoverStatus.RUNNING.value
            ).values_list("id", flat=True)
        )
        if not running_record_ids:
            return False

        existing_task_keys = set(
            HandoverTask.objects.filter(handover_record_id__in=running_record_ids).values_list(
                "object_type", "object_id"
            )
        )

        return bool(new_task_keys & existing_task_keys)

    def _gen_handover_tasks(self, handover_from, handover_info):
        """根据交接信息生成子任务列表（未关联 handover_record，由调用方回填）"""
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
                        object_type=key,
                        object_id=str(one["id"]),
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
        handover_record_id = kwargs["handover_record_id"]
        handover_tasks = HandoverTask.objects.filter(handover_record_id=handover_record_id)
        serializer = HandoverTaskSLZ(handover_tasks, many=True)
        return Response(serializer.data)
