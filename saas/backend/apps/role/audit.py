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

from backend.audit.audit import DataProvider, NoNeedAuditException, audit_context_getter
from backend.audit.constants import AuditObjectType, AuditType


class BaseRoleDataProvider(DataProvider):
    @property
    def role(self):
        return audit_context_getter(self.request, "role")

    @property
    def extra(self):
        return {}  # TODO 按需求提供数据

    @property
    def object_type(self):
        return AuditObjectType.ROLE.value

    @property
    def object_id(self):
        if not self.role:
            raise NoNeedAuditException
        return str(self.role.id)

    @property
    def object_name(self):
        return self.role.name


class RoleCreateAuditProvider(BaseRoleDataProvider):
    type = AuditType.ROLE_CREATE.value


class RoleUpdateAuditProvider(BaseRoleDataProvider):
    type = AuditType.ROLE_UPDATE.value

    @property
    def extra(self):
        return {key: value for key, value in self.request.data.items() if key in {"name", "description"}}


class RoleDeleteAuditProvider(BaseRoleDataProvider):
    type = AuditType.ROLE_DELETE.value


class RoleMemberUpdateAuditProvider(BaseRoleDataProvider):
    type = AuditType.ROLE_MEMBER_UPDATE.value

    @property
    def extra(self):
        return {"members": self.request.data["members"]}


class BaseRoleMemberProvider(BaseRoleDataProvider):
    @property
    def extra(self):
        return {"members": audit_context_getter(self.request, "members")}


class RoleMemberCreateAuditProvider(BaseRoleMemberProvider):
    type = AuditType.ROLE_MEMBER_CREATE.value


class RoleMemberDeleteAuditProvider(BaseRoleMemberProvider):
    type = AuditType.ROLE_MEMBER_DELETE.value


class RolePolicyAuditProvider(BaseRoleDataProvider):
    @property
    def type(self):
        enable = audit_context_getter(self.request, "enable")
        if enable:
            return AuditType.ROLE_MEMBER_POLICY_CREATE.value

        return AuditType.ROLE_MEMBER_POLICY_DELETE.value

    @property
    def extra(self):
        username = audit_context_getter(self.request, "username")
        if username:
            return {"username": username}

        return {}


class BaseCommonActionCreateProvider(BaseRoleDataProvider):
    @property
    def extra(self):
        ca = audit_context_getter(self.request, "commonaction")

        return {"commonaction": [{"type": AuditObjectType.COMMONACTION.value, "id": str(ca.id), "name": ca.name}]}


class CommonActionCreateAuditProvider(BaseCommonActionCreateProvider):
    type = AuditType.ROLE_COMMONACTION_CREATE.value


class CommonActionDeleteAuditProvider(BaseCommonActionCreateProvider):
    type = AuditType.ROLE_COMMONACTION_DELETE.value


class RoleGroupRenewAuditProvider(BaseRoleDataProvider):
    type = AuditType.ROLE_GROUP_RENEW.value

    @property
    def extra(self):
        members = audit_context_getter(self.request, "members")
        return {"members": members}


class RoleUpdateGroupConfigProvider(BaseRoleDataProvider):
    type = AuditType.ROLE_UPDATE_GROUP_CONFIG.value

    @property
    def extra(self):
        return {"data": audit_context_getter(self.request, "data")}


class RoleUpdateNotificationConfigProvider(BaseRoleDataProvider):
    type = AuditType.ROLE_UPDATE_NOTIFICATION_CONFIG.value

    @property
    def extra(self):
        return {"data": audit_context_getter(self.request, "data")}
