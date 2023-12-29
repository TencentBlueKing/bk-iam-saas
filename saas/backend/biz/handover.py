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

from abc import ABC, abstractmethod
from typing import List

from backend.apps.handover.constants import HandoverTaskStatus
from backend.apps.handover.models import HandoverTask
from backend.apps.role.models import Role
from backend.audit.audit import log_group_event, log_role_event, log_subject_template_event, log_user_event
from backend.audit.constants import AuditSourceType, AuditType
from backend.biz.group import GroupBiz
from backend.biz.helper import RoleWithPermGroupBiz
from backend.biz.policy import PolicyOperationBiz, PolicyQueryBiz
from backend.biz.role import RoleBiz
from backend.biz.subject_template import SubjectTemplateBiz
from backend.service.constants import RoleType
from backend.service.models import Subject


class BaseHandoverHandler(ABC):
    def handler(self):
        try:
            self.grant_permission()
            self.revoke_permission()
        except Exception as e:  # pylint: disable=broad-except
            self._set_status(status=HandoverTaskStatus.FAILED.value, error_info=str(e))
            return False

        self._set_status(status=HandoverTaskStatus.SUCCEED.value)
        return True

    def _set_status(self, status, error_info=""):
        HandoverTask.objects.filter(id=self.handover_task_id).update(status=status, error_info=error_info)

    @abstractmethod
    def grant_permission(self):
        pass

    @abstractmethod
    def revoke_permission(self):
        pass


class GroupHandoverHandler(BaseHandoverHandler):
    biz = GroupBiz()

    def __init__(self, handover_task_id, handover_from, handover_to, object_detail):
        self.handover_task_id = handover_task_id

        self.grant_subject = Subject.from_username(handover_to)
        self.remove_subject = Subject.from_username(handover_from)

        self.group_id = object_detail["id"]
        self.expired_at = object_detail["expired_at"]

    def grant_permission(self):
        # TODO 需不需要校验？
        # GroupCheckBiz().check_member_count(group_id, len(grant_subject))    # 检查用户组成员数量未超限
        # GroupCheckBiz().check_subject_group_limit()   # 检查subject授权的group数量是否超限
        self.biz.add_members(group_id=int(self.group_id), members=[self.grant_subject], expired_at=self.expired_at)

        # 审计
        log_group_event(
            AuditType.GROUP_MEMBER_CREATE.value,
            self.grant_subject,
            [int(self.group_id)],
            username=self.remove_subject.id,
            source_type=AuditSourceType.HANDOVER.value,
        )

    def revoke_permission(self):
        self.biz.remove_members(group_id=str(self.group_id), subjects=[self.remove_subject])


class CustomHandoverHandler(BaseHandoverHandler):
    query_biz = PolicyQueryBiz()
    operation_biz = PolicyOperationBiz()

    def __init__(self, handover_task_id, handover_from, handover_to, object_detail):
        self.handover_task_id = handover_task_id

        self.grant_subject = Subject.from_username(handover_to)
        self.remove_subject = Subject.from_username(handover_from)

        self.system_id = object_detail["id"]
        self.policy_ids = object_detail["policy_ids"]

    def _get_subject_policies(self):
        policies = self.query_biz.list_by_subject(self.system_id, self.remove_subject)
        return [p for p in policies if p.policy_id in self.policy_ids]

    def grant_permission(self):
        policies = self._get_subject_policies()
        self.operation_biz.alter(system_id=self.system_id, subject=self.grant_subject, policies=policies)

        # 审计
        log_user_event(
            AuditType.USER_POLICY_CREATE.value,
            self.grant_subject,
            self.system_id,
            [one.dict() for one in policies],
            username=self.remove_subject.id,
            source_type=AuditSourceType.HANDOVER.value,
        )

    def revoke_permission(self):
        self.operation_biz.delete_by_ids(
            system_id=self.system_id, subject=self.remove_subject, policy_ids=self.policy_ids
        )


class RoleHandoverHandler(BaseHandoverHandler):
    biz = RoleBiz()
    role_with_perm_group_biz = RoleWithPermGroupBiz()

    def __init__(self, handover_task_id, handover_from, handover_to, object_detail):
        self.handover_task_id = handover_task_id
        self.handover_from = handover_from
        self.handover_to = handover_to

        self.role_id = object_detail["id"]
        self.role_type = object_detail["type"]

        self.role = Role.objects.get(id=self.role_id)

    def grant_permission(self):
        if self.role_type == RoleType.SUPER_MANAGER.value:
            need_sync_backend_role = self.handover_from in self.role.system_permission_enabled_content.enabled_users
            self.biz.add_super_manager_member(username=self.handover_to, need_sync_backend_role=need_sync_backend_role)
        elif self.role_type == RoleType.SYSTEM_MANAGER.value:
            members = self._get_system_manager_members()
            if self.handover_to in members:
                return
            members.append(self.handover_to)
            self.biz.modify_system_manager_members(role_id=self.role_id, members=members)
        elif self.role_type in [RoleType.GRADE_MANAGER.value, RoleType.SUBSET_MANAGER.value]:
            self.role_with_perm_group_biz.batch_add_grade_manager_member(self.role, [self.handover_to])

        # 审计
        log_role_event(
            AuditType.ROLE_MEMBER_CREATE.value,
            Subject.from_username(self.handover_from),
            self.role,
            extra={"members": [self.handover_to]},
            source_type=AuditSourceType.HANDOVER.value,
        )

    def revoke_permission(self):
        if self.role_type == RoleType.SUPER_MANAGER.value:
            self.biz.delete_super_manager_member(username=self.handover_from)
        elif self.role_type == RoleType.SYSTEM_MANAGER.value:
            members = self._get_system_manager_members()
            members.remove(self.handover_from)
            self.biz.modify_system_manager_members(role_id=self.role_id, members=members)
        elif self.role_type in [RoleType.GRADE_MANAGER.value, RoleType.SUBSET_MANAGER.value]:
            self.role_with_perm_group_biz.delete_role_member(self.role, self.handover_from)

    def _get_system_manager_members(self) -> List[str]:
        if self.role_type != RoleType.SYSTEM_MANAGER.value:
            return []
        return self.biz.list_members_by_role_id(self.role_id)


class SubjectTemplateHandoverHandler(BaseHandoverHandler):
    biz = SubjectTemplateBiz()

    def __init__(self, handover_task_id, handover_from, handover_to, object_detail):
        self.handover_task_id = handover_task_id

        self.grant_subject = Subject.from_username(handover_to)
        self.remove_subject = Subject.from_username(handover_from)

        self.template_id = object_detail["id"]

    def grant_permission(self):
        self.biz.add_members(self.template_id, members=[self.grant_subject])

        # 审计
        log_subject_template_event(
            AuditType.SUBJECT_TEMPLATE_MEMBER_CREATE.value,
            self.grant_subject,
            [self.template_id],
            username=self.remove_subject.id,
            source_type=AuditSourceType.HANDOVER.value,
        )

    def revoke_permission(self):
        self.biz.delete_members(self.template_id, members=[self.remove_subject])
