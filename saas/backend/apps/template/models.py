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

from backend.common.models import BaseModel, CompressedJSONField
from backend.service.constants import SubjectType, TemplatePreUpdateStatus
from backend.util.json import json_dumps

from .managers import (
    PermTemplateManager,
    PermTemplatePolicyAuthorizedManager,
    PermTemplatePreGroupSyncManager,
    PermTemplatePreUpdateLockManager,
)


class PermTemplate(BaseModel):
    """
    权限模板
    """

    name = models.CharField("模板名称", max_length=128)
    system_id = models.CharField("系统ID", max_length=32)
    description = models.CharField("描述", max_length=255, default="")
    subject_count = models.IntegerField("授权对象数量", default=0)
    _action_ids = models.TextField("操作列表", db_column="action_ids")

    objects = PermTemplateManager()

    class Meta:
        verbose_name = "权限模板"
        verbose_name_plural = "权限模板"
        ordering = ["-created_time"]
        index_together = ["system_id"]

    @property
    def action_ids(self):
        return json.loads(self._action_ids)

    @action_ids.setter
    def action_ids(self, data):
        self._action_ids = json_dumps(data)


class PermTemplatePolicyAuthorized(BaseModel):
    """
    权限模板授权
    """

    template_id = models.IntegerField("模板ID")
    subject_type = models.CharField("授权对象类型", max_length=32, choices=SubjectType.get_choices())
    subject_id = models.CharField("授权对象ID", max_length=64)
    system_id = models.CharField("系统ID", max_length=32)
    _data = models.TextField("授权数据", db_column="data")  # 调研压缩的json字段

    objects = PermTemplatePolicyAuthorizedManager()

    class Meta:
        verbose_name = "权限模板授权"
        verbose_name_plural = "权限模板授权"
        index_together = [
            ["system_id"],
        ]
        unique_together = ["template_id", "subject_type", "subject_id"]
        ordering = ["-updated_time"]

    @property
    def data(self):
        return json.loads(self._data)

    @data.setter
    def data(self, data):
        self._data = json_dumps(data)


class PermTemplatePreUpdateLock(BaseModel):
    """
    模板的预提交信息锁

    1. 获取已有的预提交信息时不能是running
    2. 获取模板预更新的到用户组的预览信息只能是waiting
    3. 模板预更新提交时, 需要从 waiting -> running
    4. 如果模板存在预更新的信息锁, 不能授权到用户组
    5. 删除预提交信息时, 不能是running
    6. 提交用户组的更新信息, 锁只能是 waiting
    7. 如果锁是running, 不能从新提交预更新信息
    """

    template_id = models.IntegerField("模板ID")
    status = models.CharField(
        "类型",
        max_length=32,
        choices=TemplatePreUpdateStatus.get_choices(),
        default=TemplatePreUpdateStatus.WAITING.value,
    )
    action_ids = CompressedJSONField("操作列表", default=None)

    objects = PermTemplatePreUpdateLockManager()

    class Meta:
        verbose_name = "权限模板更新预提交"
        verbose_name_plural = "权限模板更新预提交"
        ordering = ["-created_time"]
        unique_together = ["template_id"]


class PermTemplatePreGroupSync(BaseModel):
    template_id = models.IntegerField("模板ID")
    group_id = models.IntegerField("模板ID")
    status = models.CharField(
        "类型",
        max_length=32,
        choices=TemplatePreUpdateStatus.get_choices(),
        default=TemplatePreUpdateStatus.WAITING.value,
    )
    data = CompressedJSONField("授权数据", default=None)

    objects = PermTemplatePreGroupSyncManager()

    class Meta:
        verbose_name = "权限模板更新用户组同步预提交"
        verbose_name_plural = "权限模板更新用户组同步预提交"
        unique_together = ["template_id", "group_id"]
        ordering = ["-updated_time"]
