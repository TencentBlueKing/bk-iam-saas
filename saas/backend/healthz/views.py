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
import copy
from logging import getLogger

import requests
from django.conf import settings
from django.http import HttpResponse, HttpResponseServerError, JsonResponse
from rest_framework import serializers

from backend.component import usermgr
from backend.util.url import url_join

logger = getLogger("app")


def pong(request):
    return HttpResponse("pong")


def healthz(request):
    checker = HealthChecker()

    data = {}
    for name in ["mysql", "redis", "celery", "iam"]:
        ok, message = getattr(checker, name)()
        if not ok:
            return HttpResponseServerError(message)

        data[name] = message

    return JsonResponse(data)


class HealthChecker:
    """
    健康检查
    """

    def mysql(self):
        """
        Connect to each database and do a generic standard SQL query
        that doesn't write any data and doesn't depend on any tables
        being present.
        """
        try:
            from django.db import connections
        except ImportError as e:
            logger.exception("mysql connect fail")
            return False, f"mysql connect fail, error: {str(e)}"

        try:
            for name in connections:
                with connections[name].cursor() as cursor:
                    cursor.execute("SELECT 1;")
                    row = cursor.fetchone()
                    if row is None:
                        return False, f"mysql connection {name} `Select 1` Not Return Row"
        except Exception as e:  # pylint: disable=broad-except
            logger.exception("mysql query fail")
            return False, f"mysql query fail, error: {str(e)}"

        return True, "ok"

    def redis(self):
        """
        Check whether a redis cache is alive by pinging it.
        """
        try:
            from redis.exceptions import ConnectionError

            from backend.common.redis import get_redis_connection
        except ImportError as e:
            logger.exception("redis module import fail")
            return False, f"redis module import fail, error: {str(e)}"

        try:
            get_redis_connection().ping()
        except ConnectionError as e:
            logger.exception("redis ping test fail")
            return False, f"redis ping test fail, error: {str(e)}"

        return True, "ok"

    def celery(self):
        """
        Check whether celery is alive by checking its stats.
        """
        try:
            from celery import current_app
        except ImportError as e:
            logger.exception("celery import fail")
            return False, f"celery import fail, error: {str(e)}"

        try:
            # Build a new app with shorter timeouts.
            new_app = copy.deepcopy(current_app)
            # 这里设置连接消息队列的相关配置
            new_app.conf.CELERY_BROKER_CONNECTION_TIMEOUT = 5
            new_app.conf.CELERY_BROKER_CONNECTION_MAX_RETRIES = 1
            new_app.conf.CELERY_BROKER_TRANSPORT_OPTIONS = {"max_retries": 1, "interval_step": 0, "interval_max": 0}
            # 进行Ping测试
            # Note: Celery的Ping命令也是异步执行的
            # 这里仅仅是测试ping命令能否被发送的消息队列（上面代码已设置与消息队列通讯的相关配置），无法送达将raise exception
            # 不对ping命令的返回结果进行检查，因为worker可能存在满负载情况，无法及时消费
            # Limit=1表示只要有一个worker响应了就进行返回，没必要等待timeout再返回结果，Timeout表示最多等待多少秒返回结果
            new_app.control.inspect(limit=1, timeout=2).ping()
        except Exception as e:  # pylint: disable=broad-except
            logger.exception("celery ping test fail")
            return False, f"celery ping test fail, error: {str(e)}"
        finally:
            new_app.close()

        return True, "ok"

    def iam(self):
        try:
            url = url_join(settings.BK_IAM_HOST, "/healthz")
            resp = requests.get(url)
            if resp.status_code != requests.codes.ok:
                return False, f"iam backend response status[{resp.status_code}] not OK"
        except Exception as e:  # pylint: disable=broad-except
            logger.exception("iam backend request fail")
            return False, f"iam backend request fail, error: {str(e)}"

        return True, "ok"

    def usermgr(self):
        """
        Check User Manager
        """
        try:
            # TODO: 暂时不引入JSON-Schema进行校验，待校验接入系统回调接口数据时再引入
            # 校验查询目录返回的数据结构是否OK
            class CategorySLZ(serializers.Serializer):
                id = serializers.CharField()
                display_name = serializers.CharField()

            categories = usermgr.list_category()
            for category in categories:
                CategorySLZ(data=category).is_valid(raise_exception=True)
        except Exception as e:  # pylint: disable=broad-except
            logger.exception("usermgr request fail")
            return True, f"usermgr request fail, error: {str(e)}"
        return True, "ok"
