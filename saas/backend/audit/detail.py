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

from typing import Dict, List, Type

from django.utils.translation import gettext as _
from pydantic.tools import parse_obj_as

from backend.apps.group.models import Group
from backend.apps.organization.models import User
from backend.apps.role.models import Role
from backend.apps.subject_template.models import SubjectTemplate
from backend.apps.template.models import PermTemplate
from backend.audit.models import Event
from backend.biz.subject import SubjectInfoList
from backend.biz.system import SystemBiz
from backend.service.action import ActionService
from backend.service.approval import ApprovalProcessService
from backend.service.constants import ApplicationType, GroupMemberType
from backend.service.models import Subject
from backend.util.time import timestamp_to_local

from .constants import AuditObjectType, AuditType


class BaseProvider:
    def __init__(self, event: Event):
        self.event = event

    @property
    def description(self) -> str:
        return ""

    @property
    def sub_objects(self) -> List:
        return []

    @property
    def extra_info(self) -> Dict:
        return {}


class GroupTemplateProvider(BaseProvider):
    @property
    def sub_objects(self) -> List:
        templates = self.event.extra["templates"]
        perm_templates = PermTemplate.objects.filter(id__in=[t["template_id"] for t in templates])
        data = [{"type": AuditObjectType.TEMPLATE.value, "id": t.id, "name": t.name} for t in perm_templates]

        system_list = SystemBiz().new_system_list()
        for t in templates:
            if t["template_id"] != 0:
                continue
            system = system_list.get(t["system_id"])
            name = system.name if system else t["system_id"]
            data.append({"type": AuditObjectType.TEMPLATE.value, "id": t["template_id"], "name": f"自定义：{name}"})

        return data


class GroupMemberProvider(BaseProvider):
    @property
    def sub_objects(self) -> List:
        subject_list = SubjectInfoList(
            parse_obj_as(
                List[Subject],
                [one for one in self.event.extra["members"] if one["type"] != GroupMemberType.TEMPLATE.value],
            )
        )
        objects = []
        for subject in subject_list.subjects:
            data = {"type": subject.type, "id": subject.id, "name": subject.name}

            if subject.type == AuditObjectType.DEPARTMENT.value:
                data["name"] = subject.full_name
            objects.append(data)

        subject_template_ids = [
            one["id"] for one in self.event.extra["members"] if one["type"] == GroupMemberType.TEMPLATE.value
        ]
        if not subject_template_ids:
            return objects

        subject_templates = SubjectTemplate.objects.filter(id__in=subject_template_ids)
        for subject_template in subject_templates:
            data = {"type": GroupMemberType.TEMPLATE.value, "id": subject_template.id, "name": subject_template.name}
            objects.append(data)

        return objects


class GroupUpdateProvider(BaseProvider):
    @property
    def description(self) -> str:
        extra = self.event.extra
        return _("名称：{}, 描述：{}").format(extra["name"], extra["description"])


class GroupTransferProvider(BaseProvider):
    @property
    def sub_objects(self) -> List:
        extra = self.event.extra

        groups = Group.objects.filter(id__in=extra["group_ids"])
        role = Role.objects.filter(id=extra["role_id"]).first()

        objects = [{"type": AuditObjectType.GROUP.value, "id": str(g.id), "name": g.name} for g in groups]

        if role:
            objects.append({"type": AuditObjectType.ROLE.value, "id": str(role.id), "name": role.name})

        return objects


class SubjectPoliciesProvider(BaseProvider):
    biz = SystemBiz()

    @property
    def extra_info(self) -> Dict:
        extra = self.event.extra
        system_id = extra["system_id"]
        system = self.biz.get(system_id)
        policies = extra["policies"]
        for p in policies:
            if "expired_at" in p and p["expired_at"]:
                p["expired_display"] = timestamp_to_local(p["expired_at"])

        return {"system": {"id": system.id, "name": system.name, "name_en": system.name_en}, "policies": policies}


