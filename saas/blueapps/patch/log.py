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
import os

from blueapps.conf.default_settings import BASE_DIR, APP_CODE

from blueapps.conf.log import RequestIDFilter


def get_paas_v2_logging_config_dict(is_local, bk_log_dir, log_level):
    """
    日志V2对外版设置
    """

    app_code = os.environ.get('APP_ID', APP_CODE)

    # 设置日志文件夹路径
    log_dir = os.path.join(os.path.join(bk_log_dir, app_code))

    if is_local:
        # 本地环境, 如果没有设置日志的环境变量, 使用BASE_DIR
        if bk_log_dir == '/data/apps/logs/':
            log_dir = os.path.join(os.path.dirname(BASE_DIR), 'logs', app_code)

    # 如果日志文件夹不存在则创建,日志文件存在则延用
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    return {
        'version': 1,
        'disable_existing_loggers': False,
        'filters': {
            'request_id_filter': {
                '()': RequestIDFilter,
            }
        },
        'formatters': {
            'simple': {
                'format': '%(levelname)s %(message)s \n',
            },
            'verbose': {
                'format':
                '%(levelname)s [%(asctime)s] %(pathname)s '
                '%(lineno)d %(funcName)s %(process)d %(thread)d '
                '\n \t %(request_id)s\t%(message)s \n',
                'datefmt':
                '%Y-%m-%d %H:%M:%S',
            },
        },
        'handlers': {
            'component': {
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'verbose',
                'filename': os.path.join(log_dir, 'component.log'),
                'maxBytes': 1024 * 1024 * 10,
                'backupCount': 5,
                'filters': ['request_id_filter']
            },
            'celery': {
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'verbose',
                'filename': os.path.join(log_dir, 'celery.log'),
                'maxBytes': 1024 * 1024 * 10,
                'backupCount': 5,
                'filters': ['request_id_filter']
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'simple'
            },
            'null': {
                'level': 'DEBUG',
                'class': 'logging.NullHandler',
            },
            'root': {
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'verbose',
                'filename': os.path.join(log_dir, '%s.log' % app_code),
                'maxBytes': 1024 * 1024 * 10,
                'backupCount': 5,
                'filters': ['request_id_filter']
            },
            'wb_mysql': {
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'verbose',
                'filename': os.path.join(log_dir, 'wb_mysql.log'),
                'maxBytes': 1024 * 1024 * 4,
                'backupCount': 5,
                'filters': ['request_id_filter']
            },
        },
        'loggers': {
            # V2旧版开发框架使用的logger
            'component': {
                'handlers': ['component'],
                'level': 'WARNING',
                'propagate': True,
            },
            'django': {
                'handlers': ['null'],
                'level': 'INFO',
                'propagate': True,
            },
            'django.server': {
                'handlers': ['console'],
                'level': log_level,
                'propagate': True,
            },
            'django.request': {
                'handlers': ['console'],
                'level': 'ERROR',
                'propagate': True,
            },
            'django.db.backends': {
                'handlers': ['wb_mysql'],
                'level': log_level,
                'propagate': True,
            },
            'root': {
                'handlers': ['root'],
                'level': log_level,
                'propagate': True,
            },

            # V3新版使用的日志
            'celery': {
                'handlers': ['celery'],
                'level': log_level,
                'propagate': True,
            },
            'blueapps': {
                'handlers': ['root'],
                'level': log_level,
                'propagate': True,
            },
            'app': {
                'handlers': ['root'],
                'level': log_level,
                'propagate': True,
            },
            # 组织架构同步日志
            'organization': {
                'handlers': ['root'],
                'level': log_level,
                'propagate': True,
            },
            # 授权相关的日志
            'permission': {
                'handlers': ['root'],
                'level': log_level,
                'propagate': True,
            }
        }
    }
