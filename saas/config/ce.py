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
import random
import string
from urllib.parse import urlparse

from . import RequestIDFilter
from .default import BASE_DIR, env

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": env.str("MYSQL_NAME"),
        "USER": env.str("MYSQL_USER"),
        "PASSWORD": env.str("MYSQL_PASSWORD"),
        "HOST": env.str("MYSQL_HOST"),
        "PORT": env.int("MYSQL_PORT"),
    },
    "audit": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": env.str("AUDIT_DB_NAME", default=env.str("MYSQL_NAME")),
        "USER": env.str("AUDIT_DB_USERNAME", default=env.str("MYSQL_USER")),
        "PASSWORD": env.str("AUDIT_DB_PASSWORD", default=env.str("MYSQL_PASSWORD")),
        "HOST": env.str("AUDIT_DB_HOST", default=env.str("MYSQL_HOST")),
        "PORT": env.int("AUDIT_DB_PORT", default=env.int("MYSQL_PORT")),
    },
}

# cache
REDIS_HOST = env.str("REDIS_HOST")
REDIS_PORT = env.str("REDIS_PORT")
REDIS_PASSWORD = env.str("REDIS_PASSWORD")
REDIS_DB = env.int("REDIS_DB", default=0)

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


# 判断是否为本地开发环境
IS_LOCAL = not env.str("BKPAAS_ENVIRONMENT", default="")

APP_CODE = BK_APP_CODE = env.str("BKPAAS_APP_CODE", default="bk_iam")
APP_SECRET = BK_APP_SECRET = env.str("BKPAAS_APP_SECRET", default="af76be9c-2b24-4006-a68e-e66abcfd67af")

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = APP_SECRET

APP_URL = env.str("BK_IAM_APP_URL", default="")

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
SITE_URL = env.str("BKPAAS_SUB_PATH", default="/")
FORCE_SCRIPT_NAME = SITE_URL
STATIC_URL = SITE_URL + "staticfiles/"
AJAX_URL_PREFIX = SITE_URL + "api/v1"

# 只对正式环境日志级别进行配置，可以在这里修改
LOG_LEVEL = env.str("BKAPP_LOG_LEVEL", default="ERROR")
_LOG_CLASS = "logging.handlers.RotatingFileHandler"
if IS_LOCAL:
    LOG_LEVEL = "DEBUG"
    _LOG_DIR = os.path.join(os.path.dirname(BASE_DIR), "logs", APP_CODE)
    _LOG_NAME_PREFIX = env.str("BKPAAS_LOG_NAME_PREFIX", default=APP_CODE)
    _LOGGING_FORMAT = {
        "format": (
            "%(levelname)s [%(asctime)s] %(pathname)s "
            "%(lineno)d %(funcName)s %(process)d %(thread)d "
            "\n \t %(request_id)s\t%(message)s \n"
        ),
        "datefmt": "%Y-%m-%d %H:%M:%S",
    }
else:
    _LOG_DIR = env.str("BKPAAS_APP_LOG_PATH", default="/")
    _RAND_STR = "".join(random.sample(string.ascii_letters + string.digits, 4))
    _LOG_NAME_PREFIX = "%s-%s" % (env.str("BKPAAS_PROCESS_TYPE"), _RAND_STR)

    _LOGGING_FORMAT = {
        "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
        "fmt": (
            "%(levelname)s %(asctime)s %(pathname)s %(lineno)d "
            "%(funcName)s %(process)d %(thread)d %(request_id)s %(message)s"
        ),
    }
if not os.path.exists(_LOG_DIR):
    os.makedirs(_LOG_DIR)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "request_id_filter": {
            "()": RequestIDFilter,
        }
    },
    "formatters": {
        "verbose": _LOGGING_FORMAT,
        "simple": {"format": "%(levelname)s %(message)s"},
    },
    "handlers": {
        "null": {
            "level": "DEBUG",
            "class": "logging.NullHandler",
        },
        "console": {"level": "DEBUG", "class": "logging.StreamHandler", "formatter": "simple"},
        "root": {
            "class": _LOG_CLASS,
            "formatter": "verbose",
            "filename": os.path.join(_LOG_DIR, "%s-django.log" % _LOG_NAME_PREFIX),
            "maxBytes": 1024 * 1024 * 10,
            "backupCount": 5,
            "filters": ["request_id_filter"],
        },
        "component": {
            "class": _LOG_CLASS,
            "formatter": "verbose",
            "filename": os.path.join(_LOG_DIR, "%s-component.log" % _LOG_NAME_PREFIX),
            "maxBytes": 1024 * 1024 * 10,
            "backupCount": 5,
            "filters": ["request_id_filter"],
        },
        "mysql": {
            "class": _LOG_CLASS,
            "formatter": "verbose",
            "filename": os.path.join(_LOG_DIR, "%s-mysql.log" % _LOG_NAME_PREFIX),
            "maxBytes": 1024 * 1024 * 10,
            "backupCount": 5,
            "filters": ["request_id_filter"],
        },
        "celery": {
            "class": _LOG_CLASS,
            "formatter": "verbose",
            "filename": os.path.join(_LOG_DIR, "%s-celery.log" % _LOG_NAME_PREFIX),
            "maxBytes": 1024 * 1024 * 10,
            "backupCount": 5,
            "filters": ["request_id_filter"],
        },
        "organization": {
            "class": _LOG_CLASS,
            "formatter": "verbose",
            "filename": os.path.join(_LOG_DIR, "%s-json.log" % _LOG_NAME_PREFIX),
            "maxBytes": 1024 * 1024 * 10,
            "backupCount": 5,
            "filters": ["request_id_filter"],
        },
    },
    "loggers": {
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
            "handlers": ["root"],
            "level": "ERROR",
            "propagate": True,
        },
        "django.db.backends": {
            "handlers": ["mysql"],
            "level": LOG_LEVEL,
            "propagate": True,
        },
        # the root logger ,用于整个project的logger
        "root": {
            "handlers": ["root"],
            "level": LOG_LEVEL,
            "propagate": True,
        },
        # 组件调用日志
        "component": {
            "handlers": ["component"],
            "level": LOG_LEVEL,
            "propagate": True,
        },
        "celery": {
            "handlers": ["celery"],
            "level": LOG_LEVEL,
            "propagate": True,
        },
        # 普通app日志
        "app": {
            "handlers": ["root"],
            "level": LOG_LEVEL,
            "propagate": True,
        },
        # 组织架构同步日志
        "organization": {
            "handlers": ["root" if IS_LOCAL else "organization"],
            "level": LOG_LEVEL,
            "propagate": True,
        },
    },
}

APP_API_URL = APP_URL  # 前后端分离架构下, APP_URL 与 APP_API_URL 不一样

BK_COMPONENT_API_URL = env.str("BK_COMPONENT_API_URL", default="")
BK_COMPONENT_INNER_API_URL = BK_COMPONENT_API_URL

BK_ITSM_APP_URL = env.str("BK_ITSM_APP_URL", default="")

LOGIN_SERVICE_URL = env.str("BK_LOGIN_URL", default="/")
LOGIN_SERVICE_PLAIN_URL = LOGIN_SERVICE_URL + "plain/"

# 蓝鲸PASS平台URL
BK_PAAS_HOST = env.str("BK_PAAS_HOST", default=env.str("BKPAAS_URL", default=""))

# 用于 用户认证、用户信息获取 的蓝鲸主机
BK_PAAS_INNER_HOST = env.str("BK_PAAS2_URL", default=env.str("BK_PAAS_INNER_HOST", default=BK_PAAS_HOST))
