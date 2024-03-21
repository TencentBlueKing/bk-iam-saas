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
from aenum import LowerStrEnum, StrEnum, auto, skip
from django.utils.translation import gettext as _

from backend.util.enum import ChoicesEnum


class PolicyTag(LowerStrEnum):
    """
    策略新增更新标签
    """

    ADD = auto()
    UPDATE = auto()
    UNCHANGED = auto()
    DELETE = auto()
    RELATED = auto()


class ConditionTag(LowerStrEnum):
    ADD = auto()
    DELETE = auto()
    UNCHANGED = auto()


class ActionTag(LowerStrEnum):
    READONLY = auto()
    CHECKED = auto()
    UNCHECKED = auto()
    DELETE = auto()


# 新用户自动同步的用户数量
NEW_USER_AUTO_SYNC_COUNT_LIMIT = 50


class StaffStatus(ChoicesEnum, StrEnum):
    IN = auto()
    OUT = auto()

    _choices_labels = skip(((IN, _("在职")), (OUT, _("离职"))))


class HandoverTaskStatus(ChoicesEnum, LowerStrEnum):
    """权限交接具体任务的执行状态"""

    RUNNING = auto()
    SUCCEED = auto()
    FAILED = auto()

    _choices_labels = skip(
        (
            (RUNNING, _("正在交接")),
            (SUCCEED, _("交接成功")),
            (
                FAILED,
                _("交接失败"),
            ),
        )
    )


class PermissionTypeEnum(ChoicesEnum, LowerStrEnum):
    """权限类型"""

    CUSTOM = auto()
    TEMPLATE = auto()
    RESOURCE_INSTANCE = auto()

    _choices_labels = skip(((CUSTOM, _("自定义权限")), (TEMPLATE, _("模板权限")), (RESOURCE_INSTANCE, _("资源实例"))))
