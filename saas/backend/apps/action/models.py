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

from backend.util.json import json_dumps


class AggregateAction(models.Model):
    system_id = models.CharField("系统ID", max_length=32)
    _action_ids = models.TextField("操作列表", db_column="action_ids")
    _aggregate_resource_type = models.TextField("聚合资源类型", db_column="aggregate_resource_type")

    class Meta:
        verbose_name = "聚合操作"
        verbose_name_plural = "聚合操作"

        indexes = [models.Index(fields=["system_id"])]

    @property
    def action_ids(self):
        return json.loads(self._action_ids)

    @action_ids.setter
    def action_ids(self, action_ids):
        self._action_ids = json_dumps(action_ids)

    @property
    def aggregate_resource_type(self):
        return json.loads(self._aggregate_resource_type)

    @aggregate_resource_type.setter
    def aggregate_resource_type(self, aggregate_resource_type):
        self._aggregate_resource_type = json_dumps(aggregate_resource_type)
