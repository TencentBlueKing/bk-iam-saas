from __future__ import absolute_import

"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-权限中心(BlueKing-IAM) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import os

import environ
from celery.schedules import crontab

# environ
env = environ.Env()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# load environment variables from .env file
environ.Env.read_env()

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["*"]

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "backend.account",
    "rest_framework",
    "django_filters",
    "drf_yasg",
    "corsheaders",
    "mptt",
    "django_prometheus",
    "django_celery_beat",
    "apigw_manager.apigw",
    "iam.contrib.iam_migration",
    "backend.common",
    "backend.long_task",
    "backend.audit",
    "backend.debug",
    "backend.iam",
    "backend.metrics",
    "backend.apps.system",
    "backend.apps.action",
    "backend.apps.policy",
    "backend.apps.application",
    "backend.apps.resource",
    "backend.apps.approval",
    "backend.apps.group",
    "backend.apps.subject",
    "backend.apps.template",
    "backend.apps.organization",
    "backend.apps.role",
    "backend.apps.user",
    "backend.apps.model_builder",
    "backend.apps.handover",
    "backend.apps.mgmt",
    "backend.apps.temporary_policy",
    "backend.api.authorization",
    "backend.api.admin",
    "backend.api.management",
    "backend.api.bkci",
]

# 登录中间件
_LOGIN_MIDDLEWARE = env.str("BKAPP_LOGIN_MIDDLEWARE", default="backend.account.middlewares.LoginMiddleware")

MIDDLEWARE = [
    "backend.common.middlewares.CustomProfilerMiddleware",
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "backend.common.middlewares.RequestProvider",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    _LOGIN_MIDDLEWARE,
    "backend.account.middlewares.TimezoneMiddleware",
    "backend.account.middlewares.RoleAuthenticationMiddleware",
    "django_prometheus.middleware.PrometheusAfterMiddleware",
    "backend.common.middlewares.LanguageMiddleware",
    "corsheaders.middleware.CorsMiddleware",
]

ROOT_URLCONF = "urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "resources/templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# django 3.2 add
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# DB router
DATABASE_ROUTERS = ["backend.audit.routers.AuditRouter"]

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators
AUTHENTICATION_BACKENDS = (env.str("BKAPP_AUTHENTICATION_BACKEND", default="backend.account.backends.TokenBackend"),)
AUTH_USER_MODEL = "account.User"
AUTH_PASSWORD_VALIDATORS = []

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/
LANGUAGE_CODE = "zh-hans"
LANGUAGE_COOKIE_NAME = "blueking_language"
LANGUAGE_COOKIE_PATH = "/"
TIME_ZONE = "Asia/Shanghai"
USE_I18N = True
USE_L10N = True
USE_TZ = True
LOCALE_PATHS = (os.path.join(BASE_DIR, "resources/locale"),)

# static
STATIC_VERSION = "1.0"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
WHITENOISE_STATIC_PREFIX = "/staticfiles/"

# cookie
SESSION_COOKIE_NAME = "bkiam_sessionid"
SESSION_COOKIE_AGE = 60 * 60 * 24  # 1天

# cors
CORS_ALLOW_CREDENTIALS = True  # 在 response 添加 Access-Control-Allow-Credentials, 即允许跨域使用 cookies

# rest_framework
REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "backend.common.exception_handler.exception_handler",
    "DEFAULT_PAGINATION_CLASS": "backend.common.pagination.CompatiblePagination",
    "PAGE_SIZE": 10,
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
    "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework.authentication.SessionAuthentication",),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_RENDERER_CLASSES": ("backend.common.renderers.BKAPIRenderer",),
    "DATETIME_FORMAT": "%Y-%m-%d %H:%M:%S",
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
}

# Swagger 文档统一配置
SWAGGER_SETTINGS = {
    "DEFAULT_AUTO_SCHEMA_CLASS": "backend.common.swagger.ResponseSwaggerAutoSchema",
}

