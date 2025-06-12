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

from backend.apps.role.audit import BaseRoleDataProvider
from backend.audit.audit import audit_context_getter
from backend.audit.constants import AuditType


class ApprovalProcessGlobalConfigAuditProvider(BaseRoleDataProvider):
    type = AuditType.APPROVAL_GLOBAL_UPDATE.value

    @property
    def extra(self):
        return {
            "type": audit_context_getter(self.request, "type"),
            "process_id": audit_context_getter(self.request, "process_id"),
        }


class ApprovalProcessActionAuditProvider(BaseRoleDataProvider):
    type = AuditType.APPROVAL_ACTION_UPDATE.value

    @property
    def system_id(self) -> str:
        return audit_context_getter(self.request, "system_id")

    @property
    def extra(self):
        return {
            "system_id": audit_context_getter(self.request, "system_id"),
            "action_ids": audit_context_getter(self.request, "action_ids"),
            "process_id": audit_context_getter(self.request, "process_id"),
        }


class ActionSensitivityLevelAuditProvider(BaseRoleDataProvider):
    type = AuditType.ACTION_SENSITIVITY_LEVEL_UPDATE.value

    @property
    def system_id(self) -> str:
        return audit_context_getter(self.request, "system_id")

    @property
    def extra(self):
        return {
            "system_id": audit_context_getter(self.request, "system_id"),
            "action_ids": audit_context_getter(self.request, "action_ids"),
            "sensitivity_level": audit_context_getter(self.request, "sensitivity_level"),
        }


class ApprovalProcessGroupAuditProvider(BaseRoleDataProvider):
    type = AuditType.APPROVAL_GROUP_UPDATE.value

    @property
    def extra(self):
        return {
            "group_ids": audit_context_getter(self.request, "group_ids"),
            "process_id": audit_context_getter(self.request, "process_id"),
        }
