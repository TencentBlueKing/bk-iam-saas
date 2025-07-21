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

import json

from django.db import models

from backend.common.constants import DEFAULT_TENANT_ID
from backend.common.models import BaseModel
from backend.util.json import json_dumps


class TemporaryPolicy(BaseModel):
    """
    临时权限
    """

    tenant_id = models.CharField("租户 ID", max_length=64, default=DEFAULT_TENANT_ID)

    # subject
    subject_type = models.CharField(max_length=32)
    subject_id = models.CharField(max_length=64)

    # system
    system_id = models.CharField(max_length=32)

    # action
    action_type = models.CharField("操作类型", max_length=32, default="")
    action_id = models.CharField("操作 ID", max_length=64)

    # policy
    _resources = models.TextField("资源策略", db_column="resources")  # json
    expired_at = models.IntegerField("过期时间")
    policy_id = models.BigIntegerField("后端 policy_id", default=0)

    class Meta:
        verbose_name = "临时权限策略"
        verbose_name_plural = "临时权限策略"

        indexes = [models.Index(fields=["subject_id", "subject_type", "system_id"])]

    @property
    def resources(self):
        return json.loads(self._resources)

    @resources.setter
    def resources(self, resources):
        self._resources = json_dumps(resources)

    @property
    def display_name(self):
        return f"subject: {self.subject_type}/{self.subject_id} system: {self.system_id} action: {self.action_id}"
