"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云 - 权限中心 (BlueKing-IAM) available.
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
import ssl
import string
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from . import RequestIDFilter
from .default import BASE_DIR, BROKER_URL, env

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

if env.str("BKCI_DB_NAME", default="") and env.str("BKCI_DB_USERNAME", default=""):
    DATABASES["bkci"] = {
        "ENGINE": "django.db.backends.mysql",
        "NAME": env.str("BKCI_DB_NAME", default="bkci"),
        "USER": env.str("BKCI_DB_USERNAME", default="root"),
        "PASSWORD": env.str("BKCI_DB_PASSWORD", default=""),
        "HOST": env.str("BKCI_DB_HOST", default="localhost"),
        "PORT": env.int("BKCI_DB_PORT", default=3306),
    }

# Default MySQL TLS
MYSQL_TLS_ENABLED = env.bool("MYSQL_TLS_ENABLED", default=False)
MYSQL_TLS_CERT_CA_FILE = env.str("MYSQL_TLS_CERT_CA_FILE", default="")
MYSQL_TLS_CERT_FILE = env.str("MYSQL_TLS_CERT_FILE", default="")
MYSQL_TLS_CERT_KEY_FILE = env.str("MYSQL_TLS_CERT_KEY_FILE", default="")
MYSQL_TLS_CHECK_HOSTNAME = env.bool("MYSQL_TLS_CHECK_HOSTNAME", default=True)
if MYSQL_TLS_ENABLED:
    ssl_options = {"ca": MYSQL_TLS_CERT_CA_FILE, "check_hostname": MYSQL_TLS_CHECK_HOSTNAME}
    # mTLS
    if MYSQL_TLS_CERT_FILE and MYSQL_TLS_CERT_KEY_FILE:
        ssl_options["cert"] = MYSQL_TLS_CERT_FILE
        ssl_options["key"] = MYSQL_TLS_CERT_KEY_FILE

    if "OPTIONS" not in DATABASES["default"]:
        DATABASES["default"]["OPTIONS"] = {}

    DATABASES["default"]["OPTIONS"]["ssl"] = ssl_options

# Audit MySQL TLS
AUDIT_DB_TLS_ENABLED = env.bool("AUDIT_DB_TLS_ENABLED", default=MYSQL_TLS_ENABLED)
AUDIT_DB_TLS_CERT_CA_FILE = env.str("AUDIT_DB_TLS_CERT_CA_FILE", default=MYSQL_TLS_CERT_CA_FILE)
AUDIT_DB_TLS_CERT_FILE = env.str("AUDIT_DB_TLS_CERT_FILE", default=MYSQL_TLS_CERT_FILE)
AUDIT_DB_TLS_CERT_KEY_FILE = env.str("AUDIT_DB_TLS_CERT_KEY_FILE", default=MYSQL_TLS_CERT_KEY_FILE)
AUDIT_DB_TLS_CHECK_HOSTNAME = env.bool("AUDIT_DB_TLS_CHECK_HOSTNAME", default=MYSQL_TLS_CHECK_HOSTNAME)
if AUDIT_DB_TLS_ENABLED:
    ssl_options = {"ca": AUDIT_DB_TLS_CERT_CA_FILE, "check_hostname": AUDIT_DB_TLS_CHECK_HOSTNAME}
    # mTLS
    if AUDIT_DB_TLS_CERT_FILE and AUDIT_DB_TLS_CERT_KEY_FILE:
        ssl_options["cert"] = AUDIT_DB_TLS_CERT_FILE
        ssl_options["key"] = AUDIT_DB_TLS_CERT_KEY_FILE

    if "OPTIONS" not in DATABASES["default"]:
        DATABASES["audit"]["OPTIONS"] = {}

    DATABASES["audit"]["OPTIONS"]["ssl"] = ssl_options

