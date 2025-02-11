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
from typing import Dict

from django.conf import settings
from django.utils import translation

from backend.common.local import local
from backend.util.url import url_join

from .constants import ComponentEnum
from .http import http_get, http_post
from .util import do_blueking_http_request, remove_notification_exemption_user


def _call_esb_api(http_func, url_path, data, timeout=30, request_session=None):
    # 默认请求头
    headers = {
        "Content-Type": "application/json",
        "X-Request-Id": local.request_id,
        "blueking-language": translation.get_language(),
        "X-Bkapi-Authorization": json.dumps(
            {
                "bk_app_code": settings.APP_CODE,
                "bk_app_secret": settings.APP_SECRET,
                "bk_username": "admin",  # 存在后台任务，无法使用登录态的方式
            }
        ),
    }

    url = url_join(settings.BK_COMPONENT_INNER_API_URL, url_path)
    return do_blueking_http_request(ComponentEnum.ESB.value, http_func, url, data, headers, timeout, request_session)


def get_api_public_key() -> Dict:
    """获取目录列表"""
    url_path = "/api/c/compapi/v2/esb/get_api_public_key/"
    return _call_esb_api(http_get, url_path, data={})


def send_mail(username, title, content, body_format="Html"):
    """发送邮件"""
    # 移除豁免的用户，如果为空，则直接返回
    username = ",".join(remove_notification_exemption_user(username.split(",")))
    if not username:
        return None

    url_path = "/api/c/compapi/cmsi/send_mail/"
    data = {"receiver__username": username, "title": title, "content": content, "body_format": body_format}
    return _call_esb_api(http_post, url_path, data=data)
