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

from backend.apps.organization.models import User
from backend.component import iam

from .base import BaseSyncIAMBackendService

organization_logger = logging.getLogger("organization")


class IAMBackendUserSyncService(BaseSyncIAMBackendService):
    """SaaS与IAM后台用户同步服务"""

    def __init__(self):
        """初始化数据"""
        self.db_users = list(User.objects.all())
        self.backend_users = iam.list_all_subject("user")

    def created_handler(self):
        """后台需要新增的用户处理"""
        backend_user_set = {i["id"] for i in self.backend_users}
        created_users = [
            {"type": "user", "id": i.username, "name": i.display_name or i.username}
            for i in self.db_users
            if i.username not in backend_user_set
        ]

        if not created_users:
            return

        iam.create_subjects_by_auto_paging(created_users)

        organization_logger.info(
            f"create users by sync task, the length of users: {len(created_users)} "
            f"the detail of users: {created_users}"
        )

    def deleted_handler(self):
        """后台需要删除的用户处理"""
        db_user_set = {i.username for i in self.db_users}
        deleted_users = [{"type": "user", "id": i["id"]} for i in self.backend_users if i["id"] not in db_user_set]

        if not deleted_users:
            return

        iam.delete_subjects_by_auto_paging(deleted_users)

        organization_logger.info(
            f"delete users by sync task, the length of users: {len(deleted_users)} "
            f"the detail of users: {deleted_users}"
        )

    def sync_to_iam_backend(self):
        """同步IAM后台 相关变更"""
        # 新增用户
        self.created_handler()
        # 删除用户
        self.deleted_handler()
