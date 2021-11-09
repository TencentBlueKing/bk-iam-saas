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
from typing import Any, Dict

import redis
from django.conf import settings
from dogpile.cache import make_region

# 默认是内存的Cache
cache_dictionary: Dict[str, Any] = {}  # 内存cache是使用Python dictionary来作为Cache的
region = make_region().configure("dogpile.cache.memory_pickle", arguments={"cache_dict": cache_dictionary})

# TODO: 对于Redis并非IAM独享，需要单独的key_generator
#  https://dogpilecache.sqlalchemy.org/en/latest/api.html#module-dogpile.cache.region
# 使用Redis缓存，可使用StrictRedis和ConnectionPool来缓存，这里使用ConnectionPool来缓存
rd_pool = redis.ConnectionPool(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD,
    encoding="utf8",
    decode_responses=True,
    # 必须设置，否则在redis有问题的情况下某些命令可能会一直block
    socket_connect_timeout=5,
    socket_timeout=5,
)
redis_region = make_region().configure(
    "dogpile.cache.redis",
    expiration_time=60 * 10 * 10,  # 避免忘记设置过期时间，可设置个长时间的默认值
    arguments={
        "connection_pool": rd_pool,
        # Disable distributed lock for better performance
        "distributed_lock": False,
    },
)

# Note: 使用region.cache_on_arguments() 对类的相关方法应用时，会忽略self和cls参数，进而是在类的所有对象上缓存的，并不是针对某个对象
# 如果需要针对对象缓存，则需要自定义 function_key_generator参数传入cache_on_arguments()里