# CELERY 开关，使用时请改为 True，否则请保持为False。启动方式为以下两行命令：
# worker: python manage.py celery worker -l info
# beat: python manage.py celery beat -l info
IS_USE_CELERY = True
# 连接 BROKER 超时时间
BROKER_CONNECTION_TIMEOUT = 1  # 单位秒
# CELERY与RabbitMQ增加60秒心跳设置项
BROKER_HEARTBEAT = 60
# CELERY 并发数，默认为 2，可以通过环境变量或者 Procfile 设置
CELERYD_CONCURRENCY = env.int("BK_CELERYD_CONCURRENCY", default=2)
# 与周期任务配置的定时相关UTC
CELERY_ENABLE_UTC = False
# 周期任务beat生产者来源
CELERYBEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
# Celery队列名称
CELERY_DEFAULT_QUEUE = "bk_iam"
# close celery hijack root logger
CELERYD_HIJACK_ROOT_LOGGER = False
# disable remote control
CELERY_ENABLE_REMOTE_CONTROL = False
# Celery 消息序列化
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
# CELERY 配置，申明任务的文件路径，即包含有 @task 装饰器的函数文件
CELERY_IMPORTS = (
    "backend.apps.organization.tasks",
    "backend.apps.role.tasks",
    "backend.apps.application.tasks",
    "backend.apps.user.tasks",
    "backend.apps.group.tasks",
    "backend.apps.action.tasks",
    "backend.apps.policy.tasks",
    "backend.audit.tasks",
    "backend.long_task.tasks",
    "backend.apps.temporary_policy.tasks",
    "backend.api.bkci.tasks",
)
CELERYBEAT_SCHEDULE = {
    "periodic_sync_organization": {
        "task": "backend.apps.organization.tasks.sync_organization",
        "schedule": crontab(minute=0, hour=0),  # 每天凌晨执行
    },
    "periodic_sync_new_users": {
        "task": "backend.apps.organization.tasks.sync_new_users",
        "schedule": crontab(),  # 每1分钟执行一次
    },
    "periodic_sync_system_manager": {
        "task": "backend.apps.role.tasks.sync_system_manager",
        "schedule": crontab(minute="*/5"),  # 每5分钟执行一次
    },
    "periodic_check_or_update_application_status": {
        "task": "backend.apps.application.tasks.check_or_update_application_status",
        "schedule": crontab(minute="*/30"),  # 每30分钟执行一次
    },
    "periodic_user_group_policy_expire_remind": {
        "task": "backend.apps.user.tasks.user_group_policy_expire_remind",
        "schedule": crontab(minute=0, hour=11),  # 每天早上11时执行
    },
    "periodic_role_group_expire_remind": {
        "task": "backend.apps.role.tasks.role_group_expire_remind",
        "schedule": crontab(minute=0, hour=11),  # 每天早上11时执行
    },
    "periodic_user_expired_policy_cleanup": {
        "task": "backend.apps.user.tasks.user_cleanup_expired_policy",
        "schedule": crontab(minute=0, hour=2),  # 每天凌晨2时执行
    },
    "periodic_group_expired_member_cleanup": {
        "task": "backend.apps.group.tasks.group_cleanup_expired_member",
        "schedule": crontab(minute=0, hour=2),  # 每天凌晨0时执行
    },
    "periodic_pre_create_audit_model": {
        "task": "backend.audit.tasks.pre_create_audit_model",
        "schedule": crontab(0, 0, day_of_month="25"),  # 每月25号执行
    },
    "periodic_generate_action_aggregate": {
        "task": "backend.apps.action.tasks.generate_action_aggregate",
        "schedule": crontab(minute=0, hour="*"),  # 每小时执行
    },
    "periodic_execute_model_change_event": {
        "task": "backend.apps.policy.tasks.execute_model_change_event",
        "schedule": crontab(minute="*/30"),  # 每30分钟执行一次
    },
    "periodic_cleanup_finished_model_change_event": {
        "task": "backend.apps.policy.tasks.cleanup_finished_model_change_event",
        "schedule": crontab(minute=0, hour=1),  # 每天凌晨1时执行
    },
    "periodic_retry_long_task": {
        "task": "backend.long_task.tasks.retry_long_task",
        "schedule": crontab(minute="*/30"),  # 每30分钟执行一次
    },
    "periodic_delete_unreferenced_expressions": {
        "task": "backend.apps.policy.tasks.delete_unreferenced_expressions",
        "schedule": crontab(minute=0, hour=4),  # 每天凌晨4时执行
    },
    "periodic_clean_expired_temporary_policies": {
        "task": "backend.apps.temporary_policy.tasks.clean_expired_temporary_policies",
        "schedule": crontab(minute=0, hour="*"),  # 每小时执行
    },
    "check_user_permission_clean_task": {
        "task": "backend.apps.user.tasks.check_user_permission_clean_task",
        "schedule": crontab(minute=0, hour="*"),  # 每小时执行
    },
    "clean_user_permission_clean_record": {
        "task": "backend.apps.user.tasks.clean_user_permission_clean_record",
        "schedule": crontab(minute=0, hour=5),  # 每天凌晨5时执行
    },
}

