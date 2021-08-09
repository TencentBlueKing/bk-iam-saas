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
from typing import Dict, List

from backend.biz.policy import ConditionBean, RelatedResourceBean, group_paths


class ToPolicyRelatedResources:
    """转换为策略里Action关联的资源实例数据结构，可能 包括多种资源类型"""

    @staticmethod
    def _from_single_resource_paths(resource: Dict) -> RelatedResourceBean:
        """
        resource数据结构：{system, type, paths:[ [{system, type, id, name}], [...], ...] }
        """
        # 将paths:[ [{system, type, id, name}], [...], ...]里的system改为system_id
        # 因为group_paths方法里系统key是以system_id标识的
        for path in resource["paths"]:
            for node in path:
                node["system_id"] = node.pop("system")

        # RelatedResource.Condition.Instances是以分类后的资源实例存储的
        instances = group_paths(resource["paths"])

        # 若instances为空，则为无限制
        condition = [ConditionBean(instances=instances, attributes=[])] if instances else []

        # 构造RelatedResource数据
        return RelatedResourceBean(system_id=resource["system"], type=resource["type"], condition=condition)

    def from_resource_paths(self, resources: List[Dict]) -> List[RelatedResourceBean]:
        """
        resources 数据结构：[
            {system, type, paths:[ [{system, type, id, name}], [...], ...] }
        ]
        将API里的Resources数据转换为Policy RelatedResourceTypes数据结构
        这里的Resources指的Action关联的多种资源类型，并非批量资源实例
        """
        return [self._from_single_resource_paths(r) for r in resources]
