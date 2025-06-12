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

from aenum import LowerStrEnum, auto, skip
from django.utils.translation import gettext as _

from backend.util.enum import ChoicesEnum


class TaskStatus(ChoicesEnum):
    PENDING = 0
    RUNNING = 1
    SUCCESS = 2
    FAILURE = 3
    CANCEL = 4

    _choices_labels = skip(
        ((PENDING, "未开始"), (RUNNING, "运行中"), (SUCCESS, "成功"), (FAILURE, "失败"), (CANCEL, "取消"))
    )


class TaskType(ChoicesEnum, LowerStrEnum):
    TEMPLATE_UPDATE = auto()
    GROUP_AUTHORIZATION = auto()

    _choices_labels = skip(((TEMPLATE_UPDATE, _("模板更新")), (GROUP_AUTHORIZATION, _("用户组授权"))))
