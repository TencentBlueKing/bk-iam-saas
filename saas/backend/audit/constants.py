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
from aenum import LowerStrEnum, StrEnum, auto

from backend.util.enum import ChoicesEnum


class AuditSourceType(ChoicesEnum, LowerStrEnum):
    WEB = auto()
    OPENAPI = auto()
    TASK = auto()
    APPROVAL = auto()
    HANDOVER = auto()

    @classmethod
    def to_int(cls, _type: str) -> int:
        return {
            cls.WEB.value: 0,
            cls.OPENAPI.value: 1,
        }.get(_type, -1)


class AuditObjectType(ChoicesEnum, LowerStrEnum):
    GROUP = auto()
    USER = auto()
    DEPARTMENT = auto()
    TEMPLATE = auto()
    SUBJECT_TEMPLATE = auto()
    ROLE = auto()
    TASK = auto()
    EVENT = auto()
    COMMONACTION = auto()
    ACTION = auto()
    WHITE_LIST = auto()

    # 用户黑名单, 用于冻结/解冻用户使用
    USER_BLACK_LIST = auto()

    # 用户权限清理
    USER_PERMISSION_CLEAN = auto()


class AuditStatus(ChoicesEnum):
    SUCCEED = 0
    FAILED = 1
    COMPLETED = 2
    ERROR = 3


class AuditType(ChoicesEnum, StrEnum):
    def _generate_next_value_(name, start, count, last_values):
        return name.lower().replace("_", ".")

    GROUP_CREATE = auto()
    GROUP_UPDATE = auto()
    GROUP_DELETE = auto()
    GROUP_MEMBER_CREATE = auto()
    GROUP_MEMBER_DELETE = auto()
    GROUP_MEMBER_RENEW = auto()
    GROUP_POLICY_CREATE = auto()
    GROUP_POLICY_UPDATE = auto()
    GROUP_POLICY_DELETE = auto()
    GROUP_TEMPLATE_CREATE = auto()
    GROUP_TEMPLATE_DELETE = auto()  # unused
    GROUP_TRANSFER = auto()

    USER_POLICY_CREATE = auto()
    USER_POLICY_UPDATE = auto()
    USER_POLICY_DELETE = auto()  # unused
    USER_TEMPORARY_POLICY_CREATE = auto()
    USER_TEMPORARY_POLICY_DELETE = auto()
    DEPARTMENT_UPDATE = auto()  # unused

    TEMPLATE_CREATE = auto()
    TEMPLATE_UPDATE = auto()
    TEMPLATE_DELETE = auto()
    TEMPLATE_MEMBER_CREATE = auto()  # unused
    TEMPLATE_MEMBER_UPDATE = auto()  # unused
    TEMPLATE_MEMBER_DELETE = auto()
    TEMPLATE_PREUPDATE_CREATE = auto()
    TEMPLATE_PREUPDATE_DELETE = auto()
    TEMPLATE_UPDATE_COMMIT = auto()
    TEMPLATE_VERSION_SYNC = auto()  # unused
    TEMPLATE_VERSION_UPDATE = auto()  # unused

    SUBJECT_TEMPLATE_CREATE = auto()
    SUBJECT_TEMPLATE_UPDATE = auto()
    SUBJECT_TEMPLATE_DELETE = auto()
    SUBJECT_TEMPLATE_MEMBER_CREATE = auto()
    SUBJECT_TEMPLATE_MEMBER_DELETE = auto()
    SUBJECT_TEMPLATE_GROUP_DELETE = auto()

    ROLE_CREATE = auto()
    ROLE_UPDATE = auto()
    ROLE_DELETE = auto()
    ROLE_MEMBER_CREATE = auto()
    ROLE_MEMBER_DELETE = auto()
    ROLE_MEMBER_UPDATE = auto()
    ROLE_MEMBER_POLICY_CREATE = auto()
    ROLE_MEMBER_POLICY_DELETE = auto()
    ROLE_COMMONACTION_CREATE = auto()
    ROLE_COMMONACTION_DELETE = auto()
    ROLE_GROUP_RENEW = auto()

    APPROVAL_GLOBAL_UPDATE = auto()
    APPROVAL_ACTION_UPDATE = auto()
    APPROVAL_GROUP_UPDATE = auto()
    ACTION_SENSITIVITY_LEVEL_UPDATE = auto()

    EVENT_ROLLBACK = auto()  # unused

    ADMIN_API_ALLOW_LIST_CONFIG_CREATE = auto()
    ADMIN_API_ALLOW_LIST_CONFIG_DELETE = auto()

    AUTHORIZATION_API_ALLOW_LIST_CONFIG_CREATE = auto()
    AUTHORIZATION_API_ALLOW_LIST_CONFIG_DELETE = auto()

    MANAGEMENT_API_ALLOW_LIST_CONFIG_CREATE = auto()
    MANAGEMENT_API_ALLOW_LIST_CONFIG_DELETE = auto()

    USER_BLACKLIST_MEMBER_CREATE = auto()
    USER_BLACKLIST_MEMBER_DELETE = auto()
    USER_PERMISSION_CLEAN = auto()
