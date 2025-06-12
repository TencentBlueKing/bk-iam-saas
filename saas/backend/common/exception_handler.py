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

from blue_krill.web.std_error import APIError
from django.conf import settings
from django.http.response import Http404
from rest_framework import status
from rest_framework.exceptions import (
    AuthenticationFailed,
    MethodNotAllowed,
    NotAuthenticated,
    NotFound,
    ParseError,
    PermissionDenied,
    UnsupportedMediaType,
    ValidationError,
)
from rest_framework.fields import ListField
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.settings import api_settings as drf_api_settings
from rest_framework.views import set_rollback
from sentry_sdk import capture_exception

from backend.common.debug import log_api_error_trace
from backend.common.error_codes import error_codes

from .base import is_open_api_request_path, is_v1_open_api_request_path

logger = logging.getLogger("app")


def _one_line_error(exc):
    """
    从 serializer ValidationError 中抽取一行的错误消息
    """
    detail = exc.detail

    # handle ValidationError("error")
    if isinstance(detail, list):
        return detail[0]

    key, error = next(iter(detail.items()))
    if isinstance(error, list):
        error = error[0]
    elif isinstance(error, dict) and getattr(exc, "serializer", None):
        if key in getattr(exc.serializer, "fields", {}):
            field = exc.serializer.fields[key]
            if isinstance(field, ListField):  # 处理嵌套的ListField
                _, child = next(iter(error.items()))
                child_error = ValidationError(child)
                child_error.serializer = field.child
                return _one_line_error(child_error)
            if isinstance(field, Serializer):  # 处理嵌套的serializer
                child_error = ValidationError(error)
                child_error.serializer = field
                return _one_line_error(child_error)

        if isinstance(exc.serializer, ListField):
            _, child = next(iter(detail.items()))
            child_error = ValidationError(child)
            child_error.serializer = exc.serializer.child
            return _one_line_error(child_error)

    # handle non_field_errors, 非单个字段错误
    if key == drf_api_settings.NON_FIELD_ERRORS_KEY:
        return error

    # handle custom is_valid, show label in error
    if getattr(exc, "serializer", None) and key in exc.serializer.fields:
        key = exc.serializer.fields[key].label

    return f"{key}: {error}"


def _exception_to_error(request, exc) -> Optional[APIError]:
    """把预期中的异常转换成error"""
    if isinstance(exc, (NotAuthenticated, AuthenticationFailed)):
        return error_codes.UNAUTHORIZED

    if isinstance(exc, PermissionDenied):
        return error_codes.FORBIDDEN.format(message=exc.detail)

    if isinstance(exc, MethodNotAllowed):
        return error_codes.METHOD_NOT_ALLOWED.format(message=exc.detail)

    if isinstance(exc, ParseError):
        return error_codes.JSON_FORMAT_ERROR.format(message=exc.detail)

    if isinstance(exc, UnsupportedMediaType):
        return error_codes.UNSUPPORTED_MEDIA_TYPE.format(message=exc.detail)

    if isinstance(exc, ValidationError):
        if is_open_api_request_path(request.path):
            return error_codes.VALIDATE_ERROR.format(message=json.dumps(exc.detail), replace=True)

        return error_codes.VALIDATE_ERROR.format(message=_one_line_error(exc))

    if isinstance(exc, (NotFound, Http404)):
        return error_codes.NOT_FOUND_ERROR

    if isinstance(exc, APIError):
        # 回滚事务
        set_rollback()
        # 记录Debug信息
        log_api_error_trace(request)

        return exc

    return None


def exception_handler(exc, context):
    request = context["request"]

    error = _exception_to_error(request, exc)
    if error is None:
        # 处理预期之外的异常
        error = error_codes.SYSTEM_ERROR

        # 用户未主动捕获的异常
        logger.error(
            (
                """catch unhandled exception, stack->[%s], request url->[%s], """
                """request method->[%s] request params->[%s]"""
            ),
            traceback.format_exc(),
            request.path,
            request.method,
            json.dumps(getattr(request, request.method, None)),
        )

        # 记录debug信息
        log_api_error_trace(request, True)

        # notify sentry
        capture_exception(exc)

        # 如果是调试，异常交给Django 默认处理
        if settings.DEBUG:
            return None

    # NOTE: v1 openapi 为了兼容调用方使用习惯, 除以下error外，其他error的status code 默认返回 200
    ignore_error_codes = {
        error_codes.UNAUTHORIZED.code_num,
        error_codes.FORBIDDEN.code_num,
        error_codes.NOT_FOUND_ERROR.code_num,
        error_codes.SYSTEM_ERROR.code_num,
    }

    status_code = error.status_code
    if (
        is_v1_open_api_request_path(request.path)
        and isinstance(error, APIError)
        and error.code_num not in ignore_error_codes
    ):
        status_code = status.HTTP_200_OK

    return Response(
        {"result": False, "code": error.code_num, "message": f"{error.message} ({error.code})", "data": error.data},
        status=status_code,
    )
