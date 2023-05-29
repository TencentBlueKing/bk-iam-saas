"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-权限中心(BlueKing-IAM) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import hashlib
import os
from urllib.parse import urlparse

from . import RequestIDFilter
from .default import BROKER_URL, env

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": env.str("DB_NAME"),
        "USER": env.str("DB_USERNAME"),
        "PASSWORD": env.str("DB_PASSWORD"),
        "HOST": env.str("DB_HOST"),
        "PORT": env.int("DB_PORT"),
    },
    "audit": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": env.str("AUDIT_DB_NAME", default=env.str("DB_NAME")),
        "USER": env.str("AUDIT_DB_USERNAME", default=env.str("DB_USERNAME")),
        "PASSWORD": env.str("AUDIT_DB_PASSWORD", default=env.str("DB_PASSWORD")),
        "HOST": env.str("AUDIT_DB_HOST", default=env.str("DB_HOST")),
        "PORT": env.int("AUDIT_DB_PORT", default=env.int("DB_PORT")),
    },
}

if env.str("BKCI_DB_NAME", default="") and env.str("BKCI_DB_USERNAME", default=""):
    DATABASES["bkci"] = {
        "ENGINE": "django.db.backends.mysql",
        "NAME": env.str("BKCI_DB_NAME", default="bkci"),
        "USER": env.str("BKCI_DB_USERNAME", default="root"),
        "PASSWORD": env.str("BKCI_DB_PASSWORD", default=""),
        "HOST": env.str("BKCI_DB_HOST", default="localhost"),
        "PORT": env.int("BKCI_DB_PORT", default=3306),
    }

# cache
REDIS_HOST = env.str("BKAPP_REDIS_HOST")
REDIS_PORT = env.int("BKAPP_REDIS_PORT", 6379)
REDIS_PASSWORD = env.str("BKAPP_REDIS_PASSWORD", "")
REDIS_MAX_CONNECTIONS = env.int("BKAPP_REDIS_MAX_CONNECTIONS", 100)
REDIS_DB = env.int("BKAPP_REDIS_DB", 0)
# sentinel check
REDIS_USE_SENTINEL = env.bool("BKAPP_REDIS_USE_SENTINEL", False)
REDIS_SENTINEL_MASTER_NAME = env.str("BKAPP_REDIS_SENTINEL_MASTER_NAME", "mymaster")
REDIS_SENTINEL_PASSWORD = env.str("BKAPP_REDIS_SENTINEL_PASSWORD", "")
REDIS_SENTINEL_ADDR_STR = env.str("BKAPP_REDIS_SENTINEL_ADDR", "")
# parse sentinel address from "host1:port1,host2:port2" to [("host1", port1), ("host2", port2)]
REDIS_SENTINEL_ADDR_LIST = []
try:
    REDIS_SENTINEL_ADDR_LIST = [tuple(addr.split(":")) for addr in REDIS_SENTINEL_ADDR_STR.split(",") if addr]
except Exception as e:  # pylint: disable=broad-except noqa
    print(f"BKAPP_REDIS_SENTINEL_ADDR {REDIS_SENTINEL_ADDR_STR} is invalid: {e}")

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
                "max_connections": REDIS_MAX_CONNECTIONS,
            },
        },
    },
}

