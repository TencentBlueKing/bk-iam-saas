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

from urllib.parse import urlparse

from aenum import LowerStrEnum, auto
from prometheus_client import Histogram


class ComponentEnum(LowerStrEnum):
    IAM_BACKEND = auto()
    IAM_ENGINE = auto()
    ITSM = auto()
    USERMGR = auto()
    ESB = auto()
    CMSI = auto()


def get_component_by_url(url: str) -> str:
    path = urlparse(url).path
    if "/api/v1/web/" in path:
        return ComponentEnum.IAM_BACKEND.value
    elif "/api/v1/engine" in path or "/api/v1/batch-search" in path:
        return ComponentEnum.IAM_ENGINE.value
    elif "/api/c/compapi/v2/usermanage/" in path:
        return ComponentEnum.USERMGR.value
    elif "/api/c/compapi/v2/itsm/" in path:
        return ComponentEnum.ITSM.value
    elif "/api/c/compapi/v2/esb/" in path:
        return ComponentEnum.ESB.value
    elif "/api/c/compapi/cmsi/" in path:
        return ComponentEnum.CMSI.value
    return "unknown"


# for usermgr/itsm/login/iam_backend
component_request_duration = Histogram(
    "component_request_duration_milliseconds",
    "How long it took to process the request, partitioned by status code, method and HTTP path.",
    ("component", "method", "path", "status"),
    buckets=(50, 100, 200, 500, 1000, 2000, 5000),
)

# for callback of all systems
callback_request_duration = Histogram(
    "callback_request_duration_milliseconds",
    "How long it took to process the request, partitioned by status code, method and HTTP path.",
    ("system", "resource_type", "function", "method", "path", "status"),
    buckets=(50, 100, 200, 500, 1000, 2000, 5000),
)
