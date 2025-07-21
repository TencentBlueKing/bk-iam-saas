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

from backend.apps.organization.models import DepartmentMember
from backend.component.client.bk_user import BkUserClient

from .base import BaseSyncDBService


class DBDepartmentMemberSyncService(BaseSyncDBService):
    """部门成员同步服务"""

    def __init__(self, tenant_id: str):
        """初始数据"""
        self.tenant_id = tenant_id
        # 初始化数据
        self.new_department_members = BkUserClient(self.tenant_id).list_department_user_relation()
        self.old_department_members = list(DepartmentMember.objects.filter(tenant_id=self.tenant_id))

    def created_handler(self):
        """关于新建部门成员，DB 的处理"""
        old_department_member_set = {(i.department_id, i.username) for i in self.old_department_members}
        created_department_members = [
            DepartmentMember(tenant_id=self.tenant_id, department_id=i["department_id"], username=i["bk_username"])
            for i in self.new_department_members
            if (i["department_id"], i["bk_username"]) not in old_department_member_set
        ]

        if not created_department_members:
            return

        DepartmentMember.objects.bulk_create(created_department_members, batch_size=1000)

    def deleted_handler(self):
        """关于删除部门成员，DB 的处理"""
        new_department_member_set = {(i["department_id"], i["bk_username"]) for i in self.new_department_members}
        deleted_ids = [
            i.id for i in self.old_department_members if (i.department_id, i.username) not in new_department_member_set
        ]

        if not deleted_ids:
            return

        DepartmentMember.objects.filter(tenant_id=self.tenant_id, id__in=deleted_ids).delete()

    def sync_to_db(self):
        """SaaS DB 相关变更"""
        with transaction.atomic():
            # 新增部门成员
            self.created_handler()
            # 删除部门成员
            self.deleted_handler()
