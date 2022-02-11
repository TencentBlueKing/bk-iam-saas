import base64
import json
import logging
import os
import random
import string

from backend.common.local import local


def get_app_service_url(app_code: str) -> str:
    """
    使用app_code获取服务地址

    兼容环境变量配置与v3 smart的服务发现
    """
    if app_code == os.getenv("BKPAAS_APP_ID") and "BK_IAM_APP_URL" in os.environ:
        return os.environ["BK_IAM_APP_URL"]

    if app_code == "bk_itsm" and "BK_ITSM_APP_URL" in os.environ:
        return os.environ["BK_ITSM_APP_URL"]

    value = os.getenv("BKPAAS_SERVICE_ADDRESSES_BKSAAS")
    if not value:
        return ""

    decoded_value = json.loads(base64.b64decode(value).decode("utf-8"))
    return {item["key"]["bk_app_code"]: item["value"]["prod"] for item in decoded_value}.get(app_code, "")


class RequestIDFilter(logging.Filter):
    def filter(self, record):
        record.request_id = local.request_id
        return True


def get_logging_config_dict(settings_module):
    log_class = "logging.handlers.RotatingFileHandler"
    log_level = settings_module.get("LOG_LEVEL", "INFO")

    is_local = settings_module.get("IS_LOCAL", False)
    if is_local:
        app_code = settings_module.get("APP_CODE", "")
        log_dir = os.path.join(os.path.dirname(settings_module.get("BASE_DIR", "/")), "logs", app_code)
        log_name_prefix = os.getenv("BKPAAS_LOG_NAME_PREFIX", app_code)
        logging_format = {
            "format": (
                "%(levelname)s [%(asctime)s] %(pathname)s "
                "%(lineno)d %(funcName)s %(process)d %(thread)d "
                "\n \t %(request_id)s\t%(message)s \n"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    else:
        log_dir = os.getenv("BKPAAS_APP_LOG_PATH", "/")
        rand_str = "".join(random.sample(string.ascii_letters + string.digits, 4))
        log_name_prefix = "%s-%s" % (os.getenv("BKPAAS_PROCESS_TYPE"), rand_str)

        logging_format = {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "fmt": (
                "%(levelname)s %(asctime)s %(pathname)s %(lineno)d "
                "%(funcName)s %(process)d %(thread)d %(request_id)s %(message)s"
            ),
        }
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "request_id_filter": {
                "()": RequestIDFilter,
            }
        },
        "formatters": {
            "verbose": logging_format,
            "simple": {"format": "%(levelname)s %(message)s"},
        },
        "handlers": {
            "null": {
                "level": "DEBUG",
                "class": "logging.NullHandler",
            },
            "console": {"level": "DEBUG", "class": "logging.StreamHandler", "formatter": "simple"},
            "root": {
                "class": log_class,
                "formatter": "verbose",
                "filename": os.path.join(log_dir, "%s-django.log" % log_name_prefix),
                "maxBytes": 1024 * 1024 * 10,
                "backupCount": 5,
                "filters": ["request_id_filter"],
            },
            "component": {
                "class": log_class,
                "formatter": "verbose",
                "filename": os.path.join(log_dir, "%s-component.log" % log_name_prefix),
                "maxBytes": 1024 * 1024 * 10,
                "backupCount": 5,
                "filters": ["request_id_filter"],
            },
            "mysql": {
                "class": log_class,
                "formatter": "verbose",
                "filename": os.path.join(log_dir, "%s-mysql.log" % log_name_prefix),
                "maxBytes": 1024 * 1024 * 10,
                "backupCount": 5,
                "filters": ["request_id_filter"],
            },
            "celery": {
                "class": log_class,
                "formatter": "verbose",
                "filename": os.path.join(log_dir, "%s-celery.log" % log_name_prefix),
                "maxBytes": 1024 * 1024 * 10,
                "backupCount": 5,
                "filters": ["request_id_filter"],
            },
            "organization": {
                "class": log_class,
                "formatter": "verbose",
                "filename": os.path.join(log_dir, "%s-json.log" % log_name_prefix),
                "maxBytes": 1024 * 1024 * 10,
                "backupCount": 5,
                "filters": ["request_id_filter"],
            },
            "permission": {
                "class": log_class,
                "formatter": "verbose",
                "filename": os.path.join(log_dir, "%s-json.log" % log_name_prefix),
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
                "level": log_level,
                "propagate": True,
            },
            "django.request": {
                "handlers": ["root"],
                "level": "ERROR",
                "propagate": True,
            },
            "django.db.backends": {
                "handlers": ["mysql"],
                "level": log_level,
                "propagate": True,
            },
            # the root logger ,用于整个project的logger
            "root": {
                "handlers": ["root"],
                "level": log_level,
                "propagate": True,
            },
            # 组件调用日志
            "component": {
                "handlers": ["component"],
                "level": log_level,
                "propagate": True,
            },
            "celery": {
                "handlers": ["celery"],
                "level": log_level,
                "propagate": True,
            },
            # 普通app日志
            "app": {
                "handlers": ["root"],
                "level": log_level,
                "propagate": True,
            },
            # 组织架构同步日志
            "organization": {
                "handlers": ["root" if is_local else "organization"],
                "level": log_level,
                "propagate": True,
            },
            # 授权相关的日志
            "permission": {
                "handlers": ["root" if is_local else "permission"],
                "level": log_level,
                "propagate": True,
            },
        },
    }