class SubjectPoliciesUpdateProvider(BaseProvider):
    biz = SystemBiz()

    @property
    def extra_info(self) -> Dict:
        extra = self.event.extra
        system_id = extra["system_id"]
        system = self.biz.get(system_id)
        policies = extra["policies"]
        for p in policies:
            if "expired_at" in p and p["expired_at"]:
                p["expired_display"] = timestamp_to_local(p["expired_at"])

        template_id = extra["template_id"]
        data = {"system": {"id": system.id, "name": system.name, "name_en": system.name_en}, "policies": policies}
        if template_id == 0:
            return data

        template = PermTemplate.objects.filter(id=template_id).first()
        data["template"] = {"id": template_id, "name": template.name if template else ""}
        return data


class TemplateUpdateProvider(BaseProvider):
    @property
    def description(self) -> str:
        extra = self.event.extra
        return _("名称：{}, 描述：{}").format(extra["name"], extra["description"])

    @property
    def extra_info(self) -> Dict:
        extra = self.event.extra
        return {"version": extra["version"]}


class TemplateMemberProvider(BaseProvider):
    @property
    def sub_objects(self) -> List:
        extra = self.event.extra
        group_ids = [m["id"] for m in extra["members"]]

        groups = Group.objects.filter(id__in=group_ids)

        return [{"type": AuditObjectType.GROUP.value, "id": str(g.id), "name": g.name} for g in groups]

    @property
    def extra_info(self) -> Dict:
        extra = self.event.extra
        return {"version": extra["version"]} if "version" in extra else {}


class RoleUpdateProvider(BaseProvider):
    @property
    def description(self) -> str:
        extra = self.event.extra
        return _("名称：{}, 描述：{}").format(extra["name"], extra["description"])


class RoleMemberProvider(BaseProvider):
    @property
    def sub_objects(self) -> List:
        extra = self.event.extra
        members = extra["members"]

        users = User.objects.filter(username__in=members)
        return [{"type": AuditObjectType.USER.value, "id": user.username, "name": user.display_name} for user in users]


class RoleMemberPolicyProvider(BaseProvider):
    @property
    def description(self) -> str:
        extra = self.event.extra
        desc = ""
        if "username" in extra:
            desc += f"对用户：{extra['username']} "

        if self.event.type == AuditType.ROLE_MEMBER_POLICY_CREATE:
            desc = "授权"
        elif self.event.type == AuditType.ROLE_MEMBER_POLICY_DELETE:
            desc = "回收权限"

        return desc


class RoleCommonActionProvider(BaseProvider):
    @property
    def sub_objects(self) -> List:
        extra = self.event.extra
        return extra["commonaction"]


class RoleGroupRenewProvider(BaseProvider):
    @property
    def extra_info(self) -> Dict:
        members = self.event.extra["members"]

        groups = Group.objects.filter(id__in=[int(m["parent_id"]) for m in members])
        group_dict = {str(group.id): group for group in groups}
        users = User.objects.filter(username__in=[m["id"] for m in members])
        user_dict = {user.username: user for user in users}

        data = []
        for m in members:
            user = user_dict.get(m["id"])
            group = group_dict.get(m["parent_id"])

            data.append(
                {
                    "group": {"id": int(m["parent_id"]), "name": group.name if group else m["parent_id"]},
                    "user": {"id": m["id"], "name": user.display_name if user else m["id"]},
                    "expired_at": m["expired_at"],
                    "expired_at_display": timestamp_to_local(m["expired_at"]),
                }
            )

        return {"members": data}


class RoleConfigProvider(BaseProvider):
    @property
    def extra_info(self) -> Dict:
        return {"data": self.event.extra["data"]}


class ApprovalNameMixin:
    event: Event

    @property
    def approval_svc(self):
        return ApprovalProcessService(self.event.tenant_id)

    def get_process_name(self, process_id):
        return self.approval_svc.get_process_name(process_id)


