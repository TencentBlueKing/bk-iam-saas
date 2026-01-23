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
import threading

from celery.app.task import Task
from backend.util.uuid import gen_uuid

# 主线程或请求线程使用的 local
_main_local = threading.local()


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
        return getattr(_main_local, "request", None)

    @request.setter
    def request(self, value):
        """设置全局request对象"""
        _main_local.request = value

    @property
    def request_id(self):
        # celery后台没有request对象
        if self.request:
            return self.request.request_id

        return new_request_id()

    def get_http_request_id(self):
        """从接入层获取request_id，或者生成一个新的request_id"""
        try:
            request_id = (
                self.request.META.get("HTTP_X_REQUEST_ID")
                or self.request.META.get("HTTP_X_BKAPI_REQUEST_ID", "")
            )
            if request_id:
                return request_id
        except Exception:
            pass

        return new_request_id()

    @property
    def request_username(self) -> str:
        try:
            if self.request and hasattr(self.request, "user"):
                return self.request.user.username
        except Exception:
            return ""

        return ""

    def release(self):
        if hasattr(_main_local, "request"):
            delattr(_main_local, "request")


local = Local()

# ========== celery 专用区域 ==========


def inspect_task_id():
    for info in inspect.stack()[1:]:
        locals_ = info.frame.f_locals
        if "self" in locals_ and isinstance(locals_["self"], Task):
            return locals_["self"].request.id
    return ""


# celery worker 中专用的 thread-local 存储
class CeleryThreadLocal(threading.local):
    def __init__(self):
        super().__init__()
        self._task_id = inspect_task_id()


celery_local = CeleryThreadLocal()


def get_local():
    """根据是否有 request 判断使用哪种 local"""
    if getattr(_main_local, "request", None) is not None:
        return _main_local
    return celery_local
