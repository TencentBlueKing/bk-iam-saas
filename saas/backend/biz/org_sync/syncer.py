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

from backend.apps.organization.models import Department, DepartmentMember, User
from backend.component import iam
from backend.component.client.bk_user import BkUserClient


class Syncer:
    """
    组织架构同步
    需要特别注意同步任务间是否有冲突
    """

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.client = BkUserClient(tenant_id=tenant_id)

    def sync_single_user(self, username):
        """
        单一用户同步（后续可以添加 with_relation=True 参数同步用户的相关部门和 leader 等）
        # NOTE：被 migration(organization.0004_auto_20201230_1653) 调用到了
        # 如果有调整，需要注意是否需要调整 migration，避免出现循环依赖导致 migrate 失败
        # 目前依赖 1 张表：User
        """
        # 1. 查询用户是否在 DB
        if User.objects.filter(username=username).exists():
            # 已存在则不需要再同步
            return

        # TODO: 考虑并发情况，需要添加分布式锁
        # 2. 查询 UserMgr API
        user_info = self.client.retrieve_user_or_virtual_user(username)
        # 3. 同步到 DB
        user, is_created = User.objects.get_or_create(
            username=user_info["bk_username"],
            defaults={
                "tenant_id": self.tenant_id,
                "display_name": user_info["display_name"],
                "full_name": user_info["full_name"],
            },
        )
        if not is_created:
            return

        # 4. 同步到 IAM 后台
        iam.create_subjects([{"type": "user", "id": user.username, "name": user.display_name}])

        # 5. 同步部门
        department_ids = [d["id"] for d in self.client.list_user_department(username)]
        if not department_ids:
            return

        # 只建立存在的部门与用户的关系，不存在的部门就等全量同步时处理
        departments = Department.objects.filter(id__in=department_ids)
        if not departments:
            return

        # 创建用户与部门关系
        DepartmentMember.objects.bulk_create(
            [
                DepartmentMember(tenant_id=self.tenant_id, department_id=dept.id, username=username)
                for dept in departments
            ]
        )

        department_id_set = set(department_ids)
        for dept in departments:
            for i in dept.parse_ancestors():
                department_id_set.add(i["id"])

        iam.create_subject_departments_by_auto_paging(
            [{"id": user.username, "departments": [str(_id) for _id in department_id_set]}]
        )
