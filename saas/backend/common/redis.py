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
from django.core.cache import caches
from django_redis import get_redis_connection as get_django_cache_redis_connection

from .cache import CacheEnum


def make_redis_key(key: str) -> str:
    """
    所有通过get_redis_connection获取原生Redis来使用Redis的，其最终key都需要避免与Django Cache冲突
    所以这里提供了方法来协助生成避免Key冲突的，这样使用原生Redis时不需要关注与其他项目或者项目内Cache的key冲突
    """
    cache = caches[CacheEnum.REDIS.value]
    # 对于Cache来说version是有意义的，但对于原生使用Redis，没意义，为了避免与Cache Key冲突，这里可以使用任何version不可能去的值来代替，比如"raw"
    return cache.make_key(key, version="raw")


def get_redis_connection():
    """
    复用Django Cache其配置的Redis Cache的Redis Client Connection
    这样可以不需要根据Redis配置来生成Redis Client Connection
    Note：
    1. 这里返回的是原生Redis Connection，所以Django Cache里配置的KEY_PREFIX、TIMEOUT、VERSION都不会生效
    2. 使用时为了避免与Cache的key冲突，需要先查看
    """
    return get_django_cache_redis_connection(alias=CacheEnum.REDIS.value)
