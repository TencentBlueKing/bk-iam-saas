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
from typing import Optional

from django.conf import settings
from django.http import Http404
from django.utils import translation
from django.utils.deprecation import MiddlewareMixin
from pyinstrument.middleware import ProfilerMiddleware
from rest_framework import status
from rest_framework.exceptions import (
    AuthenticationFailed,
    MethodNotAllowed,
    NotAuthenticated,
    ParseError,
    PermissionDenied,
    ValidationError,
)
from rest_framework.response import Response
from rest_framework.views import set_rollback

from backend.common.constants import DjangoLanguageEnum
from backend.common.debug import log_api_error_trace
from backend.common.error_codes import CodeException, error_codes
from backend.common.exception_handler import one_line_error

try:
    from raven.contrib.django.raven_compat.models import sentry_exception_handler
# 兼容未有安装sentry的情况
except ImportError:
    sentry_exception_handler = None

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
    def _is_open_api_request(self, request) -> bool:
        return "/api/v1/open/" in request.path

    def process_request(self, request):
        # 如果是 openapi 请求, 设置默认语言为 english
        # openapi 的错误信息返回为英文
        if self._is_open_api_request(request):
            translation.activate(DjangoLanguageEnum.EN.value)
            request.LANGUAGE_CODE = translation.get_language()

    def _exception_to_error(self, request, exc) -> Optional[CodeException]:
        """把预期中的异常转换成error"""
        if isinstance(exc, (NotAuthenticated, AuthenticationFailed)):
            return error_codes.UNAUTHORIZED

        if isinstance(exc, PermissionDenied):
            return error_codes.FORBIDDEN

        if isinstance(exc, MethodNotAllowed):
            return error_codes.METHOD_NOT_ALLOWED.format(message=exc.detail)

        if isinstance(exc, ParseError):
            return error_codes.JSON_FORMAT_ERROR.format(message=exc.detail)

        if isinstance(exc, ValidationError):
            if self._is_open_api_request(request):
                return error_codes.VALIDATE_ERROR.format(message=json.dumps(exc.detail), replace=True)

            return error_codes.VALIDATE_ERROR.format(message=one_line_error(exc))

        if isinstance(exc, CodeException):
            # 回滚事务
            set_rollback()
            # 记录Debug信息
            log_api_error_trace(request)

            return exc

        return None

    def process_exception(self, request, exc):
        """
        app后台错误统一处理
        """
        if isinstance(exc, Http404):
            return None

        error = self._exception_to_error(request, exc)
        if error is None:
            # 处理预期之外的异常
            error = error_codes.SYSTEM_ERROR

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

            # 记录debug信息
            log_api_error_trace(request, True)

            # notify sentry
            if sentry_exception_handler is not None:
                sentry_exception_handler(request=request)

        # NOTE: openapi 为了兼容调用方使用习惯, status code 默认返回 200
        ignore_errors = (
            error_codes.UNAUTHORIZED,
            error_codes.FORBIDDEN,
            error_codes.NOT_FOUND_ERROR,
            error_codes.SYSTEM_ERROR,
        )

        if self._is_open_api_request(request) and not isinstance(error, ignore_errors):
            error.status_code = status.HTTP_200_OK

        return Response(error.as_json(), status=error.status_code)
