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

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get("DB_NAME"),
        "USER": os.environ.get("DB_USERNAME"),
        "PASSWORD": os.environ.get("DB_PASSWORD"),
        "HOST": os.environ.get("DB_HOST"),
        "PORT": os.environ.get("DB_PORT"),
    },
    "audit": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get("AUDIT_DB_NAME") or os.environ.get("DB_NAME"),
        "USER": os.environ.get("AUDIT_DB_USERNAME") or os.environ.get("DB_USERNAME"),
        "PASSWORD": os.environ.get("AUDIT_DB_PASSWORD") or os.environ.get("DB_PASSWORD"),
        "HOST": os.environ.get("AUDIT_DB_HOST") or os.environ.get("DB_HOST"),
        "PORT": os.environ.get("AUDIT_DB_PORT") or os.environ.get("DB_PORT"),
    },
}


# cache
REDIS_HOST = os.environ.get("BKAPP_REDIS_HOST")
REDIS_PORT = os.environ.get("BKAPP_REDIS_PORT")
REDIS_PASSWORD = os.environ.get("BKAPP_REDIS_PASSWORD")
REDIS_DB = os.environ.get("BKAPP_REDIS_DB", 0)

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
IS_LOCAL = False

APP_CODE = os.getenv("APP_ID", "bk_iam")
APP_SECRET = os.getenv("APP_TOKEN", "af76be9c-2b24-4006-a68e-e66abcfd67af")


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = APP_SECRET


# 蓝鲸PASS平台URL
BK_PAAS_HOST = os.getenv("BK_PAAS_HOST")

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

CORS_ALLOW_CREDENTIALS = True  # 在 response 添加 Access-Control-Allow-Credentials, 即允许跨域使用 cookies
CORS_ORIGIN_WHITELIST = (
    [f"{_BK_PAAS_SCHEME}://{_BK_PAAS_HOSTNAME}", f"{_BK_PAAS_SCHEME}://{_BK_PAAS_NETLOC}"]
    if _BK_PAAS_IS_SPECIAL_PORT
    else [f"{_BK_PAAS_SCHEME}://{_BK_PAAS_NETLOC}"]
)


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

# 站点URL
SITE_URL = os.environ.get("BK_SITE_URL", "/o/%s/" % APP_CODE)

FORCE_SCRIPT_NAME = SITE_URL
STATIC_URL = SITE_URL + "staticfiles/"
AJAX_URL_PREFIX = SITE_URL + "api/v1"


# 只对正式环境日志级别进行配置，可以在这里修改
LOG_LEVEL = "ERROR"

_LOG_DIR = os.path.join(os.path.join(os.getenv("BK_LOG_DIR", "/data/apps/logs/"), APP_CODE))

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
        # 授权相关的日志
        "permission": {
            "handlers": ["root"],
            "level": LOG_LEVEL,
            "propagate": True,
        },
    },
}


# 用于 用户认证、用户信息获取 的蓝鲸主机
BK_PAAS_INNER_HOST = os.getenv("BK_PAAS_INNER_HOST", BK_PAAS_HOST)


APP_API_URL = BK_PAAS_INNER_HOST.rstrip("/") + "/o/" + APP_CODE

BK_COMPONENT_INNER_API_URL = BK_PAAS_INNER_HOST
BK_COMPONENT_API_URL = BK_PAAS_HOST

BK_ITSM_APP_URL = BK_PAAS_HOST.rstrip("/") + "/o/bk_itsm"

LOGIN_SERVICE_URL = BK_PAAS_HOST.rstrip("/") + "/login/"
LOGIN_SERVICE_PLAIN_URL = LOGIN_SERVICE_URL + "plain/"
