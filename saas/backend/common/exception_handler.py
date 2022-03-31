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
import logging

from rest_framework.exceptions import ValidationError
from rest_framework.fields import ListField
from rest_framework.serializers import Serializer
from rest_framework.settings import api_settings as drf_api_settings

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