# 是否开启初始化分级管理员
ENABLE_INIT_GRADE_MANAGER = env.bool("BKAPP_ENABLE_INIT_GRADE_MANAGER", default=False)
if ENABLE_INIT_GRADE_MANAGER:
    CELERYBEAT_SCHEDULE["init_biz_grade_manager"] = {
        "task": "backend.apps.role.tasks.InitBizGradeManagerTask",
        "schedule": crontab(minute="*/2"),  # 每2分钟执行一次
    }

# 是否开启初始化BCS一级/二级管理员
ENABLE_INIT_BCS_PROJECT_MANAGER = env.bool("BKAPP_ENABLE_INIT_BCS_PROJECT_MANAGER", default=False)
if ENABLE_INIT_BCS_PROJECT_MANAGER:
    CELERYBEAT_SCHEDULE["init_bcs_manager"] = {
        "task": "backend.apps.role.tasks.InitBcsProjectManagerTask",
        "schedule": crontab(minute="*/2"),  # 每2分钟执行一次
    }

# 环境变量中有rabbitmq时使用rabbitmq, 没有时使用BK_BROKER_URL
# V3 Smart可能会配RABBITMQ_HOST或者BK_BROKER_URL
# V2 Smart只有BK_BROKER_URL
if "RABBITMQ_HOST" in env:
    BROKER_URL = "amqp://{user}:{password}@{host}:{port}/{vhost}".format(
        user=env.str("RABBITMQ_USER"),
        password=env.str("RABBITMQ_PASSWORD"),
        host=env.str("RABBITMQ_HOST"),
        port=env.str("RABBITMQ_PORT"),
        vhost=env.str("RABBITMQ_VHOST"),
    )
else:
    BROKER_URL = env.str("BK_BROKER_URL", default="")

# tracing: sentry support
SENTRY_DSN = env.str("SENTRY_DSN", default="")
# tracing: otel 相关配置
# if enable, default false
ENABLE_OTEL_TRACE = env.bool("BKAPP_ENABLE_OTEL_TRACE", default=False)
BKAPP_OTEL_SERVICE_NAME = env.str("BKAPP_OTEL_SERVICE_NAME", default="bk-iam-saas")
BKAPP_OTEL_SAMPLER = env.str("BKAPP_OTEL_SAMPLER", default="always_on")
BKAPP_OTEL_GRPC_HOST = env.str("BKAPP_OTEL_GRPC_HOST", default="")
BKAPP_OTEL_DATA_TOKEN = env("BKAPP_OTEL_DATA_TOKEN", default="")
BKAPP_OTEL_INSTRUMENT_DB_API = env.bool("BKAPP_OTEL_INSTRUMENT_DB_API", default=False)
if ENABLE_OTEL_TRACE or SENTRY_DSN:
    INSTALLED_APPS += ("backend.tracing",)

# debug trace的过期时间
MAX_DEBUG_TRACE_TTL = 7 * 24 * 60 * 60  # 7天
# debug trace的最大数量
MAX_DEBUG_TRACE_COUNT = 1000

