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

import copy
import logging
from typing import Any, Callable, Dict, List, Optional, Tuple
from urllib.parse import urlparse

from django.conf import settings

from backend.common.error_codes import error_codes
from backend.common.local import local

logger = logging.getLogger("component")


# TODO: 后续抽象成通用的公共函数，比如 paging_func 支持可变参数等，同时改成一个通用装饰器
def list_all_data_by_paging(
    paging_func: Callable[[int, int], Tuple[int, List[Dict]]], page_size: int = 1000
) -> List[Dict]:
    """获取所有数据通过循环分页"""
    page = 1
    # 先第一次调用
    total, results = paging_func(page, page_size)
    # 返回的数据数量
    result_count = len(results)
    # 已获取的数据总数
    count = result_count
    # 已获得的数据
    data = results
    # 最大循环次数，避免死循环
    maximum = int(total / page_size + 1)
    # 返回数据数量等于 page_size 且已获取的总数小于 total
    while result_count == page_size and count < total and page <= maximum:
        page += 1
        _, results = paging_func(page, page_size)
        result_count = len(results)
        count += result_count
        data.extend(results)
    return data


def execute_all_data_by_paging(
    paging_func: Callable[[List[Any]], None], data: List[Any], page_size: int = 1000
) -> None:
    """通过分页数据的方式循环执行调用"""
    for i in range(0, len(data), page_size):
        paging_func(data[i : i + page_size])


def _remove_sensitive_info(info: Optional[Dict]) -> str:
    """
    去除敏感信息
    """
    if info is None:
        return ""

    data = copy.copy(info)
    sensitive_info_keys = ["bk_token", "bk_app_secret", "app_secret"]

    for key in sensitive_info_keys:
        if key in data:
            data[key] = data[key][:6] + "******"
    return str(data)


def do_blueking_http_request(
    component: str,
    http_func,
    url: str,
    data: Dict | None = None,
    headers: Dict | None = None,
    timeout: int | None = None,
    request_session=None,
):
    kwargs = {
        "url": url,
        "data": data,
        "headers": headers,
        "timeout": timeout,
        "request_session": request_session,
    }

    ok, resp_data = http_func(**kwargs)
    if not ok:
        logger.error(
            "%s api failed! %s %s, data: %s, request_id: %s, error: %s",
            component,
            http_func.__name__,
            url,
            _remove_sensitive_info(data),
            local.request_id,
            resp_data["error"],
        )
        raise error_codes.REMOTE_REQUEST_ERROR.format(
            f"request {component} fail! "
            f"Request=[{http_func.__name__} {urlparse(url).path} request_id={local.request_id}]"
            f"error={resp_data['error']}"
        )

    code = resp_data.get("code", -1)
    message = resp_data.get("message", "unknown")

    # code may be string or int, and login v1 the code is "00"
    try:
        code = int(code)
    except Exception:  # pylint: disable=broad-except
        pass
    if code in ("0", 0, "00", 20000):
        return resp_data["data"]

    logger.error(
        "%s api error! %s %s, data: %s, request_id: %s, code: %s, message: %s",
        component,
        http_func.__name__,
        url,
        _remove_sensitive_info(data),
        local.request_id,
        code,
        message,
    )

    raise error_codes.REMOTE_REQUEST_ERROR.format(
        f"request {component} error! "
        f"Request=[{http_func.__name__} {urlparse(url).path} request_id={local.request_id}] "
        f"Response[code={code}, message={message}]"
    )


def remove_notification_exemption_user(usernames: List[str]) -> List[str]:
    """
    从给定的用户列表里移除豁免通知的人员
    :param usernames: 待处理的用户名列表
    :return: 处理后的用户名列表
    """
    exemption_user_set = {u.strip().lower() for u in settings.BK_NOTIFICATION_EXEMPTION_USERS if u.strip()}

    return [u for u in usernames if u.strip().lower() not in exemption_user_set]
