# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-权限中心(BlueKing-IAM) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

所有与ITSM单据的申请内容渲染相关
"""
from aenum import LowerStrEnum, auto


# 表格样式和格式
class FormSchemeEnum(LowerStrEnum):
    # 基本文本
    BASE_TEXT = auto()  # 基本文本展示样式
    BASE_TABLE_TEXT = auto()  # 表格里的基础文本展示样式
    # 用户组相关
    GROUP_TABLE = auto()  # 用户组表格
    # 操作相关
    ACTION_TABLE_WITHOUT_EXP = auto()  # Action的表格，不含有申请期限
    ACTION_TABLE = auto()  # Action的表格
    RESOURCE_GROUP_TABLE = auto()  # 资源组的表格
    # 操作关联的资源
    RESOURCE_INSTANCE_TABLE = auto()  # 资源实例表格
    RESOURCE_ATTRIBUTE_TABLE = auto()  # 资源属性表格
    RESOURCE_BOTH_TABLE = auto()  # 资源属性和实例表格
    # 环境属性
    ENVIRONMENT_TABLE = auto()


FORM_SCHEMES = {
    FormSchemeEnum.BASE_TEXT.value: {
        "type": "text",
        "attrs": {"styles": {"label": ["border"], "value": ["highlight", "border"]}},
    },
    FormSchemeEnum.BASE_TABLE_TEXT.value: {
        "type": "text",
        "attrs": {"styles": {"label": ["border"], "value": ["highlight", "border"]}},
    },
    FormSchemeEnum.GROUP_TABLE.value: {
        "type": "table",
        "attrs": {
            "column": [
                {"name": "ID", "type": "text", "key": "id"},
                {"name": "管理空间", "type": "text", "key": "role_name"},
                {"name": "用户组", "key": "group_info", "scheme": FormSchemeEnum.BASE_TABLE_TEXT.value},
                {"name": "最高敏感等级", "type": "text", "key": "highest_sensitivity_level"},
                {"name": "描述", "type": "text", "key": "desc"},
                {"name": "申请期限", "type": "text", "key": "expired_display"},
            ]
        },
    },
    FormSchemeEnum.ACTION_TABLE_WITHOUT_EXP.value: {
        "type": "table",
        "attrs": {
            "column": [
                {"name": "操作", "type": "text", "key": "action"},
                {
                    "name": "资源组合",
                    "key": "resource_groups",
                    "scheme": FormSchemeEnum.BASE_TABLE_TEXT.value,
                },
            ]
        },
    },
    FormSchemeEnum.ACTION_TABLE.value: {
        "type": "table",
        "attrs": {
            "column": [
                {"name": "操作", "type": "text", "key": "action"},
                {"name": "敏感等级", "type": "text", "key": "sensitivity_level"},
                {
                    "name": "资源组合",
                    "key": "resource_groups",
                    "scheme": FormSchemeEnum.BASE_TABLE_TEXT.value,
                },
                {"name": "申请期限", "type": "text", "key": "expired_display"},
            ]
        },
    },
    FormSchemeEnum.RESOURCE_GROUP_TABLE.value: {
        "type": "table",
        "attrs": {
            "column": [
                {"name": "资源实例", "key": "related_resource_types", "scheme": FormSchemeEnum.BASE_TABLE_TEXT.value},
                {"name": "环境属性", "key": "environments", "scheme": FormSchemeEnum.BASE_TABLE_TEXT.value},
            ]
        },
    },
    FormSchemeEnum.RESOURCE_INSTANCE_TABLE.value: {
        "type": "table",
        "attrs": {
            "column": [
                {"name": "拓扑实例分类", "type": "text", "key": "type"},
                {"name": "拓扑实例", "key": "path", "scheme": FormSchemeEnum.BASE_TABLE_TEXT.value},
            ]
        },
    },
    FormSchemeEnum.RESOURCE_ATTRIBUTE_TABLE.value: {
        "type": "table",
        "attrs": {"column": [{"name": "属性条件", "key": "attributes", "scheme": FormSchemeEnum.BASE_TABLE_TEXT.value}]},
    },
    FormSchemeEnum.RESOURCE_BOTH_TABLE.value: {
        "type": "table",
        "attrs": {
            "column": [
                {"name": "拓扑实例分类", "type": "text", "key": "type"},
                {"name": "拓扑实例", "key": "path", "scheme": FormSchemeEnum.BASE_TABLE_TEXT.value},
                {"name": "属性条件", "key": "attributes", "scheme": FormSchemeEnum.BASE_TABLE_TEXT.value},
            ]
        },
    },
    FormSchemeEnum.ENVIRONMENT_TABLE.value: {
        "type": "table",
        "attrs": {
            "column": [
                {"name": "环境属性分类", "type": "text", "key": "type"},
                {"name": "属性条件", "key": "condition", "scheme": FormSchemeEnum.BASE_TABLE_TEXT.value},
            ]
        },
    },
}