# profile record
ENABLE_PYINSTRUMENT = env.bool("BKAPP_ENABLE_PYINSTRUMENT", default=False)  # 需要开启时则配置环境变量
PYINSTRUMENT_PROFILE_DIR = os.path.join(BASE_DIR, "profiles")


# ---------------
# app 自定义配置
# ---------------
# 初始化管理员列表，列表中的人员将拥有预发布环境和正式环境的管理员权限
# 注意：请在首次提测和上线前修改，之后的修改将不会生效
INIT_SUPERUSER = []

# version log
VERSION_LOG_MD_FILES_DIR = os.path.join(BASE_DIR, "resources/version_log")

# iam host
BK_IAM_HOST = env.str("BK_IAM_V3_INNER_HOST", default="http://bkiam.service.consul:9081")
BK_IAM_HOST_TYPE = env.str("BKAPP_IAM_HOST_TYPE", default="direct")  # direct/apigateway

# iam engine host
BK_IAM_ENGINE_HOST = env.str("BKAPP_IAM_ENGINE_HOST", default="")
BK_IAM_ENGINE_HOST_TYPE = env.str("BKAPP_IAM_ENGINE_HOST_TYPE", default="direct")  # direct/apigateway

# authorization limit
# 授权对象授权用户组, 模板的最大限制
SUBJECT_AUTHORIZATION_LIMIT = {
    # -------- 用户 ---------
    # 用户能加入的分级管理员的最大数量
    "subject_grade_manager_limit": env.int("BKAPP_SUBJECT_GRADE_MANAGER_LIMIT", default=500),
    # -------- 用户组 ---------
    # 用户组能加入同一个系统的权限模板的最大数量
    "default_subject_system_template_limit": env.int("BKAPP_DEFAULT_SUBJECT_SYSTEM_TEMPLATE_LIMIT", default=10),
    "subject_system_template_limit": {
        # key: system_id, value: int
    },  # 系统可自定义配置的 用户组能加入同一个系统的权限模板的最大数量
    # 用户组成员最大数量
    "group_member_limit": env.int("BKAPP_GROUP_MEMBER_LIMIT", default=500),
    # 用户组单次授权模板数
    "group_auth_template_once_limit": env.int("BKAPP_GROUP_AUTH_TEMPLATE_ONCE_LIMIT", default=10),
    # 用户组单次授权的系统数
    "group_auth_system_once_limit": env.int("BKAPP_GROUP_AUTH_SYSTEM_ONCE_LIMIT", default=10),
    # -------- 分级管理员 ---------
    # 一个分级管理员可创建的用户组个数
    "grade_manager_group_limit": env.int("BKAPP_GRADE_MANAGER_GROUP_LIMIT", default=100),
    # 一个分级管理员可添加的成员个数
    "grade_manager_member_limit": env.int("BKAPP_GRADE_MANAGER_MEMBER_LIMIT", default=100),
    # 默认每个系统可创建的分级管理数量
    "default_grade_manager_of_system_limit": env.int("BKAPP_DEFAULT_GRADE_MANAGER_OF_SYSTEM_LIMIT", default=500),
    # 可配置单独指定某些系统可创建的分级管理员数量 其值的格式为：system_id1:number1,system_id2:number2,...
    "grade_manager_of_specified_systems_limit": env.str(
        "BKAPP_GRADE_MANAGER_OF_SPECIFIED_SYSTEMS_LIMIT", default="bk_ci_rbac:30000"
    ),
}
# 授权的实例最大数量限制
AUTHORIZATION_INSTANCE_LIMIT = env.int("BKAPP_AUTHORIZATION_INSTANCE_LIMIT", default=200)
# 策略中实例数量的最大限制
SINGLE_POLICY_MAX_INSTANCES_LIMIT = env.int("BKAPP_SINGLE_POLICY_MAX_INSTANCES_LIMIT", default=10000)
# 一次申请策略中中新增实例数量限制
APPLY_POLICY_ADD_INSTANCES_LIMIT = env.int("BKAPP_APPLY_POLICY_ADD_INSTANCES_LIMIT", default=20)
# 临时权限一个操作最大数量
TEMPORARY_POLICY_LIMIT = env.int("BKAPP_TEMPORARY_POLICY_LIMIT", default=10)
# 最长已过期权限删除期限
MAX_EXPIRED_POLICY_DELETE_TIME = 365 * 24 * 60 * 60  # 1年
# 最长已过期临时权限期限
MAX_EXPIRED_TEMPORARY_POLICY_DELETE_TIME = 3 * 24 * 60 * 60  # 3 Days
# 接入系统的资源实例ID最大长度，默认36（已存在长度为36的数据）
MAX_LENGTH_OF_RESOURCE_ID = env.int("BKAPP_MAX_LENGTH_OF_RESOURCE_ID", default=36)

