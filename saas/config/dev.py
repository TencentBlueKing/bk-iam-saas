"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-权限中心(BlueKing-IAM) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from .default import *  # noqa
from .v3 import *  # noqa

DEBUG = True

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

# 本地开发数据库设置
# USE FOLLOWING SQL TO CREATE THE DATABASE NAMED APP_CODE
# SQL: CREATE DATABASE `framework_py` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci; # noqa: E501
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": APP_CODE,
        "USER": "root",
        "PASSWORD": "",
        "HOST": "localhost",
        "PORT": "3306",
    },
    "audit": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": APP_CODE,
        "USER": "root",
        "PASSWORD": "",
        "HOST": "localhost",
        "PORT": "3306",
    },
}


# cache
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_PASSWORD = ""
REDIS_DB = 0

CACHES = {
    # 默认缓存是本地内存，使用最近最少使用（LRU）的淘汰策略，使用pickle 序列化数据
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "",  # 多个本地内存缓存时才需要设置
        "TIMEOUT": 60 * 30,  # 避免使用时忘记设置过期时间，可设置个长时间的默认值，30分钟，特殊值0表示立刻过期，实际上就是不缓存
        "KEY_PREFIX": "bk_iam",  # 缓存的Key的前缀
        # "VERSION": 1,  # 用于避免同一个缓存Key在不同SaaS版本之间存在差异导致读取的值非期望的，由于内存缓存每次部署都会重置，所以不需要设置
        # "KEY_FUNCTION": "",  # Key的生成函数，默认是 key_prefix:version:key
        # 内存缓存特有参数
        "OPTIONS": {
            "MAX_ENTRIES": 1000,  # 支持缓存的key最多数量，越大将会占用更多内存
            "CULL_FREQUENCY": 3,  # 当达到 MAX_ENTRIES 时被淘汰的部分条目，淘汰率是 1 / CULL_FREQUENCY，默认淘汰 1/3的缓存key
        },
    },
    "redis": {
        "BACKEND": "django_redis.cache.RedisCache",
        # 若需要支持主从配置，则LOCATION为List[master_url, slave_url]
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
        "TIMEOUT": 60 * 30,  # 避免使用时忘记设置过期时间，可设置个长时间的默认值，30分钟，特殊值0表示立刻过期，实际上就是不缓存
        "KEY_PREFIX": "bk_iam",  # 缓存的Key的前缀
        "VERSION": 1,  # 避免同一个缓存Key在不同SaaS版本之间存在差异导致读取的值非期望的
        # "KEY_FUNCTION": "",  # Key的生成函数，默认是 key_prefix:version:key
        "OPTIONS": {
            # Sentinel模式 django_redis.client.SentinelClient (django-redis>=5.0.0)
            # 集群模式 django_redis.client.HerdClient
            # 单实例模式 django_redis.client.DefaultClient
            "CLIENT_CLASS": "django_redis.client.DefaultClient",  # 根据redis是单机还是集群模式, 修改Client class
            "PASSWORD": REDIS_PASSWORD,
            "SOCKET_CONNECT_TIMEOUT": 5,  # socket 建立连接超时设置，单位秒
            "SOCKET_TIMEOUT": 5,  # 连接建立后的读写操作超时设置，单位秒
            "IGNORE_EXCEPTIONS": True,  # redis 只作为缓存使用, 触发异常不能影响正常逻辑，可能只是稍微慢点而已
            # 默认使用pickle 序列化数据，可选序列化方式有：pickle、json、msgpack
            # "SERIALIZER": "django_redis.serializers.pickle.PickleSerializer"
            # Redis 连接池配置
            "CONNECTION_POOL_KWARGS": {
                # redis-py 默认不会关闭连接, 尽可能重用连接，但可能会造成连接过多，导致Redis无法服务，所以需要设置最大值连接数
                "max_connections": 100
            },
        },
    },
}
# 当Redis Cache 使用IGNORE_EXCEPTIONS时，设置指定的 logger 输出异常
DJANGO_REDIS_LOGGER = "app"


# celery
BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"


# cors
CORS_ORIGIN_WHITELIST = []


# 多人开发时，无法共享的本地配置可以放到新建的 local_settings.py 文件中
# 并且把 local_settings.py 加入版本管理忽略文件中
try:
    from .local_settings import *  # noqa
except ImportError:
    pass
