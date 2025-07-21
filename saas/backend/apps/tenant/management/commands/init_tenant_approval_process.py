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

from django.core.management.base import BaseCommand

from backend.plugins.approval_process.itsm import ITSMApprovalProcessProvider


class Command(BaseCommand):
    """
    初始化租户审批流程
    $ python manage.py init_tenant_approval_process --tenant_id <tenant_id>
    """

    def add_arguments(self, parser):
        parser.add_argument("--tenant_id", type=str, help="Tenant ID", required=True)

    def handle(self, *args, **options):
        tenant_id = options["tenant_id"]

        provider = ITSMApprovalProcessProvider(tenant_id=tenant_id)
        provider.create_workflow()
        # TODO：判断是否初始化流程（调用 ITSM 接口查询？）
        # TODO：ITSM 接口调用 - migrate system
        self.stdout.write(f"tenant({tenant_id}) approval process initialized successfully")
