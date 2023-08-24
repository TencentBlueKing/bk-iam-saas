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

from backend.common.models import BaseModel, BaseSystemHiddenModel, CompressedJSONField, TimestampedModel

from .managers import GroupAuthorizeLockManager


class Group(BaseModel, BaseSystemHiddenModel):
    """
    用户组
    """

    name = models.CharField("名称", max_length=512)
    description = models.CharField("描述", max_length=512)
    user_count = models.IntegerField("用户数", default=0)
    department_count = models.IntegerField("部门数", default=0)
    readonly = models.BooleanField("用户组只读标识", default=False)  # 增加可读标识
    apply_disable = models.BooleanField("用户组不可申请", default=False, db_index=True)

    class Meta:
        verbose_name = "用户组"
        verbose_name_plural = "用户组"
        ordering = ["-id"]

    @property
    def member_count(self):
        return self.user_count + self.department_count


class GroupAuthorizeLock(models.Model):
    group_id = models.IntegerField("用户组ID")
    template_id = models.IntegerField("模板ID")
    system_id = models.CharField("系统ID", max_length=32)
    data = CompressedJSONField("授权数据", default=None)
    key = models.CharField("key", max_length=32)

    objects = GroupAuthorizeLockManager()

    class Meta:
        verbose_name = "用户组授权锁"
        verbose_name_plural = "用户组授权锁"
        unique_together = ["template_id", "group_id", "system_id"]


class GroupSaaSAttribute(TimestampedModel):
    """用户组产品属性，不用于鉴权，只用于产品上，比如readonly=1，表示只可读，不可删除的用户组"""

    group_id = models.IntegerField("用户组ID")
    key = models.CharField("属性的Key", max_length=32)
    value = models.CharField("属性的value", max_length=64, default="")

    class Meta:
        verbose_name = "用户组SaaS属性"
        verbose_name_plural = "用户组SaaS属性"
        # Note: 只允许用户组的某个属性的值最多只有一个，后续需要支持一个用户组的一个属性多个值，则去除唯一约束即可
        unique_together = ["group_id", "key"]
