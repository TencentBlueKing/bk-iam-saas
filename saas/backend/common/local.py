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

from celery.app.task import Task
from werkzeug.local import Local as _Local
from werkzeug.local import release_local

from backend.util.uuid import gen_uuid

_local = _Local()


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
    def __init__(self):
        object.__setattr__(self, "__storage__", {})
        object.__setattr__(self, "__ident_func__", inspect_task_id)

    def __release_local__(self):
        """重写释放方法避免递归"""
        try:
            # 直接访问存储避免触发__getattr__
            storage = object.__getattribute__(self, "__storage__")
            ident_func = object.__getattribute__(self, "__ident_func__")
            ident = ident_func()

            # 安全释放存储
            if ident in storage:
                del storage[ident]
        except Exception:
            # 安全回退
            object.__setattr__(self, "__storage__", {})


celery_local = CeleryLocal()


def get_local():
    if local.request:
        return _local

    return celery_local
