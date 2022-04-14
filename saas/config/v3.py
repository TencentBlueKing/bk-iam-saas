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
from .default import BASE_DIR

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("MYSQL_NAME"),
        "USER": os.getenv("MYSQL_USER"),
        "PASSWORD": os.getenv("MYSQL_PASSWORD"),
        "HOST": os.getenv("MYSQL_HOST"),
        "PORT": os.getenv("MYSQL_PORT"),
    },
    "audit": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("AUDIT_DB_NAME") or os.getenv("MYSQL_NAME"),
        "USER": os.getenv("AUDIT_DB_USERNAME") or os.getenv("MYSQL_USER"),
        "PASSWORD": os.getenv("AUDIT_DB_PASSWORD") or os.getenv("MYSQL_PASSWORD"),
        "HOST": os.getenv("AUDIT_DB_HOST") or os.getenv("MYSQL_HOST"),
        "PORT": os.getenv("AUDIT_DB_PORT") or os.getenv("MYSQL_PORT"),
    },
}


# cache
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
REDIS_DB = os.getenv("REDIS_DB", 0)

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",  # 根据redis是单机还是集群模式, 修改Client class
            "PASSWORD": REDIS_PASSWORD,
            "SOCKET_CONNECT_TIMEOUT": 5,  # in seconds
            "SOCKET_TIMEOUT": 5,  # in seconds
        },
    }
}


# 判断是否为本地开发环境
IS_LOCAL = not os.getenv("BKPAAS_ENVIRONMENT", False)

APP_CODE = BK_APP_CODE = os.getenv("BKPAAS_APP_CODE", "bk_iam")
APP_SECRET = BK_APP_SECRET = os.getenv("BKPAAS_APP_SECRET", "af76be9c-2b24-4006-a68e-e66abcfd67af")


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = APP_SECRET


APP_URL = os.getenv("BK_IAM_APP_URL", "")


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


CORS_ALLOW_CREDENTIALS = True  # 在 response 添加 Access-Control-Allow-Credentials, 即允许跨域使用 cookies
CORS_ORIGIN_WHITELIST = (
    [f"{_BK_PAAS_SCHEME}://{_BK_PAAS_HOSTNAME}", f"{_BK_PAAS_SCHEME}://{_BK_PAAS_NETLOC}"]
    if _BK_PAAS_IS_SPECIAL_PORT
    else [f"{_BK_PAAS_SCHEME}://{_BK_PAAS_NETLOC}"]
)


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

# 站点URL
SITE_URL = os.getenv("BKPAAS_SUB_PATH", "/")

FORCE_SCRIPT_NAME = SITE_URL
STATIC_URL = SITE_URL + "staticfiles/"
AJAX_URL_PREFIX = SITE_URL + "api/v1"


# 只对正式环境日志级别进行配置，可以在这里修改
LOG_LEVEL = os.getenv("BKAPP_LOG_LEVEL", "ERROR")

_LOG_CLASS = "logging.handlers.RotatingFileHandler"

if IS_LOCAL:
    LOG_LEVEL = "DEBUG"
    _LOG_DIR = os.path.join(os.path.dirname(BASE_DIR), "logs", APP_CODE)
    _LOG_NAME_PREFIX = os.getenv("BKPAAS_LOG_NAME_PREFIX", APP_CODE)
    _LOGGING_FORMAT = {
        "format": (
            "%(levelname)s [%(asctime)s] %(pathname)s "
            "%(lineno)d %(funcName)s %(process)d %(thread)d "
            "\n \t %(request_id)s\t%(message)s \n"
        ),
        "datefmt": "%Y-%m-%d %H:%M:%S",
    }
else:
    _LOG_DIR = os.getenv("BKPAAS_APP_LOG_PATH", "/")
    _RAND_STR = "".join(random.sample(string.ascii_letters + string.digits, 4))
    _LOG_NAME_PREFIX = "%s-%s" % (os.getenv("BKPAAS_PROCESS_TYPE"), _RAND_STR)

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
        "permission": {
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
        # 授权相关的日志
        "permission": {
            "handlers": ["root" if IS_LOCAL else "permission"],
            "level": LOG_LEVEL,
            "propagate": True,
        },
    },
}


APP_API_URL = APP_URL  # 前后端分离架构下, APP_URL 与 APP_API_URL 不一样

BK_COMPONENT_API_URL = os.getenv("BK_COMPONENT_API_URL")
BK_COMPONENT_INNER_API_URL = BK_COMPONENT_API_URL

BK_ITSM_APP_URL = os.getenv("BK_ITSM_APP_URL")

LOGIN_SERVICE_URL = os.getenv("BK_LOGIN_URL", "/")
LOGIN_SERVICE_PLAIN_URL = LOGIN_SERVICE_URL + "plain/"

# 蓝鲸PASS平台URL
BK_PAAS_HOST = os.getenv("BK_PAAS_HOST", os.getenv("BKPAAS_URL"))

# 用于 用户认证、用户信息获取 的蓝鲸主机
BK_PAAS_INNER_HOST = os.getenv("BK_PAAS2_URL", os.getenv("BK_PAAS_INNER_HOST", BK_PAAS_HOST))
