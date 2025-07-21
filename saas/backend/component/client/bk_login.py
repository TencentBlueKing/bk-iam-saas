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
from urllib.parse import urlparse

from django.conf import settings

from backend.common.error_codes import error_codes
from backend.util.url import url_join

from .apigw import BkApigwBaseClient
from .http import http_get_20x

logger = logging.getLogger("component")


class BkLoginClient(BkApigwBaseClient):
    """蓝鲸登录通过 API 网关提供的接口"""

    def __init__(self):
        # Note: 登录接口，基本上都无法提前知道租户信息，所以这里使用 IAM 本身所属租户
        self.tenant_id = settings.BK_APP_TENANT_ID
        self.api_url = url_join(
            settings.BK_API_URL_TMPL.format(api_name=settings.BK_LOGIN_APIGW_NAME), settings.BK_LOGIN_APIGW_STAGE
        )
        self.headers = {
            **self.request_id_headers,
            # 只使用应用态接口
            **self.app_authorization_header,
            # 支持多租户
            "X-Bk-Tenant-Id": self.tenant_id,
        }

    def _call(self, http_func_only_20x, url_path, **kwargs):
        url = url_join(self.api_url, url_path)
        kwargs.setdefault("headers", {}).update(self.headers)
        ok, resp_data = http_func_only_20x(url, **kwargs)

        if not ok:
            logger.error(
                "bk-login api failed! %s %s, kwargs: %s, request_id: %s, error: %s",
                http_func_only_20x.__name__,
                url,
                kwargs,
                self.request_id,
                resp_data["error"],
            )
            raise error_codes.REMOTE_REQUEST_ERROR.format(
                f"request bk-login api fail! "
                f"Request=[{http_func_only_20x.__name__} {urlparse(url).path} request_id={self.request_id}]"
                f"error={resp_data['error']}"
            )

        return resp_data["data"]

    def get_user_info(self, bk_token: str):
        """
        获取用户信息
        """
        url_path = "/login/api/v3/open/bk-tokens/userinfo/"
        return self._call(http_get_20x, url_path, params={"bk_token": bk_token})
