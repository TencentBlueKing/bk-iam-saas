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
from django.core.paginator import Paginator
from django.db import connection

from backend.apps.role.models import Role
from backend.biz.role import RoleResourceRelationHelper


class Command(BaseCommand):
    help = "migrate role resource label"

    def handle(self, *args, **options):
        # 使用原始SQL获取所有非隐藏角色的ID，绕过可能不存在的enabled字段
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM role_role WHERE hidden = false")
            role_ids = [row[0] for row in cursor.fetchall()]

        print(f"找到 {len(role_ids)} 个需要迁移的角色")

        # 批量处理角色
        batch_size = 100
        for i in range(0, len(role_ids), batch_size):
            batch_ids = role_ids[i : i + batch_size]

            for role_id in batch_ids:
                # 创建临时的Role对象,RoleResourceRelationHelper.handle()方法只使用role.id
                role = Role(id=role_id)
                RoleResourceRelationHelper(role).handle()
