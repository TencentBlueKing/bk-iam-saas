# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-权限中心(BlueKing-IAM) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

所有组织架构同步操作 统一处理
"""
import datetime

from backend.apps.organization.constants import NEW_USER_AUTO_SYNC_COUNT_LIMIT
from backend.apps.organization.models import Department, DepartmentMember, SubjectToDelete, User
from backend.component import iam, usermgr
from backend.service.constants import SubjectType


class Syncer:
    """
    组织架构同步
    需要特别注意同步任务间是否有冲突
    """

    def sync_single_user(self, username):
        """
        单一用户同步（后续可以添加with_relation=True参数同步用户的相关部门和leader等）
        # NOTE：被migration(organization.0004_auto_20201230_1653)调用到了
        # 如果有调整，需要注意是否需要调整migration，避免出现循环依赖导致migrate失败
        # 目前依赖1张表：User
        """
        # 1. 查询用户是否在DB
        if User.objects.filter(username=username).exists():
            # 已存在则不需要再同步
            return
        # TODO: 考虑并发情况，需要添加分布式锁
        # 2. 查询UserMgr API
        user_info = usermgr.retrieve_user(
            username, fields="id,username,display_name,staff_status,category_id,departments"
        )
        # 3. 同步到DB
        user, is_created = User.objects.get_or_create(
            id=user_info["id"],
            defaults={
                "username": user_info["username"],
                "display_name": user_info["display_name"] or user_info["username"],
                "staff_status": user_info["staff_status"],
                "category_id": user_info["category_id"],
            },
        )
        if not is_created:
            return

        # 4. 同步到IAM后台
        iam.create_subjects([{"type": "user", "id": user.username, "name": user.display_name}])

        # 5. 同步部门
        department_ids = [one["id"] for one in user_info["departments"]]
        if not department_ids:
            return

        departments = Department.objects.filter(id__in=department_ids)
        if not departments:
            return

        # 创建用户与部门关系
        DepartmentMember.objects.bulk_create(
            [DepartmentMember(department_id=department.id, user_id=user_info["id"]) for department in departments]
        )

        department_id_set = set(department_ids)
        for dept in departments:
            for i in dept.parse_ancestors():
                department_id_set.add(i["id"])

        iam.create_subject_departments_by_auto_paging(
            [{"id": user.username, "departments": [str(_id) for _id in department_id_set]}]
        )

    def sync_new_users(self):
        """
        执行新增用户同步
        1. 获取需要新增的用户列表
        2. 如果用户列表大于一定数量，则使用全量同步的方式（评估1分钟内最多同步多少个用户）
        3. 小于一定数量的新增用户，则直接单用户同步
        """
        # 查询5分钟内新增用户
        users = usermgr.list_new_user(datetime.datetime.utcnow(), 20)
        # 如果没有则无需执行
        if not users:
            return

        # 去除已存在的用户
        exist_users = set(User.objects.filter(id__in=[u["id"] for u in users]).values_list("id", flat=True))
        users = [u for u in users if u["id"] not in exist_users]
        # 执行用户同步
        created_users = [
            User(
                id=user["id"],
                username=user["username"],
                display_name=user["display_name"],
                staff_status=user["staff_status"],
                category_id=user["category_id"],
            )
            for user in users
        ]
        # 没有需要新建的，直接返回
        if len(created_users) == 0:
            return
        # 对于新增用户，执行对应变更
        User.objects.bulk_create(created_users, batch_size=1000)
        # 后台新建
        iam.create_subjects([{"type": "user", "id": user["username"], "name": user["display_name"]} for user in users])

        # 移除待删除的用户
        SubjectToDelete.objects.filter(
            subject_type=SubjectType.USER.value, subject_id__in=[u.username for u in created_users]
        ).delete()

        # 如果用户大于一定量，则直接全量同步
        if len(created_users) > NEW_USER_AUTO_SYNC_COUNT_LIMIT:
            from backend.apps.organization.tasks import sync_organization

            sync_organization.delay()

    # def sync_full_organization(self):
    #     # TODO: 重构时将 backend.apps.organization.tasks里的全量同步迁移到这里
    #     pass
