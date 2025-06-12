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

from backend.util.enum import ChoicesEnum


class OperateEnum(ChoicesEnum, LowerStrEnum):
    GROUP_UPDATE = auto()
    GROUP_DELETE = auto()
    GROUP_MEMBER_CREATE = auto()
    GROUP_MEMBER_DELETE = auto()
    GROUP_POLICY_CREATE = auto()
    GROUP_POLICY_DELETE = auto()
    GROUP_POLICY_UPDATE = auto()
    GROUP_MEMBER_RENEW = auto()
    GROUP_TRANSFER = auto()

    _choices_labels = skip(
        (
            (GROUP_UPDATE, "修改用户组"),
            (GROUP_DELETE, "删除用户组"),
            (GROUP_MEMBER_CREATE, "添加用户组成员"),
            (GROUP_MEMBER_DELETE, "删除用户组成员"),
            (GROUP_POLICY_CREATE, "用户组添加权限"),
            (GROUP_POLICY_DELETE, "用户组删除权限"),
            (GROUP_POLICY_UPDATE, "用户组更新权限"),
            (GROUP_MEMBER_RENEW, "用户组成员续期"),
            (GROUP_TRANSFER, "用户组转移"),
        )
    )
