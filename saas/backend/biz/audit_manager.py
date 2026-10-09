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

from typing import List
from django.db import transaction

from backend.apps.role.models import Role, RoleUser
from backend.service.constants import RoleType


class AuditManagerService:
    """审计管理员服务"""

    def get_audit_manager_role(self) -> Role:
        return Role.objects.get(type=RoleType.AUDIT_MANAGER.value)

    def is_audit_manager(self, username: str) -> bool:
        role = self.get_audit_manager_role()
        return RoleUser.objects.filter(role_id=role.id, username=username).exists()

    def list_audit_manager_members(self) -> List[str]:
        role = self.get_audit_manager_role()
        return list(RoleUser.objects.filter(role_id=role.id).values_list("username", flat=True))

    @transaction.atomic
    def add_audit_manager_member(self, username: str) -> bool:
        role = self.get_audit_manager_role()
        
        if RoleUser.objects.filter(role_id=role.id, username=username).exists():
            return False
        
        RoleUser.objects.create(role_id=role.id, username=username)
        return True

    @transaction.atomic
    def remove_audit_manager_member(self, username: str) -> bool:
        role = self.get_audit_manager_role()
        deleted_count, _ = RoleUser.objects.filter(role_id=role.id, username=username).delete()
        return deleted_count > 0

    @transaction.atomic
    def batch_add_audit_manager_members(self, usernames: List[str]) -> dict:
        role = self.get_audit_manager_role()

        unique_usernames = list(dict.fromkeys(usernames))

        existing_usernames = set(
            RoleUser.objects.filter(role_id=role.id, username__in=unique_usernames).values_list("username", flat=True)
        )

        new_usernames = [username for username in unique_usernames if username not in existing_usernames]

        if new_usernames:
            RoleUser.objects.bulk_create([
                RoleUser(role_id=role.id, username=username)
                for username in new_usernames
            ])

        return {
            "success": new_usernames,
            "failed": list(existing_usernames)
        }
