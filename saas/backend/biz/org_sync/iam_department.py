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

from backend.apps.organization.models import Department
from backend.component import iam

from .base import BaseSyncIAMBackendService

logger = logging.getLogger("organization")


class IAMBackendDepartmentSyncService(BaseSyncIAMBackendService):
    """SaaS 与 IAM 后台部门同步服务"""

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

        logger.info(f"create departments by sync task, count={len(created_depts)} detail={created_depts}")

    def deleted_handler(self):
        """后台需要删除的部门处理"""
        # db_dept_set = {str(i.id) for i in self.db_departments}
        # deleted_depts = [
        #     {"type": "department", "id": i["id"]} for i in self.backend_departments if i["id"] not in db_dept_set
        # ]
        #
        # if not deleted_depts:
        #     return
        #
        # iam.delete_subjects_by_auto_paging(deleted_depts)
        #
        # logger.info(
        #     f"delete departments by sync task, count={len(deleted_depts)} detail={deleted_depts}"
        # )

        # Note: 对于 SaaS 已删除部门，由于不确定是用户管理本身有 bug 导致的还是部门真实不存在了，
        # 所以为了避免影响部门权限，这里将不删除后端部门
        # 后续将会通过 SaaS 标记已删除部门，然后发起审批流程等方式再进行后端用户权限的删除

    def sync_to_iam_backend(self):
        """同步 IAM 后台 相关变更"""
        # 新增部门
        self.created_handler()
        # 删除部门
        self.deleted_handler()
