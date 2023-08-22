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
import zlib

from django.db import models
from django.utils import timezone

from backend.util.json import json_dumps


class BaseModel(models.Model):
    """
    基础model
    """

    creator = models.CharField("创建者", max_length=64)
    updater = models.CharField("更新者", max_length=64)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    @property
    def created_time_display(self):
        # 转换成本地时间
        local_time = timezone.localtime(self.created_time)
        return local_time.strftime("%Y-%m-%d %H:%M:%S")

    @property
    def updated_time_display(self):
        # 转换成本地时间
        local_time = timezone.localtime(self.updated_time)
        return local_time.strftime("%Y-%m-%d %H:%M:%S")

    @property
    def created_timestamp(self):
        # 时间戳
        return int(self.created_time.timestamp())

    @property
    def updated_timestamp(self):
        # 时间戳
        return int(self.updated_time.timestamp())

    class Meta:
        abstract = True


class TimestampedModel(models.Model):
    """Model with 'created' and 'updated' fields."""

    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    @property
    def created_time_display(self):
        # 转换成本地时间
        local_time = timezone.localtime(self.created_time)
        return local_time.strftime("%Y-%m-%d %H:%M:%S")

    @property
    def updated_time_display(self):
        # 转换成本地时间
        local_time = timezone.localtime(self.updated_time)
        return local_time.strftime("%Y-%m-%d %H:%M:%S")

    class Meta:
        abstract = True


# FROM https://github.com/Tencent/bk-sops/blob/bc3c36108d7681f969aeca52253be811981b8de7/pipeline/models.py#L42
class CompressedJSONField(models.BinaryField):
    compress_level = 6

    def get_prep_value(self, value):
        value = super(CompressedJSONField, self).get_prep_value(value)
        return zlib.compress(json_dumps(value).encode("utf-8"), self.compress_level)

    def to_python(self, value):
        value = super(CompressedJSONField, self).to_python(value)
        return json.loads(zlib.decompress(value).decode("utf-8"))

    def from_db_value(self, value, expression, connection, context=None):
        return self.to_python(value)


class BaseSystemHiddenModel(models.Model):
    """
    系统隐藏字段

    用于记录model对象是否需要在权限中心SaaS隐藏
    """

    source_system_id = models.CharField(max_length=32, default="")
    hidden = models.BooleanField(default=False, db_index=True)

    class Meta:
        abstract = True
