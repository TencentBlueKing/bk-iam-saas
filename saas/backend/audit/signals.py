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
from django.db.models.signals import post_save
from django.dispatch import receiver

from backend.audit.tasks import log_audit_event


@receiver(post_save)
def audit_event_handler(sender, instance, created, **kwargs):
    # NOTE: 由于审计的模型是分表的动态模型, 所以这里不能直接指定sender, 只能在获取所有模型的post_save事件
    if not sender.__name__.startswith("Event_"):
        return

    # 只有创建事件需要处理
    if not created:
        return

    # 发送到celery处理
    suffix = sender.__name__.split("_")[1]
    id = instance.id.hex

    log_audit_event.delay(suffix, id)


def send_bulk_create_signal(model_class, instances):
    """提供批量创建的信号"""
    for instance in instances:
        post_save.send(sender=model_class, instance=instance, created=True)
