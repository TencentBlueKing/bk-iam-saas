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
import hashlib
import logging
import time

from django.conf import settings
from rest_framework import authentication, exceptions

from backend.common.error_codes import error_codes

logger = logging.getLogger("app")


class ResignApiAuthentication(authentication.BaseAuthentication):
    """API签名认证类"""

    # 时间戳有效期（秒）
    TIMESTAMP_VALIDITY = 60

    def authenticate(self, request):
        """
        签名认证方法
        """

        try:
            # 提取并验证请求头参数
            resign_sign = request.META.get("HTTP_RESIGN_SIGN", "").strip()
            resign_timestamp = request.META.get("HTTP_RESIGN_TIMESTAMP", "").strip()
            resign_app_id = request.META.get("HTTP_RESIGN_APP_ID", "").strip()

            # 验证必需参数完整性
            self._validate_required_params(resign_sign, resign_timestamp, resign_app_id)

            # 验证签名和时间戳
            self._check_sign(resign_sign, resign_timestamp, resign_app_id, settings.PCG_RESIGN_APP_SECRET)

            logger.info("重签名认证成功：app_id=%s, path=%s", resign_app_id, request.path)

            # 认证成功，返回None表示没有具体用户对象，但认证通过
            # 可以根据需要返回自定义的用户对象和认证信息
            return (None, {"app_id": resign_app_id, "timestamp": resign_timestamp})

        except exceptions.AuthenticationFailed:
            # 重新抛出认证异常
            raise error_codes.FORBIDDEN.format("签名认证失败")
        except Exception as e:
            logger.error("重签名认证异常：%s", str(e), exc_info=True)
            raise error_codes.FORBIDDEN.format("重签名认证异常：%s", str(e))

    def authenticate_header(self, request):
        """返回认证失败时的HTTP头信息"""
        return 'ResignAPI realm="API"'

    def _validate_required_params(self, resign_sign: str, resign_timestamp: str, resign_app_id: str):
        """验证必需参数是否存在且有效"""
        if not all([resign_sign, resign_timestamp, resign_app_id]):
            missing_params = []
            if not resign_sign:
                missing_params.append("resign-sign")
            if not resign_timestamp:
                missing_params.append("resign-timestamp")
            if not resign_app_id:
                missing_params.append("resign-app-id")

            logger.warning("签名认证失败：缺少必需参数 %s", ", ".join(missing_params))
            raise exceptions.AuthenticationFailed(f"签名认证失败：缺少必需参数 {', '.join(missing_params)}")

    def _check_sign(self, resign_sign: str, resign_timestamp: str, resign_app_id: str, resign_secret_key: str):
        """验证签名和时间戳"""
        # 验证时间戳格式和有效性
        timestamp = self._validate_timestamp(resign_timestamp)

        # 验证签名
        sign_content = f"{timestamp}{resign_secret_key}{resign_app_id}"
        expected_sign = hashlib.md5(sign_content.encode("utf-8")).hexdigest()

        if resign_sign != expected_sign:
            logger.warning("签名认证失败：签名不匹配，app_id=%s", resign_app_id)
            raise exceptions.AuthenticationFailed("重签名认证失败：签名无效")

        logger.debug("签名认证成功：app_id=%s, timestamp=%s", resign_app_id, timestamp)

    def _validate_timestamp(self, resign_timestamp: str) -> int:
        """验证时间戳格式和有效性"""
        try:
            timestamp = int(resign_timestamp)
        except ValueError:
            raise ValueError("时间戳格式错误，必须为有效整数")

        current_time = int(time.time())
        time_diff = current_time - timestamp

        if time_diff > self.TIMESTAMP_VALIDITY:
            logger.warning("签名认证失败：时间戳过期，timestamp=%s, current_time=%s, diff=%s秒", timestamp, current_time, time_diff)
            raise exceptions.AuthenticationFailed("签名认证失败：时间戳已过期")

        if time_diff < -self.TIMESTAMP_VALIDITY:
            logger.warning("签名认证失败：时间戳超前，timestamp=%s, current_time=%s, diff=%s秒", timestamp, current_time, time_diff)
            raise exceptions.AuthenticationFailed("签名认证失败：时间戳超前")

        return timestamp
