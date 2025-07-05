"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云 - 权限中心 (BlueKing-IAM) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import json
import logging
from urllib.parse import urlparse

from django.conf import settings

from backend.common.error_codes import error_codes
from backend.util.url import url_join

from .http import http_get

logger = logging.getLogger("component")


def _call_login_api(http_func, url_path, data):
    """
    调用登录 API 网关
    """
    # 登录请求 Header
    headers = {
        "Content-Type": "application/json",
        "X-Bkapi-Authorization": json.dumps(
            {"bk_app_code": settings.BK_APP_CODE, "bk_app_secret": settings.BK_APP_SECRET},
        ),
        # Note: 对于全租户应用，登录前是无法获取租户 ID 的，所以这里使用任意租户作为租户 ID 都可以
        "X-Bk-Tenant-Id": "system",
    }

    # 登录请求 URL
    url = url_join(
        settings.BK_API_URL_TMPL.format(api_name=settings.BK_LOGIN_APIGW_NAME),
        settings.BK_LOGIN_APIGW_STAGE,
        url_path,
    )

    ok, resp_data = http_func(url=url, data=data, headers=headers, timeout=5, verify=False)
    if not ok:
        logger.error(
            "login api failed! %s %s, data: %s, error: %s",
            http_func.__name__,
            url,
            data,
            resp_data["error"],
        )
        raise error_codes.REMOTE_REQUEST_ERROR.format(
            f"request login api fail! Request=[{http_func.__name__} {urlparse(url).path} error={resp_data['error']}"
        )

    return resp_data["data"]


def get_user_info(bk_token: str):
    """
    获取用户信息
    """
    url_path = "/login/api/v3/open/bk-tokens/userinfo/"
    return _call_login_api(http_get, url_path, data={"bk_token": bk_token})
