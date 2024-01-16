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
from backend.apps.organization.models import SubjectToDelete, User
from backend.component import usermgr
from backend.service.constants import SubjectType

from .base import BaseSyncDBService


class DBUserSyncService(BaseSyncDBService):
    """DB用户同步服务"""

    def __init__(self):
        """初始化数据"""
        # 新数据从usermgr API获取
        self.new_users = usermgr.list_profile()
        # 老数据从DB获取
        self.old_users = list(User.objects.all())

    def created_handler(self):
        """关于新建用户，DB的处理"""
        # 对比新老数据，获取需要新增的用户
        old_user_id_set = {i.id for i in self.old_users}
        # 遍历新数据，只要老数据里不存在的都是需要新增的
        created_users = [
            User(
                id=user["id"],
                username=user["username"],
                display_name=user["display_name"] or user["username"],
                staff_status=user["staff_status"],
                category_id=user["category_id"],
            )
            for user in self.new_users
            if user["id"] not in old_user_id_set
        ]

        if not created_users:
            return

        # 先校验是否有重复用户
        uniq_usernames = set()
        for user in created_users:
            if user.username in uniq_usernames:
                raise Exception(f"username duplicate: {user.username}")
            uniq_usernames.add(user.username)

        # 对于新增用户，执行对应变更
        User.objects.bulk_create(created_users, batch_size=1000)

        # 移除待删除的用户
        SubjectToDelete.objects.filter(
            subject_type=SubjectType.USER.value, subject_id__in=[u.username for u in created_users]
        ).delete()

    def updated_handler(self):
        """关于更新用户，DB的处理"""
        # 只更新变更了的 display_name、staff_status、category_id的用户
        new_user_dict = {i["id"]: i for i in self.new_users}
        updated_users = []
        for user in self.old_users:
            new_user = new_user_dict.get(user.id)
            # 新用户里不存在则表示将被删除，不需要处理
            if not new_user:
                continue
            if (user.display_name, user.staff_status, user.category_id) != (
                new_user["display_name"],
                new_user["staff_status"],
                new_user["category_id"],
            ):
                user.display_name = new_user["display_name"] or user.username
                user.staff_status = new_user["staff_status"]
                user.category_id = new_user["category_id"]
                updated_users.append(user)

        if not updated_users:
            return

        User.objects.bulk_update(updated_users, ["display_name", "staff_status", "category_id"], batch_size=1000)

    def deleted_handler(self):
        """关于删除用户，DB的处理"""
        # 对比新老数据，获取需要新增的用户
        new_user_id_set = {i["id"] for i in self.new_users}
        # 遍历老数据，只要新数据不存在，则表示需要删除的；删除只需要ID即可
        deleted_user_ids = [user.id for user in self.old_users if user.id not in new_user_id_set]

        if not deleted_user_ids:
            return

        # TODO: 可添加其他流程后再真正的删除，只要DB里不删除，IAM后台和SaaS都不受影响
        User.objects.filter(id__in=deleted_user_ids).delete()
        # TODO: DB里其他表存在了被删的记录如何处理？不处理可能展示有些问题，比如权限模板授权表等等

        # TODO 删除用户所属角色的成员
        # TODO 删除用户属于角色的授权范围

        # 以上TODO都在延迟删除的任务中处理, 这里只记录待删除的用户
        subject_to_delete = [
            SubjectToDelete(subject_id=user.username, subject_type=SubjectType.USER.value)
            for user in self.old_users
            if user.id not in new_user_id_set
        ]
        SubjectToDelete.objects.bulk_create(subject_to_delete, batch_size=100, ignore_conflicts=True)

    def sync_to_db(self):
        """SaaS DB 相关变更"""
        # 新增用户
        self.created_handler()
        # 更新用户
        self.updated_handler()
        # 删除用户
        self.deleted_handler()

        # TODO: 离职用户如何处理 (1) 管理员确认？（2）SaaS 除用户表和关系表外，其他都删除用户相关的（2）后台除Subject表外其他都删除
        # TODO: 用户名更新的用户 => (1)仅通知管理员和记录日志等，不做变更
