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

from celery import shared_task
from django.conf import settings
from django.db import transaction

from backend.apps.temporary_policy.models import TemporaryPolicy
from backend.common.time import db_time
from backend.component import iam


@shared_task(ignore_result=True)
def clean_expired_temporary_policies():
    """清理过期3天以上的临时权限"""
    expired_at = int(db_time()) - settings.MAX_EXPIRED_TEMPORARY_POLICY_DELETE_TIME
    limit = 10000
    with transaction.atomic():
        # NOTE： 同后端的删除策略一致，避免表锁，分批次删除
        for _ in range(10):
            ids = list(TemporaryPolicy.objects.filter(expired_at__lt=expired_at).values_list("id", flat=True)[:limit])
            if ids:
                TemporaryPolicy.objects.filter(id__in=ids).delete()

            if len(ids) < limit:
                break

        iam.delete_temporary_policies_before_expired_at(expired_at)
