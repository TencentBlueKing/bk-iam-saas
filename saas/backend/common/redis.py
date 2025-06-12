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

from django.core.cache import caches
from django_redis import get_redis_connection as get_django_cache_redis_connection

from .cache import CacheEnum


def make_redis_key(key: str) -> str:
    """
    所有通过 get_redis_connection 获取原生 Redis 来使用 Redis 的，其最终 key 都需要避免与 Django Cache 冲突
    所以这里提供了方法来协助生成避免 Key 冲突的，这样使用原生 Redis 时不需要关注与其他项目或者项目内 Cache 的 key 冲突
    """
    cache = caches[CacheEnum.REDIS.value]
    # 对于 Cache 来说 version 是有意义的，但对于原生使用 Redis，没意义，
    # 为了避免与 Cache Key 冲突，这里可以使用任何 version 不可能去的值来代替，比如"raw"
    return cache.make_key(key, version="raw")


def get_redis_connection():
    """
    复用 Django Cache 其配置的 Redis Cache 的 Redis Client Connection
    这样可以不需要根据 Redis 配置来生成 Redis Client Connection
    Note：
    这里返回的是原生 Redis Connection，所以 Django Cache 里配置的 KEY_PREFIX、TIMEOUT、VERSION 都不会生效
    所以使用时为了避免与 Cache 的 key 冲突，必须配合 make_redis_key 方法一起使用
    """
    return get_django_cache_redis_connection(alias=CacheEnum.REDIS.value)
