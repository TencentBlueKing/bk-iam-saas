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

from typing import Any, Dict, List

from pydantic import BaseModel


class SystemProviderConfig(BaseModel):
    auth: str
    token: str
    host: str
    healthz: str = ""


class ResourceTypeProviderConfig(BaseModel):
    path: str


class ResourceAttribute(BaseModel):
    id: str
    display_name: str


class ResourceAttributeValue(BaseModel):
    id: str
    display_name: str


class ResourceInstanceBaseInfo(BaseModel):
    id: str
    display_name: str
    child_type: str = ""


class ResourceInstanceInfo(BaseModel):
    id: str
    # 由于查询某个资源的属性接口是动态传入要查询的属性，属性key是不固定的，属性值可能是list[str/bool/int]/str/bool/int
    attributes: Dict[str, Any]


class ResourceApproverAttribute(BaseModel):
    id: str
    approver: List[str]
