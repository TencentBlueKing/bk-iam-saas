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

from django.db import transaction

from backend.apps.organization.constants import SyncTaskStatus
from backend.apps.organization.models import SyncRecord
from backend.apps.organization.tasks import sync_organization
from backend.apps.role.models import Role, RolePolicyExpiredNotificationConfig, RoleScope
from backend.service.constants import RoleScopeType, RoleType
from backend.util.json import json_dumps


def create_super_manager(tenant_id: str):
    """ "创建租户超级管理员空间"""
    with transaction.atomic():
        role, is_created = Role.objects.get_or_create(
            tenant_id=tenant_id,
            type=RoleType.SUPER_MANAGER.value,
            defaults={
                "name": "超级管理员",
                "name_en": "super administrator",
                "creator": "admin",
                "updater": "admin",
            },
        )
        if is_created:
            # 创建超级管理员的授权范围
            RoleScope.objects.bulk_create(
                [
                    RoleScope(
                        tenant_id=tenant_id,
                        role_id=role.id,
                        type=RoleScopeType.AUTHORIZATION.value,
                        content=json_dumps(
                            [{"system_id": "*", "actions": [{"id": "*", "related_resource_types": []}]}]
                        ),
                    ),
                    RoleScope(
                        tenant_id=tenant_id,
                        role_id=role.id,
                        type=RoleScopeType.SUBJECT.value,
                        content=json_dumps([{"type": "*", "id": "*"}]),
                    ),
                ]
            )


def create_default_notification_config(tenant_id: str):
    """初始化超级管理员通知设置"""
    role = Role.objects.get(tenant_id=tenant_id, type=RoleType.SUPER_MANAGER.value)
    RolePolicyExpiredNotificationConfig.objects.get_or_create(
        role_id=role.id,
        tenant_id=tenant_id,
        defaults={
            "_config": json_dumps(
                {
                    "enable": True,
                    "notification_types": ["mail", "rtx"],
                    "send_time": "10:00",
                    "expire_days_before": 15,
                    "expire_days_after": 1,
                    "send_days": ["monday"],
                }
            )
        },
    )


def manual_sync_organization(tenant_id: str):
    """
    手动同步组织架构（阻塞的）
    :param tenant_id: 租户 ID
    """
    record_id = sync_organization(tenant_id=tenant_id)
    record = SyncRecord.objects.get(id=record_id)
    if record.status == SyncTaskStatus.Failed.value:
        raise Exception(json.dumps(record.detail))  # noqa: TRY002