# 前端页面功能开关
ENABLE_FRONT_END_FEATURES = {
    "enable_model_build": env.bool("BKAPP_ENABLE_FRONT_END_MODEL_BUILD", default=False),
    "enable_permission_handover": env.bool("BKAPP_ENABLE_FRONT_END_PERMISSION_HANDOVER", default=True),
    "enable_temporary_policy": env.bool("BKAPP_ENABLE_FRONT_END_TEMPORARY_POLICY", default=False),
}

# Open API接入APIGW后，需要对APIGW请求来源认证，使用公钥解开jwt
BK_APIGW_PUBLIC_KEY = env.str("BKAPP_APIGW_PUBLIC_KEY", default="")

# apigateway 相关配置
# NOTE: it sdk will read settings.APP_CODE and settings.APP_SECRET, so you should set it
BK_APIGW_NAME = "bk-iam"
BK_API_URL_TMPL = env.str("BK_API_URL_TMPL", default="")
BK_IAM_BACKEND_SVC = env.str("BK_IAM_BACKEND_SVC", default="bkiam-web")
BK_IAM_SAAS_API_SVC = env.str("BK_IAM_SAAS_API_SVC", default="bkiam-saas-api")
BK_IAM_ENGINE_SVC = env.str("BK_IAM_ENGINE_SVC", default="bkiam-search-engine")
BK_APIGW_RESOURCE_DOCS_BASE_DIR = os.path.join(BASE_DIR, "resources/apigateway/docs/")

# Requests pool config
REQUESTS_POOL_CONNECTIONS = env.int("REQUESTS_POOL_CONNECTIONS", default=20)
REQUESTS_POOL_MAXSIZE = env.int("REQUESTS_POOL_MAXSIZE", default=20)

# Init Grade Manger system list
INIT_GRADE_MANAGER_SYSTEM_LIST = env.list(
    "INIT_GRADE_MANAGER_SYSTEM_LIST",
    default=["bk_job", "bk_cmdb", "bk_monitorv3", "bk_log_search", "bk_sops", "bk_nodeman", "bk_gsekit"],
)

# disable display systems
HIDDEN_SYSTEM_LIST = env.list("BKAPP_HIDDEN_SYSTEM_LIST", default=["bk_iam", "bk_ci_rbac"])


# 对接审计中心相关配置, 包括注册权限模型到权限中心后台的配置
BK_IAM_SYSTEM_ID = "bk_iam"
if BK_IAM_HOST_TYPE == "direct":
    BK_IAM_USE_APIGATEWAY = False
    BK_IAM_INNER_HOST = BK_IAM_HOST
elif BK_IAM_HOST_TYPE == "apigateway":
    BK_IAM_USE_APIGATEWAY = True
    BK_IAM_APIGATEWAY_URL = BK_IAM_HOST
BK_IAM_MIGRATION_APP_NAME = "iam"
BK_IAM_MIGRATION_JSON_PATH = "resources/iam/"


# IAM metric 接口密码
BK_IAM_METRIC_TOKEN = env.str("BK_IAM_METRIC_TOKEN", default="")


# BCS初始化ROLE网关api配置
BK_BCS_APIGW_URL = env.str("BK_BCS_APIGW_URL", default="")
