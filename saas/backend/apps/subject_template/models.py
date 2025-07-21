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

from backend.common.constants import DEFAULT_TENANT_ID
from backend.common.models import BaseModel


class SubjectTemplate(BaseModel):
    """产品模板"""

    tenant_id = models.CharField("租户 ID", max_length=64, default=DEFAULT_TENANT_ID)

    name = models.CharField("名称", max_length=512)
    description = models.CharField("描述", max_length=512)
    readonly = models.BooleanField("只读标识", default=False)
    source_group_id = models.IntegerField("来源用户组 ID", default=0, db_index=True)

    class Meta:
        verbose_name = "人员模板"
        verbose_name_plural = "人员模板"
        ordering = ["-id"]


class SubjectTemplateRelation(BaseModel):
    """人员模板关联关系"""

    tenant_id = models.CharField("租户 ID", max_length=64, default=DEFAULT_TENANT_ID)

    template_id = models.IntegerField("模板 ID", db_index=True)
    subject_type = models.CharField("类型", max_length=32)
    subject_id = models.CharField("ID", max_length=64)

    class Meta:
        verbose_name = "人员模板关联关系"
        verbose_name_plural = "人员模板关联关系"
        ordering = ["-id"]
        unique_together = ["template_id", "subject_type", "subject_id"]


class SubjectTemplateGroup(BaseModel):
    """人员模板用户组关联关系"""

    tenant_id = models.CharField("租户 ID", max_length=64, default=DEFAULT_TENANT_ID)

    template_id = models.IntegerField("模板 ID", db_index=True)
    group_id = models.IntegerField("用户组 ID", db_index=True)
    expired_at = models.BigIntegerField("过期时间")

    class Meta:
        verbose_name = "人员模板用户组关联关系"
        verbose_name_plural = "人员模板用户组关联关系"
        ordering = ["-id"]
        unique_together = ["template_id", "group_id"]
