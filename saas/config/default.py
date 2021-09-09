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
import hashlib
from urllib.parse import urlparse

from celery.schedules import crontab

from blueapps.conf.default_settings import *  # noqa
from blueapps.conf.log import get_logging_config_dict

# 这里是默认的 INSTALLED_APPS，大部分情况下，不需要改动
# 如果你已经了解每个默认 APP 的作用，确实需要去掉某些 APP，请去掉下面的注释，然后修改
# INSTALLED_APPS = (
#     'bkoauth',
#     # 框架自定义命令
#     'blueapps.contrib.bk_commands',
#     'django.contrib.admin',
#     'django.contrib.auth',
#     'django.contrib.contenttypes',
#     'django.contrib.sessions',
#     'django.contrib.sites',
#     'django.contrib.messages',
#     'django.contrib.staticfiles',
#     # account app
#     'blueapps.account',
# )

# 请在这里加入你的自定义 APP
INSTALLED_APPS += (
    # framework
    "rest_framework",
    "django_filters",
    "drf_yasg",
    "corsheaders",
    "mptt",
    "django_prometheus",
    # backend apps
    "backend.account",
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
    "backend.api.authorization",
    "backend.api.admin",
    "backend.api.management",
    "backend.apps.role",
    "backend.apps.user",
    "backend.apps.model_builder",
    "backend.long_task",
    "backend.audit",
    "backend.debug",
)

# 这里是默认的中间件，大部分情况下，不需要改动
# 如果你已经了解每个默认 MIDDLEWARE 的作用，确实需要去掉某些 MIDDLEWARE，或者改动先后顺序，请去掉下面的注释，然后修改
MIDDLEWARE = (
    # profile record
    "backend.common.middlewares.CustomProfilerMiddleware",
    # prometheus
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    # request instance provider
    "blueapps.middleware.request_provider.RequestProvider",
    "backend.common.middlewares.RequestProvider",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    # 跨域检测中间件， 默认关闭
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "django.middleware.security.SecurityMiddleware",
    # 蓝鲸静态资源服务
    "whitenoise.middleware.WhiteNoiseMiddleware",
    # Auth middleware
    "backend.account.middlewares.LoginMiddleware",
    # Timezone middleware
    "backend.account.middlewares.TimezoneMiddleware",
    # Role Auth middleware
    "backend.account.middlewares.RoleAuthenticationMiddleware",
    # exception middleware
    "blueapps.core.exceptions.middleware.AppExceptionMiddleware",
    # prometheus
    "django_prometheus.middleware.PrometheusAfterMiddleware",
)

# 自定义中间件
MIDDLEWARE += ("corsheaders.middleware.CorsMiddleware",)

# 所有环境的日志级别可以在这里配置
# LOG_LEVEL = 'INFO'

# STATIC_VERSION_BEGIN
# 静态资源文件(js,css等）在APP上线更新后, 由于浏览器有缓存,
# 可能会造成没更新的情况. 所以在引用静态资源的地方，都把这个加上
# Django 模板中：<script src="/a.js?v={{ STATIC_VERSION }}"></script>
# mako 模板中：<script src="/a.js?v=${ STATIC_VERSION }"></script>
# 如果静态资源修改了以后，上线前改这个版本号即可
# STATIC_VERSION_END
STATIC_VERSION = "1.0"

STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

# local time
USE_TZ = True

# i18n
USE_I18N = True
USE_L10N = True
LANGUAGE_CODE = "zh-hans"
LANGUAGE_COOKIE_NAME = "blueking_language"
LANGUAGE_COOKIE_PATH = "/"
LOCALE_PATHS = (os.path.join(BASE_DIR, "resources/locale"),)

# load logging settings
LOGGING = get_logging_config_dict(locals())

# 初始化管理员列表，列表中的人员将拥有预发布环境和正式环境的管理员权限
# 注意：请在首次提测和上线前修改，之后的修改将不会生效
INIT_SUPERUSER = []


# 使用mako模板时，默认打开的过滤器：h(过滤html)
MAKO_DEFAULT_FILTERS = ["h"]

# BKUI是否使用了history模式
IS_BKUI_HISTORY_MODE = False

