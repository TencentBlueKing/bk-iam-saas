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

from aenum import StrEnum, auto, skip

from backend.util.enum import ChoicesEnum


class TicketStatus(ChoicesEnum, StrEnum):
    RUNNING = auto()
    FINISHED = auto()
    TERMINATION = auto()
    SUSPENDED = auto()
    REVOKED = auto()

    _choices_labels = skip(
        (
            (RUNNING, "处理中"),
            (SUSPENDED, "被挂起"),
            (FINISHED, "已结束"),
            (TERMINATION, "被终止"),  # 处理人撤销
            (REVOKED, "被撤销"),  # 申请人撤销
        )
    )
