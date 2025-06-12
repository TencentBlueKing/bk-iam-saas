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

from backend.apps.subject.audit import BaseSubjectProvider
from backend.audit.audit import NoNeedAuditException, audit_context_getter
from backend.audit.constants import AuditType
from backend.service.constants import ADMIN_USER, SubjectType
from backend.service.models import Subject

from .constants import OperateEnum


class SubjectPolicyGrantOrRevokeAuditProvider(BaseSubjectProvider):
    @property
    def subject(self) -> Subject:
        subject = audit_context_getter(self.request, "subject")
        if subject.type == SubjectType.USER.value and subject.id.lower() == ADMIN_USER:
            raise NoNeedAuditException

        return subject

    @property
    def type(self):
        operate = audit_context_getter(self.request, "operate")

        if operate == OperateEnum.REVOKE.value:
            return AuditType.USER_POLICY_UPDATE.value

        if operate == OperateEnum.GRANT.value:
            return AuditType.USER_POLICY_CREATE.value

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
