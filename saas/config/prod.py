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

# static file
WHITENOISE_STATIC_PREFIX = "/staticfiles/"
FORCE_SCRIPT_NAME = SITE_URL
STATIC_URL = SITE_URL + "staticfiles/"
AJAX_URL_PREFIX = SITE_URL + "api/v1"

# 正式环境
RUN_MODE = "PRODUCT"

# 只对正式环境日志级别进行配置，可以在这里修改
LOG_LEVEL = "ERROR"

# V2
# import logging
# logging.getLogger('root').setLevel('INFO')
# V3
# import logging
# logging.getLogger('app').setLevel('INFO')

# V3 Smart 配置
if "BKPAAS_ENVIRONMENT" in os.environ:
    import base64
    import json

    def get_app_service_url(app_code: str) -> str:
        value = os.environ["BKPAAS_SERVICE_ADDRESSES_BKSAAS"]
        decoded_value = json.loads(base64.b64decode(value).decode("utf-8"))
        return decoded_value[app_code]

    # 兼容component的APP_ID,APP_TOKEN
    APP_CODE = APP_ID = os.environ.get("BKPAAS_APP_ID", APP_CODE)
    SECRET_KEY = APP_TOKEN = os.environ.get("BKPAAS_APP_SECRET", SECRET_KEY)

    # 正式环境数据库可以在这里配置
    DATABASES.update(  # 需要兼容V3环境变量
        {
            "default": {
                "ENGINE": "django.db.backends.mysql",
                "NAME": os.environ.get("MYSQL_NAME"),
                "USER": os.environ.get("MYSQL_USER"),
                "PASSWORD": os.environ.get("MYSQL_PASSWORD"),
                "HOST": os.environ.get("MYSQL_HOST"),
                "PORT": os.environ.get("MYSQL_PORT"),
            },
            "audit": {
                "ENGINE": "django.db.backends.mysql",
                "NAME": os.environ.get("AUDIT_DB_NAME") or os.environ.get("MYSQL_NAME"),
                "USER": os.environ.get("AUDIT_DB_USERNAME") or os.environ.get("MYSQL_USER"),
                "PASSWORD": os.environ.get("AUDIT_DB_PASSWORD") or os.environ.get("MYSQL_PASSWORD"),
                "HOST": os.environ.get("AUDIT_DB_HOST") or os.environ.get("MYSQL_HOST"),
                "PORT": os.environ.get("AUDIT_DB_PORT") or os.environ.get("MYSQL_PORT"),
            },
        }
    )

    # for vue
    LOGIN_SERVICE_URL = os.environ.get("BK_LOGIN_URL")
    LOGIN_SERVICE_PLAIN_URL = LOGIN_SERVICE_URL + "plain/"
    APP_URL = get_app_service_url(APP_CODE)
    APP_API_URL = APP_URL

    # cache
    REDIS_HOST = os.environ.get("REDIS_HOST")
    REDIS_PORT = os.environ.get("REDIS_PORT")
    REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD")
    REDIS_DB = os.environ.get("REDIS_DB", 0)

    # itsm saas url
    BK_ITSM_APP_URL = get_app_service_url("bk_itsm")

# V2 Smart 配置
else:
    # 正式环境数据库可以在这里配置
    DATABASES.update(
        {
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
    )

    # for vue
    LOGIN_SERVICE_URL = BK_PAAS_HOST.rstrip("/") + "/login/"
    LOGIN_SERVICE_PLAIN_URL = LOGIN_SERVICE_URL + "plain/"
    APP_URL = BK_PAAS_HOST.rstrip("/") + "/o/" + APP_CODE
    APP_API_URL = BK_PAAS_INNER_HOST.rstrip("/") + "/o/" + APP_CODE

    # cache
    REDIS_HOST = os.environ.get("BKAPP_REDIS_HOST")
    REDIS_PORT = os.environ.get("BKAPP_REDIS_PORT")
    REDIS_PASSWORD = os.environ.get("BKAPP_REDIS_PASSWORD")
    REDIS_DB = os.environ.get("BKAPP_REDIS_DB", 0)

    # itsm saas url
    BK_ITSM_APP_URL = BK_PAAS_HOST.rstrip("/") + "/o/bk_itsm"


BK_PAAS_HOST_PARSE_URL = urlparse(APP_URL)
_BK_PAAS_HOSTNAME = BK_PAAS_HOST_PARSE_URL.hostname  # 去除端口的域名
_BK_PAAS_NETLOC = BK_PAAS_HOST_PARSE_URL.netloc  # 若有端口，则会带上对应端口
_BK_PAAS_IS_SPECIAL_PORT = BK_PAAS_HOST_PARSE_URL.port in [None, 80, 443]
_BK_PAAS_SCHEME = BK_PAAS_HOST_PARSE_URL.scheme
# 特殊端口，则只需要取域名，否则取原生的(若有端口则会自动带上端口)
SESSION_COOKIE_DOMAIN = _BK_PAAS_HOSTNAME if _BK_PAAS_IS_SPECIAL_PORT else _BK_PAAS_NETLOC
CSRF_COOKIE_DOMAIN = SESSION_COOKIE_DOMAIN
APP_URL_MD5_16BIT = hashlib.md5(APP_URL.encode("utf-8")).hexdigest()[8:-8]
CSRF_COOKIE_NAME = f"{CSRF_COOKIE_NAME}_{APP_URL_MD5_16BIT}"
# 对于特殊端口，带端口和不带端口都得添加，其他只需要添加默认原生的即可
CSRF_TRUSTED_ORIGINS = [_BK_PAAS_HOSTNAME, _BK_PAAS_NETLOC] if _BK_PAAS_IS_SPECIAL_PORT else [_BK_PAAS_NETLOC]
CORS_ORIGIN_WHITELIST = (
    [f"{_BK_PAAS_SCHEME}://{_BK_PAAS_HOSTNAME}", f"{_BK_PAAS_SCHEME}://{_BK_PAAS_NETLOC}"]
    if _BK_PAAS_IS_SPECIAL_PORT
    else [f"{_BK_PAAS_SCHEME}://{_BK_PAAS_NETLOC}"]
)

CACHE_REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": CACHE_REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",  # 根据redis是单机还是集群模式, 修改Client class
            "PASSWORD": REDIS_PASSWORD,
            "SOCKET_CONNECT_TIMEOUT": 5,  # in seconds
            "SOCKET_TIMEOUT": 5,  # in seconds
        },
    }
}

# iam backend host
BK_IAM_HOST = os.environ.get("BK_IAM_V3_INNER_HOST", "http://bkiam.service.consul:9081")
