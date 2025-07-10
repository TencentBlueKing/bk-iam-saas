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

from collections import defaultdict
from typing import Dict, List, Tuple

from backend.component import iam

from .models import ResourceType, ResourceTypeDict


class ResourceTypeService:
    def get_system_resource_type_list_map(self, system_ids: List[str]) -> Dict[str, List[ResourceType]]:
        """批量获取多个系统的资源类别"""
        system_resource_type_dict = iam.list_resource_type(system_ids)

        system_resource_types = {}
        for system_id, resource_types in system_resource_type_dict.items():
            system_resource_types[system_id] = [ResourceType(**i) for i in resource_types]

        return system_resource_types

    def get_system_resource_type_dict(self, system_ids: List[str]) -> ResourceTypeDict:
        """
        获取resource type name provider
        """
        if not system_ids:
            return ResourceTypeDict(data={})

        system_resource_types = iam.list_resource_type(system_ids)
        resource_type_dict: Dict[Tuple[str, str], Dict] = defaultdict(dict)
        for system_id, resource_types in system_resource_types.items():
            for rt in resource_types:
                resource_type_dict[(system_id, rt["id"])] = rt
        return ResourceTypeDict(data=resource_type_dict)
