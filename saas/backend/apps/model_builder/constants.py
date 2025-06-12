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


class ModelSectionEnum(ChoicesEnum, LowerStrEnum):
    SYSTEM = auto()

    RESOURCE_TYPE = auto()
    INSTANCE_SELECTION = auto()
    ACTION = auto()

    ACTION_GROUPS = auto()
    COMMON_ACTIONS = auto()

    _choices_labels = skip(
        (
            (SYSTEM, "系统"),
            (RESOURCE_TYPE, "资源类型"),
            (INSTANCE_SELECTION, "实例视图"),
            (ACTION, "操作"),
            (ACTION_GROUPS, "操作组"),
            (COMMON_ACTIONS, "常用操作"),
        )
    )


# 类型是dict, 直接set更新或全删除
ModelSectionTypeDict = [
    ModelSectionEnum.SYSTEM.value,
    ModelSectionEnum.COMMON_ACTIONS.value,
    ModelSectionEnum.ACTION_GROUPS.value,
]

# 类型是列表, 可以根据id进行更新和删除
ModelSectionTypeList = [
    ModelSectionEnum.RESOURCE_TYPE.value,
    ModelSectionEnum.INSTANCE_SELECTION.value,
    ModelSectionEnum.ACTION.value,
]


class SystemProviderAuthEnum(ChoicesEnum, LowerStrEnum):
    NONE = auto()
    BASIC = auto()

    _choices_labels = skip(
        (
            (NONE, "none"),
            (BASIC, "basic auth"),
        )
    )


class ActionTypeEnum(ChoicesEnum, LowerStrEnum):
    CREATE = auto()
    EDIT = auto()
    VIEW = auto()
    DELETE = auto()
    LIST = auto()
    MANAGE = auto()
    EXECUTE = auto()
    DEBUG = auto()
    USE = auto()

    _choices_labels = skip(
        (
            (CREATE, "创建"),
            (EDIT, "编辑"),
            (VIEW, "查看"),
            (DELETE, "删除"),
            (LIST, "列表"),
            (MANAGE, "管理"),
            (EXECUTE, "执行"),
            (DEBUG, "调试"),
            (USE, "使用"),
        )
    )


class GenerateJsonTypeEnum(ChoicesEnum, LowerStrEnum):
    API = auto()
    MIGRATE = auto()

    _choices_labels = skip(
        (
            (API, "api注册"),
            (MIGRATE, "do migrate"),
        )
    )
