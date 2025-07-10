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

import re

# 只需要判断 v1 - v9 的 open api，一般不会有超过9个版本的Open API
OPEN_API_PATH_PATTERN = re.compile(r"/api/v\d/open/")


def is_open_api_request_path(path: str) -> bool:
    """检查路径是否为open api请求的路径"""
    return OPEN_API_PATH_PATTERN.search(path) is not None


def _is_certain_version_open_api_request_path(path: str, version: int) -> bool:
    """判断是否某个固定版本OpenAPI路径"""
    version_open_api_path = f"/api/v{version}/open/"
    return version_open_api_path in path


def is_v1_open_api_request_path(path: str) -> bool:
    """判断是否V1 Open API请求"""
    return _is_certain_version_open_api_request_path(path, version=1)
