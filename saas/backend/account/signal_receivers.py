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

import logging

from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from backend.biz.org_sync.syncer import Syncer

logger = logging.getLogger("app")


@receiver(user_logged_in, dispatch_uid="backend.account.sync_user")
def sync_user(sender, user, **kwargs):
    try:
        Syncer(user.get_property("tenant_id")).sync_single_user(user.username)
    except Exception:  # pylint: disable=broad-except
        # 异常仅仅记录日志，不报错，不影响登录逻辑
        logger.exception("sync single user fail when user %s logged in", user.username)
