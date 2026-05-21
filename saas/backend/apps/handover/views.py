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
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, mixins

from backend.apps.application.models import Application
from backend.apps.application.views import admin_not_need_apply_check
from backend.apps.handover.constants import HandoverStatus
from backend.apps.handover.models import HandoverRecord, HandoverTask
from backend.biz.application import ApplicationBiz, HandoverApplicationDataBean
from backend.biz.handover import HANDOVER_INFO_ENRICHER_MAP
from backend.common.error_codes import error_codes
from backend.common.lock import gen_permission_handover_lock
from backend.service.constants import ApplicationStatus, ApplicationType
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

        # 1. 校验合法性 + 提取详细信息（同时作为后续锁 key / 互斥校验的输入）
        detailed_handover_info = self._validate_and_extract_handover_info(handover_from, handover_info)

        # 2. 按对象粒度加分布式锁，避免同一用户对同一对象并发发起交接
        locks = self._acquire_handover_task_locks(handover_from, detailed_handover_info)

        try:
            # 3. 互斥校验：已存在运行中 record 或审批中 application 且对象重叠时拒绝
            # 双重校验，避免配置切换造成风险
            self._check_running_handover_conflict(handover_from, detailed_handover_info)
            self._check_pending_application_conflict(handover_from, detailed_handover_info)

            # 4. 审批开关开启时, 走 Application + ITSM 审批流; 否则保持原有立即生效逻辑
            if getattr(settings, "ENABLE_HANDOVER_APPROVAL", False):
                return self._create_with_approval(handover_from, handover_to, reason, detailed_handover_info)

            return self._create_immediately(handover_from, handover_to, reason, detailed_handover_info)
        finally:
            for lock in locks:
                lock.release()

    def _create_immediately(self, handover_from, handover_to, reason, detailed_handover_info):
        """关闭审批开关:  立即创建 HandoverRecord 并触发异步执行"""
        with transaction.atomic():
            # 创建任务
            handover_record = HandoverRecord.objects.create(
                handover_from=handover_from, handover_to=handover_to, reason=reason
            )

            handover_task_details = self._gen_handover_tasks(detailed_handover_info, handover_record)

            # 创建子任务信息
            if handover_task_details:
                HandoverTask.objects.bulk_create(handover_task_details, batch_size=100)
        # 不可在事务里启动异步任务，因为任务启动时可能 DB 查询不到 HandoverTask 数据（事务提交比任务启动慢的情况）
        execute_handover_task.delay(
            handover_from=handover_from, handover_to=handover_to, handover_record_id=handover_record.id
        )

        return Response({"id": handover_record.id})

    def _create_with_approval(self, handover_from, handover_to, reason, detailed_handover_info):
        """开启审批开关: 走 ITSM 审批"""
        # 创建审批单
        application = self.application_biz.create_for_handover(
            HandoverApplicationDataBean(
                applicant=handover_from,
                reason=reason,
                handover_to=handover_to,
                handover_info=detailed_handover_info,
            ),
        )

        return Response(
            {
                "application_id": application.id,
                "approval_sn": application.sn,
                "status": ApplicationStatus.PENDING.value,
            }
        )

    def _acquire_handover_task_locks(self, handover_from, detailed_handover_info):
        """按对象粒度逐个获取分布式锁，任一锁获取失败时回滚已持有的锁并抛出 TASK_EXIST"""
        locks = []

        for key in self._gen_handover_task_lock_keys(handover_from, detailed_handover_info):
            lock = gen_permission_handover_lock(key)
            if not lock.acquire():
                for acquired_lock in locks:
                    acquired_lock.release()
                raise error_codes.TASK_EXIST.format(message="请勿重复提交")
            locks.append(lock)

        return locks

    def _gen_handover_task_lock_keys(self, handover_from, detailed_handover_info):
        """生成排序后的锁 key 集合，格式为 handover_from:object_type:object_id，排序以避免死锁"""
        keys = set()
        for object_type, infos in detailed_handover_info.items():
            for one in infos:
                keys.add("{}:{}:{}".format(handover_from, object_type, one["id"]))
        return sorted(keys)

    def _check_running_handover_conflict(self, handover_from, detailed_handover_info):
        """检查是否已存在相同交接对象的运行中 HandoverRecord，通过 (object_type, object_id) 集合交集判断"""
        new_task_keys = {
            (object_type, str(one["id"])) for object_type, infos in detailed_handover_info.items() for one in infos
        }
        if not new_task_keys:
            return

        running_record_ids = list(
            HandoverRecord.objects.filter(
                handover_from=handover_from, status=HandoverStatus.RUNNING.value
            ).values_list("id", flat=True)
        )
        if not running_record_ids:
            return

        existing_task_keys = set(
            HandoverTask.objects.filter(handover_record_id__in=running_record_ids).values_list(
                "object_type", "object_id"
            )
        )

        if new_task_keys & existing_task_keys:
            # 找出具体的冲突对象
            conflict_keys = new_task_keys & existing_task_keys
            conflict_object_pairs = [f"{object_type}:{object_id}" for object_type, object_id in conflict_keys]
            raise error_codes.TASK_EXIST.format(
                message=f"存在正在执行的交接任务，冲突对象: {', '.join(conflict_object_pairs)}", replace=True
            )

    def _check_pending_application_conflict(self, handover_from, detailed_handover_info):
        """检查是否已存在审批中且交接对象有重叠的交接申请单（按 (object_type, object_id) 集合交集判断）"""
        if not getattr(settings, "ENABLE_HANDOVER_APPROVAL", False):
            return

        new_task_keys = {
            (object_type, str(one["id"])) for object_type, infos in detailed_handover_info.items() for one in infos
        }
        if not new_task_keys:
            return

        pending_applications = Application.objects.filter(
            applicant=handover_from,
            type=ApplicationType.HANDOVER.value,
            status=ApplicationStatus.PENDING.value,
        ).only("id", "_data")

        for application in pending_applications:
            existing_handover_info = (application.data or {}).get("handover_info") or {}
            existing_task_keys = {
                (object_type, str(one["id"]))
                for object_type, infos in existing_handover_info.items()
                if infos
                for one in infos
                if isinstance(one, dict) and "id" in one
            }
            if new_task_keys & existing_task_keys:
                # 找出具体的冲突对象
                conflict_keys = new_task_keys & existing_task_keys
                conflict_object_pairs = [f"{object_type}:{object_id}" for object_type, object_id in conflict_keys]
                raise error_codes.TASK_EXIST.format(
                    message=f"存在审批中的交接申请，冲突对象: {', '.join(conflict_object_pairs)}", replace=True
                )

    def _validate_and_extract_handover_info(self, handover_from, handover_info):
        """校验交接内容合法性 + 将仅含 ID 的 handover_info 扩展为含详细信息的数据"""
        detailed: Dict[str, list] = {}
        for key, value in handover_info.items():
            if not value:
                continue
            # 1. 合法性校验
            HANDOVER_VALIDATOR_MAP[key](handover_from, value).validate()
            # 2. 提取详细信息
            provider_cls = HANDOVER_INFO_ENRICHER_MAP[key]
            detailed[key] = provider_cls(handover_from, value).get_info()
        return detailed

    def _gen_handover_tasks(self, detailed_handover_info, handover_record):
        """基于已展开的详细信息构造 HandoverTask 列表"""
        handover_task_details = []
        for key, infos in detailed_handover_info.items():
            if not infos:
                continue
            for one in infos:
                handover_task_details.append(
                    HandoverTask(
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
        return super().list(request, *args, **kwargs)


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
