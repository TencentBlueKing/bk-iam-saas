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

from backend.audit.audit import DataProvider, audit_context_getter
from backend.audit.constants import AuditObjectType, AuditType


class BaseSubjectTemplateDataProvider(DataProvider):
    @property
    def template(self):
        return audit_context_getter(self.request, "template")

    @property
    def extra(self):
        return {}  # TODO 按需求提供数据

    @property
    def object_type(self):
        return AuditObjectType.SUBJECT_TEMPLATE.value

    @property
    def object_id(self):
        return str(self.template.id)

    @property
    def object_name(self):
        return self.template.name


class SubjectTemplateCreateAuditProvider(BaseSubjectTemplateDataProvider):
    type = AuditType.SUBJECT_TEMPLATE_CREATE.value


class SubjectTemplateUpdateAuditProvider(BaseSubjectTemplateDataProvider):
    type = AuditType.SUBJECT_TEMPLATE_UPDATE.value

    @property
    def extra(self):
        return {key: value for key, value in self.request.data.items() if key in {"name", "description"}}


class SubjectTemplateDeleteAuditProvider(BaseSubjectTemplateDataProvider):
    type = AuditType.SUBJECT_TEMPLATE_DELETE.value


class BaseSubjectTemplateMemberProvider(BaseSubjectTemplateDataProvider):
    @property
    def extra(self):
        return {"subjects": audit_context_getter(self.request, "subjects")}


class SubjectTemplateMemberCreateAuditProvider(BaseSubjectTemplateMemberProvider):
    type = AuditType.SUBJECT_TEMPLATE_MEMBER_CREATE.value


class SubjectTemplateMemberDeleteAuditProvider(BaseSubjectTemplateMemberProvider):
    type = AuditType.SUBJECT_TEMPLATE_MEMBER_DELETE.value


class SubjectTemplateGroupDeleteAuditProvider(BaseSubjectTemplateDataProvider):
    type = AuditType.SUBJECT_TEMPLATE_GROUP_DELETE.value

    @property
    def extra(self):
        group = audit_context_getter(self.request, "group")
        if not group:
            return {}
        return {
            "group": {
                "id": group.id,
                "name": group.name,
            }
        }
