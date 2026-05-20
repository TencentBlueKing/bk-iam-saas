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

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Type

from backend.apps.group.models import Group
from backend.apps.handover.models import HandoverTask
from backend.apps.role.models import Role
from backend.apps.subject_template.models import SubjectTemplate
from backend.audit.audit import log_group_event, log_role_event, log_subject_template_event, log_user_event
from backend.audit.constants import AuditSourceType, AuditType
from backend.biz.constants import HandoverTaskStatus
from backend.biz.group import GroupBiz
from backend.biz.helper import RoleWithPermGroupBiz
from backend.biz.policy import PolicyOperationBiz, PolicyQueryBiz
from backend.biz.role import RoleBiz
from backend.biz.subject_template import SubjectTemplateBiz
from backend.biz.system import SystemBiz
from backend.service.constants import RoleType
from backend.service.models import Subject

logger = logging.getLogger(__name__)


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


class BaseHandoverInfoProvider(ABC):
    """交接对象信息提取器基类: 将仅含 ID 的交接数据扩展为带名称、描述等详细信息"""

    def __init__(self, handover_from: str, *args, **kwargs):
        """
        Args:
            handover_from: 交接来源用户
            *args: 其他参数, 由子类定义
            **kwargs: 其他关键字参数
        """
        self.handover_from = handover_from

    @abstractmethod
    def get_info(self) -> List[Dict[str, Any]]:
        """返回该交接对象的详细信息列表"""


class GroupInfoProvider(BaseHandoverInfoProvider):
    """用户组交接信息提取"""

    biz = GroupBiz()

    def __init__(self, handover_from: str, group_ids: List[int]) -> None:
        super().__init__(handover_from)
        self.group_ids = group_ids

    def get_info(self) -> List[Dict[str, Any]]:
        # apps.*.models 在 .importlinter 中已加入 ignore_imports, biz 层可直接查询
        groups = Group.objects.filter(id__in=self.group_ids)
        subject = Subject.from_username(self.handover_from)
        # NOTE: 可能会有性能问题, 这里需要查询用户的所有组列表
        subject_groups = self.biz.list_all_subject_group(subject)
        group_expired_at = {g.id: g.expired_at for g in subject_groups}
        return [
            {
                "id": group.id,
                "name": group.name,
                "description": group.description,
                "expired_at": group_expired_at[group.id],
            }
            for group in groups
        ]


class CustomPolicyInfoProvider(BaseHandoverInfoProvider):
    """自定义权限交接信息提取"""

    biz = PolicyQueryBiz()
    system_biz = SystemBiz()

    def __init__(self, handover_from: str, custom_policies: List[Dict[str, Any]]) -> None:
        super().__init__(handover_from)
        self.custom_policies = custom_policies

    def get_info(self) -> List[Dict[str, Any]]:
        system_list = self.system_biz.new_system_list()
        subject = Subject.from_username(self.handover_from)
        infos: List[Dict[str, Any]] = []
        for system_policy in self.custom_policies:
            sys = system_list.get(system_policy["system_id"])
            # 获取策略详情
            policy_details: List[Dict[str, Any]] = []
            if system_policy["policy_ids"]:
                policies = self.biz.list_by_subject(system_policy["system_id"], subject)
                policy_map = {p.policy_id: p for p in policies if not p.is_expired()}
                for policy_id in system_policy["policy_ids"]:
                    if policy_id in policy_map:
                        policy = policy_map[policy_id]
                        policy_details.append(
                            {
                                "id": policy_id,
                                "action_name": policy.name,
                                "expired_at": policy.expired_at,
                                "expired_display": policy.expired_display,
                            }
                        )
            infos.append(
                {
                    "id": system_policy["system_id"],
                    "policy_ids": system_policy["policy_ids"],
                    "name": sys.name if sys else "",
                    "name_en": sys.name_en if sys else "",
                    "policy_details": policy_details,
                }
            )
        return infos


class RoleInfoProvider(BaseHandoverInfoProvider):
    """管理员角色交接信息提取"""

    def __init__(self, handover_from: str, role_ids: List[int]) -> None:
        super().__init__(handover_from)
        self.role_ids = role_ids

    def get_info(self) -> List[Dict[str, Any]]:
        roles = Role.objects.filter(id__in=self.role_ids)
        return [
            {
                "id": role.id,
                "type": role.type,
                "name": role.name,
                "name_en": role.name_en,
                "description": role.description,
            }
            for role in roles
        ]


class SubjectTemplateInfoProvider(BaseHandoverInfoProvider):
    """人员模板交接信息提取"""

    biz = SubjectTemplateBiz()

    def __init__(self, handover_from: str, subject_template_ids: List[int]) -> None:
        super().__init__(handover_from)
        self.subject_template_ids = subject_template_ids

    def get_info(self) -> List[Dict[str, Any]]:
        # apps.*.models 在 .importlinter 中已加入 ignore_imports, biz 层可直接查询
        templates = SubjectTemplate.objects.filter(id__in=self.subject_template_ids)
        return [{"id": t.id, "name": t.name, "description": t.description} for t in templates]


# 交接对象类型 -> 信息提取器
HANDOVER_INFO_PROVIDER_MAP: Dict[str, Type[BaseHandoverInfoProvider]] = {
    "group_ids": GroupInfoProvider,
    "custom_policies": CustomPolicyInfoProvider,
    "role_ids": RoleInfoProvider,
    "subject_template_ids": SubjectTemplateInfoProvider,
}
