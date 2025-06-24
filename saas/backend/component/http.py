# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云 - 权限中心 (BlueKing-IAM) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.


请求登录的 http 基础方法
Rules:
1. POST/DELETE/PUT: json in - json out, 如果 resp.json 报错，则是登录接口问题
2. GET 带参数 HEAD 不带参数
3. 以统一的 header 头发送请求
"""  # noqa

from __future__ import unicode_literals

import logging
import time
import traceback
from functools import partial
from urllib.parse import urlparse

import requests
from django.conf import settings

from backend.common.debug import http_trace
from backend.metrics import component_request_duration, get_component_by_url

logger = logging.getLogger("component")


def _gen_header():
    return {
        "Content-Type": "application/json",
    }


session = requests.Session()
adapter = requests.adapters.HTTPAdapter(
    pool_connections=settings.REQUESTS_POOL_CONNECTIONS, pool_maxsize=settings.REQUESTS_POOL_MAXSIZE
)
session.mount("https://", adapter)
session.mount("http://", adapter)


def _http_request(
    method,
    url,
    headers=None,
    data=None,
    timeout=None,
    verify=False,
    cert=None,
    cookies=None,
    request_session=None
):
    trace_func = partial(http_trace, method=method, url=url, data=data)

    if request_session is None:
        request_session = session

    request_id = headers.get("X-Request-Id", "-") if headers else "-"
    st = time.time()
    try:
        if method == "GET":
            resp = request_session.get(
                url=url, headers=headers, params=data, timeout=timeout, verify=verify, cert=cert, cookies=cookies
            )
        elif method == "HEAD":
            resp = request_session.head(url=url, headers=headers, verify=verify, cert=cert, cookies=cookies)
        elif method == "POST":
            if "file" in data:
                headers.pop("Content-Type")
                resp = request_session.post(
                    url=url, headers=headers, files=data, timeout=timeout, verify=verify, cert=cert, cookies=cookies
                )
            else:
                resp = request_session.post(
                    url=url, headers=headers, json=data, timeout=timeout, verify=verify, cert=cert, cookies=cookies
                )
        elif method == "DELETE":
            resp = request_session.delete(
                url=url, headers=headers, json=data, timeout=timeout, verify=verify, cert=cert, cookies=cookies
            )
        elif method == "PUT":
            resp = request_session.put(
                url=url, headers=headers, json=data, timeout=timeout, verify=verify, cert=cert, cookies=cookies
            )
        elif method == "PATCH":
            resp = request_session.patch(
                url=url, headers=headers, json=data, timeout=timeout, verify=verify, cert=cert, cookies=cookies
            )
        else:
            return False, {"error": "method not supported"}
    except requests.exceptions.RequestException as e:
        logger.exception("http request error! %s %s, data: %s, request_id: %s", method, url, data, request_id)
        trace_func(exc=traceback.format_exc())
        return False, {"error": str(e)}
    else:
        # record for /metrics
        latency = int((time.time() - st) * 1000)
        component_request_duration.labels(
            component=get_component_by_url(url),
            method=method,
            path=urlparse(url).path,
            status=resp.status_code,
        ).observe(latency)

        # greater than 100ms
        if latency > 100:  # noqa: PLR2004
            logger.warning("http slow request! method: %s, url: %s, latency: %dms", method, url, latency)

        if resp.status_code != 200:  # noqa: PLR2004
            content = resp.content[:256] if resp.content else ""
            error_msg = (
                "http request fail! %s %s, data: %s, request_id: %s, response.status_code: %s, response.body: %s"
            )
            logger.error(error_msg, method, url, str(data), request_id, resp.status_code, content)

            trace_func(status_code=resp.status_code, content=content)

            return False, {
                "error": (
                    f"status_code is {resp.status_code}, not 200! "
                    f"{method} {urlparse(url).path}, request_id={request_id}, resp.body={content}"
                )
            }

        return True, resp.json()


def http_get(url, data, headers=None, verify=False, cert=None, timeout=None, cookies=None, request_session=None):
    if not headers:
        headers = _gen_header()
    return _http_request(
        method="GET",
        url=url,
        headers=headers,
        data=data,
        verify=verify,
        cert=cert,
        timeout=timeout,
        cookies=cookies,
        request_session=request_session,
    )


def http_post(url, data, headers=None, verify=False, cert=None, timeout=None, cookies=None, request_session=None):
    if not headers:
        headers = _gen_header()
    return _http_request(
        method="POST",
        url=url,
        headers=headers,
        data=data,
        timeout=timeout,
        verify=verify,
        cert=cert,
        cookies=cookies,
        request_session=request_session,
    )


def http_put(url, data, headers=None, verify=False, cert=None, timeout=None, cookies=None, request_session=None):
    if not headers:
        headers = _gen_header()
    return _http_request(
        method="PUT",
        url=url,
        headers=headers,
        data=data,
        timeout=timeout,
        verify=verify,
        cert=cert,
        cookies=cookies,
        request_session=request_session,
    )


def http_patch(url, data, headers=None, verify=False, cert=None, timeout=None, cookies=None, request_session=None):
    if not headers:
        headers = _gen_header()
    return _http_request(
        method="PATCH",
        url=url,
        headers=headers,
        data=data,
        timeout=timeout,
        verify=verify,
        cert=cert,
        cookies=cookies,
        request_session=request_session,
    )


def http_delete(url, data, headers=None, verify=False, cert=None, timeout=None, cookies=None, request_session=None):
    if not headers:
        headers = _gen_header()
    return _http_request(
        method="DELETE",
        url=url,
        headers=headers,
        data=data,
        timeout=timeout,
        verify=verify,
        cert=cert,
        cookies=cookies,
        request_session=request_session,
    )
