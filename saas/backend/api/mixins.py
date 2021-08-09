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

from django.utils import translation
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import set_rollback

from backend.common.constants import DjangoLanguageEnum
from backend.common.error_codes import error_codes
from backend.component import iam
from backend.util.cache import region


class SystemClientCheckMixin:
    def verify_system_client(self, system_id: str, app_code: str):
        """
        验证app_code是否能访问系统
        """
        clients = self._get_system_clients(system_id)

        if app_code not in set(clients):
            raise exceptions.PermissionDenied(
                detail="app_code {} can not access system {}".format(app_code, system_id)
            )

    @staticmethod
    @region.cache_on_arguments(expiration_time=5 * 60)  # 5分钟过期
    def _get_system_clients(system_id: str):
        system = iam.get_system(system_id, fields="clients")
        return system["clients"].split(",")


class ExceptionHandlerMixin:
    """
    open api 直接返回serializer的error
    """

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        translation.activate(DjangoLanguageEnum.EN.value)
        request.LANGUAGE_CODE = translation.get_language()

    def get_exception_handler(self):
        return self._exception_handler

    def _exception_handler(self, exc, context):
        """
        返回serializer的error detail 到调用方
        """
        if isinstance(exc, exceptions.ValidationError):
            set_rollback()
            data = {
                "result": False,
                "code": error_codes.VALIDATE_ERROR.code,
                "message": json.dumps(exc.detail),
                "data": None,
            }
            return Response(data, headers={})

        default_handler = api_settings.EXCEPTION_HANDLER

        return default_handler(exc, context)
