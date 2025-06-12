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

from django.conf import settings
from django.utils import translation
from django.utils.deprecation import MiddlewareMixin
from pyinstrument.middleware import ProfilerMiddleware

from backend.common.base import is_open_api_request_path
from backend.common.constants import DjangoLanguageEnum
from backend.common.local import local


class CustomProfilerMiddleware(ProfilerMiddleware):
    """
    自定义 pyinstrument 中间件，便于开启和配置仅API请求统计性能
    """

    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        response = None
        # 仅仅统计API请求的性能
        api_url_prefix = f"{settings.SITE_URL}api/"
        # 开启了统计性能并且请求为API请求，则统计
        if getattr(settings, "ENABLE_PYINSTRUMENT", False) and request.path.startswith(api_url_prefix):
            response = self.process_request(request)

        response = response or self.get_response(request)

        return self.process_response(request, response)


class RequestProvider(object):
    """request_id中间件
    调用链使用
    """

    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        local.request = request
        request.request_id = local.get_http_request_id()

        response = self.get_response(request)
        response["X-Request-Id"] = request.request_id

        local.release()

        return response

    # Compatibility methods for Django <1.10
    def process_request(self, request):
        local.request = request
        request.request_id = local.get_http_request_id()

    def process_response(self, request, response):
        response["X-Request-Id"] = request.request_id
        local.release()
        return response


class LanguageMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # 如果是 openapi 请求, 设置默认语言为 english
        # openapi 的错误信息返回为英文
        if is_open_api_request_path(request.path):
            translation.activate(DjangoLanguageEnum.EN.value)
            request.LANGUAGE_CODE = translation.get_language()
