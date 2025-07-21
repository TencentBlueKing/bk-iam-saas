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

from collections import defaultdict
from typing import Dict, List

from backend.apps.organization.models import Department, DepartmentMember
from backend.component import iam

from .base import BaseSyncIAMBackendService


class IAMBackendUserDepartmentSyncService(BaseSyncIAMBackendService):
    """SaaS 与 IAM 后台用户部门同步服务"""

    def __init__(self):
        """初始化数据"""
        self.db_user_departments = self.calculate_db_user_departments()
        self.backend_user_departments = iam.list_all_subject_department()

    def calculate_db_user_departments(self) -> Dict[str, List[str]]:
        """根据部门和部门用户关系的表数据计算出每个用户的所在的所有部门"""
        # 获取每个部门的祖先
        ancestors_map = defaultdict(list)
        for dept in Department.objects.all():
            ancestors_map[dept.id] = [i["id"] for i in dept.parse_ancestors()]

        # 每个用户的所在的所有部门 (包括部门的祖先)
        user_depts_dict = defaultdict(set)
        for dm in DepartmentMember.objects.all():
            user_depts_dict[dm.username].add(dm.department_id)
            user_depts_dict[dm.username].update(ancestors_map[dm.department_id])

        # 组装返回数据
        return {username: [str(i) for i in depts] for username, depts in user_depts_dict.items() if len(depts) > 0}

    def created_handler(self):
        """后台需要新增的用户部门处理"""
        backend_user_dept_set = {i["id"] for i in self.backend_user_departments}
        created_user_depts = [
            {"id": username, "departments": depts}
            for username, depts in self.db_user_departments.items()
            if username not in backend_user_dept_set
        ]

        if not created_user_depts:
            return

        iam.create_subject_departments_by_auto_paging(created_user_depts)

    def deleted_handler(self):
        """后台需要删除的用户部门处理"""
        db_user_dept_set = set(self.db_user_departments.keys())
        deleted_user_depts = [i["id"] for i in self.backend_user_departments if i["id"] not in db_user_dept_set]

        if not deleted_user_depts:
            return

        iam.delete_subject_departments_by_auto_paging(deleted_user_depts)

    def updated_handler(self):
        """后台需要更新的用户部门处理"""
        updated_user_depts = []
        for user_depts in self.backend_user_departments:
            if user_depts["id"] not in self.db_user_departments:
                continue

            db_depts = self.db_user_departments[user_depts["id"]]
            # 判断是否需要更新
            if set(user_depts["departments"]) == set(db_depts):
                updated_user_depts.append({"id": user_depts["id"], "departments": db_depts})

        if not updated_user_depts:
            return

        iam.update_subject_departments_by_auto_paging(updated_user_depts)

    def sync_to_iam_backend(self):
        """同步 IAM 后台 相关变更"""
        # 新增用户部门
        self.created_handler()
        # 删除用户部门
        self.deleted_handler()
        # 更新用户部门
        self.updated_handler()
