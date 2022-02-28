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

from .http import http_post, logger


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
    kwargs = {"url": url, "data": data, "headers": headers, "timeout": timeout}

    ok, data = http_func(**kwargs)
    # remove sensitive info
    kwargs["headers"] = {}

    # process result
    if not ok:
        logger.error("engine api failed, method: %s, info: %s", http_func.__name__, kwargs)
        raise error_codes.ENGINE_REQUEST_ERROR.format(f'request engine api error: {data["error"]}')

    code = data["code"]
    message = data["message"]

    if code == 0:
        return data["data"]

    logger.error(
        "engine api error, request_id: %s, method: %s, info: %s, code: %d message: %s",
        local.request_id,
        http_func.__name__,
        kwargs,
        code,
        message,
    )

    error_message = (
        f"Request=[{http_func.__name__} {url_path} request_id={local.request_id}],"
        f"Response[code={code}, message={message}]"
    )
    raise error_codes.ENGINE_REQUEST_ERROR.format(error_message)


def batch_query_subjects(data: List[Dict[str, Any]]):
    url_path = "/batch-search"
    return _call_engine_api(http_post, url_path, data=data)


def query_subjects(data: Dict[str, Any]):
    url_path = "/search"
    return _call_engine_api(http_post, url_path, data=data)
