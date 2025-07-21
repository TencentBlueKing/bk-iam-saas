# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云 - 权限中心 (BlueKing-IAM) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import copy
import logging
from collections import defaultdict
from typing import Any, Dict, List

from backend.apps.group.models import GroupSaaSAttribute
from backend.common.error_codes import error_codes

from .constants import (
    GROUP_SAAS_ATTRIBUTE_DEFAULT_VALUE_MAP,
    GROUP_SAAS_ATTRIBUTE_VALUE_TYPE_MAP,
    GroupAttributeValueType,
    GroupSaaSAttributeEnum,
)
from .models import GroupAttributes

logger = logging.getLogger("app")


class GroupAttributeService:
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id

    def convert_attr_value(self, value_str: str, data_type: GroupAttributeValueType) -> Any:
        """将属性值的数据类型从 string 转换为实际数据类型"""
        error_message = f"convert attr value from str to {data_type} fail, value_str: {value_str}"

        # 字符串
        if data_type == GroupAttributeValueType.String.value:
            return value_str

        # 整数
        if data_type == GroupAttributeValueType.Integer.value:
            # 如果转换错误则直接异常
            try:
                return int(value_str, base=10)
            except Exception:  # pylint: disable=broad-except
                logger.exception(f"{error_message}")
                raise error_codes.VALUE_ERROR.format(error_message, replace=True)
        # 布尔
        if data_type == GroupAttributeValueType.Boolean.value:
            if value_str not in ["True", "False"]:
                raise error_codes.VALUE_ERROR.format(error_message, replace=True)
            return value_str == "True"

        return None

    def batch_get_attributes(self, group_ids: List[int]) -> Dict[int, GroupAttributes]:
        """批量获取用户组属性"""
        # 查询所有用户组配置的属性
        gsas = GroupSaaSAttribute.objects.filter(group_id__in=group_ids)
        group_attr_values = defaultdict(str)
        for gsa in gsas:
            group_attr_values[(gsa.group_id, gsa.key)] = gsa.value

        group_attrs = {}
        # 遍历每个用户组的每个属性
        for group_id in group_ids:
            # 初始化为每个属性默认值
            attrs = copy.deepcopy(GROUP_SAAS_ATTRIBUTE_DEFAULT_VALUE_MAP)
            # 遍历每个属性是否配置了，若配置了则使用配置的值
            for attr_enum in GroupSaaSAttributeEnum:  # type: ignore[attr-defined]
                attr = attr_enum.value
                value_str = group_attr_values[(group_id, attr)]
                # 若 value 为空字符串，则说明没有配置
                if value_str == "":
                    continue
                value = self.convert_attr_value(value_str, GROUP_SAAS_ATTRIBUTE_VALUE_TYPE_MAP[attr])
                # 将属性默认值替换掉
                attrs[attr] = value

            group_attrs[group_id] = GroupAttributes(attributes=attrs)

        # Note: 以上仅仅是处理了 Group SaaS 属性，后续可添加鉴权所需属性

        return group_attrs

    def batch_delete_attributes(self, group_ids: List[int]):
        """批量删除用户组属性"""
        # Note: 目前仅仅处理了 Group SaaS 属性，后续可删除鉴权属性
        GroupSaaSAttribute.objects.filter(group_id__in=group_ids).delete()

    def batch_set_attributes(self, group_attrs: Dict[int, Dict[str, Any]]):
        """批量设置用户组属性，已存在将会进行覆盖
        group_attrs: {group_id: {attr: value, ...}, ...}
        """
        # Note: 以下仅仅是处理了 Group SaaS 属性，后续可添加鉴权所需属性

        # 查询已存在的
        gsas = GroupSaaSAttribute.objects.filter(group_id__in=group_attrs.keys())
        group_attr_values = defaultdict(str)
        for gsa in gsas:
            group_attr_values[(gsa.group_id, gsa.key)] = gsa

        created_group_saas_attrs = []
        updated_group_saas_attrs = []
        for group_id, attrs in group_attrs.items():
            # 遍历每个属性
            for attr, value in attrs.items():
                # 若非支持的属性，则获取默认值时将异常
                default_value = GROUP_SAAS_ATTRIBUTE_DEFAULT_VALUE_MAP[attr]
                # DB 保存所有都以字符串报错
                value_str = str(value)

                # 如果以存在 key，则更新即可
                if (group_id, attr) in group_attr_values:
                    group_saas_attribute = group_attr_values[(group_id, attr)]
                    # 判断是否与旧值一样，不一样才更新
                    if group_saas_attribute.value != value_str:
                        group_saas_attribute.value = value_str
                        updated_group_saas_attrs.append(group_saas_attribute)
                    continue

                # 若与默认值相同，则无需存储
                if default_value == value:
                    continue
                created_group_saas_attrs.append(
                    GroupSaaSAttribute(tenant_id=self.tenant_id, group_id=group_id, key=attr, value=value_str)
                )

        # 批量创建
        if created_group_saas_attrs:
            GroupSaaSAttribute.objects.bulk_create(created_group_saas_attrs, batch_size=100)
        # 批量更新
        if updated_group_saas_attrs:
            GroupSaaSAttribute.objects.bulk_update(updated_group_saas_attrs, ["value"], batch_size=100)
