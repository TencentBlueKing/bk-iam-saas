# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云 - 权限中心 (BlueKing-IAM) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import logging
import time
from typing import Dict, Tuple
from urllib.parse import urlparse

import requests
from django.conf import settings
from requests.adapters import HTTPAdapter

logger = logging.getLogger("component")
# 定义慢请求耗时，单位毫秒
SLOW_REQUEST_LATENCY = 100

session = requests.Session()
adapter = HTTPAdapter(pool_connections=settings.REQUESTS_POOL_CONNECTIONS, pool_maxsize=settings.REQUESTS_POOL_MAXSIZE)
session.mount("https://", adapter)
session.mount("http://", adapter)


class HttpStatusCode:
    def __init__(self, status_code: int):
        self.code = status_code

    @property
    def is_invalid(self) -> bool:
        return self.code < 0  # noqa: PLR2004

    @property
    def is_success(self) -> bool:
        return 200 <= self.code <= 299  # noqa: PLR2004

    @property
    def is_redirect(self) -> bool:
        return 300 <= self.code <= 399  # noqa: PLR2004

    @property
    def is_client_error(self) -> bool:
        return 400 <= self.code <= 499  # noqa: PLR2004

    @property
    def is_server_error(self) -> bool:
        return 500 <= self.code <= 599  # noqa: PLR2004

    @property
    def is_unauthorized(self) -> bool:
        return self.code == 401  # noqa: PLR2004

    @property
    def is_forbidden(self) -> bool:
        return self.code == 403  # noqa: PLR2004

    @property
    def is_not_found(self) -> bool:
        return self.code == 404  # noqa: PLR2004


# 定义无效请求的 Http 状态码
INVALID_REQUEST_STATUS_CODE = HttpStatusCode(status_code=-1)
# Request Body 非 JSON 格式
INVALID_JSON_STATUS_CODE = HttpStatusCode(status_code=-2)


def _http_request(method: str, url: str, **kwargs) -> Tuple[HttpStatusCode, Dict]:
    """
    通用的 Http 接口请求，目前只支持 JSON 格式的 Body 数据返回，对于其他格式的返回，都认为是调用失败
    :param method: http 请求 method，大写，GET/POST/DELETE/PUT/PATCH/HEAD
    :param url: http 请求 URL
    :param kwargs: 与 Requests 库一致的请求参数 (params/json/data/headers/auth/verify/timeout 等等)
    :return http_status_code, response_body_data:
        只要是 Response Body 为 json 格式数据，都会返回有效的 Http 状态码，表示请求发送和接收成功，不关注业务逻辑
        - status_code < 0: 表示非预期请求，无效请求
        - status_code > 0: 表示正常请求且 Response Body 为 JSON 格式的状态码
        - data: status_code < 0 时，包含 error 字段，描述非预期请求的原因，
            status_code > 0 时，则为经 JSON 解析后的 Response Body 数据
    """
    # 添加默认 Header
    headers = kwargs.setdefault("headers", {})
    # 如果没有传入 files，则默认 Content-Type 为 application/json
    # 如果传入了 files，则 Content-Type 自动设置为 multipart/form-data，并且生成一个随机的边界字符串（boundary）
    if "files" not in kwargs:
        headers.setdefault("Content-Type", "application/json")

    # 默认 30 秒超时
    kwargs.setdefault("timeout", 30)
    # 默认不校验证书
    kwargs.setdefault("verify", False)

    # FIXME(tenant): 日志等需要记录 Request ID

    st = time.time()

    if method not in ["GET", "POST", "DELETE", "PUT", "PATCH", "HEAD"]:
        return INVALID_REQUEST_STATUS_CODE, {"error": f"request method - {method} not supported"}

    try:
        resp = session.request(method, url, **kwargs)
    except requests.exceptions.RequestException as e:
        logger.exception("http request error! %s %s, kwargs: %s", method, url, kwargs)
        return INVALID_REQUEST_STATUS_CODE, {"error": str(e)}

    # 记录耗时，单位 ms
    latency = int((time.time() - st) * 1000)
    # 记录慢请求，默认大于 100ms 即为慢请求
    if latency > SLOW_REQUEST_LATENCY:
        logger.warning("http slow request! method: %s, url: %s, latency: %dms", method, url, latency)

    # 对于 204 且 body 内容为空时允许的，一般是 DELETE 情况
    if resp.status_code == 204 and not resp.content:  # noqa: PLR2004
        return HttpStatusCode(resp.status_code), {}

    # 其他情况只支持 JSON 格式的 Body 数据返回
    try:
        return HttpStatusCode(resp.status_code), resp.json()
    except Exception as e:
        content = resp.content[:256] if resp.content else ""
        logger.exception(
            "http request fail, response.body not json!"
            " %s %s, kwargs: %s, response.status_code: %s, response.body: %s",
            method,
            url,
            str(kwargs),
            resp.status_code,
            content,
        )
        return (
            INVALID_JSON_STATUS_CODE,
            {
                "error": (
                    f"http response body not json, http status code is {resp.status_code}! "  # type: ignore
                    f"{method} {urlparse(url).path}, response.body={content}, error:{e}"
                )
            },
        )


def _http_request_only_20x(method: str, url: str, **kwargs) -> Tuple[bool, Dict]:
    """只支持 20x 且 Response Body 为 JSON 的请求，其他均为异常请求"""
    status, resp_data = _http_request(method, url, **kwargs)
    if status.is_success:
        return True, resp_data

    # 无效请求
    if status.is_invalid:
        return False, resp_data

    # 非 20x 请求
    logger.error(
        "http response status code is %s, not 20x! %s %s, kwargs: %s, response.body: %s",
        status.code,
        method,
        url,
        str(kwargs),
        resp_data,
    )
    return False, {
        "error": f"status_code is {status.code}, not 20x! {method} {urlparse(url).path}, response.body={resp_data}",
    }


# 标准的 API 请求，JSON 响应
def http_get(url, **kwargs):
    return _http_request(method="GET", url=url, **kwargs)


def http_post(url, **kwargs):
    return _http_request(method="POST", url=url, **kwargs)


def http_put(url, **kwargs):
    return _http_request(method="PUT", url=url, **kwargs)


def http_patch(url, **kwargs):
    return _http_request(method="PATCH", url=url, **kwargs)


def http_delete(url, **kwargs):
    return _http_request(method="DELETE", url=url, **kwargs)


# 只允许 20x 的 API 请求，JSON 响应
def http_get_20x(url, **kwargs):
    return _http_request_only_20x(method="GET", url=url, **kwargs)


def http_post_20x(url, **kwargs):
    return _http_request_only_20x(method="POST", url=url, **kwargs)


def http_put_20x(url, **kwargs):
    return _http_request_only_20x(method="PUT", url=url, **kwargs)


def http_patch_20x(url, **kwargs):
    return _http_request_only_20x(method="PATCH", url=url, **kwargs)


def http_delete_20x(url, **kwargs):
    return _http_request_only_20x(method="DELETE", url=url, **kwargs)
