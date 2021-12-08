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

from backend.apps.organization.models import Department
from backend.component import iam

from .base import BaseSyncIAMBackendService

organization_logger = logging.getLogger("organization")


class IAMBackendDepartmentSyncService(BaseSyncIAMBackendService):
    """SaaS与IAM后台部门同步服务"""

    def __init__(self):
        """初始化数据"""
        self.db_departments = list(Department.objects.all())
        self.backend_departments = iam.list_all_subject("department")

    def created_handler(self):
        """后台需要新增的部门处理"""
        backend_dept_set = {i["id"] for i in self.backend_departments}
        created_depts = [
            {"type": "department", "id": str(i.id), "name": i.name or str(i.id)}
            for i in self.db_departments
            if str(i.id) not in backend_dept_set
        ]

        if not created_depts:
            return

        iam.create_subjects_by_auto_paging(created_depts)

        organization_logger.info(
            f"create departments by sync task, the length of departments: {len(created_depts)} "
            f"the detail of departments: {created_depts}"
        )

    def deleted_handler(self):
        """后台需要删除的部门处理"""
        db_dept_set = {str(i.id) for i in self.db_departments}
        deleted_depts = [
            {"type": "department", "id": i["id"]} for i in self.backend_departments if i["id"] not in db_dept_set
        ]

        if not deleted_depts:
            return

        iam.delete_subjects_by_auto_paging(deleted_depts)

        organization_logger.info(
            f"delete departments by sync task, the length of departments: {len(deleted_depts)} "
            f"the detail of departments: {deleted_depts}"
        )

    def sync_to_iam_backend(self):
        """同步IAM后台 相关变更"""
        # 新增部门
        self.created_handler()
        # 删除部门
        # self.deleted_handler()
