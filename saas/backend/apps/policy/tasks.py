# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云 - 权限中心 (BlueKing-IAM) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import logging
import time

from celery import shared_task

from backend.biz.model_event import ModelEventBiz
from backend.component import iam
from backend.service.constants import ModelChangeEventStatus

logger = logging.getLogger("celery")


@shared_task(ignore_result=True)
def execute_model_change_event():
    """作为后台模型事件的异步任务消费者，目前包括删除 Action 的相关策略，删除 Action 权限模型"""
    biz = ModelEventBiz()

    # 1. 查询未执行过的模型变更事件
    # Note: 由于定时任务处理时，若数量过多，单个周期内处理不完，会导致多个周期重叠处理相同事件，所以默认只处理 1000 条
    events = biz.list(ModelChangeEventStatus.Pending.value)
    # 2. 逐一执行事件
    for event in events:
        executor = biz.get_executor(event)
        try:
            executor.run()
        except Exception:  # pylint: disable=broad-except
            # 对于失败的事件，不影响其他事件执行，暂时只能记录日志
            logger.exception(f"execute model change event fail! event={event}")


@shared_task(ignore_result=True)
def cleanup_finished_model_change_event():
    """
    清理已经结束很长时间的模型变更事件
    """
    biz = ModelEventBiz()

    # 默认删除一个月前的已结束的模型变更事件，
    # 为避免对后台造成负载，一次只删除 1000 条数据（毕竟模型变更数据量一般并不大）
    before_updated_at = int(time.time()) - 60 * 60 * 24 * 30
    biz.delete_finished_event(before_updated_at, 1000)


@shared_task(ignore_result=True)
def delete_unreferenced_expressions():
    """删除未被引用的 expression"""
    iam.delete_unreferenced_expressions()
