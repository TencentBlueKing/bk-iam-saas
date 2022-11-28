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
from django.utils.functional import SimpleLazyObject
from iam import IAM
from iam.contrib.django.dispatcher import DjangoBasicResourceApiDispatcher

from .providers import (
    AdminAPIAllowListConfigResourceProvider,
    AuthAPIAllowListConfigResourceProvider,
    GroupResourceProvider,
    ManagementAPIAllowListConfigResourceProvider,
    PolicyResourceProvider,
    RoleResourceProvider,
    TemplateResourceProvider,
    TemporaryPolicyResourceProvider,
)


def init_iam():
    if settings.BK_IAM_USE_APIGATEWAY:
        iam = IAM(settings.APP_CODE, settings.SECRET_KEY, bk_apigateway_url=settings.BK_IAM_APIGATEWAY_URL)
    else:
        iam = IAM(
            settings.APP_CODE,
            settings.SECRET_KEY,
            bk_iam_host=settings.BK_IAM_INNER_HOST,
            bk_paas_host=settings.BK_PAAS_HOST,
        )

    return iam


dispatcher = DjangoBasicResourceApiDispatcher(SimpleLazyObject(init_iam), settings.BK_IAM_SYSTEM_ID)

dispatcher.register("policy", PolicyResourceProvider())
dispatcher.register("temporary_policy", TemporaryPolicyResourceProvider())
dispatcher.register("role", RoleResourceProvider())
dispatcher.register("group", GroupResourceProvider())
dispatcher.register("template", TemplateResourceProvider())
dispatcher.register("admin_api_white_list", AdminAPIAllowListConfigResourceProvider())
dispatcher.register("auth_api_white_list", AuthAPIAllowListConfigResourceProvider())
dispatcher.register("management_api_white_list", ManagementAPIAllowListConfigResourceProvider())
