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


class AllowGrantSubjectTypeEnum(ChoicesEnum, LowerStrEnum):
    """允许授权的Subject类型"""

    USER = auto()
    GROUP = auto()

    _choices_labels = skip(((USER, "用户"), (GROUP, "用户组")))


class Operate(ChoicesEnum, LowerStrEnum):
    GRANT = auto()
    REVOKE = auto()

    _choices_labels = skip(((GRANT, "授权"), (REVOKE, "回收")))


class AuthorizationAPIEnum(ChoicesEnum, LowerStrEnum):
    # 实例授权API，白名单控制时主要是控制System+Action
    AUTHORIZATION_INSTANCE = auto()
    # 新建关联实例授权API，白名单控制时主要是控制System+ResourceType
    CREATOR_AUTHORIZATION_INSTANCE = auto()

    _choices_labels = skip(((AUTHORIZATION_INSTANCE, "实例授权"), (CREATOR_AUTHORIZATION_INSTANCE, "新建关联实例授权")))


# 白名单控制时的任意
ALLOW_ANY = "*"
