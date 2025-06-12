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

from django.conf import settings

from backend.common.error_codes import error_codes
from backend.common.local import local
from backend.util.json import json_dumps
from backend.util.url import url_join

from .constants import ComponentEnum
from .http import http_post
from .util import do_blueking_http_request


def _call_engine_api(http_func, url_path, data, timeout=30):
    # 默认请求头
    headers = {
        "Content-Type": "application/json",
        "X-Request-Id": local.request_id,
    }
    if not getattr(settings, "BK_IAM_ENGINE_HOST", None):
        raise error_codes.ENGINE_REQUEST_ERROR.format("iam engine may not deploy")

    if settings.BK_IAM_ENGINE_HOST_TYPE == "apigateway":
        headers["x-bkapi-authorization"] = json_dumps(
            {"bk_app_code": settings.APP_CODE, "bk_app_secret": settings.APP_SECRET}
        )

    if settings.BK_IAM_ENGINE_HOST_TYPE == "direct":
        headers.update({"X-Bk-App-Code": settings.APP_CODE, "X-Bk-App-Secret": settings.APP_SECRET})

    url = url_join(settings.BK_IAM_ENGINE_HOST, f"/api/v1/engine{url_path}")
    if settings.BK_IAM_ENGINE_HOST_TYPE == "direct":
        url = url_join(settings.BK_IAM_ENGINE_HOST, f"/api/v1{url_path}")

    return do_blueking_http_request(ComponentEnum.ENGINE.value, http_func, url, data, headers, timeout)


def batch_query_subjects(data: List[Dict[str, Any]]):
    url_path = "/batch-search"
    return _call_engine_api(http_post, url_path, data=data)


def query_subjects(data: Dict[str, Any]):
    url_path = "/search"
    return _call_engine_api(http_post, url_path, data=data)
