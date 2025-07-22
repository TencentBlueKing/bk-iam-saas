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

from django.conf import settings
from django.core.management.base import BaseCommand

from backend.apps.organization.constants import SyncTaskStatus
from backend.apps.organization.models import SyncRecord
from backend.apps.organization.tasks import sync_organization
from backend.apps.tenant.helper import create_default_notification_config, create_super_manager
from backend.component.client.bk_user import BkUserClient


class Command(BaseCommand):
    """
    初始化租户，当租户创建后，执行此命令来初始化租户的相关数据。
    $ python manage.py init_tenant --tenant_id=<tenant_id>
    """

    def add_arguments(self, parser):
        parser.add_argument("--tenant_id", type=str, help="Tenant ID", required=True)

    def _check_tenant_exists(self, tenant_id: str) -> bool:
        """
        检查租户是否存在
        :param tenant_id: 租户 ID
        :return: 如果租户存在，返回 True；否则返回 False
        """
        return tenant_id in {i["id"] for i in BkUserClient(settings.BK_APP_TENANT_ID).list_tenant()}

    def handle(self, *args, **options):
        tenant_id = options["tenant_id"]
        if not self._check_tenant_exists(tenant_id):
            raise ValueError(f"tenant with id - {tenant_id} does not exist.")

        # 创建租户的超级管理空间
        create_super_manager(tenant_id)
        # Note: 这里不创建租户下的各个系统管理空间，因为有 5 分钟的周期任务 sync_system_manager，
        #       如果手动创建，可能会产生并发问题，导致一个系统的管理空间被创建多次
        # sync_system_manager
        # 创建租户的通知配置
        create_default_notification_config(tenant_id)

        # 同步组织架构
        # Note: 这里不异步，因为在租户初始化时，组织架构应该是最新的，有问题直接抛出异常
        record_id = sync_organization(tenant_id=tenant_id)
        record = SyncRecord.objects.get(id=record_id)
        if record.status == SyncTaskStatus.Failed.value:
            raise ValueError(f"sync organization failed for tenant({tenant_id}): {record.detail}")

        self.stdout.write(f"tenant({tenant_id}) initialized successfully")
