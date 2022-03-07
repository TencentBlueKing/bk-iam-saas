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

from backend.common.models import BaseModel
from backend.util.json import json_dumps


class Policy(BaseModel):
    """
    subject-系统-操作-策略
    """

    # subject
    subject_type = models.CharField(max_length=32)
    subject_id = models.CharField(max_length=64)

    # system
    system_id = models.CharField(max_length=32)

    # action
    action_type = models.CharField("操作类型", max_length=32, default="")
    action_id = models.CharField("操作ID", max_length=64)

    # policy
    _resources = models.TextField("资源策略", db_column="resources")  # json
    policy_id = models.BigIntegerField("后端policy_id", default=0)

    class Meta:
        verbose_name = "权限策略"
        verbose_name_plural = "权限策略"

        index_together = ["subject_id", "subject_type", "system_id"]

    @property
    def resources(self):
        return json.loads(self._resources)

    @resources.setter
    def resources(self, resources):
        self._resources = json_dumps(resources)


class TemporaryPolicy(BaseModel):
    """
    临时权限
    """

    # subject
    subject_type = models.CharField(max_length=32)
    subject_id = models.CharField(max_length=64)

    # system
    system_id = models.CharField(max_length=32)

    # action
    action_type = models.CharField("操作类型", max_length=32, default="")
    action_id = models.CharField("操作ID", max_length=64)

    # policy
    _resources = models.TextField("资源策略", db_column="resources")  # json
    expired_at = models.IntegerField("过期时间")
    policy_id = models.BigIntegerField("后端policy_id", default=0)

    class Meta:
        verbose_name = "临时权限策略"
        verbose_name_plural = "临时权限策略"

        index_together = ["subject_id", "subject_type", "system_id"]

    @property
    def resources(self):
        return json.loads(self._resources)

    @resources.setter
    def resources(self, resources):
        self._resources = json_dumps(resources)
