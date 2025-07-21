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

from backend.apps.organization.models import Department, User
from backend.audit.audit import DataProvider, NoNeedAuditException, audit_context_getter
from backend.audit.constants import AuditObjectType, AuditSourceType, AuditType
from backend.audit.models import get_event_model
from backend.service.constants import SubjectType
from backend.service.models import Subject


class BaseSubjectProvider(DataProvider):
    @property
    def subject(self) -> Subject:
        return audit_context_getter(self.request, "subject")

    @property
    def extra(self):
        return {}  # TODO 按需求提供数据

    @property
    def object_type(self):
        return self.subject.type

    @property
    def object_id(self):
        return self.subject.id

    @property
    def object_name(self):
        if self.subject.type == SubjectType.DEPARTMENT.value:
            department = Department.objects.filter(id=self.subject.id).first()
            return department.full_name if department else ""

        if self.subject.type == SubjectType.USER.value:
            user = User.objects.filter(username=self.subject.id).first()
            return user.display_name if user else self.subject.id

        return ""


class SubjectPolicyDeleteAuditProvider(BaseSubjectProvider):
    @property
    def type(self):
        if self.subject.type == SubjectType.USER.value:
            return AuditType.USER_POLICY_DELETE.value

        return ""

    @property
    def extra(self):
        system_id = audit_context_getter(self.request, "system_id")
        policies = audit_context_getter(self.request, "policies")

        if not policies:
            raise NoNeedAuditException

        return {"system_id": system_id, "policies": [p.dict() for p in policies]}

    @property
    def system_id(self) -> str:
        return audit_context_getter(self.request, "system_id")


class SubjectTemporaryPolicyDeleteAuditProvider(SubjectPolicyDeleteAuditProvider):
    @property
    def type(self):
        return AuditType.USER_TEMPORARY_POLICY_DELETE.value


# TODO: [重构] log_user_cleanup_policy_audit_event 放到 apps.user.audit 里
def log_user_cleanup_policy_audit_event(task_id: str, user: User, system_id: str, policies: List):
    """
    用户清理长时间过期策略记录审计
    """
    Event = get_event_model()  # noqa: N806

    event = Event(
        tenant_id=user.tenant_id,
        source_type=AuditSourceType.TASK.value,
        type=AuditType.USER_POLICY_UPDATE.value,
        source_data_task_id=task_id,
        username="admin",
        system_id=system_id,
        object_type=AuditObjectType.USER.value,
        object_id=user.username,
        object_name=user.display_name,
    )

    event.extra = {"system_id": system_id, "policies": [p.dict() for p in policies]}

    event.save(force_insert=True)
