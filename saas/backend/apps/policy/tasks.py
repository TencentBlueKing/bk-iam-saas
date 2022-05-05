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

from celery import task

from backend.biz.model_event import ModelEventBiz
from backend.component import iam
from backend.service.constants import ModelChangeEventStatusEnum

logger = logging.getLogger("celery")


@task(ignore_result=True)
def execute_model_change_event():
    """作为后台模型事件的异步任务消费者，目前包括删除Action的相关策略，删除Action权限模型"""
    biz = ModelEventBiz()

    # 1. 查询未执行过的模型变更事件
    events = biz.list(ModelChangeEventStatusEnum.Pending.value)
    # 2. 逐一执行事件
    for event in events:
        executor = biz.get_executor(event)
        try:
            executor.run()
        except Exception:  # pylint: disable=broad-except
            # 对于失败的事件，不影响其他事件执行，暂时只能记录日志
            logger.exception(f"execute model change event fail! event={event}")


@task(ignore_result=True)
def delete_unreferenced_expressions():
    """删除未被引用的expression"""
    iam.delete_unreferenced_expressions()
