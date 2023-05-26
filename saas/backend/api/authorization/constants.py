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

from backend.api.constants import BaseAPIEnum
from backend.util.enum import ChoicesEnum


class OperateEnum(ChoicesEnum, LowerStrEnum):
    GRANT = auto()
    REVOKE = auto()

    _choices_labels = skip(((GRANT, "授权"), (REVOKE, "回收")))


class AuthorizationAPIEnum(BaseAPIEnum):
    # 实例授权API，白名单控制时主要是控制System+Action
    AUTHORIZATION_INSTANCE = auto()
    # 新建关联实例授权API，白名单控制时主要是控制System+ResourceType
    CREATOR_AUTHORIZATION_INSTANCE = auto()

    _choices_labels = skip(((AUTHORIZATION_INSTANCE, "实例授权"), (CREATOR_AUTHORIZATION_INSTANCE, "新建关联实例授权")))


class AllowListMatchOperationEnum(ChoicesEnum, LowerStrEnum):
    EQ = auto()
    STARTS_WITH = auto()


ALLOW_LIST_OBJECT_OPERATION_STEP = ":"


class VerifyApiParamLocationEnum(ChoicesEnum, LowerStrEnum):
    SYSTEM_IN_BODY = auto()
    RESOURCE_TYPE_IN_BODY = auto()
    ACTION_IN_BODY = auto()
    ACTIONS_IN_BODY = auto()

    _choices_labels = skip(
        (
            (SYSTEM_IN_BODY, "在body data里的system参数"),
            (RESOURCE_TYPE_IN_BODY, "在body data里的type参数"),
            (ACTION_IN_BODY, "在body data里的action参数"),
            (ACTIONS_IN_BODY, "在body data里的actions参数"),
        )
    )
