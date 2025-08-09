# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-权限中心(BlueKing-IAM) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

全局相关
"""

import logging

from celery import current_task
from werkzeug.local import Local as _Local
from werkzeug.local import release_local

from backend.util.uuid import gen_uuid

_local = _Local()
logger = logging.getLogger("celery")


def new_request_id():
    return gen_uuid()


class Singleton(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance


class Local(Singleton):
    """local对象
    必须配合中间件RequestProvider使用
    """

    @property
    def request(self):
        """获取全局request对象"""
        return getattr(_local, "request", None)
        # if not request:
        #     raise RuntimeError("request object not in local")

    @request.setter
    def request(self, value):
        """设置全局request对象"""
        _local.request = value

    @property
    def request_id(self):
        # celery后台没有request对象
        if self.request:
            return self.request.request_id

        return new_request_id()

    def get_http_request_id(self):
        """从接入层获取request_id，或者生成一个新的request_id"""
        # 在从header中获取
        request_id = self.request.META.get("HTTP_X_REQUEST_ID") or self.request.META.get("HTTP_X_BKAPI_REQUEST_ID", "")
        if request_id:
            return request_id

        # 最后主动生成一个
        return new_request_id()

    @property
    def request_username(self) -> str:
        try:
            # celery后台，openAPI都可能没有user，需要判断
            if self.request and hasattr(self.request, "user"):
                return self.request.user.username
        except Exception:  # pylint: disable=broad-except
            return ""

        return ""

    def release(self):
        release_local(_local)


local = Local()


# celery task 专用
class CeleryLocal(_Local):
    """
    一个基于任务ID（task_id）区分的本地存储（local storage）
    从而使不同的 Celery 任务能有自己的独立上下文，手动管理任务ID隔离
    """

    def _get_task_id(self) -> str:
        try:
            if current_task and hasattr(current_task, "request"):
                task_id = getattr(current_task.request, "id", None)
                if task_id:
                    return task_id
        except Exception:
            pass
        return "__no_task__"

    def _get_storage(self) -> dict:
        total_storage = super().__storage.get({})
        task_id = self._get_task_id()
        if task_id not in total_storage:
            total_storage = total_storage.copy()
            total_storage[task_id] = {}
            super().__storage.set(total_storage)
        return total_storage[task_id]

    def __getattr__(self, name):
        storage = self._get_storage()
        if name in storage:
            return storage[name]
        raise AttributeError(name)

    def __setattr__(self, name, value):
        task_id = self._get_task_id()
        total_storage = super().__storage.get({}).copy()
        storage = total_storage.get(task_id, {}).copy()
        storage[name] = value
        total_storage[task_id] = storage
        super().__storage.set(total_storage)

    def __delattr__(self, name):
        task_id = self._get_task_id()
        total_storage = super().__storage.get({}).copy()
        storage = total_storage.get(task_id, {}).copy()
        if name in storage:
            del storage[name]
            total_storage[task_id] = storage
            super().__storage.set(total_storage)
        else:
            raise AttributeError(name)

    def __release_local__(self):
        total_storage = super().__storage.get({}).copy()
        task_id = self._get_task_id()
        if task_id in total_storage:
            total_storage.pop(task_id)
            super().__storage.set(total_storage)


celery_local = CeleryLocal()


def get_local():
    if local.request:
        return _local

    return celery_local