# 是否需要对AJAX弹窗登录强行打开
IS_AJAX_PLAIN_MODE = False


"""
以下为框架代码 请勿修改
"""

# CELERY 开关，使用时请改为 True，否则请保持为False。启动方式为以下两行命令：
# worker: python manage.py celery worker -l info
# beat: python manage.py celery beat -l info
IS_USE_CELERY = True

# 连接 BROKER 超时时间
BROKER_CONNECTION_TIMEOUT = 1  # 单位秒
# CELERY与RabbitMQ增加60秒心跳设置项
BROKER_HEARTBEAT = 60

# CELERY 并发数，默认为 2，可以通过环境变量或者 Procfile 设置
CELERYD_CONCURRENCY = os.getenv("BK_CELERYD_CONCURRENCY", 2)

# CELERY 配置，申明任务的文件路径，即包含有 @task 装饰器的函数文件
CELERY_IMPORTS = ("backend.apps.organization.tasks", "backend.apps.role.tasks", "backend.publisher.tasks")

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
        "schedule": crontab(minute=0, hour=2),  # 每天凌晨0时执行
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
        "schedule": crontab(minute=0, hour=1),  # 每天凌晨1时执行
    },
    "periodic_execute_model_change_event": {
        "task": "backend.apps.policy.tasks.execute_model_change_event",
        "schedule": crontab(minute="*/30"),  # 每30分钟执行一次
    },
}

# celery settings
if IS_USE_CELERY:
    INSTALLED_APPS = locals().get("INSTALLED_APPS", [])
    import djcelery

    INSTALLED_APPS += ("djcelery",)
    djcelery.setup_loader()
    CELERY_ENABLE_UTC = True
    CELERYBEAT_SCHEDULER = "djcelery.schedulers.DatabaseScheduler"

# remove disabled apps
if locals().get("DISABLED_APPS"):
    INSTALLED_APPS = locals().get("INSTALLED_APPS", [])
    DISABLED_APPS = locals().get("DISABLED_APPS", [])

    INSTALLED_APPS = [_app for _app in INSTALLED_APPS if _app not in DISABLED_APPS]

    _keys = (
        "AUTHENTICATION_BACKENDS",
        "DATABASE_ROUTERS",
        "FILE_UPLOAD_HANDLERS",
        "MIDDLEWARE",
        "PASSWORD_HASHERS",
        "TEMPLATE_LOADERS",
        "STATICFILES_FINDERS",
        "TEMPLATE_CONTEXT_PROCESSORS",
    )

    import itertools

    for _app, _key in itertools.product(DISABLED_APPS, _keys):
        if locals().get(_key) is None:
            continue
        locals()[_key] = tuple([_item for _item in locals()[_key] if not _item.startswith(_app + ".")])

# Django RestFramework
REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "backend.common.exception_handler.custom_exception_handler",
    "DEFAULT_PAGINATION_CLASS": "backend.common.pagination.CustomLimitOffsetPagination",
    "PAGE_SIZE": 10,
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
    "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework.authentication.SessionAuthentication",),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_RENDERER_CLASSES": ("backend.common.renderers.BKAPIRenderer",),
    "DATETIME_FORMAT": "%Y-%m-%d %H:%M:%S",
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
}

# static file
WHITENOISE_STATIC_PREFIX = "/staticfiles/"
FORCE_SCRIPT_NAME = SITE_URL
STATIC_URL = SITE_URL + "staticfiles/"
AJAX_URL_PREFIX = SITE_URL + "api/v1"

# iam host
BK_IAM_HOST = os.environ.get("BK_IAM_V3_INNER_HOST", "http://bkiam.service.consul:9081")

# cors
CORS_ALLOW_CREDENTIALS = True  # 在 response 添加 Access-Control-Allow-Credentials, 即允许跨域使用 cookies
CORS_ORIGIN_WHITELIST = []  # 默认只支持同域名请求

# cookie
SESSION_COOKIE_NAME = "bkiam_sessionid"
CSRF_COOKIE_NAME = "bkiam_csrftoken"
SESSION_COOKIE_AGE = 60 * 60 * 24  # 1天

# version log
VERSION_LOG_MD_FILES_DIR = os.path.join(BASE_DIR, "resources/version_log")

