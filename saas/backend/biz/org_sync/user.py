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

from django.db import transaction

from backend.apps.organization.models import SubjectToDelete, User
from backend.component.client.bk_user import BkUserClient
from backend.service.constants import SubjectType

from .base import BaseSyncDBService


class DBUserSyncService(BaseSyncDBService):
    """DB 用户同步服务"""

    def __init__(self, tenant_id: str):
        """初始化数据"""
        self.tenant_id = tenant_id
        # 新数据从 usermgr API 获取
        client = BkUserClient(tenant_id)
        # Note: 这里用户需要包括实名和虚拟用户
        self.new_users = client.list_user() + client.list_virtual_user()
        # 老数据从 DB 获取
        self.old_users = list(User.objects.filter(tenant_id=tenant_id))

    def created_handler(self):
        """关于新建用户，DB 的处理"""
        # 对比新老数据，获取需要新增的用户
        old_username_set = {i.username for i in self.old_users}
        # 遍历新数据，只要老数据里不存在的都是需要新增的
        created_users = [
            User(
                tenant_id=self.tenant_id,
                username=user["bk_username"],
                full_name=user["full_name"],
                display_name=user["display_name"],
            )
            for user in self.new_users
            if user["bk_username"] not in old_username_set
        ]

        if not created_users:
            return

        # 先校验是否有重复用户
        uniq_usernames = set()
        for user in created_users:
            if user.username in uniq_usernames:
                raise Exception(f"username duplicate: {user.username}")  # noqa: TRY002
            uniq_usernames.add(user.username)

        # 对于新增用户，执行对应变更
        User.objects.bulk_create(created_users, batch_size=1000)

        # 移除待删除的用户
        SubjectToDelete.objects.filter(
            tenant_id=self.tenant_id,
            subject_type=SubjectType.USER.value,
            subject_id__in=[u.username for u in created_users],
        ).delete()

    def updated_handler(self):
        """关于更新用户，DB 的处理"""
        # 只更新变更了的 display_name、staff_status、category_id 的用户
        new_user_dict = {i["bk_username"]: i for i in self.new_users}
        updated_users = []
        for user in self.old_users:
            new_user = new_user_dict.get(user.username)
            # 新用户里不存在则表示将被删除，不需要处理
            if not new_user:
                continue
            if (user.display_name, user.full_name) != (new_user["display_name"], new_user["full_name"]):
                user.display_name = new_user["display_name"]
                user.full_name = new_user["full_name"]
                updated_users.append(user)

        if not updated_users:
            return

        User.objects.bulk_update(updated_users, ["display_name", "full_name"], batch_size=1000)

    def deleted_handler(self):
        """关于删除用户，DB 的处理"""
        # 对比新老数据，获取需要新增的用户
        new_username_set = {i["bk_username"] for i in self.new_users}
        # 遍历老数据，只要新数据不存在，则表示需要删除的；删除只需要 username 即可
        deleted_usernames = [user.username for user in self.old_users if user.username not in new_username_set]

        if not deleted_usernames:
            return

        # TODO: 可添加其他流程后再真正的删除，只要 DB 里不删除，IAM 后台和 SaaS 都不受影响
        User.objects.filter(tenant_id=self.tenant_id, username__in=deleted_usernames).delete()
        # TODO: DB 里其他表存在了被删的记录如何处理？不处理可能展示有些问题，比如权限模板授权表等等

        # TODO 删除用户所属角色的成员
        # TODO 删除用户属于角色的授权范围

        # 以上 TODO 都在延迟删除的任务中处理，这里只记录待删除的用户
        subject_to_delete = [
            SubjectToDelete(tenant_id=self.tenant_id, subject_id=username, subject_type=SubjectType.USER.value)
            for username in deleted_usernames
        ]
        SubjectToDelete.objects.bulk_create(subject_to_delete, batch_size=100, ignore_conflicts=True)

    def sync_to_db(self):
        """SaaS DB 相关变更"""
        with transaction.atomic():
            # 新增用户
            self.created_handler()
            # 更新用户
            self.updated_handler()
            # 删除用户
            self.deleted_handler()

        # TODO: 离职用户如何处理
        #  (1) 管理员确认？
        #  （2）SaaS 除用户表和关系表外，其他都删除用户相关的
        #  （3）后台除 Subject 表外其他都删除
        # TODO: 用户名更新的用户 => (1) 仅通知管理员和记录日志等，不做变更
