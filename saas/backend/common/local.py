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

import inspect
import logging

from celery import current_task
from celery.app.task import Task
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


def inspect_task_id():
    for info in inspect.stack()[1:]:
        locals = info.frame.f_locals
        if "self" in locals and isinstance(locals["self"], Task):
            return locals["self"].request.id

    return ""


class CeleryLocal(_Local):
    """为 Celery 任务定制的 Local 类"""

    def __init__(self):
        # 调用父类初始化
        super().__init__()

    def _get_ident(self):
        """重写标识符获取方法"""
        try:
            # 使用 Celery 的 current_task 获取当前任务 ID
            if current_task and hasattr(current_task, 'request'):
                task_id = getattr(current_task.request, 'id', None)
                if task_id:
                    return task_id
        except Exception as e:
            # 记录异常以便调试，但不中断主流程
            logger.debug("Failed to get Celery task ID: %s", str(e), exc_info=True)
            pass
        # 返回 None 或默认值表示不在任务上下文中
        return None

    # 通过属性名称空间隔离不同任务的数据
    def __getattr__(self, name):
        task_id = self._get_ident()
        if task_id is None:
            # 不在任务上下文中，使用正常属性访问
            return super().__getattr__(name)

        # 构造任务特定的属性名
        task_specific_name = f"_task_{task_id}_{name}"
        try:
            return super().__getattr__(task_specific_name)
        except AttributeError:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def __setattr__(self, name, value):
        if name.startswith('_'):
            # 私有属性直接设置
            return super().__setattr__(name, value)

        task_id = self._get_ident()
        if task_id is None:
            # 不在任务上下文中，正常设置属性
            return super().__setattr__(name, value)

        # 构造任务特定的属性名
        task_specific_name = f"_task_{task_id}_{name}"
        super().__setattr__(task_specific_name, value)

    def __delattr__(self, name):
        task_id = self._get_ident()
        if task_id is None:
            # 不在任务上下文中，正常删除属性
            return super().__delattr__(name)

        # 构造任务特定的属性名
        task_specific_name = f"_task_{task_id}_{name}"
        try:
            super().__delattr__(task_specific_name)
        except AttributeError:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def __release_local__(self):
        """重写释放方法，只清理当前任务的上下文"""
        task_id = self._get_ident()
        if task_id is None:
            # 不在任务上下文中，正常释放
            return super().__release_local__()

        # 只清理当前任务相关的数据
        try:
            storage = self._storage.get({}).copy()
        except LookupError:
            return

        # 删除所有以当前任务ID为前缀的属性
        keys_to_remove = [key for key in storage.keys() if key.startswith(f"_task_{task_id}_")]
        if keys_to_remove:
            for key in keys_to_remove:
                storage.pop(key, None)
            self._storage.set(storage)


celery_local = CeleryLocal()


def get_local():
    if local.request:
        return _local

    return celery_local
