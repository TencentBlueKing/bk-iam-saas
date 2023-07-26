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

from backend.apps.role.models import Role
from backend.biz.role import RoleResourceRelationHelper


class Command(BaseCommand):
    help = "migrate role resource label"

    def handle(self, *args, **options):
        queryset = Role.objects.filter(hidden=False).all()

        paginator = Paginator(queryset, 100)

        for i in paginator.page_range:
            for role in paginator.page(i):
                RoleResourceRelationHelper(role).handle()
