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

from aenum import LowerStrEnum, StrEnum, auto, skip
from django.utils.translation import gettext as _

from backend.util.enum import ChoicesEnum


class SyncType(ChoicesEnum, LowerStrEnum):
    """同步任务的类型"""

    Full = auto()
    SingleUser = auto()

    _choices_labels = skip(((Full, _("全量")), (SingleUser, _("单个用户"))))


class SyncTaskStatus(ChoicesEnum, StrEnum):
    """同步任务的类型"""

    Running = auto()
    Succeed = auto()
    Failed = auto()

    _choices_labels = skip(((Running, _("正在执行")), (Succeed, _("执行成功")), (Failed, _("执行失败"))))


class SyncTaskLockKey(ChoicesEnum):
    """同步任务锁的 Key"""

    Full = f"sync_task_{SyncType.Full.value}"
    SingleUser = f"sync_task_{SyncType.SingleUser.value}"


class TriggerType(ChoicesEnum, LowerStrEnum):
    PERIODIC_TASK = auto()
    MANUAL_SYNC = auto()

    _choices_labels = skip(((PERIODIC_TASK, _("周期同步")), (MANUAL_SYNC, _("手动同步"))))


SYNC_TASK_DEFAULT_EXECUTOR = "periodic_task"
