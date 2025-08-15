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

from celery.signals import task_failure, task_success
from werkzeug.local import release_local

from backend.common.debug import log_task_error_trace
from backend.common.local import celery_local


# @task_success.connect
def task_success_handler(sender, **kwargs):
    # TODO werkzeug升级3.1.3 发生递归调用，待修复
    try:
        log_task_error_trace(sender)
        release_local(celery_local)
    except IndexError:
        return


# @task_failure.connect
def task_failure_handler(sender, exception, traceback, **kwargs):
    # TODO werkzeug升级3.1.3 发生递归调用，待修复
    try:
        log_task_error_trace(sender)
        release_local(celery_local)
    except IndexError:
        return
