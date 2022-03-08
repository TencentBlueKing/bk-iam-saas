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
import logging
import traceback

from django.conf import settings
from django.http import Http404, JsonResponse
from django.utils.deprecation import MiddlewareMixin
from pyinstrument.middleware import ProfilerMiddleware
from sentry_sdk import capture_exception

from backend.common.local import local

logger = logging.getLogger("app")


class CustomProfilerMiddleware(ProfilerMiddleware):
    """
    自定义 pyinstrument 中间件，便于开启和配置仅API请求统计性能
    """

    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        response = None
        # 仅仅统计API请求的性能
        api_url_prefix = f"{settings.SITE_URL}api/v1"
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


class AppExceptionMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        """
        app后台错误统一处理
        """

        self.exception = exception
        self.request = request

        # 用户未主动捕获的异常
        logger.error(
            ("""捕获未处理异常,异常具体堆栈->[%s], 请求URL->[%s], """ """请求方法->[%s] 请求参数->[%s]""")
            % (
                traceback.format_exc(),
                request.path,
                request.method,
                json.dumps(getattr(request, request.method, None)),
            )
        )

        # 对于check开头函数进行遍历调用，如有满足条件的函数，则不屏蔽异常
        check_funtions = self.get_check_functions()
        for check_function in check_funtions:
            if check_function():
                return None

        response = JsonResponse({"result": False, "code": "1902500", "message": "系统异常,请联系管理员处理", "data": None})
        response.status_code = 500

        # notify sentry
        capture_exception(exception)

        return response

    def get_check_functions(self):
        """获取需要判断的函数列表"""
        return [
            getattr(self, func) for func in dir(self) if func.startswith("check") and callable(getattr(self, func))
        ]

    def check_is_debug(self):
        """判断是否是开发模式"""
        return settings.DEBUG

    def check_is_http404(self):
        """判断是否基于Http404异常"""
        return isinstance(self.exception, Http404)
