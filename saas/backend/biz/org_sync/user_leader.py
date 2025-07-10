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

from backend.apps.organization.models import UserLeader
from backend.component import usermgr

from .base import BaseSyncDBService


class DBUserLeaderSyncService(BaseSyncDBService):
    """用户Leader同步服务"""

    def __init__(self):
        """初始数据"""
        self.new_user_leaders = usermgr.list_profile_leader()
        self.old_user_leaders = list(UserLeader.objects.all())

    def created_handler(self):
        """关于新建用户Leader，DB的处理"""
        old_user_leader_set = {(i.user_id, i.leader_id) for i in self.old_user_leaders}
        created_user_leader = [
            UserLeader(user_id=i["from_profile_id"], leader_id=i["to_profile_id"])
            for i in self.new_user_leaders
            if (i["from_profile_id"], i["to_profile_id"]) not in old_user_leader_set
        ]

        if not created_user_leader:
            return

        UserLeader.objects.bulk_create(created_user_leader, batch_size=1000)

    def deleted_handler(self):
        """关于删除用户Leader，DB的处理"""
        new_user_leader_set = {(i["from_profile_id"], i["to_profile_id"]) for i in self.new_user_leaders}
        deleted_ids = [i.id for i in self.old_user_leaders if (i.user_id, i.leader_id) not in new_user_leader_set]

        if not deleted_ids:
            return

        UserLeader.objects.filter(id__in=deleted_ids).delete()

    def sync_to_db(self):
        """SaaS DB 相关变更"""
        # 新增用户Leader
        self.created_handler()
        # 删除用户Leader
        self.deleted_handler()
