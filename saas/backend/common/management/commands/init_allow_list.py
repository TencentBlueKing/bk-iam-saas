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
import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from backend.api.authorization.constants import AuthorizationAPIEnum
from backend.api.authorization.models import AuthAPIAllowListConfig
from backend.api.constants import ALLOW_ANY
from backend.api.management.models import ManagementAPIAllowListConfig

logger = logging.getLogger("app")


class Command(BaseCommand):

    help = (
        "默认使用 settings.APP_CODE 作为 system_id，也可通过 --system-id 参数覆盖。"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--system-id",
            dest="system_ids",
            action="append",
            default=None,
            metavar="SYSTEM_ID",
            help=(
                "需要初始化白名单的 system_id（可重复指定多个）。"
                "若不指定，默认使用 settings.APP_CODE。"
            ),
        )

    def handle(self, *args, **options):
        # 确定需要初始化白名单的 system_id 列表
        system_ids: list[str] = options["system_ids"] or [settings.APP_CODE]

        self.stdout.write(f"开始初始化 API 白名单，目标 system_id: {system_ids}")
        logger.info("init_allow_list: start, system_ids=%s", system_ids)

        auth_created, auth_skipped = self._init_auth_api_allow_list(system_ids)
        mgmt_created, mgmt_skipped = self._init_management_api_allow_list(system_ids)

        summary = (
            f"白名单初始化完成。"
            f"授权API白名单: 新增 {auth_created} 条，跳过 {auth_skipped} 条；"
            f"管理API白名单: 新增 {mgmt_created} 条，跳过 {mgmt_skipped} 条。"
        )
        self.stdout.write(self.style.SUCCESS(summary))
        logger.info("init_allow_list: done. %s", summary)

    def _init_auth_api_allow_list(self, system_ids: list[str]) -> tuple[int, int]:
        created_count = 0
        skipped_count = 0

        for system_id in system_ids:
            obj, created = AuthAPIAllowListConfig.objects.get_or_create(
                type=AuthorizationAPIEnum.AUTHORIZATION_INSTANCE.value,
                system_id=system_id,
                object_id=ALLOW_ANY,
                defaults={
                    "creator": "",
                    "updater": "",
                },
            )
            if created:
                created_count += 1
                self.stdout.write(
                    f"  [授权API白名单] 新增: type={obj.type}, system_id={system_id}, object_id={ALLOW_ANY}"
                )
                logger.info(
                    "init_allow_list: auth_api created, type=%s, system_id=%s, object_id=%s",
                    obj.type,
                    system_id,
                    ALLOW_ANY,
                )
            else:
                skipped_count += 1
                self.stdout.write(
                    f"  [授权API白名单] 已存在，跳过: type={obj.type}, system_id={system_id}, object_id={ALLOW_ANY}"
                )

        return created_count, skipped_count

    def _init_management_api_allow_list(self, system_ids: list[str]) -> tuple[int, int]:
        created_count = 0
        skipped_count = 0

        for system_id in system_ids:
            obj, created = ManagementAPIAllowListConfig.objects.get_or_create(
                system_id=system_id,
                api=ALLOW_ANY,
                defaults={
                    "creator": "",
                    "updater": "",
                },
            )
            if created:
                created_count += 1
                self.stdout.write(
                    f"  [管理API白名单] 新增: system_id={system_id}, api={ALLOW_ANY}"
                )
                logger.info(
                    "init_allow_list: management_api created, system_id=%s, api=%s",
                    system_id,
                    ALLOW_ANY,
                )
            else:
                skipped_count += 1
                self.stdout.write(
                    f"  [管理API白名单] 已存在，跳过: system_id={system_id}, api={ALLOW_ANY}"
                )

        return created_count, skipped_count
