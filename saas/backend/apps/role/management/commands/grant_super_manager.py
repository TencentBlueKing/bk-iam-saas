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
from django.core.management.base import BaseCommand

from backend.biz.org_sync.syncer import Syncer
from backend.biz.role import RoleBiz


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--bk_username", type=str, help="BK Username", required=True)
        parser.add_argument(
            "--has_super_permission", type=bool, help="Has super permission", required=False, default=False
        )

    def handle(self, *args, **options):
        bk_username = options["bk_username"]
        has_super_permission = options["has_super_permission"]

        # 单一用户同步
        Syncer().sync_single_user(bk_username)

        # 授权超级管理员空间权限
        RoleBiz().add_super_manager_member(bk_username, has_super_permission)

        self.stdout.write(f"grant super manager for {bk_username} successfully")