# authorization limit
# 授权对象授权用户组, 模板的最大限制
SUBJECT_AUTHORIZATION_LIMIT = {
    # 用户能加入的用户组的最大数量
    "default_subject_group_limit": int(os.environ.get("BKAPP_DEFAULT_SUBJECT_GROUP_LIMIT", 100)),
    # 用户组能加入同一个系统的权限模板的最大数量
    "default_subject_system_template_limit": int(os.environ.get("BKAPP_DEFAULT_SUBJECT_SYSTEM_TEMPLATE_LIMIT", 10)),
    "subject_system_template_limit": {
        # key: system_id, value: int
    },  # 系统可自定义配置的 用户组能加入同一个系统的权限模板的最大数量
    # 用户组成员最大数量
    "group_member_limit": int(os.environ.get("BKAPP_GROUP_MEMBER_LIMIT", 500)),
    # 用户组单次授权模板数
    "group_auth_template_once_limit": int(os.environ.get("BKAPP_GROUP_AUTH_TEMPLATE_ONCE_LIMIT", 10)),
    # 用户组单次授权的系统数
    "group_auth_system_once_limit": int(os.environ.get("BKAPP_GROUP_AUTH_SYSTEM_ONCE_LIMIT", 5)),
}

# 授权的实例最大数量限制
AUTHORIZATION_INSTANCE_LIMIT = int(os.environ.get("BKAPP_AUTHORIZATION_INSTANCE_LIMIT", 200))

# 策略中实例数量的最大限制
SINGLE_POLICY_MAX_INSTANCES_LIMIT = int(os.environ.get("BKAPP_SINGLE_POLICY_MAX_INSTANCES_LIMIT", 10000))

# 一次申请策略中中新增实例数量限制
APPLY_POLICY_ADD_INSTANCES_LIMIT = int(os.environ.get("BKAPP_APPLY_POLICY_ADD_INSTANCES_LIMIT", 20))

# profile record
PYINSTRUMENT_PROFILE_DIR = os.path.join(os.path.dirname(BASE_DIR), "logs", APP_CODE, "profiles")  # 默认在日志目录下
ENABLE_PYINSTRUMENT = os.environ.get("BKAPP_ENABLE_PYINSTRUMENT", "False").lower() == "true"  # 需要开启时则配置环境变量

# DB router
DATABASE_ROUTERS = ["backend.audit.routers.AuditRouter"]

# debug trace的过期时间
MAX_DEBUG_TRACE_TTL = 7 * 24 * 60 * 60  # 7天
# debug trace的最大数量
MAX_DEBUG_TRACE_COUNT = 1000

# 最长已过期权限删除期限
MAX_EXPIRED_POLICY_DELETE_TIME = 365 * 24 * 60 * 60  # 1年

# Open API接入APIGW后，需要对APIGW请求来源认证，使用公钥解开jwt
BK_APIGW_PUBLIC_KEY = os.environ.get("BKAPP_APIGW_PUBLIC_KEY", "")

# iam engine host
BK_IAM_ENGINE_HOST = os.environ.get("BKAPP_IAM_ENGINE_HOST", "")
BK_IAM_ENGINE_HOST_TYPE = os.environ.get("BKAPP_IAM_ENGINE_HOST_TYPE", "direct")  # direct/apigateway

# 用于发布订阅的Redis
PUB_SUB_REDIS_HOST = os.environ.get("BKAPP_PUB_SUB_REDIS_HOST", "")
PUB_SUB_REDIS_PORT = os.environ.get("BKAPP_PUB_SUB_REDIS_PORT", "")
PUB_SUB_REDIS_PASSWORD = os.environ.get("BKAPP_PUB_SUB_REDIS_PASSWORD", "")
PUB_SUB_REDIS_DB = os.environ.get("BKAPP_PUB_SUB_REDIS_DB", 0)

# 前端页面功能开关
ENABLE_FRONT_END_FEATURES = {
    "enable_model_build": os.environ.get("BKAPP_ENABLE_FRONT_END_MODEL_BUILD", "False").lower() == "true"
}

# 是否是smart部署方式
IS_SMART_DEPLOY = os.environ.get("BKAPP_IS_SMART_DEPLOY", "True").lower() == "true"