# redis sentinel
if REDIS_USE_SENTINEL:
    # Enable the alternate connection factory.
    DJANGO_REDIS_CONNECTION_FACTORY = "django_redis.pool.SentinelConnectionFactory"

    CACHES["redis"] = {
        "BACKEND": "django_redis.cache.RedisCache",
        # The hostname in LOCATION is the primary (service / master) name
        "LOCATION": f"redis://{REDIS_SENTINEL_MASTER_NAME}/{REDIS_DB}",
        "TIMEOUT": 60 * 30,  # 避免使用时忘记设置过期时间，可设置个长时间的默认值，30分钟，特殊值0表示立刻过期，实际上就是不缓存
        "KEY_PREFIX": "bk_iam",  # 缓存的Key的前缀
        "VERSION": 1,  # 避免同一个缓存Key在不同SaaS版本之间存在差异导致读取的值非期望的
        # "KEY_FUNCTION": "",  # Key的生成函数，默认是 key_prefix:version:key
        "OPTIONS": {
            # While the default client will work, this will check you
            # have configured things correctly, and also create a
            # primary and replica pool for the service specified by
            # LOCATION rather than requiring two URLs.
            "CLIENT_CLASS": "django_redis.client.SentinelClient",
            "PASSWORD": REDIS_PASSWORD,
            "SOCKET_CONNECT_TIMEOUT": 5,  # socket 建立连接超时设置，单位秒
            "SOCKET_TIMEOUT": 5,  # 连接建立后的读写操作超时设置，单位秒
            "IGNORE_EXCEPTIONS": True,  # redis 只作为缓存使用, 触发异常不能影响正常逻辑，可能只是稍微慢点而已
            # Sentinels which are passed directly to redis Sentinel.
            "SENTINELS": REDIS_SENTINEL_ADDR_LIST,
            # kwargs for redis Sentinel (optional).
            "SENTINEL_KWARGS": {
                "password": REDIS_SENTINEL_PASSWORD,
                "socket_timeout": 5,
            },
            # You can still override the connection pool (optional).
            "CONNECTION_POOL_CLASS": "redis.sentinel.SentinelConnectionPool",
            # Redis 连接池配置
            "CONNECTION_POOL_KWARGS": {
                # redis-py 默认不会关闭连接, 尽可能重用连接，但可能会造成连接过多，导致Redis无法服务，所以需要设置最大值连接数
                "max_connections": REDIS_MAX_CONNECTIONS
            },
        },
    }

    # celery broker
    # https://docs.celeryq.dev/en/v4.3.0/history/whatsnew-4.0.html?highlight=sentinel#redis-support-for-sentinel
    if not BROKER_URL:
        BROKER_URL = ";".join(
            [f"sentinel://:{REDIS_PASSWORD}@" + ":".join(addr) + f"/{REDIS_DB}" for addr in REDIS_SENTINEL_ADDR_LIST]
        )
        BROKER_TRANSPORT_OPTIONS = {
            "master_name": REDIS_SENTINEL_MASTER_NAME,
            "sentinel_kwargs": {"password": REDIS_SENTINEL_PASSWORD},
            "socket_timeout": 5,
            "socket_connect_timeout": 5,
            "socket_keepalive": True,
        }

# 当Redis Cache 使用IGNORE_EXCEPTIONS时，设置指定的 logger 输出异常
DJANGO_REDIS_LOGGER = "app"


# 判断是否为本地开发环境
IS_LOCAL = False

APP_CODE = BK_APP_CODE = env.str("APP_ID", default="bk_iam")
APP_SECRET = BK_APP_SECRET = env.str("APP_TOKEN", default="af76be9c-2b24-4006-a68e-e66abcfd67af")

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = APP_SECRET

# 蓝鲸PASS平台URL
BK_PAAS_HOST = env.str("BK_PAAS_HOST")
APP_URL = BK_PAAS_HOST.rstrip("/") + "/o/" + APP_CODE

# csrf
_BK_PAAS_HOST_PARSE_URL = urlparse(APP_URL)
_BK_PAAS_HOSTNAME = _BK_PAAS_HOST_PARSE_URL.hostname  # 去除端口的域名
_BK_PAAS_NETLOC = _BK_PAAS_HOST_PARSE_URL.netloc  # 若有端口，则会带上对应端口
_BK_PAAS_IS_SPECIAL_PORT = _BK_PAAS_HOST_PARSE_URL.port in [None, 80, 443]
_BK_PAAS_SCHEME = _BK_PAAS_HOST_PARSE_URL.scheme
# 注意：Cookie Domain是不支持端口的
SESSION_COOKIE_DOMAIN = _BK_PAAS_HOSTNAME
CSRF_COOKIE_DOMAIN = SESSION_COOKIE_DOMAIN
_APP_URL_MD5_16BIT = hashlib.md5(APP_URL.encode("utf-8")).hexdigest()[8:-8]
CSRF_COOKIE_NAME = f"bkiam_csrftoken_{_APP_URL_MD5_16BIT}"
# 对于特殊端口，带端口和不带端口都得添加，其他只需要添加默认原生的即可
CSRF_TRUSTED_ORIGINS = [_BK_PAAS_HOSTNAME, _BK_PAAS_NETLOC] if _BK_PAAS_IS_SPECIAL_PORT else [_BK_PAAS_NETLOC]

