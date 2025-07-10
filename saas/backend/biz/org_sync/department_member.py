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

from backend.apps.organization.models import DepartmentMember
from backend.component import usermgr

from .base import BaseSyncDBService


class DBDepartmentMemberSyncService(BaseSyncDBService):
    """部门成员同步服务"""

    def __init__(self):
        """初始数据"""
        # 初始化数据
        self.new_department_members = usermgr.list_department_profile()
        self.old_department_members = list(DepartmentMember.objects.all())

    def created_handler(self):
        """关于新建部门成员，DB的处理"""
        old_department_member_set = {(i.department_id, i.user_id) for i in self.old_department_members}
        created_department_members = [
            DepartmentMember(department_id=i["department_id"], user_id=i["profile_id"])
            for i in self.new_department_members
            if (i["department_id"], i["profile_id"]) not in old_department_member_set
        ]

        if not created_department_members:
            return

        DepartmentMember.objects.bulk_create(created_department_members, batch_size=1000)

    def deleted_handler(self):
        """关于删除部门成员，DB的处理"""
        new_department_member_set = {(i["department_id"], i["profile_id"]) for i in self.new_department_members}
        deleted_ids = [
            i.id for i in self.old_department_members if (i.department_id, i.user_id) not in new_department_member_set
        ]

        if not deleted_ids:
            return

        DepartmentMember.objects.filter(id__in=deleted_ids).delete()

    def sync_to_db(self):
        """SaaS DB 相关变更"""
        # 新增部门成员
        self.created_handler()
        # 删除部门成员
        self.deleted_handler()
