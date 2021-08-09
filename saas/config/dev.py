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
from config import RUN_VER

if RUN_VER == "open":
    from blueapps.patch.settings_open_saas import *  # noqa
else:
    from blueapps.patch.settings_paas_services import *  # noqa

# 本地开发环境
RUN_MODE = "DEVELOP"

# APP本地静态资源目录
# STATIC_URL = '/static/'

# APP静态资源目录url
# REMOTE_STATIC_URL = '%sremote/' % STATIC_URL

# Celery 消息队列设置 RabbitMQ
BROKER_URL = "amqp://guest:guest@localhost:5672//"
# Celery 消息队列设置 Redis
# BROKER_URL = 'redis://localhost:6379/0'

DEBUG = True

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

# ==============================================================================
# 应用基本信息配置 (请按照说明修改)
# ==============================================================================
# 在蓝鲸智云开发者中心 -> 点击应用ID -> 基本信息 中获取 APP_ID 和 APP_TOKEN 的值
APP_ID = ""
APP_TOKEN = ""
# 蓝鲸智云开发者中心的域名，形如：http://paas.bking.com
BK_PAAS_HOST = ""

APP_ID = os.environ.get("APP_ID", APP_ID)
APP_TOKEN = os.environ.get("APP_TOKEN", APP_TOKEN)
BK_PAAS_HOST = os.environ.get("BK_PAAS_HOST", BK_PAAS_HOST)
BK_PAAS_INNER_HOST = os.environ.get("BK_PAAS_INNER_HOST", BK_PAAS_HOST)
BK_IAM_HOST = ""

# for vue
LOGIN_SERVICE_URL = BK_PAAS_HOST.rstrip("/") + "/login/"
LOGIN_SERVICE_PLAIN_URL = LOGIN_SERVICE_URL + "plain/"
APP_URL = os.environ.get("APP_URL", "")
APP_API_URL = APP_URL
BK_ITSM_APP_URL = BK_PAAS_HOST + "/o/bk_itsm"

BK_PAAS_HOST_PARSE_URL = urlparse(BK_PAAS_HOST)
_BK_PAAS_HOSTNAME = BK_PAAS_HOST_PARSE_URL.hostname  # 去除端口的域名
_BK_PAAS_NETLOC = BK_PAAS_HOST_PARSE_URL.netloc  # 若有端口，则会带上对应端口
_BK_PAAS_IS_SPECIAL_PORT = BK_PAAS_HOST_PARSE_URL.port in [None, 80, 443, 8000]
# 特殊端口，则只需要取域名，否则取原生的(若有端口则会自动带上端口)
SESSION_COOKIE_DOMAIN = _BK_PAAS_HOSTNAME if _BK_PAAS_IS_SPECIAL_PORT else _BK_PAAS_NETLOC
CSRF_COOKIE_DOMAIN = SESSION_COOKIE_DOMAIN
APP_URL_MD5_16BIT = hashlib.md5(APP_URL.encode("utf-8")).hexdigest()[8:-8]
CSRF_COOKIE_NAME = f"{CSRF_COOKIE_NAME}_{APP_URL_MD5_16BIT}"

CORS_ORIGIN_ALLOW_ALL = True
CORS_URLS_REGEX = ""

# cache
REDIS_HOST = os.environ.get("BKAPP_REDIS_HOST", "localhost")
REDIS_PORT = os.environ.get("BKAPP_REDIS_PORT", "6379")
REDIS_PASSWORD = os.environ.get("BKAPP_REDIS_PASSWORD", "")
REDIS_DB = os.environ.get("BKAPP_REDIS_DB", 0)

# cache
if REDIS_PASSWORD:
    CACHE_REDIS_URL = f"redis://[:{REDIS_PASSWORD}]@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
else:
    CACHE_REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": CACHE_REDIS_URL,
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
    }
}

# 开启性能统计
# ENABLE_PYINSTRUMENT = True

# 多人开发时，无法共享的本地配置可以放到新建的 local_settings.py 文件中
# 并且把 local_settings.py 加入版本管理忽略文件中
try:
    from .local_settings import *  # noqa
except ImportError:
    pass

# iam engine host
BK_IAM_ENGINE_HOST = os.environ.get("BKAPP_IAM_ENGINE_HOST", "")
BK_IAM_ENGINE_HOST_TYPE = os.environ.get("BKAPP_IAM_ENGINE_HOST_TYPE", "direct")  # direct/apigateway
