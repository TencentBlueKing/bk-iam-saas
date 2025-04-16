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
import json
from typing import Dict, Type

from celery import shared_task

from backend.apps.handover.models import HandoverRecord, HandoverTask
from backend.biz.handover import (
    BaseHandoverHandler,
    CustomHandoverHandler,
    GroupHandoverHandler,
    RoleHandoverHandler,
    SubjectTemplateHandoverHandler,
)

from .constants import HandoverObjectType, HandoverStatus

EXECUTE_HANDOVER_MAP: Dict[str, Type[BaseHandoverHandler]] = {
    HandoverObjectType.GROUP_IDS.value: GroupHandoverHandler,
    HandoverObjectType.CUSTOM_POLICIES.value: CustomHandoverHandler,
    HandoverObjectType.ROLE_IDS.value: RoleHandoverHandler,
    HandoverObjectType.SUBJECT_TEMPLATE_IDS.value: SubjectTemplateHandoverHandler,
}


@shared_task(ignore_result=True)
def execute_handover_task(handover_from, handover_to, handover_record_id):
    handover_task_list = HandoverTask.objects.filter(handover_record_id=handover_record_id)

    # 用于整个交接的最终状态判断
    total_task_count = handover_task_list.count()
    success_task_count = 0

    for handover_task in handover_task_list:
        handover_task_id = handover_task.id
        object_type = handover_task.object_type
        object_detail = json.loads(handover_task.object_detail)

        # 根据任务类别获取对应执行的类方法，每个子任务执行的成功或失败不相干扰
        handover_handler = EXECUTE_HANDOVER_MAP[object_type](
            handover_task_id, handover_from, handover_to, object_detail
        )

        is_success = handover_handler.handler()
        if is_success:
            success_task_count += 1

    HandoverRecord.objects.filter(id=handover_record_id).update(
        status=_calculate_record_status(success_task_count, total_task_count)
    )


def _calculate_record_status(success_task_count, total_task_count):
    """
    获取交接任务执行状态
    """
    if success_task_count == 0:
        return HandoverStatus.FAILED.value
    elif success_task_count == total_task_count:
        return HandoverStatus.SUCCEED.value
    else:
        return HandoverStatus.PARTIAL_FAILED.value
