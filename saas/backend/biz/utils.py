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
from itertools import groupby
from typing import Any, Dict, List

from backend.biz.group import GroupBiz

groupbiz = GroupBiz()


def fill_resources_attribute(resources: List[Dict[str, Any]]):
    """
    为资源实例填充属性
    """
    need_fetch_resources = []
    for resource in resources:
        if resource["id"] != "*" and not resource["attribute"]:
            need_fetch_resources.append(resource)

    if not need_fetch_resources:
        return

    for key, parts in groupby(need_fetch_resources, key=lambda resource: (resource["system"], resource["type"])):
        groupbiz._exec_fill_resources_attribute(key[0], key[1], list(parts))
