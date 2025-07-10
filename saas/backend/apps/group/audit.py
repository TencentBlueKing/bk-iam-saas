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

from typing import List

from backend.apps.group.models import Group
from backend.audit.audit import DataProvider, NoNeedAuditException, audit_context_getter
from backend.audit.constants import AuditObjectType, AuditSourceType, AuditType
from backend.audit.models import get_event_model
from backend.service.models import Subject


class BaseGroupDataProvider(DataProvider):
    @property
    def group(self):
        return audit_context_getter(self.request, "group")

    @property
    def extra(self):
        return {}  # TODO 按需求提供数据

    @property
    def object_type(self):
        return AuditObjectType.GROUP.value

    @property
    def object_id(self):
        if not self.group:
            raise NoNeedAuditException
        return str(self.group.id)

    @property
    def object_name(self):
        return self.group.name


class GroupCreateAuditProvider(BaseGroupDataProvider):
    type = AuditType.GROUP_CREATE.value


class GroupUpdateAuditProvider(BaseGroupDataProvider):
    type = AuditType.GROUP_UPDATE.value

    @property
    def extra(self):
        return {key: value for key, value in self.request.data.items() if key in {"name", "description"}}


class GroupDeleteAuditProvider(BaseGroupDataProvider):
    type = AuditType.GROUP_DELETE.value


class BaseGroupMemberProvider(BaseGroupDataProvider):
    @property
    def extra(self):
        return {"members": audit_context_getter(self.request, "members")}


class GroupMemberCreateAuditProvider(BaseGroupMemberProvider):
    type = AuditType.GROUP_MEMBER_CREATE.value


class GroupMemberDeleteAuditProvider(BaseGroupMemberProvider):
    type = AuditType.GROUP_MEMBER_DELETE.value


class GroupMemberRenewAuditProvider(BaseGroupMemberProvider):
    type = AuditType.GROUP_MEMBER_RENEW.value


class GroupTemplateCreateAuditProvider(BaseGroupDataProvider):
    type = AuditType.GROUP_TEMPLATE_CREATE.value

    @property
    def extra(self):
        return {"templates": audit_context_getter(self.request, "templates")}


class GroupPolicyUpdateAuditProvider(BaseGroupDataProvider):
    type = AuditType.GROUP_POLICY_UPDATE.value

    @property
    def extra(self):
        policies = audit_context_getter(self.request, "policies")

        return {
            "template_id": audit_context_getter(self.request, "template_id"),
            "system_id": audit_context_getter(self.request, "system_id"),
            "policies": [p.dict() for p in policies],
        }


class GroupTransferAuditProvider(DataProvider):
    type = AuditType.GROUP_TRANSFER.value

    @property
    def object_type(self):
        return self.request.role.type

    @property
    def object_id(self):
        return str(self.request.role.id)

    @property
    def object_name(self):
        return self.request.role.name

    @property
    def extra(self):
        return {
            "group_ids": audit_context_getter(self.request, "group_ids"),
            "role_id": audit_context_getter(self.request, "role_id"),
        }


class BaseGroupPolicyProvider(BaseGroupDataProvider):
    @property
    def extra(self):
        system_id = audit_context_getter(self.request, "system_id")
        policies = audit_context_getter(self.request, "policies")

        return {"system_id": system_id, "policies": [p.dict() for p in policies]}

    @property
    def system_id(self) -> str:
        return audit_context_getter(self.request, "system_id")


class GroupPolicyCreateAuditProvider(BaseGroupPolicyProvider):
    type = AuditType.GROUP_POLICY_CREATE.value


class GroupPolicyDeleteAuditProvider(BaseGroupPolicyProvider):
    type = AuditType.GROUP_POLICY_DELETE.value


def log_group_cleanup_member_audit_event(task_id: str, group: Group, members: List[Subject]):
    """
    用户组清理长时间过期的成员记录审计信息
    """
    Event = get_event_model()  # noqa: N806

    event = Event(
        source_type=AuditSourceType.TASK.value,
        type=AuditType.GROUP_MEMBER_DELETE.value,
        source_data_task_id=task_id,
        username="admin",
        object_type=AuditObjectType.GROUP.value,
        object_id=str(group.id),
        object_name=group.name,
    )

    event.extra = {"members": [m.dict() for m in members]}

    event.save(force_insert=True)
