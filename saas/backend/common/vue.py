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
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.generic.base import TemplateView


class VueTemplateView(TemplateView):
    template_name = "index.html"

    @xframe_options_exempt
    def get(self, request):
        try:
            context = {
                "BK_PAAS_HOST": settings.BK_PAAS_HOST.rstrip("/"),
                "BK_COMPONENT_API_URL": settings.BK_COMPONENT_API_URL.rstrip("/"),
                "LOGIN_SERVICE_URL": settings.LOGIN_SERVICE_URL.rstrip("/"),
                "AJAX_URL_PREFIX": settings.AJAX_URL_PREFIX.rstrip("/"),
                "SITE_URL": settings.SITE_URL,
                # 去除末尾的 /, 前端约定
                "STATIC_URL": settings.STATIC_URL.rstrip("/"),
                # 去除开头的 . document.domain需要
                "SESSION_COOKIE_DOMAIN": settings.SESSION_COOKIE_DOMAIN.lstrip("."),
                # csrftoken name
                "CSRF_COOKIE_NAME": settings.CSRF_COOKIE_NAME,
                # BK_ITSM
                "BK_ITSM_APP_URL": settings.BK_ITSM_APP_URL.rstrip("/"),
                # BK_DOMAIN
                "BK_DOMAIN": settings.BK_DOMAIN,
                "BK_DOCS_URL_PREFIX": settings.BK_DOCS_URL_PREFIX.rstrip("/"),
                # BK Res
                "BK_SHARED_RES_URL": settings.BK_SHARED_RES_URL.rstrip("/"),
                # App Code
                "BK_APP_CODE": settings.APP_CODE,
                # 不允许作为用户组成员的部门 ID,用英文逗号分割
                "DEPARTMENT_IDS_NOT_ALLOWED_AS_GROUP_MEMBER": settings.DEPARTMENT_IDS_NOT_ALLOWED_AS_GROUP_MEMBER
            }

            # 添加前端功能启用开关
            for feature, is_enabled in settings.ENABLE_FRONT_END_FEATURES.items():
                context[feature.upper()] = is_enabled

            response = super(VueTemplateView, self).get(request, **context)
            return response
        except Exception as error:  # pylint: disable=broad-except
            print(error)


class LoginSuccessView(VueTemplateView):
    template_name = "login_success.html"
