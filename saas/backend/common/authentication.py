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
from django.contrib.auth import get_user_model
from rest_framework.authentication import BasicAuthentication

from backend.apps.role.models import AnonymousRole, Role
from backend.service.constants import RoleType


class BasicAppCodeAuthentication(BasicAuthentication):
    """
    使用app_code认证的BasicAuth
    """

    def authenticate_credentials(self, userid, password, request=None):
        if userid != settings.APP_CODE or password != settings.APP_SECRET:
            return None
        user_model = get_user_model()
        user, _ = user_model.objects.get_or_create(
            username="admin", defaults={"is_active": True, "is_staff": False, "is_superuser": False}
        )
        if request:
            request.bk_app_code = userid
        return user, None

    def authenticate(self, request):
        user_auth_tuple = super().authenticate(request)
        if user_auth_tuple is not None:
            role = Role.objects.filter(type=RoleType.SUPER_MANAGER.value).first() or AnonymousRole()
            request.role = role
        return user_auth_tuple
