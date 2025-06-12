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

from django.db import models

from backend.api.constants import ALLOW_ANY
from backend.common.models import BaseModel

from .constants import AdminAPIEnum


class AdminAPIAllowListConfig(BaseModel):
    """Admin API允许app_code白名单"""

    api = models.CharField("API", choices=AdminAPIEnum.get_choices(), max_length=32, help_text="*代表任意")
    app_code = models.CharField("API调用者", max_length=32)

    class Meta:
        verbose_name = "Admin API允许的应用白名单"
        verbose_name_plural = "Admin API允许的应用白名单"
        ordering = ["-id"]
        unique_together = [["app_code", "api"]]
        db_table = "api.admin_adminapiallowlistconfig"

    @classmethod
    def is_allowed(cls, app_code: str, api: str):
        """
        检测某个AppCode是否允许调用某个Admin API
        由于支持配置任意，所以判断还需要判断是否包含了任意
        """
        return cls.objects.filter(app_code=app_code, api__in=[ALLOW_ANY, api]).exists()