class ApprovalGlobalProvider(ApprovalNameMixin, BaseProvider):
    @property
    def description(self) -> str:
        type_ = self.event.extra["type"]
        type_name = dict(ApplicationType.get_choices()).get(type_)
        process_id = self.event.extra["process_id"]
        process_name = self.get_process_name(process_id)
        return f"设置 [{type_name}] 类型全局审批流程：{process_name}(#{process_id})"


class ApprovalActionProvider(ApprovalNameMixin, BaseProvider):
    system_biz = SystemBiz()
    action_svc = ActionService()

    @property
    def description(self) -> str:
        system_id = self.event.extra["system_id"]
        system = self.system_biz.get(system_id)
        process_id = self.event.extra["process_id"]
        process_name = self.get_process_name(process_id)
        return f"设置 [{system.name}] 系统操作审批流程：{process_name}(#{process_id})"

    @property
    def sub_objects(self) -> List:
        system_id = self.event.extra["system_id"]
        action_ids = self.event.extra["action_ids"]
        actions = self.action_svc.new_action_list(system_id).filter(action_ids)
        return [{"type": AuditObjectType.ACTION.value, "id": ac.id, "name": ac.name} for ac in actions]


class ActionSensitivityLevelProvider(BaseProvider):
    system_biz = SystemBiz()
    action_svc = ActionService()

    @property
    def description(self) -> str:
        system_id = self.event.extra["system_id"]
        system = self.system_biz.get(system_id)
        sensitivity_level = self.event.extra["sensitivity_level"]
        return f"设置 [{system.name}] 系统操作敏感等级：{sensitivity_level}"

    @property
    def sub_objects(self) -> List:
        system_id = self.event.extra["system_id"]
        action_ids = self.event.extra["action_ids"]
        actions = self.action_svc.new_action_list(system_id).filter(action_ids)
        return [{"type": AuditObjectType.ACTION.value, "id": ac.id, "name": ac.name} for ac in actions]


class ApprovalGroupProvider(ApprovalNameMixin, BaseProvider):
    @property
    def description(self) -> str:
        process_id = self.event.extra["process_id"]
        process_name = self.get_process_name(process_id)
        return f"设置用户组审批流程：{process_name}(#{process_id})"

    @property
    def sub_objects(self) -> List:
        group_ids = self.event.extra["group_ids"]
        groups = Group.objects.filter(id__in=group_ids)
        return [{"type": AuditObjectType.GROUP.value, "id": str(group.id), "name": group.name} for group in groups]


class SubjectTemplateUpdateProvider(BaseProvider):
    @property
    def description(self) -> str:
        extra = self.event.extra
        return _("名称：{}, 描述：{}").format(extra["name"], extra["description"])


class SubjectTemplateMemberProvider(BaseProvider):
    @property
    def sub_objects(self) -> List:
        subject_list = SubjectInfoList(parse_obj_as(List[Subject], self.event.extra["subjects"]))
        objects = []
        for subject in subject_list.subjects:
            data = {"type": subject.type, "id": subject.id, "name": subject.name}

            if subject.type == AuditObjectType.DEPARTMENT.value:
                data["name"] = subject.full_name
            objects.append(data)
        return objects


class SubjectTemplateGroupProvider(BaseProvider):
    @property
    def sub_objects(self) -> List:
        group = self.event.extra.get("group", None)
        if not group:
            return []
        return [{"type": AuditObjectType.GROUP.value, "id": str(group.id), "name": group.name}]