# cache
REDIS_HOST = env.str("REDIS_HOST")
REDIS_PORT = env.int("REDIS_PORT", default=6379)
REDIS_PASSWORD = env.str("REDIS_PASSWORD", default="")
REDIS_DB = env.int("REDIS_DB", default=0)
REDIS_MAX_CONNECTIONS = env.int("REDIS_MAX_CONNECTIONS", default=100)
# redis tls
REDIS_TLS_ENABLED = env.bool("REDIS_TLS_ENABLED", default=False)
REDIS_TLS_CERT_CA_FILE = env.str("REDIS_TLS_CERT_CA_FILE", default="")
REDIS_TLS_CERT_FILE = env.str("REDIS_TLS_CERT_FILE", default="")
REDIS_TLS_CERT_KEY_FILE = env.str("REDIS_TLS_CERT_KEY_FILE", default="")
REDIS_TLS_CHECK_HOSTNAME = env.bool("REDIS_TLS_CHECK_HOSTNAME", default=True)
# ssl.CERT_NONE = 0 / ssl.CERT_OPTIONAL = 1 / ssl.CERT_REQUIRED = 2
REDIS_TLS_CERT_REQS = ssl.VerifyMode(env.int("REDIS_TLS_CERT_REQS", default=2))
# sentinel check
REDIS_USE_SENTINEL = env.bool("REDIS_USE_SENTINEL", False)
REDIS_SENTINEL_MASTER_NAME = env.str("REDIS_SENTINEL_MASTER_NAME", "mymaster")
REDIS_SENTINEL_PASSWORD = env.str("REDIS_SENTINEL_PASSWORD", "")
# env[REDIS_SENTINEL_ADDR] format: "host1:port1,host2:port2"
# REDIS_SENTINEL_ADDR value: ["host1:port1", "host2:port2"]
REDIS_SENTINEL_ADDR = env.list("REDIS_SENTINEL_ADDR", default=[])

CACHES = {
    # 默认缓存是本地内存，使用最近最少使用（LRU）的淘汰策略，使用 pickle 序列化数据
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "",  # 多个本地内存缓存时才需要设置
        "TIMEOUT": 60 * 30,  # 避免使用时忘记设置过期时间，可设置个长时间的默认值，30 分钟，特殊值 0 表示立刻过期，实际上就是不缓存
        "KEY_PREFIX": "bk_iam",  # 缓存的 Key 的前缀
        # "VERSION": 1,  # 用于避免同一个缓存 Key 在不同 SaaS 版本之间存在差异导致读取的值非期望的，由于内存缓存每次部署都会重置，所以不需要设置
        # "KEY_FUNCTION": "",  # Key 的生成函数，默认是 key_prefix:version:key
        # 内存缓存特有参数
        "OPTIONS": {
            "MAX_ENTRIES": 1000,  # 支持缓存的 key 最多数量，越大将会占用更多内存
            "CULL_FREQUENCY": 3,  # 当达到 MAX_ENTRIES 时被淘汰的部分条目，淘汰率是 1 / CULL_FREQUENCY，默认淘汰 1/3的缓存key
        },
    },
    "redis": {
        "BACKEND": "django_redis.cache.RedisCache",
        # 若需要支持主从配置，则 LOCATION 为 List[master_url, slave_url]
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
        "TIMEOUT": 60 * 30,  # 避免使用时忘记设置过期时间，可设置个长时间的默认值，30 分钟，特殊值 0 表示立刻过期，实际上就是不缓存
        "KEY_PREFIX": "bk_iam",  # 缓存的 Key 的前缀
        "VERSION": 1,  # 避免同一个缓存 Key 在不同 SaaS 版本之间存在差异导致读取的值非期望的
        # "KEY_FUNCTION": "",  # Key 的生成函数，默认是 key_prefix:version:key
        "OPTIONS": {
            # Sentinel 模式 django_redis.client.SentinelClient (django-redis>=5.0.0)
            # 单实例模式 django_redis.client.DefaultClient
            # Note: django_redis.client.HerdClient 并不是 RedisCluster 的客户端，
            #       而是削峰模式，通过分散缓存失效时间来减少同时构建缓存带来的负载峰值
            "CLIENT_CLASS": "django_redis.client.DefaultClient",  # 根据 redis 是单机还是集群模式，修改 Client class
            "PASSWORD": REDIS_PASSWORD,
            "SOCKET_CONNECT_TIMEOUT": 5,  # socket 建立连接超时设置，单位秒
            "SOCKET_TIMEOUT": 5,  # 连接建立后的读写操作超时设置，单位秒
            "IGNORE_EXCEPTIONS": True,  # redis 只作为缓存使用，触发异常不能影响正常逻辑，可能只是稍微慢点而已
            # 默认使用 pickle 序列化数据，可选序列化方式有：pickle、json、msgpack
            # "SERIALIZER": "django_redis.serializers.pickle.PickleSerializer"
            # Redis 连接池配置
            "CONNECTION_POOL_KWARGS": {
                # redis-py 默认不会关闭连接，尽可能重用连接，但可能会造成连接过多，导致 Redis 无法服务，所以需要设置最大值连接数
                "max_connections": REDIS_MAX_CONNECTIONS
            },
        },
    },
}

