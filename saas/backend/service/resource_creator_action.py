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

from typing import Optional

from backend.component import iam

from .models import ResourceCreatorActionConfig


class ResourceCreatorActionService:
    @staticmethod
    def get(system_id: str) -> Optional[ResourceCreatorActionConfig]:
        """获取系统的新建关联配置"""
        rca = iam.get_resource_creator_actions(system_id)
        if not rca:
            return None

        return ResourceCreatorActionConfig(**rca)
