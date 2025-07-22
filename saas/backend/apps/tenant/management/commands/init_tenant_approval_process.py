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

from backend.component.client.bk_itsm import BkITSMClient
from backend.plugins.approval_process.itsm import ITSMApprovalProcessProvider


class Command(BaseCommand):
    """
    初始化租户审批流程
    $ python manage.py init_tenant_approval_process --tenant_id <tenant_id>
    """

    def add_arguments(self, parser):
        parser.add_argument("--tenant_id", type=str, help="Tenant ID", required=True)

    def _register_system_to_itsm(self, tenant_id: str):
        """ "注册系统到 ITSM; 仅初始化运营租户时操作"""
        if tenant_id != settings.BK_APP_TENANT_ID:
            return

        try:
            BkITSMClient(tenant_id).create_system(
                name="权限中心",
                code=settings.ITSM_SYSTEM_ID,
                token=settings.ITSM_SYSTEM_TOKEN,
                desc="蓝鲸权限中心的权限申请审批",
            )
        except Exception as e:
            # Note: 当前 ITSM 还没有提供查询系统是否存在的接口或判断的错误码；只能先通过异常信息来判断
            if "Duplicate entry" in str(e):
                # 系统已存在
                return
            # 其他异常则抛出
            raise

    def handle(self, *args, **options):
        tenant_id = options["tenant_id"]

        # 注册系统到 ITSM
        self._register_system_to_itsm(tenant_id)

        provider = ITSMApprovalProcessProvider(tenant_id=tenant_id)
        # 默认流程
        default_workflow_keys = provider.get_default_workflow_key()
        # 在 ITSM 中有的流程
        workflow_keys = [i.id for i in provider.list()]
        # 如果默认流程不存在，则创建
        if set(default_workflow_keys).issubset(set(workflow_keys)):
            self.stdout.write(f"tenant({tenant_id}) approval process already initialized")
            return

        provider.create_workflow()
        self.stdout.write(f"tenant({tenant_id}) approval process initialized successfully")
