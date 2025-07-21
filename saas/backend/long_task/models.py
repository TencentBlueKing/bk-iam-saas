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
from typing import Any, List

from django.db import models

from backend.common.constants import DEFAULT_TENANT_ID
from backend.common.error_codes import error_codes
from backend.common.lock import gen_long_task_create_lock
from backend.common.models import BaseModel

from .constants import TaskStatus

EXISTS_TASK_ERROR = error_codes.INVALID_ARGS.format("已存在未完成的相同任务")


class TaskDetail(BaseModel):
    """
    长时任务
    """

    tenant_id = models.CharField("租户 ID", max_length=64, default=DEFAULT_TENANT_ID)

    type = models.CharField("任务类型", max_length=32)  # NOTE 提供任务执行时在上层提供阻止哪些操作的规则方式
    # title = models.CharField("任务标题")  # 可能需要界面上的展示
    _args = models.TextField("参数", db_column="args")
    _params = models.TextField("子任务参数集", db_column="params", default="")  # List[Dict]
    unique_sign = models.CharField("任务唯一标识", max_length=64, default="")  # 运行中的任务，不允许重新创建
    status = models.IntegerField(
        "任务状态",
        choices=TaskStatus.get_choices(),
        default=TaskStatus.PENDING.value,  # type: ignore[attr-defined]
    )
    celery_id = models.CharField("celery 任务 id", max_length=36, default="")
    _results = models.TextField("结果集", db_column="results", default="")

    class Meta:
        verbose_name = "长时任务"
        verbose_name_plural = "长时任务"
        ordering = ["-id"]

    @property
    def args(self):
        return json.loads(self._args) if self._args else []

    @property
    def params(self):
        return json.loads(self._params) if self._params else []

    @property
    def results(self):
        results = json.loads(self._results) if self._results else []

        # 运行中的任务，实时从 redis 中取结果
        if self.status == TaskStatus.RUNNING.value:
            from .tasks import ResultStore

            store = ResultStore(self.id)
            results += store.list()

        return results

    @classmethod
    def create(cls, tenant_id: str, type_: str, args: List[Any], sign: str = ""):
        # 如果同一时间有运行中的任务，则阻止新的任务
        if sign:
            if cls.exists(type_, sign):
                raise EXISTS_TASK_ERROR

            with gen_long_task_create_lock(cls._gen_unique_sign(type_, sign)):
                if not cls.exists(type_, sign):
                    return cls._create(tenant_id, type_, args, sign)

                raise EXISTS_TASK_ERROR

        return cls._create(tenant_id, type_, args, sign)

    @classmethod
    def _create(cls, tenant_id: str, type_: str, args: List[Any], sign: str = ""):
        task = cls(
            tenant_id=tenant_id,
            type=type_,
            _args=json.dumps(args),
            unique_sign=cls._gen_unique_sign(type_, sign) if sign else sign,
        )

        task.save(force_insert=True)

        # from .tasks import TaskFactory

        # TaskFactory().delay(task.id)  # NOTE 保证事务执行完成以后再执行任务
        return task

    @staticmethod
    def _gen_unique_sign(type_, sign):
        return f"{type_}:{sign}"

    @classmethod
    def exists(cls, type_, sign):
        """
        是否已有任务存在
        """
        us = cls._gen_unique_sign(type_, sign)
        return cls.objects.filter(unique_sign=us, status__lte=TaskStatus.RUNNING.value).exists()

    def cancel(self):
        if self.status in [TaskStatus.PENDING.value, TaskStatus.RUNNING.value]:
            self.status = TaskStatus.CANCEL.value
            self.save(update_fields=["status"])


class SubTaskState(models.Model):
    tenant_id = models.CharField("租户 ID", max_length=64, default=DEFAULT_TENANT_ID)

    task_id = models.IntegerField("父亲任务 id")
    celery_id = models.CharField("celery 任务 id", max_length=36)
    index = models.IntegerField("子任务索引")
    status = models.IntegerField(
        "任务状态",
        choices=TaskStatus.get_choices(),
        default=TaskStatus.RUNNING.value,  # type: ignore[attr-defined]
    )
    exception = models.TextField("任务异常", default="")

    class Meta:
        verbose_name = "子任务状态"
        verbose_name_plural = "子任务状态"
        ordering = ["index"]
