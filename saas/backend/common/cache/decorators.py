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
# 参考来源：https://github.com/tkem/cachetools/blob/ab9e8af0d506759332a2d1a5ae9d36feae844fda/src/cachetools/__init__.py#L622
import functools
from functools import wraps

from django.core.cache import cache as default_cache

from .keys import hash_key as _default_key


def _method_key(_, *args, **kwargs):
    return _default_key(*args, **kwargs)


# cached 和 cachedmethod 其key的生成方法可以满足大部分情况下不冲突
# 但是对于类的实例方法，由于缓存key默认只用到了方法的自定义参数，若key的区分需要用到self.{attr}，则需要重新自定义
def cached(cache=default_cache, key=_default_key, timeout=None):
    """Decorator to wrap a function with a memorizing callable that saves
    results in a cache.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            namespace = f"{func.__module__}:{func.__name__}"
            k = key(*args, **kwargs, namespace=namespace)
            return cache.get_or_set(k, lambda: func(*args, **kwargs), timeout)

        return functools.update_wrapper(wrapper, func)

    return decorator


def cachedmethod(cache=default_cache, key=_method_key, timeout=None):
    """Decorator to wrap a class or instance method with a memorizing
    callable that saves results in a cache.
    """

    def decorator(method):
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            namespace = f"{method.__module__}:{method.__qualname__}:{method.__name__}"
            k = key(self, *args, **kwargs, namespace=namespace)
            return cache.get_or_set(k, lambda: method(self, *args, **kwargs), timeout)

        return functools.update_wrapper(wrapper, method)

    return decorator
