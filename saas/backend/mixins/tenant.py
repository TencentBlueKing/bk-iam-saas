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

from rest_framework.request import Request


class TenantMixin:
    """
    Mixin to add tenant information to a view.
    """

    request: Request

    @property
    def tenant_id(self):
        # Web 请求会经用户认证，将用户租户设置导致 request.tenant_id;
        # APIGateway 请求，会在 JWT 认证后，将 Header 中的 tenant_id 设置到 request.tenant_id;
        return self.request.tenant_id
