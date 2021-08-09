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


class GroupMemberType(ChoicesEnum, LowerStrEnum):
    USER = auto()
    DEPARTMENT = auto()

    _choices_labels = skip(((USER, "用户"), (DEPARTMENT, "部门")))


class SubjectRelationType(ChoicesEnum, LowerStrEnum):
    DEPARTMENT = auto()
    GROUP = auto()

    _choices_labels = skip(((GROUP, "用户组"), (DEPARTMENT, "部门")))


class GroupSaaSAttributeEnum(ChoicesEnum, LowerStrEnum):
    """用户组SaaS属性枚举"""

    READONLY = auto()

    _choices_labels = skip(((READONLY, "只读"),))


class GroupAttributeValueTypeEnum(ChoicesEnum, LowerStrEnum):
    """用户组SaaS属性值的数据类型"""

    String = auto()
    Boolean = auto()
    Integer = auto()


# 每个属性的值类型
GROUP_SAAS_ATTRIBUTE_VALUE_TYPE_MAP = {
    GroupSaaSAttributeEnum.READONLY.value: GroupAttributeValueTypeEnum.Boolean.value
}

# 每个属性的默认值
GROUP_SAAS_ATTRIBUTE_DEFAULT_VALUE_MAP = {GroupSaaSAttributeEnum.READONLY.value: False}
