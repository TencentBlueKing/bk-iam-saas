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
import json

from django.db import models

from backend.apps.user.constants import UserPermissionCleanupRecordStatusEnum
from backend.apps.user.managers import UserProfileManager
from backend.common.models import BaseModel
from backend.util.json import json_dumps


class UserProfile(BaseModel):
    """
    记录与用户个人相关的配置等信息：新手指引已读内容
    """

    username = models.CharField("用户名", max_length=255, unique=True, db_index=True)
    _newbie = models.TextField("新手指引", db_column="newbie", default="{}")

    objects = UserProfileManager()

    class Meta:
        verbose_name = "用户配置"
        verbose_name_plural = "用户配置"

    @property
    def newbie(self):
        return json.loads(self._newbie)

    @newbie.setter
    def newbie(self, newbie):
        self._newbie = json_dumps(newbie)


class UserPermissionCleanupRecord(BaseModel):
    """
    用户权限清理记录
    """

    username = models.CharField("用户名", max_length=255, unique=True, db_index=True)
    status = models.CharField(
        "单据状态",
        max_length=32,
        choices=UserPermissionCleanupRecordStatusEnum.get_choices(),
        default=UserPermissionCleanupRecordStatusEnum.CREATED.value,
    )
    error_info = models.TextField("交接异常信息", default="")

    class Meta:
        verbose_name = "用户权限清理记录"
        verbose_name_plural = "用户权限清理记录"
