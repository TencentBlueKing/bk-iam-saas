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

from backend.common.models import BaseModel, BaseSystemHiddenModel
from backend.service.constants import ApplicationStatus, ApplicationType
from backend.util.json import json_dumps


class Application(BaseModel, BaseSystemHiddenModel):
    """
    权限申请单
    """

    sn = models.CharField("申请单号", max_length=64)
    type = models.CharField("申请单类型", max_length=64, choices=ApplicationType.get_choices())
    applicant = models.CharField("申请人", max_length=64)
    reason = models.CharField("申请理由", max_length=255, default="")
    _data = models.TextField("申请数据", db_column="data")  # json
    status = models.CharField(
        "单据状态", max_length=32, choices=ApplicationStatus.get_choices(), default=ApplicationStatus.PENDING.value
    )

    callback_id = models.CharField("回调随机数ID", max_length=32, default="")

    class Meta:
        verbose_name = "权限申请"
        verbose_name_plural = "权限申请"
        ordering = ["-id"]
        indexes = [
            models.Index(fields=["created_time"]),  # 单字段索引
            models.Index(fields=["callback_id", "sn"]),  # 多字段组合索引
        ]

    @property
    def data(self):
        return json.loads(self._data)

    @data.setter
    def data(self, data):
        self._data = json_dumps(data)