class EventDetailExtra:
    provider_map: Dict[str, Type[BaseProvider]] = {
        # group
        AuditType.GROUP_CREATE.value: BaseProvider,
        AuditType.GROUP_UPDATE.value: GroupUpdateProvider,
        AuditType.GROUP_DELETE.value: BaseProvider,
        AuditType.GROUP_MEMBER_CREATE.value: GroupMemberProvider,
        AuditType.GROUP_MEMBER_DELETE.value: GroupMemberProvider,
        AuditType.GROUP_MEMBER_RENEW.value: GroupMemberProvider,
        AuditType.GROUP_TEMPLATE_CREATE.value: GroupTemplateProvider,
        AuditType.GROUP_TRANSFER.value: GroupTransferProvider,
        AuditType.GROUP_POLICY_CREATE.value: SubjectPoliciesProvider,
        AuditType.GROUP_POLICY_DELETE.value: SubjectPoliciesProvider,
        AuditType.GROUP_POLICY_UPDATE.value: SubjectPoliciesUpdateProvider,
        # department/user
        AuditType.USER_POLICY_UPDATE.value: SubjectPoliciesProvider,
        AuditType.USER_POLICY_CREATE.value: SubjectPoliciesProvider,
        AuditType.USER_POLICY_DELETE.value: SubjectPoliciesProvider,
        AuditType.USER_TEMPORARY_POLICY_CREATE.value: SubjectPoliciesProvider,
        AuditType.USER_TEMPORARY_POLICY_DELETE.value: SubjectPoliciesProvider,
        # template
        AuditType.TEMPLATE_CREATE.value: BaseProvider,
        AuditType.TEMPLATE_DELETE.value: BaseProvider,
        AuditType.TEMPLATE_UPDATE.value: TemplateUpdateProvider,
        AuditType.TEMPLATE_MEMBER_DELETE.value: TemplateMemberProvider,
        AuditType.TEMPLATE_PREUPDATE_CREATE.value: BaseProvider,
        AuditType.TEMPLATE_PREUPDATE_DELETE.value: BaseProvider,
        AuditType.TEMPLATE_UPDATE_COMMIT.value: BaseProvider,
        # role
        AuditType.ROLE_CREATE.value: BaseProvider,
        AuditType.ROLE_UPDATE.value: RoleUpdateProvider,
        AuditType.ROLE_MEMBER_UPDATE.value: RoleMemberProvider,
        AuditType.ROLE_MEMBER_CREATE.value: RoleMemberProvider,
        AuditType.ROLE_MEMBER_DELETE.value: RoleMemberProvider,
        AuditType.ROLE_MEMBER_POLICY_CREATE.value: RoleMemberPolicyProvider,
        AuditType.ROLE_MEMBER_POLICY_DELETE.value: RoleMemberPolicyProvider,
        AuditType.ROLE_COMMONACTION_CREATE.value: RoleCommonActionProvider,
        AuditType.ROLE_COMMONACTION_DELETE.value: RoleCommonActionProvider,
        AuditType.ROLE_GROUP_RENEW.value: RoleGroupRenewProvider,
        AuditType.ROLE_UPDATE_GROUP_CONFIG.value: RoleConfigProvider,
        AuditType.ROLE_UPDATE_NOTIFICATION_CONFIG.value: RoleConfigProvider,
        # approval
        AuditType.APPROVAL_GLOBAL_UPDATE.value: ApprovalGlobalProvider,
        AuditType.APPROVAL_ACTION_UPDATE.value: ApprovalActionProvider,
        AuditType.APPROVAL_GROUP_UPDATE.value: ApprovalGroupProvider,
        AuditType.ACTION_SENSITIVITY_LEVEL_UPDATE.value: ActionSensitivityLevelProvider,
        # subject template
        AuditType.SUBJECT_TEMPLATE_CREATE.value: BaseProvider,
        AuditType.SUBJECT_TEMPLATE_UPDATE.value: SubjectTemplateUpdateProvider,
        AuditType.SUBJECT_TEMPLATE_DELETE.value: BaseProvider,
        AuditType.SUBJECT_TEMPLATE_MEMBER_CREATE.value: SubjectTemplateMemberProvider,
        AuditType.SUBJECT_TEMPLATE_MEMBER_DELETE.value: SubjectTemplateMemberProvider,
        AuditType.SUBJECT_TEMPLATE_GROUP_DELETE.value: SubjectTemplateGroupProvider,
    }

    def __init__(self, event: Event):
        self.provider = self.provider_map[event.type](event)

    @property
    def description(self) -> str:
        return self.provider.description

    @property
    def sub_objects(self) -> List:
        return self.provider.sub_objects

    @property
    def extra_info(self) -> Dict:
        return self.provider.extra_info