# 当 Redis Cache 使用 IGNORE_EXCEPTIONS 时，设置指定的 logger 输出异常
DJANGO_REDIS_LOGGER = "app"

# redis tls enabled
if REDIS_TLS_ENABLED:
    CACHES["redis"]["LOCATION"] = f"rediss://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    CACHES["redis"]["OPTIONS"]["CONNECTION_POOL_KWARGS"]["ssl_cert_reqs"] = REDIS_TLS_CERT_REQS
    CACHES["redis"]["OPTIONS"]["CONNECTION_POOL_KWARGS"]["ssl_ca_certs"] = REDIS_TLS_CERT_CA_FILE
    CACHES["redis"]["OPTIONS"]["CONNECTION_POOL_KWARGS"]["ssl_check_hostname"] = REDIS_TLS_CHECK_HOSTNAME
    # mTLS
    if REDIS_TLS_CERT_FILE and REDIS_TLS_CERT_KEY_FILE:
        CACHES["redis"]["OPTIONS"]["CONNECTION_POOL_KWARGS"]["ssl_certfile"] = REDIS_TLS_CERT_FILE
        CACHES["redis"]["OPTIONS"]["CONNECTION_POOL_KWARGS"]["ssl_keyfile"] = REDIS_TLS_CERT_KEY_FILE

# redis sentinel
if REDIS_USE_SENTINEL:
    # Enable the alternate connection factory.
    DJANGO_REDIS_CONNECTION_FACTORY = "django_redis.pool.SentinelConnectionFactory"
    CACHES["redis"]["LOCATION"] = f"redis://{REDIS_SENTINEL_MASTER_NAME}/{REDIS_DB}"
    CACHES["redis"]["OPTIONS"]["CLIENT_CLASS"] = "django_redis.client.SentinelClient"
    # Sentinels which are passed directly to redis Sentinel.
    # parse sentinel address from ["host1:port1", "host2:port2"] to [("host1", port1), ("host2", port2)]
    CACHES["redis"]["OPTIONS"]["SENTINELS"] = [tuple(addr.split(":")) for addr in REDIS_SENTINEL_ADDR]
    CACHES["redis"]["OPTIONS"]["SENTINEL_KWARGS"] = {"password": REDIS_SENTINEL_PASSWORD, "socket_timeout": 5}
    CACHES["redis"]["OPTIONS"]["CONNECTION_POOL_CLASS"] = "redis.sentinel.SentinelConnectionPool"

    # redis sentinel tls
    if REDIS_TLS_ENABLED:
        CACHES["redis"]["OPTIONS"]["CONNECTION_POOL_KWARGS"]["ssl"] = True
        CACHES["redis"]["OPTIONS"]["SENTINEL_KWARGS"]["ssl"] = True
        CACHES["redis"]["OPTIONS"]["SENTINEL_KWARGS"]["ssl_cert_reqs"] = REDIS_TLS_CERT_REQS
        CACHES["redis"]["OPTIONS"]["SENTINEL_KWARGS"]["ssl_ca_certs"] = REDIS_TLS_CERT_CA_FILE
        CACHES["redis"]["OPTIONS"]["SENTINEL_KWARGS"]["ssl_check_hostname"] = REDIS_TLS_CHECK_HOSTNAME
        # mTLS
        if REDIS_TLS_CERT_FILE and REDIS_TLS_CERT_KEY_FILE:
            CACHES["redis"]["OPTIONS"]["SENTINEL_KWARGS"]["ssl_certfile"] = REDIS_TLS_CERT_FILE
            CACHES["redis"]["OPTIONS"]["SENTINEL_KWARGS"]["ssl_keyfile"] = REDIS_TLS_CERT_KEY_FILE

