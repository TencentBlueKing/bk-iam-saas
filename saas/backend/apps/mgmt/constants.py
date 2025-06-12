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

from backend.api.admin.constants import AdminAPIEnum
from backend.api.authorization.constants import AuthorizationAPIEnum
from backend.api.management.constants import ManagementAPIEnum
from backend.util.enum import ChoicesEnum


class ApiType(ChoicesEnum, LowerStrEnum):
    """API类型"""

    MANAGEMENT_API = auto()
    ADMIN_API = auto()
    AUTHORIZATION_API = auto()

    _choices_labels = skip(
        ((MANAGEMENT_API, _("管理类API")), (ADMIN_API, _("超级管理类API")), (AUTHORIZATION_API, _("授权类API")))
    )


class LongTaskObjectType(ChoicesEnum, LowerStrEnum):
    """长时任务 参数类型"""

    GROUP = auto()
    TEMPLATE = auto()

    _choices_labels = skip(((GROUP, _("用户组")), (TEMPLATE, _("模板"))))


WHITE_LIST_API_ENUM_MAP = {
    ApiType.MANAGEMENT_API.value: ManagementAPIEnum,
    ApiType.ADMIN_API.value: AdminAPIEnum,
    ApiType.AUTHORIZATION_API.value: AuthorizationAPIEnum,
}
