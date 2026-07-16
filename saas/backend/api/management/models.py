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
from django.db import models

from backend.api.constants import ALLOW_ANY
from backend.common.cache import cachedmethod
from backend.common.models import BaseModel

from .constants import ManagementAPIEnum


class ManagementAPIAllowListConfig(BaseModel):
    """管理类 API 允许系统白名单"""

    api = models.CharField("API", choices=ManagementAPIEnum.get_choices(), max_length=64, help_text="*代表任意")
    system_id = models.CharField("接入系统", max_length=32)

    class Meta:
        verbose_name = "管理类 API 允许系统白名单"
        verbose_name_plural = "管理类 API 允许系统白名单"
        ordering = ["-id"]
        unique_together = [["system_id", "api"]]

    @classmethod
    @cachedmethod(timeout=5 * 60)  # 缓存 5 分钟
    def is_allowed(cls, system_id: str, api: str):
        """
        检测某个接入系统是否允许调用某个管理类 API
        由于支持配置任意，所以判断是需要判断是否包含了任意
        """
        return cls.objects.filter(system_id=system_id, api__in=[ALLOW_ANY, api]).exists()


class ManagementObjectAPIAllowListConfig(BaseModel):
    """管理类 API 对象级白名单
    支持对 app_code 授予指定对象（Role/Group/Template）的指定 API 访问权限，
    不需要 app_code 是该对象所属系统的 client，实现细粒度的对象级鉴权旁路
    """

    app_code = models.CharField("应用编码", max_length=64)
    object_type = models.CharField("对象类型", max_length=32, help_text="role/group/template")
    object_id = models.IntegerField("对象 ID")
    api = models.CharField("API", choices=ManagementAPIEnum.get_choices(), max_length=64, help_text="*代表任意")

    class Meta:
        verbose_name = "管理类 API 对象级白名单"
        verbose_name_plural = "管理类 API 对象级白名单"
        ordering = ["-id"]
        unique_together = [["app_code", "object_type", "object_id", "api"]]

    @classmethod
    @cachedmethod(timeout=5 * 60)
    def is_allowed(cls, app_code: str, object_type: str, object_id: int, api: str) -> bool:
        """检测某个 app_code 是否允许操作某个对象的某个 API"""
        return cls.objects.filter(
            app_code=app_code,
            object_type=object_type,
            object_id=object_id,
            api__in=[ALLOW_ANY, api],
        ).exists()


class SystemAllowAuthSystem(BaseModel):
    """系统允许授权的系统
    即可配置某个系统管理其他系统的权限
    """

    system_id = models.CharField("接入系统", max_length=32)
    auth_system_id = models.CharField("接入系统", max_length=32, help_text="*代表任意")

    class Meta:
        verbose_name = "系统允许授权的系统"
        verbose_name_plural = "系统允许授权的系统"
        ordering = ["-id"]
        index_together = ["system_id", "auth_system_id"]

    @classmethod
    @cachedmethod(timeout=5 * 60)  # 缓存 5 分钟
    def list_auth_system_id(cls, system_id: str):
        return list(cls.objects.filter(system_id=system_id).values_list("auth_system_id", flat=True))
