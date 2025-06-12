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

from backend.apps.organization.models import User
from backend.component import iam

from .base import BaseSyncIAMBackendService

logger = logging.getLogger("organization")


class IAMBackendUserSyncService(BaseSyncIAMBackendService):
    """SaaS 与 IAM 后台用户同步服务"""

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

        logger.info(f"create users by sync task, count={len(created_users)} detail={created_users}")

    def deleted_handler(self):
        """后台需要删除的用户处理"""
        # db_user_set = {i.username for i in self.db_users}
        # deleted_users = [{"type": "user", "id": i["id"]} for i in self.backend_users if i["id"] not in db_user_set]
        #
        # if not deleted_users:
        #     return
        #
        # iam.delete_subjects_by_auto_paging(deleted_users)
        #
        # logger.info(
        #     f"delete users by sync task, count={len(deleted_users)} detail={deleted_users}"
        # )
        # Note: 对于 SaaS 已删除用户，由于不确定是用户管理本身有 bug 导致的还是用户真实不存在了，
        # 所以为了避免影响用户权限，这里将不删除后端用户
        # 后续将会通过 SaaS 标记已删除用户，然后发起审批流程等方式再进行后端用户权限的删除

    def sync_to_iam_backend(self):
        """同步 IAM 后台 相关变更"""
        # 新增用户
        self.created_handler()
        # 删除用户
        self.deleted_handler()
