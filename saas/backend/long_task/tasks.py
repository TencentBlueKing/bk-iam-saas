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
import logging
import random
import sys
import time
import traceback
from abc import ABCMeta, abstractmethod
from datetime import timedelta
from typing import Any, Dict, List, Type

from celery import Task, current_app, shared_task
from django.db.models import Max
from django.utils import timezone

from backend.metrics import long_task_run_counter

from .constants import TaskStatus
from .models import SubTaskState, TaskDetail

logger = logging.getLogger("celery")


# 子任务必须要做到可重入
class StepTask(metaclass=ABCMeta):
    """
    步骤任务
    """

    retry = 1  # 单步任务执行失败，重试的次数
    break_ = False  # 单步任务失败是否中断整个任务

    @abstractmethod
    def __init__(self, *args):
        """
        重做：由实现方自行定义重做，如果是重做，kwargs 中 results 表示上一次执行的所有结果
        """

    @abstractmethod
    def get_params(self) -> List[Any]:
        """
        获取所有的步骤参数
        """

    @abstractmethod
    def run(self, item: Any):
        """
        处理每次迭代的逻辑
        """

    @abstractmethod
    def on_success(self, *args):
        """
        执行完成后回调，参数与 init 参数一致
        """


# 任务类型与任务的处理的 StepTask 映射
task_type_mapping: Dict[str, Type[StepTask]] = {}


class Retry:
    """
    重试包装
    """

    def __init__(self, func, tries=1):
        self.func = func
        self._tries = tries

    def __call__(self, item: Any):
        _tries = self._tries

        while _tries:
            try:
                return self.func(item)
            except Exception:  # pylint: disable=broad-except
                _tries -= 1
                if not _tries:
                    raise

                time.sleep(random.randint(0, 100) / 1000)  # 随机 sleep 100 毫秒
        return None


class ResultStore:
    """
    子任务结果存储
    """

    def __init__(self, task_id: int):
        self._task_id = task_id

    def create(self, tenant_id: str, celery_id: str, index: int):
        SubTaskState.objects.create(tenant_id=tenant_id, task_id=self._task_id, celery_id=celery_id, index=index)

    def update(self, index: int, status: int, exception=""):
        SubTaskState.objects.filter(task_id=self._task_id, index=index).update(status=status, exception=exception)

    def list(self) -> List[Dict]:
        q = SubTaskState.objects.filter(task_id=self._task_id).values("index", "status", "exception")
        return list(q)

    def clear(self):
        SubTaskState.objects.filter(task_id=self._task_id).delete()

    def next_index(self):
        q = SubTaskState.objects.filter(task_id=self._task_id).aggregate(Max("index"))
        return 0 if q["index__max"] is None else q["index__max"] + 1


class SubTask(Task):
    name = "backend.long_task.tasks.SubTask"

    def run(self, id: int):
        # 查询任务
        task_detail = TaskDetail.objects.get(pk=id)

        # 如果任务的状态不为 running，则保存结果，退出任务
        if task_detail.status != TaskStatus.RUNNING.value:  # type: ignore[attr-defined]
            self._update_status(task_detail, task_detail.status)
            return

        handler = task_type_mapping[task_detail.type](*task_detail.args)
        store = ResultStore(id)
        index = store.next_index()

        params = task_detail.params

        # 执行子任务
        if index < len(params):
            param = params[index]

            retry_run = Retry(handler.run, handler.retry)
            celery_id = self.request.id

            store.create(task_detail.tenant_id, celery_id, index)
            try:
                retry_run(param)

                store.update(index, TaskStatus.SUCCESS.value)  # type: ignore[attr-defined]

                logger.info(f"long task {id} sub task item: {param} execute success!")
            except Exception:  # pylint: disable=broad-except
                store.update(
                    index,
                    TaskStatus.FAILURE.value,  # type: ignore[attr-defined]
                    traceback.format_exc(),
                )

                logger.exception(f"long task {id} sub task item: {param} execute fail!")

                # 子任务失败，直接失败
                if handler.break_:
                    raise

            # 流转下一个任务
            SubTask().delay(id)
            return

        # 结束任务
        try:
            handler.on_success()
        except Exception:  # pylint: disable=broad-except
            logger.warning(f"long task {id} handler on_success fail", exc_info=sys.exc_info())
        self._update_status(task_detail, TaskStatus.SUCCESS.value)  # type: ignore[attr-defined]

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        task_detail = TaskDetail.objects.get(pk=args[0])
        self._update_status(task_detail, TaskStatus.FAILURE.value)  # type: ignore[attr-defined]

    def _update_status(self, task: TaskDetail, status: int):
        results = task.results
        TaskDetail.objects.filter(id=task.id).update(status=status, _results=json.dumps(results))
        ResultStore(task.id).clear()


current_app.register_task(SubTask())


class TaskFactory(Task):
    name = "backend.long_task.tasks.TaskFactory"

    def run(self, id: int):
        # 查询任务
        task_detail = TaskDetail.objects.get(pk=id)

        # 任务在被调度之前已经取消
        if task_detail.status == TaskStatus.CANCEL.value:  # type: ignore[attr-defined]
            return

        handler_class = task_type_mapping[task_detail.type]

        args = task_detail.args

        handler = handler_class(*args)

        params = handler.get_params()

        TaskDetail.objects.filter(pk=id).update(
            celery_id="",
            status=TaskStatus.RUNNING.value,  # type: ignore[attr-defined]
            _params=json.dumps(params),
        )

        long_task_run_counter.labels(id, task_detail.type).inc(1)

        SubTask().delay(id)


current_app.register_task(TaskFactory())


def register_handler(_type: str):
    def decorate(cls):
        task_type_mapping[_type] = cls
        return cls

    return decorate


@shared_task(ignore_result=True)
def retry_long_task():
    """
    重试 30 分钟以前一直 PENDING/RUNNING 的任务
    """
    day_before = timezone.now() - timedelta(minutes=30)

    qs = TaskDetail.objects.filter(
        status__in=[TaskStatus.PENDING.value, TaskStatus.RUNNING.value], created_time__lt=day_before
    )
    for t in qs:
        if t.status == TaskStatus.RUNNING.value:
            SubTask().delay(t.id)
        else:
            TaskFactory().run(t.id)
