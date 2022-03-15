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
import logging
import time
from typing import Dict

import redis
from celery import task
from django.conf import settings

from backend.util.json import json_dumps

from .constants import DELETE_POLICY_PUB_SUB_KEY, DELETE_POLICY_REDIS_LIST_MAX_LENGTH, DeletePolicyTypeEnum

logger = logging.getLogger("celery")


@task(ignore_result=True)
def publish_delete_policies_message(message: Dict):
    """
    删除策略订阅推送
    """
    # 1. 查询用于订阅推送的Redis信息
    # 若没有Redis配置，则直接忽略
    if not getattr(settings, "PUB_SUB_REDIS_HOST", None):
        return

    rds = redis.Redis(
        host=settings.PUB_SUB_REDIS_HOST,
        port=int(settings.PUB_SUB_REDIS_PORT),
        db=int(settings.PUB_SUB_REDIS_DB),
        password=settings.PUB_SUB_REDIS_PASSWORD,
        decode_responses=True,
    )

    # 2. 将消息添加到Redis队列里
    rds.lpush(DELETE_POLICY_PUB_SUB_KEY, json_dumps(message))
    # 队列长度最多1万，避免长时间不消费导致的问题
    rds.ltrim(DELETE_POLICY_PUB_SUB_KEY, 0, DELETE_POLICY_REDIS_LIST_MAX_LENGTH - 1)


def publish_delete_policies(_type: DeletePolicyTypeEnum, data: Dict):
    """
    data: 需要根据type传入对应的数据
    """
    # 构造要push event message
    message = {"timestamp": int(time.time()), "type": _type, "data": data}

    # 提前多判断一次：若没有Redis配置，则直接忽略，避免发起celery任务
    if not getattr(settings, "PUB_SUB_REDIS_HOST", None):
        return

    # 由于订阅并非主要流程，所以错误不能引发调用者的任何异常
    try:
        # 连接不上broker，只做3次重试即可，否则会阻塞调用者，所以需要覆盖Broker默认全局配置BROKER_CONNECTION_MAX_RETRIES=100
        publish_delete_policies_message.apply_async(
            args=(message,),
            retry=True,
            retry_policy={
                # 为了避免出现：许多 Web 请求进程正在等待重试，从而阻止了其他传入请求
                # 重试的最长时间为0.4秒。默认情况下将其设置为相对较短，因为如果代理连接断开，连接失败可能导致重试堆效应
                "max_retries": 3,  # 重试3次
                "interval_start": 0,  # 第一次重试是瞬时的，不等待
                "interval_step": 0.2,  # 每次重试多添加0.2秒
                "interval_max": 0.2,  # 重试之间最大等待为0.2秒
            },
        )
    except Exception:  # pylint: disable=broad-except
        logger.exception(f"publish_delete_policies task push celery queue fail! message={message}")
