# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云 - 权限中心 (BlueKing-IAM) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

全局相关
"""

from werkzeug.local import Local as _Local
from werkzeug.local import release_local

from backend.util.uuid import gen_uuid

_local = _Local()


def new_request_id():
    return gen_uuid()


class Singleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance


class Local(Singleton):
    """local 对象
    必须配合中间件 RequestProvider 使用
    """

    @property
    def request(self):
        """获取全局 request 对象"""
        return getattr(_local, "request", None)
        # if not request:
        #     raise RuntimeError("request object not in local")

    @request.setter
    def request(self, value):
        """设置全局 request 对象"""
        _local.request = value

    @property
    def request_id(self):
        # celery 后台没有 request 对象
        if self.request:
            return self.request.request_id

        return new_request_id()

    def get_http_request_id(self):
        """从接入层获取 request_id，或者生成一个新的 request_id"""
        # 在从 header 中获取
        request_id = self.request.META.get("HTTP_X_REQUEST_ID") or self.request.META.get("HTTP_X_BKAPI_REQUEST_ID", "")
        if request_id:
            return request_id

        # 最后主动生成一个
        return new_request_id()

    @property
    def request_username(self) -> str:
        try:
            # celery 后台，openAPI 都可能没有 user，需要判断
            if self.request and hasattr(self.request, "user"):
                return self.request.user.username
        except Exception:  # pylint: disable=broad-except
            return ""

        return ""

    def release(self):
        release_local(_local)


local = Local()


def get_local():
    return _local