# cors
CORS_ALLOW_CREDENTIALS = True  # 在 response 添加 Access-Control-Allow-Credentials, 即允许跨域使用 cookies
CORS_ORIGIN_WHITELIST = (
    [f"{_BK_PAAS_SCHEME}://{_BK_PAAS_HOSTNAME}", f"{_BK_PAAS_SCHEME}://{_BK_PAAS_NETLOC}"]
    if _BK_PAAS_IS_SPECIAL_PORT
    else [f"{_BK_PAAS_SCHEME}://{_BK_PAAS_NETLOC}"]
)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/
# 站点URL
SITE_URL = env.str("BK_SITE_URL", default=f"/o/{APP_CODE}/")
FORCE_SCRIPT_NAME = SITE_URL
STATIC_URL = SITE_URL + "staticfiles/"
AJAX_URL_PREFIX = SITE_URL + "api/v1"

# 只对正式环境日志级别进行配置，可以在这里修改
LOG_LEVEL = env.str("BKAPP_LOG_LEVEL", default="ERROR")
_LOG_DIR = os.path.join(os.path.join(env.str("BK_LOG_DIR", default="/data/apps/logs/"), APP_CODE))
# 如果日志文件夹不存在则创建,日志文件存在则延用
if not os.path.exists(_LOG_DIR):
    os.makedirs(_LOG_DIR)
# logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "request_id_filter": {
            "()": RequestIDFilter,
        }
    },
    "formatters": {
        "simple": {
            "format": "%(levelname)s %(message)s \n",
        },
        "verbose": {
            "format": "%(levelname)s [%(asctime)s] %(pathname)s "
            "%(lineno)d %(funcName)s %(process)d %(thread)d "
            "\n \t %(request_id)s\t%(message)s \n",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "component": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "verbose",
            "filename": os.path.join(_LOG_DIR, "component.log"),
            "maxBytes": 1024 * 1024 * 10,
            "backupCount": 5,
            "filters": ["request_id_filter"],
        },
        "celery": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "verbose",
            "filename": os.path.join(_LOG_DIR, "celery.log"),
            "maxBytes": 1024 * 1024 * 10,
            "backupCount": 5,
            "filters": ["request_id_filter"],
        },
        "console": {"level": "DEBUG", "class": "logging.StreamHandler", "formatter": "simple"},
        "null": {
            "level": "DEBUG",
            "class": "logging.NullHandler",
        },
        "root": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "verbose",
            "filename": os.path.join(_LOG_DIR, "%s.log" % APP_CODE),
            "maxBytes": 1024 * 1024 * 10,
            "backupCount": 5,
            "filters": ["request_id_filter"],
        },
        "wb_mysql": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "verbose",
            "filename": os.path.join(_LOG_DIR, "wb_mysql.log"),
            "maxBytes": 1024 * 1024 * 4,
            "backupCount": 5,
            "filters": ["request_id_filter"],
        },
    },
    "loggers": {
        # V2旧版开发框架使用的logger
        "component": {
            "handlers": ["component"],
            "level": "WARNING",
            "propagate": True,
        },
        "django": {
            "handlers": ["null"],
            "level": "INFO",
            "propagate": True,
        },
        "django.server": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": True,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": True,
        },
        "django.db.backends": {
            "handlers": ["wb_mysql"],
            "level": LOG_LEVEL,
            "propagate": True,
        },
        "root": {
            "handlers": ["root"],
            "level": LOG_LEVEL,
            "propagate": True,
        },
        # V3新版使用的日志
        "celery": {
            "handlers": ["celery"],
            "level": LOG_LEVEL,
            "propagate": True,
        },
        "app": {
            "handlers": ["root"],
            "level": LOG_LEVEL,
            "propagate": True,
        },
        # 组织架构同步日志
        "organization": {
            "handlers": ["root"],
            "level": LOG_LEVEL,
            "propagate": True,
        },
    },
}

# 用于 用户认证、用户信息获取 的蓝鲸主机
BK_PAAS_INNER_HOST = env.str("BK_PAAS_INNER_HOST", default=BK_PAAS_HOST)

APP_API_URL = BK_PAAS_INNER_HOST.rstrip("/") + "/o/" + APP_CODE

BK_COMPONENT_INNER_API_URL = BK_PAAS_INNER_HOST
BK_COMPONENT_API_URL = BK_PAAS_HOST

BK_ITSM_APP_URL = BK_PAAS_HOST.rstrip("/") + "/o/bk_itsm"

LOGIN_SERVICE_URL = BK_PAAS_HOST.rstrip("/") + "/login/"
LOGIN_SERVICE_PLAIN_URL = LOGIN_SERVICE_URL + "plain/"

# 对接审计中心相关配置
BK_IAM_RESOURCE_API_HOST = env.str("BK_IAM_RESOURCE_API_HOST", default=APP_URL)