def get_broker_url() -> str:
    """
    celery broker url
    """
    if "RABBITMQ_HOST" in os.environ:
        return "amqp://{user}:{password}@{host}:{port}/{vhost}".format(
            user=os.getenv("RABBITMQ_USER"),
            password=os.getenv("RABBITMQ_PASSWORD"),
            host=os.getenv("RABBITMQ_HOST"),
            port=os.getenv("RABBITMQ_PORT"),
            vhost=os.getenv("RABBITMQ_VHOST"),
        )

    return os.getenv("BK_BROKER_URL")


def get_paas_v2_logging_config_dict(log_level):
    """
    日志V2对外版设置
    """
    app_code = os.environ.get("APP_ID")

    # 设置日志文件夹路径
    log_dir = os.path.join(os.path.join(os.getenv("BK_LOG_DIR", "/data/apps/logs/"), app_code))

    # 如果日志文件夹不存在则创建,日志文件存在则延用
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    return {
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
                "filename": os.path.join(log_dir, "component.log"),
                "maxBytes": 1024 * 1024 * 10,
                "backupCount": 5,
                "filters": ["request_id_filter"],
            },
            "celery": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "verbose",
                "filename": os.path.join(log_dir, "celery.log"),
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
                "filename": os.path.join(log_dir, "%s.log" % app_code),
                "maxBytes": 1024 * 1024 * 10,
                "backupCount": 5,
                "filters": ["request_id_filter"],
            },
            "wb_mysql": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "verbose",
                "filename": os.path.join(log_dir, "wb_mysql.log"),
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
                "level": log_level,
                "propagate": True,
            },
            "django.request": {
                "handlers": ["console"],
                "level": "ERROR",
                "propagate": True,
            },
            "django.db.backends": {
                "handlers": ["wb_mysql"],
                "level": log_level,
                "propagate": True,
            },
            "root": {
                "handlers": ["root"],
                "level": log_level,
                "propagate": True,
            },
            # V3新版使用的日志
            "celery": {
                "handlers": ["celery"],
                "level": log_level,
                "propagate": True,
            },
            "app": {
                "handlers": ["root"],
                "level": log_level,
                "propagate": True,
            },
            # 组织架构同步日志
            "organization": {
                "handlers": ["root"],
                "level": log_level,
                "propagate": True,
            },
            # 授权相关的日志
            "permission": {
                "handlers": ["root"],
                "level": log_level,
                "propagate": True,
            },
        },
    }
