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

from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from backend.account.permissions import role_perm_class
from backend.apps.role.audit import RoleMemberCreateAuditProvider, RoleMemberDeleteAuditProvider
from backend.apps.role.models import Role
from backend.audit.audit import audit_context_setter, view_audit_decorator
from backend.biz.audit_manager import AuditManagerService
from backend.common.error_codes import error_codes
from backend.service.constants import PermissionCodeEnum, RoleType


class AuditManagerMemberSLZ(serializers.Serializer):
    """审计管理员成员序列化器"""
    username = serializers.CharField(label="用户名", max_length=64)


class AuditManagerBatchMemberSLZ(serializers.Serializer):
    """审计管理员批量成员序列化器"""
    usernames = serializers.ListField(label="用户名列表", child=serializers.CharField(max_length=64), max_length=100)


class AuditManagerViewSet(GenericViewSet):
    """审计管理员成员管理视图"""
    
    permission_classes = [role_perm_class(PermissionCodeEnum.MANAGE_SUPER_MANAGER_MEMBER.value)]
    pagination_class = None
    
    audit_manager_service = AuditManagerService()

    @swagger_auto_schema(
        operation_description="审计管理员成员列表",
        responses={status.HTTP_200_OK: AuditManagerMemberSLZ(label="审计管理员成员", many=True)},
        tags=["role"],
    )
    def list(self, request, *args, **kwargs):
        """获取审计管理员成员列表"""
        members = self.audit_manager_service.list_audit_manager_members()
        data = [{"username": username} for username in members]
        return Response(data)

    @swagger_auto_schema(
        operation_description="添加审计管理员成员",
        request_body=AuditManagerMemberSLZ(label="审计管理员成员"),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["role"],
    )
    @view_audit_decorator(RoleMemberCreateAuditProvider)
    def create(self, request, *args, **kwargs):
        """添加审计管理员成员"""
        serializer = AuditManagerMemberSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        username = serializer.validated_data["username"]
        
        success = self.audit_manager_service.add_audit_manager_member(username)
        
        if not success:
            raise error_codes.CONFLICT.format(message=f"用户 {username} 已是审计管理员")
        
        role = Role.objects.get(type=RoleType.AUDIT_MANAGER.value)
        audit_context_setter(role=role, members=[username])
        
        return Response({})

    @swagger_auto_schema(
        operation_description="批量添加审计管理员成员",
        request_body=AuditManagerBatchMemberSLZ(label="审计管理员批量成员"),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["role"],
    )
    @view_audit_decorator(RoleMemberCreateAuditProvider)
    def batch_create(self, request, *args, **kwargs):
        """批量添加审计管理员成员"""
        serializer = AuditManagerBatchMemberSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        usernames = serializer.validated_data["usernames"]
        
        result = self.audit_manager_service.batch_add_audit_manager_members(usernames)
        
        role = Role.objects.get(type=RoleType.AUDIT_MANAGER.value)
        audit_context_setter(role=role, members=result["success"])
        
        return Response({
            "success": result["success"],
            "failed": result["failed"]
        })

    @swagger_auto_schema(
        operation_description="删除审计管理员成员",
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["role"],
    )
    @view_audit_decorator(RoleMemberDeleteAuditProvider)
    def destroy(self, request, *args, **kwargs):
        """删除审计管理员成员"""
        username = kwargs.get("pk")
        
        success = self.audit_manager_service.remove_audit_manager_member(username)
        
        if not success:
            raise error_codes.NOT_FOUND.format(message=f"用户 {username} 不是审计管理员")
        
        role = Role.objects.get(type=RoleType.AUDIT_MANAGER.value)
        audit_context_setter(role=role, members=[username])
        
        return Response({})
