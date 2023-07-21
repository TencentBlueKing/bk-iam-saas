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

import pytz
from django import forms
from django.contrib import auth
from django.http import HttpResponseForbidden, JsonResponse
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from django.utils.translation import gettext as _

from backend.biz.subject import SubjectBiz
from backend.common.cache import cached
from backend.service.constants import SubjectType

from . import role_auth
from .backends import PermissionForbidden

logger = logging.getLogger("app")


class AuthenticationForm(forms.Form):
    # bk_token format: KH7P4-VSFi_nOEoV3kj0ytcs0uZnGOegIBLV-eM3rw8
    bk_token = forms.CharField()


@cached(timeout=60)
def is_in_blacklist(username: str) -> bool:
    blacklist = []
    try:
        blacklist = SubjectBiz().list_freezed_subjects()
    except Exception:  # pylint: disable=broad-except
        logger.exception("failed to get blacklist, so the blacklist check will not working")

    for subject in blacklist:
        if subject.id == username and subject.type == SubjectType.USER.value:
            return True
    return False


class LoginMiddleware(MiddlewareMixin):
    def process_view(self, request, view, *args, **kwargs):
        if getattr(view, "login_exempt", False):
            return None

        form = AuthenticationForm(request.COOKIES)

        if form.is_valid():
            bk_token = form.cleaned_data["bk_token"]
            try:
                user = auth.authenticate(request=request, bk_token=bk_token)
            except PermissionForbidden as e:
                return JsonResponse(
                    {"result": False, "code": e.code, "message": e.message, "data": None}, status=e.status_code
                )

            if user:
                # NOTE: block the user in blacklist
                if is_in_blacklist(request.user.username):
                    return HttpResponseForbidden(_("用户账号已被冻结, 禁止使用权限中心相关功能"))

                # Succeed to login, recall self to exit process
                if user.username != request.user.username:
                    auth.login(request, user)
            else:
                auth.logout(request)
        else:
            auth.logout(request)

        return None

    def process_response(self, request, response):
        return response


class RoleAuthenticationMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 获取session当前选择的角色ID
        role_id = request.session.get(role_auth.ROLE_SESSION_KEY) or 0
        # 认证用户与角色关系
        role = role_auth.authenticate(request=request, role_id=role_id)
        # 设置当前登录角色
        setattr(request, "role", role)
        return self.get_response(request)


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_active and hasattr(request.user, "get_property"):
            tzname = request.user.get_property("time_zone")
            if tzname:
                timezone.activate(pytz.timezone(tzname))
        return self.get_response(request)
