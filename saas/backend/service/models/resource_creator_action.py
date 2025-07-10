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

from typing import List, Optional

from pydantic import BaseModel


class ResourceCreatorActionInfo(BaseModel):
    """
    新建关联配置中单个Action
    """

    id: str
    required: bool


class ResourceCreatorActionConfigItem(BaseModel):
    """
    资源类型对应的被创建时所需的Action配置等
    """

    id: str
    actions: List[ResourceCreatorActionInfo]
    sub_resource_types: Optional[List["ResourceCreatorActionConfigItem"]] = None


ResourceCreatorActionConfigItem.update_forward_refs()


class ResourceCreatorActionConfig(BaseModel):
    """
    新建关联配置
    """

    mode: str
    config: List[ResourceCreatorActionConfigItem]