# use Redis as default celery broker
if not BROKER_URL:
    BROKER_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    if REDIS_TLS_ENABLED:
        BROKER_URL = f"rediss://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
        BROKER_USE_SSL = {
            "ssl_cert_reqs": REDIS_TLS_CERT_REQS,
            "ssl_ca_certs": REDIS_TLS_CERT_CA_FILE,
            "ssl_check_hostname": REDIS_TLS_CHECK_HOSTNAME,
        }
        # mTLS
        if REDIS_TLS_CERT_FILE and REDIS_TLS_CERT_KEY_FILE:
            BROKER_USE_SSL["ssl_certfile"] = REDIS_TLS_CERT_FILE
            BROKER_USE_SSL["ssl_keyfile"] = REDIS_TLS_CERT_KEY_FILE

    # Sentinel Redis as default celery broker
    if REDIS_USE_SENTINEL:
        BROKER_URL = ";".join([f"sentinel://:{REDIS_PASSWORD}@{addr}/{REDIS_DB}" for addr in REDIS_SENTINEL_ADDR])
        BROKER_TRANSPORT_OPTIONS = {
            "master_name": REDIS_SENTINEL_MASTER_NAME,
            "sentinel_kwargs": {"password": REDIS_SENTINEL_PASSWORD},
            "socket_timeout": 5,
            "socket_connect_timeout": 5,
            "socket_keepalive": True,
        }
        if REDIS_TLS_ENABLED:
            BROKER_TRANSPORT_OPTIONS["sentinel_kwargs"]["ssl"] = True
            BROKER_TRANSPORT_OPTIONS["sentinel_kwargs"]["ssl_cert_reqs"] = REDIS_TLS_CERT_REQS
            BROKER_TRANSPORT_OPTIONS["sentinel_kwargs"]["ssl_ca_certs"] = REDIS_TLS_CERT_CA_FILE
            BROKER_TRANSPORT_OPTIONS["sentinel_kwargs"]["ssl_check_hostname"] = REDIS_TLS_CHECK_HOSTNAME
            # mTLS
            if REDIS_TLS_CERT_FILE and REDIS_TLS_CERT_KEY_FILE:
                BROKER_TRANSPORT_OPTIONS["sentinel_kwargs"]["ssl_certfile"] = REDIS_TLS_CERT_FILE
                BROKER_TRANSPORT_OPTIONS["sentinel_kwargs"]["ssl_keyfile"] = REDIS_TLS_CERT_KEY_FILE

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
# 注意：Cookie Domain 是不支持端口的
SESSION_COOKIE_DOMAIN = _BK_PAAS_HOSTNAME
CSRF_COOKIE_DOMAIN = SESSION_COOKIE_DOMAIN
_APP_URL_MD5_16BIT = hashlib.md5(APP_URL.encode("utf-8")).hexdigest()[8:-8]
CSRF_COOKIE_NAME = f"bkiam_csrftoken_{_APP_URL_MD5_16BIT}"
# 对于特殊端口，带端口和不带端口都得添加，其他只需要添加默认原生的即可
CSRF_TRUSTED_ORIGINS = (
    [f"{_BK_PAAS_SCHEME}://{_BK_PAAS_HOSTNAME}", f"{_BK_PAAS_SCHEME}://{_BK_PAAS_NETLOC}"]
    if _BK_PAAS_IS_SPECIAL_PORT
    else [f"{_BK_PAAS_SCHEME}://{_BK_PAAS_NETLOC}"]
)
# cors
CORS_ALLOW_CREDENTIALS = True  # 在 response 添加 Access-Control-Allow-Credentials, 即允许跨域使用 cookies
CORS_ORIGIN_WHITELIST = CSRF_TRUSTED_ORIGINS

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/
# 站点 URL
SITE_URL = env.str("BKPAAS_SUB_PATH", default="/")
FORCE_SCRIPT_NAME = SITE_URL
STATIC_URL = env.str("BKPAAS_STATIC_URL", default=SITE_URL + "staticfiles/")
AJAX_URL_PREFIX = SITE_URL + "api/v1"

