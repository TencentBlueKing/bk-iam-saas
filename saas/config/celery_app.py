"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云 - 权限中心 (BlueKing-IAM) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import os

from celery import Celery
from kombu import Exchange, Queue

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

app = Celery("bkiam")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# set queue ha policy if use rabbitmq
# default queue name is bk_iam
app.conf.task_queues = [
    Queue("bk_iam", Exchange("bk_iam"), routing_key="bk_iam", queue_arguments={"x-ha-policy": "all"}),
]


# set periodic tasks
# @app.on_after_finalize.connect
# def setup_periodic_tasks(sender, **kwargs):
#     from backend.biz.role import get_global_notification_config
#
#     config = get_global_notification_config()
#     hour, minute = [int(i) for i in config["send_time"].split(":")]
#
#     sender.add_periodic_task(
#         crontab(minute=minute, hour=hour),
#         permission_expire_remind.s(),
#         name="periodic_permission_expire_remind",
#     )
#
#
# @app.task
# def permission_expire_remind():
#     from backend.apps.role.tasks import role_group_expire_remind
#     from backend.apps.user.tasks import user_group_policy_expire_remind
#
#     role_group_expire_remind.delay()
#     user_group_policy_expire_remind.delay()
