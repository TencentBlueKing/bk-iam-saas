# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云 - 权限中心 (BlueKing-IAM) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import base64
import logging

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication

from backend.common.cache import cachedmethod
from backend.component import esb

from .constants import BKNonEntityUser

logger = logging.getLogger("app")


class ESBAuthentication(BaseAuthentication):
    """
    ESB authentication
    """

    www_authenticate_realm = "api"

    def authenticate(self, request):
        credentials = self.get_credentials(request)
        if not credentials:
            return None

        verified, payload = self.verify_credentials(credentials=credentials)
        if not verified:
            return None

        username = self._get_username_from_jwt_payload(payload)
        app_code = self._get_app_code_from_jwt_payload(payload)

        request.bk_app_code = app_code  # 获取到调用 app_code

        # Q: 为什么租户 ID 可以直接从 HTTP 头部获取，不需要验证么？
        # A: 经过网关 JWT 验证后，租户 ID 是可信任的，因为网关会校验 AppCode 与 HTTP_X_BK_TENANT_ID 之间的权限
        request.tenant_id = request.META.get("HTTP_X_BK_TENANT_ID")
        if not request.tenant_id:
            logger.error("X-Bk-Tenant-Id is not provided in apigw request headers for app_code: %s", app_code)
            raise exceptions.AuthenticationFailed("HTTP_X_BK_TENANT_ID is required")

        return self._get_or_create_user(username), None

    def authenticate_header(self, request):
        return '{0} realm="{1}"'.format("Bearer", self.www_authenticate_realm)

    def get_credentials(self, request):
        credentials = {
            "jwt": request.META.get("HTTP_X_BKAPI_JWT"),
            "from": request.META.get("HTTP_X_BKAPI_FROM", "esb"),
        }
        # Return None if some are empty
        if all(credentials.values()):
            return credentials
        return None

    def verify_credentials(self, credentials):
        public_key = self._get_jwt_public_key(credentials["from"])
        jwt_payload = self._decode_jwt(credentials["jwt"], public_key)
        if not jwt_payload:
            return False, None

        return True, jwt_payload

    def _decode_jwt(self, content, public_key):
        try:
            # 获取 JWT 头部信息
            header = jwt.get_unverified_header(content)
            algorithm = header.get("alg")

            if not algorithm:
                logger.error("JWT header does not contain 'alg' field, jwt: %s", content)
                return None

            return jwt.decode(content, public_key, algorithms=[algorithm], options={"verify_iss": False})
        except Exception:  # pylint: disable=broad-except
            logger.exception("decode jwt fail, jwt: %s", content)
            return None

    def _get_username_from_jwt_payload(self, jwt_payload):
        """从 jwt 里获取 username"""
        user = jwt_payload.get("user", {})
        verified = user.get("verified", False)
        username = user.get("bk_username", "") or user.get("username", "")
        # 如果 user 通过认证，则为实体用户，直接返回
        if verified:
            return username
        # 未通过认证有两种可能，（1）username 不可信任（2）username 为空
        # 非空则说明是未认证，不可信任的用户，则统一用不可信任的用户名代替，不使用传递过来的 username
        if username:
            return BKNonEntityUser.BK__UNVERIFIED_USER.value
        # 匿名用户
        return BKNonEntityUser.BK__ANONYMOUS_USER.value

    def _get_app_code_from_jwt_payload(self, jwt_payload):
        """从 jwt 里获取 app_code"""
        app = jwt_payload.get("app", {})

        if not app.get("verified", False):
            raise exceptions.AuthenticationFailed("app is not verified")

        # 兼容多版本 (企业版/TE 版/社区版) 以及兼容APIGW/ESB
        app_code = app.get("bk_app_code", "") or app.get("app_code", "")

        # 虽然 app_code 为空对于后续的鉴权一定是不通过的，但鉴权不通过有很多原因，这里提前 log 便于问题排查
        if not app_code:
            raise exceptions.AuthenticationFailed("could not get app_code from esb/apigateway jwt payload! it's empty")

        return app_code

    def _get_or_create_user(self, username):
        user_model = get_user_model()
        user, _ = user_model.objects.get_or_create(
            username=username, defaults={"is_active": True, "is_staff": False, "is_superuser": False}
        )
        return user

    def _get_apigw_public_key(self):
        """
        获取 APIGW 的 PUBLIC KEY
        由于配置文件里的 public key 是来着环境变量，且使用了 base64 编码的，所以需要获取后解码
        """
        # 如果 BK_APIGW_PUBLIC_KEY 为空，则直接报错
        if not settings.BK_APIGW_PUBLIC_KEY:
            logger.error("BK_APIGW_PUBLIC_KEY can not be empty")
            return ""

        # base64 解码
        try:
            public_key = base64.b64decode(settings.BK_APIGW_PUBLIC_KEY).decode("utf-8")
        except Exception:  # pylint: disable=broad-except
            logger.exception("BK_APIGW_PUBLIC_KEY is not the base64 string, base64.b64decode fail")
            return ""

        return public_key

    @cachedmethod(timeout=None)  # 缓存不过期，除非重新部署 SaaS
    def _get_jwt_public_key(self, request_from):
        if request_from == "apigw":
            return self._get_apigw_public_key()
        data = esb.get_api_public_key()
        return data["public_key"]
