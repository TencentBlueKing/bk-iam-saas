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
import logging
from typing import Dict

from backend.service.resource_type import ResourceTypeService

logger = logging.getLogger(__name__)


class ResourceTypeBiz:
    resource_type_svc = ResourceTypeService()

    @classmethod
    def list_resource_types_by_system_id(cls, system_id: str) -> Dict:
        system_resource_types = cls.resource_type_svc.list_resource_type_by_systems([system_id])
        return system_resource_types
