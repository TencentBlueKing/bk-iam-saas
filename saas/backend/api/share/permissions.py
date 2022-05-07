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
from rest_framework import exceptions, permissions


class ShareAPIPermission(permissions.IsAuthenticated):
    """
    Share API 权限校验
    """

    def has_permission(self, request, view):
        # ESB认证必须通过
        if not super().has_permission(request, view):
            return False

        # 判读是否Share App Code
        app_code = request.bk_app_code
        if self.is_share_app_code(app_code):
            return True

        raise exceptions.PermissionDenied(detail=f"app_code({app_code}) do not be allowed to call share api")

    @staticmethod
    def is_share_app_code(self, app_code):
        share_app_codes = set(settings.SHARE_APP_CODES.split(","))
        return app_code in share_app_codes
