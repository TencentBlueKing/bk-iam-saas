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


class MigrateTask(models.Model):
    """
    迁移任务
    """

    status = models.CharField("任务状态", default="", max_length=36)
    role_ids = models.TextField("role_ids", default="")

    class Meta:
        verbose_name = "迁移任务"
        verbose_name_plural = "迁移任务"


class MigrateData(models.Model):
    """
    迁移数据
    """

    project_id = models.CharField("项目ID", max_length=64)
    type = models.CharField("数据类型", max_length=32, default="")
    data = models.TextField("数据")

    class Meta:
        verbose_name = "迁移数据"
        verbose_name_plural = "迁移数据"
