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

from backend.common.models import BaseModel

from .constants import AuthorizationAPIEnum


class AuthAPIAllowListConfig(BaseModel):
    """
    授权API白名单配置
    """

    type = models.CharField("API类型", choices=AuthorizationAPIEnum.get_choices(), max_length=32)
    system_id = models.CharField("接入系统", max_length=32)
    object_id = models.CharField("资源类型或操作ID", max_length=32, help_text="*代表任意")

    class Meta:
        verbose_name = "授权API白名单配置"
        verbose_name_plural = "授权API白名单配置"
        ordering = ["-id"]
        index_together = ["system_id", "object_id"]
