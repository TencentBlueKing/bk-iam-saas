#!/usr/bin/env python3
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

import json

from django.conf import settings
from django.utils import translation

from backend.common.local import local
from backend.util.url import url_join

from .constants import ComponentEnum
from .util import do_blueking_http_request


def _call_apigw_api(http_func, url_path, data, timeout=30, request_session=None, bk_token=None):
    # 默认请求头
    headers = {
        "Content-Type": "application/json",
        "X-Request-Id": local.request_id,
        "blueking-language": translation.get_language(),
        "X-Bkapi-Authorization": json.dumps(
            {
                "bk_app_code": settings.APP_CODE,
                "bk_app_secret": settings.APP_SECRET,
            }
        ),
        "X-Bk-Tenant-Id": settings.BK_APP_TENANT_ID,
        "SYSTEM-TOKEN": settings.BK_ITSM_V4_SYSTEM_TOKEN,
    }
    if bk_token:
        headers["X-Bkapi-Authorization"]["bk_token"] = bk_token

    url = url_join(settings.BK_ITSM_V4_APIGW_URL, url_path)
    return do_blueking_http_request(ComponentEnum.APIGW.value, http_func, url, data, headers, timeout, request_session)
