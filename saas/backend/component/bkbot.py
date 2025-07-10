"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-权限中心(BlueKing-IAM) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.conf import settings

from backend.common.local import local
from backend.util.json import json_dumps
from backend.util.url import url_join

from .constants import ComponentEnum
from .http import http_post
from .util import do_blueking_http_request, remove_notification_exemption_user


def _call_bk_bot_approval_api(http_func, url_path, data, timeout=30):
    # 默认请求头
    headers = {
        "Content-Type": "application/json",
        "X-Request-Id": local.request_id,
        "x-bkapi-authorization": json_dumps({"bk_app_code": settings.APP_CODE, "bk_app_secret": settings.APP_SECRET}),
    }

    url = url_join(settings.BK_BOT_APPROVAL_APIGW_URL, url_path)
    return do_blueking_http_request(ComponentEnum.APIGW.value, http_func, url, data, headers, timeout)


def send_iam_ticket(data):
    # 移除豁免的用户，如果为空，则直接返回
    data["approvers"] = ",".join(remove_notification_exemption_user(data["approvers"].split(",")))
    if not data["approvers"]:
        return {}

    url_path = "/iam_app_ticket/"
    return _call_bk_bot_approval_api(http_post, url_path, data=data)
