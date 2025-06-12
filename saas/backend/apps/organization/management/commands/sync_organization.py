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

import json

from django.core.management.base import BaseCommand

from backend.apps.organization.constants import SyncTaskStatus
from backend.apps.organization.models import SyncRecord
from backend.apps.organization.tasks import sync_organization
from backend.apps.role.tasks import sync_system_manager
from backend.biz.org_sync.syncer import Syncer
from backend.biz.role import RoleBiz


class Command(BaseCommand):
    help = "Synchronous organization"

    def handle(self, *args, **options):
        # 1. 组织架构同步 - 单用户 admin
        Syncer().sync_single_user("admin")
        # 2. 将 admin 添加到超级管理员成员里，在部署 migration 里已经默认创建了分级管理员
        RoleBiz().add_super_manager_member("admin", True)
        # 3. 尽可能的初始化已存在系统的管理员
        sync_system_manager()
        # 4. 异步任务 - 全量同步组织架构
        record_id = sync_organization("admin")
        # handle sync result
        record = SyncRecord.objects.get(id=record_id)
        if record.status == SyncTaskStatus.Failed.value:
            raise Exception(json.dumps(record.detail))  # noqa: TRY002