# 日志等级，高于或等于该等级的日志才会被记录
LOG_LEVEL = env.str("BKAPP_LOG_LEVEL", default=None) or env.str("LOG_LEVEL", default="ERROR")
# 用于存放日志文件的目录，默认值为空，表示不使用任何文件，所有日志直接输出到控制台。
# 可配置为有效目录，支持相对或绝对地址，比如："logs" 或 "/var/lib/app_logs/"。
# 配置本选项后，原有的控制台日志输出将关闭。
LOGGING_DIRECTORY = env.str("BKPAAS_APP_LOG_PATH", default=None) or env.str("LOGGING_DIRECTORY", default=None)
# 日志文件格式，可选值为：json/text
LOGGING_FILE_FORMAT = env.str("LOGGING_FILE_FORMAT", default="json")

if LOGGING_DIRECTORY is None:
    logging_to_console = True
    logging_directory = None
else:
    logging_to_console = False
    # The dir allows both absolute and relative path, when it's relative, combine
    # the value with project's base directory
    logging_directory = Path(BASE_DIR) / Path(LOGGING_DIRECTORY)
    logging_directory.mkdir(exist_ok=True)

# 是否总是打印日志到控制台，默认关闭
LOGGING_ALWAYS_CONSOLE = env.bool("LOGGING_ALWAYS_CONSOLE", default=False)
if LOGGING_ALWAYS_CONSOLE:
    logging_to_console = True


