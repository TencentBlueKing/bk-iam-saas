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

from rest_framework import permissions

from backend.apps.role.models import RoleUser
from backend.biz.audit_manager import AuditManagerService
from backend.biz.role import get_super_manager


class IsAuditManagerOrSuperManager(permissions.BasePermission):
    """审计管理员或超级管理员权限检查"""

    def has_permission(self, request, view):
        username = request.user.username
        
        # 检查是否为超级管理员
        super_manager = get_super_manager()
        if super_manager and RoleUser.objects.filter(role_id=super_manager.id, username=username).exists():
            return True
        
        # 检查是否为审计管理员
        audit_manager_service = AuditManagerService()
        if audit_manager_service.is_audit_manager(username):
            return True
        
        return False
