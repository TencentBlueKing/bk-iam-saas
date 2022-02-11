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
from urllib.parse import urlencode

from django.conf import settings
from rest_framework.exceptions import (
    AuthenticationFailed,
    MethodNotAllowed,
    NotAuthenticated,
    ParseError,
    PermissionDenied,
    ValidationError,
)
from rest_framework.fields import ListField
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.settings import api_settings as drf_api_settings
from rest_framework.views import exception_handler, set_rollback

from backend.common.debug import log_api_error_trace
from backend.common.error_codes import CodeException, error_codes

logger = logging.getLogger("app")


def one_line_error(exc):
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
                return one_line_error(child_error)
            elif isinstance(field, Serializer):  # 处理嵌套的serializer
                child_error = ValidationError(error)
                child_error.serializer = field
                return one_line_error(child_error)

        if isinstance(exc.serializer, ListField):
            _, child = next(iter(detail.items()))
            child_error = ValidationError(child)
            child_error.serializer = exc.serializer.child
            return one_line_error(child_error)

    # handle non_field_errors, 非单个字段错误
    if key == drf_api_settings.NON_FIELD_ERRORS_KEY:
        return error

    # handle custom is_valid, show label in error
    if getattr(exc, "serializer", None) and key in exc.serializer.fields:
        key = exc.serializer.fields[key].label

    return f"{key}: {error}"


def custom_exception_handler(exc, context):
    if isinstance(exc, (NotAuthenticated, AuthenticationFailed)):
        set_rollback()
        error = error_codes.UNAUTHORIZED
        params = urlencode({"c_url": f"{settings.APP_URL}/login_success/", "app_code": settings.APP_CODE})
        login_plain_url = f"{settings.LOGIN_SERVICE_PLAIN_URL}?{params}"
        data = {
            "result": False,
            "code": error.code,
            "message": error.message,
            "data": {"login_url": settings.LOGIN_SERVICE_URL, "login_plain_url": login_plain_url},
        }
        return Response(data, status=error.status_code, headers={})

    elif isinstance(exc, PermissionDenied):
        set_rollback()
        error = error_codes.FORBIDDEN
        data = {
            "result": False,
            "code": error.code,
            "message": exc.detail,
            "data": {},
        }
        return Response(data, status=error.status_code)

    elif isinstance(exc, ParseError):
        set_rollback()
        error = error_codes.JSON_FORMAT_ERROR.format(message=exc.detail)
        return Response(error.as_json(), status=error.status_code, headers={})

    elif isinstance(exc, ValidationError):
        set_rollback()
        error = error_codes.VALIDATE_ERROR.format(message=one_line_error(exc))
        return Response(error.as_json(), status=error.status_code, headers={})

    elif isinstance(exc, CodeException):
        # 记录Debug信息
        log_api_error_trace(context["request"])

        set_rollback()
        return Response(exc.as_json(), status=exc.status_code, headers={})

    elif isinstance(exc, MethodNotAllowed):
        set_rollback()
        error = error_codes.METHOD_NOT_ALLOWED.format(message=exc.detail)
        return Response(error.as_json(), status=error.status_code, headers={})

    message = "iam system error"

    request = context["request"]
    if request:
        message = "iam system error, url: {}, method: {}, data: {}".format(
            request.path, request.method, json.dumps(getattr(request, request.method, None))
        )

    # 记录debug信息
    log_api_error_trace(request, True)

    # logger.exception(message)

    # Call REST framework's default exception handler to get the standard error response.
    response = exception_handler(exc, context)
    # Use a default error code
    if response is not None:
        response.data.update(code=error_codes.COMMON_ERROR.code)

    return response