def build_logging_config(log_level: str, to_console: bool, file_directory: Optional[Path], file_format: str) -> Dict:
    """Build the global logging config dict.

    :param log_level: The log level.
    :param to_console: If True, output the logs to the console.
    :param file_directory: If the value is not None, output the logs to the given directory.
    :param file_format: The format of the logging file, "json" or "text".
    :return: The logging config dict.
    """

    def _build_file_handler(log_path: Path, filename: str, format: str) -> Dict:
        if format not in ("json", "text"):
            raise ValueError(f"Invalid file_format: {file_format}")
        formatter = "verbose_json" if format == "json" else "verbose"
        return {
            "class": "concurrent_log_handler.ConcurrentRotatingFileHandler",
            "level": log_level,
            "formatter": formatter,
            "filters": ["request_id_filter"],
            "filename": str(log_path / filename),
            # Set max file size to 100MB
            "maxBytes": 100 * 1024 * 1024,
            "backupCount": 5,
        }

    handlers_config: Dict[str, Any] = {
        "null": {"level": log_level, "class": "logging.NullHandler"},
        "console": {
            "level": log_level,
            "class": "logging.StreamHandler",
            "formatter": "verbose",
            "filters": ["request_id_filter"],
        },
    }
    # 生成指定 Logger 对应的 Handlers
    logger_handlers_map: Dict[str, List[str]] = {}
    for logger_name in ["root", "component", "celery", "organization"]:
        handlers = []

        if to_console:
            handlers.append("console")

        if file_directory:
            # 生成 logger 对应日志文件的 Handler
            handlers_config[logger_name] = _build_file_handler(
                file_directory, f"{logger_name}-{file_format}.log", file_format
            )
            handlers.append(logger_name)

        logger_handlers_map[logger_name] = handlers

    # bk_audit 特殊 Handler
    handlers_config["bk_audit"] = {"class": "logging.NullHandler"}
    if file_directory:
        handlers_config["bk_audit"] = {
            "class": "concurrent_log_handler.ConcurrentRotatingFileHandler",
            "formatter": "bk_audit",
            "filename": str(file_directory / "audit.log"),
            "maxBytes": 1024 * 1024 * 10,
            "backupCount": 5,
        }

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "request_id_filter": {"()": RequestIDFilter},
        },
        "formatters": {
            "verbose": {
                "format": (
                    "%(name)s %(levelname)s [%(asctime)s] %(pathname)s %(lineno)d %(funcName)s %(process)d %(thread)d "
                    "\n \t%(request_id)s\t%(message)s \n"
                ),
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "verbose_json": {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "fmt": (
                    "%(name)s %(levelname)s %(asctime)s %(pathname)s %(lineno)d "
                    "%(funcName)s %(process)d %(thread)d %(request_id)s %(message)s"
                ),
            },
            "simple": {"format": "%(name)s %(levelname)s %(message)s"},
            "bk_audit": {"format": "%(message)s"},
        },
        "handlers": handlers_config,
        # the root logger, 用于整个项目的默认 logger
        "root": {"handlers": logger_handlers_map["root"], "level": log_level, "propagate": False},
        "loggers": {
            "django": {"handlers": ["null"], "level": "INFO", "propagate": True},
            "django.server": {"handlers": ["console"], "level": log_level, "propagate": False},
            "django.request": {"handlers": logger_handlers_map["root"], "level": log_level, "propagate": False},
            # 除 root 外的其他指定 Logger
            **{
                logger_name: {"handlers": handlers, "level": log_level, "propagate": False}
                for logger_name, handlers in logger_handlers_map.items()
                if logger_name != "root"
            },
            # 普通 app 日志
            "app": {"handlers": logger_handlers_map["root"], "level": LOG_LEVEL, "propagate": True},
            # 审计日志文件
            "bk_audit": {"handlers": ["bk_audit"], "level": "INFO", "propagate": True},
        },
    }


LOGGING = build_logging_config(LOG_LEVEL, logging_to_console, logging_directory, LOGGING_FILE_FORMAT)

APP_API_URL = APP_URL  # 前后端分离架构下，APP_URL 与 APP_API_URL 不一样

BK_COMPONENT_API_URL = env.str("BK_COMPONENT_API_URL", default="")
BK_COMPONENT_INNER_API_URL = env.str("BK_COMPONENT_INNER_API_URL", default=BK_COMPONENT_API_URL)

BK_ITSM_APP_URL = env.str("BK_ITSM_APP_URL", default="")

LOGIN_SERVICE_URL = env.str("BK_LOGIN_URL", default="/")
LOGIN_SERVICE_PLAIN_URL = LOGIN_SERVICE_URL + "plain/"

# 蓝鲸 PASS 平台 URL
BK_PAAS_HOST = env.str("BK_PAAS_HOST", default=env.str("BKPAAS_URL", default=""))

# 用于 用户认证、用户信息获取 的蓝鲸主机
BK_PAAS_INNER_HOST = env.str("BK_PAAS2_URL", default=env.str("BK_PAAS_INNER_HOST", default=BK_PAAS_HOST))

# 对接审计中心相关配置
BK_IAM_RESOURCE_API_HOST = env.str("BK_IAM_RESOURCE_API_HOST", default=APP_URL)
