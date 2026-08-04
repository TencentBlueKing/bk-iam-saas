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
import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Type

from django.db import transaction
from django.utils.functional import cached_property

from backend.apps.handover.constants import HandoverObjectType, HandoverStatus
from backend.apps.handover.models import HandoverRecord, HandoverTask
from backend.apps.role.models import Role
from backend.apps.subject_template.models import SubjectTemplate
from backend.audit.audit import log_group_event, log_role_event, log_subject_template_event, log_user_event
from backend.audit.constants import AuditSourceType, AuditType
from backend.biz.constants import HandoverTaskStatus
from backend.biz.group import GroupBiz, SubjectGroupBean
from backend.biz.helper import RoleWithPermGroupBiz
from backend.biz.policy import PolicyOperationBiz, PolicyQueryBiz
from backend.biz.role import RoleBiz
from backend.biz.subject_template import SubjectTemplateBiz
from backend.biz.system import SystemBiz
from backend.common.error_codes import error_codes
from backend.common.lock import gen_permission_handover_lock
from backend.service.constants import RoleType
from backend.service.models.subject import Subject


class BaseHandoverDataProvider(ABC):
    """权限交接数据提供器基类"""

    @abstractmethod
    def get_info(self) -> List[Dict[str, Any]]:
        """获取交接对象的详细信息"""
        pass


class GroupInfoProvider(BaseHandoverDataProvider):
    """用户组信息提供器"""

    biz = GroupBiz()

    def __init__(self, handover_from: str, group_ids: List[int]) -> None:
        self.handover_from = handover_from
        self.group_ids = group_ids

    def get_info(self):
        """获取用户组简略信息，用于生成交接任务"""
        # 从 subject_groups 中筛选出需要交接的组，避免额外查询数据库
        group_expired_at = {g.id: g.expired_at for g in self.subject_groups}
        # 只返回在 group_ids 中的组信息
        return [
            {"id": g.id, "name": g.name, "expired_at": group_expired_at.get(g.id)}
            for g in self.subject_groups
            if g.id in self.group_ids
        ]

    @cached_property
    def subject_groups(self) -> List[SubjectGroupBean]:
        subject = Subject.from_username(self.handover_from)
        # NOTE: 可能会有性能问题, 这里需要查询用户的所有组列表
        return self.biz.list_all_subject_group(subject)


class CustomPolicyProvider(BaseHandoverDataProvider):
    """自定义权限提供器"""

    biz = PolicyQueryBiz()
    system_biz = SystemBiz()

    def __init__(self, handover_from: str, custom_policies: List[Dict[str, Any]]) -> None:
        self.handover_from = handover_from
        self.custom_policies = custom_policies

    def get_info(self):
        """获取自定义权限简略信息，用于生成交接任务"""
        system_list = self.system_biz.new_system_list()
        infos = []
        for system_policy in self.custom_policies:
            sys = system_list.get(system_policy["system_id"])
            infos.append(
                {
                    "id": system_policy["system_id"],
                    "policy_ids": system_policy["policy_ids"],
                    "name": sys.name if sys else "",
                    "name_en": sys.name_en if sys else "",
                }
            )
        return infos


class RoleInfoProvider(BaseHandoverDataProvider):
    """角色信息提供器"""

    def __init__(self, handover_from: str, role_ids: List[int]) -> None:
        self.handover_from = handover_from
        self.role_ids = role_ids

    def get_info(self):
        """获取角色简略信息，用于生成交接任务"""
        roles = Role.objects.filter(id__in=self.role_ids)
        return [{"id": role.id, "type": role.type, "name": role.name, "name_en": role.name_en} for role in roles]


class SubjectTemplateProvider(BaseHandoverDataProvider):
    """主体模板提供器"""

    def __init__(self, handover_from: str, subject_template_ids: List[int]) -> None:
        self.handover_from = handover_from
        self.subject_template_ids = subject_template_ids

    def get_info(self):
        """获取主体模板简略信息，用于生成交接任务"""
        templates = SubjectTemplate.objects.filter(id__in=self.subject_template_ids)
        return [{"id": t.id, "name": t.name} for t in templates]


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


# 构建 key 到 Provider 的映射
HANDOVER_PROVIDER_MAP: Dict[str, Type[BaseHandoverDataProvider]] = {
    HandoverObjectType.GROUP_IDS.value: GroupInfoProvider,
    HandoverObjectType.CUSTOM_POLICIES.value: CustomPolicyProvider,
    HandoverObjectType.ROLE_IDS.value: RoleInfoProvider,
    HandoverObjectType.SUBJECT_TEMPLATE_IDS.value: SubjectTemplateProvider,
}


class HandoverBiz:
    """权限交接业务逻辑"""

    def create_handover_record(self, handover_from, handover_to, reason, handover_info):
        """创建交接记录及子任务，包含对象粒度的分布式锁和重复任务校验"""
        # 1. 生成交接任务详情
        handover_task_details = self._gen_handover_tasks(handover_from, handover_info)

        # 按对象粒度加锁，防止并发创建相同对象的交接任务
        locks = self._acquire_handover_task_locks(handover_from, handover_task_details)

        try:
            if self._has_running_handover_tasks(handover_from, handover_task_details):
                # 已存在相同交接对象正在运行的任务，不能新建重复任务
                raise error_codes.TASK_EXIST

            with transaction.atomic():
                handover_record = HandoverRecord.objects.create(
                    handover_from=handover_from, handover_to=handover_to, reason=reason
                )

                # 子任务在生成时未关联 record，此处回填关联关系
                for task in handover_task_details:
                    task.handover_record_id = handover_record.id

                if handover_task_details:
                    HandoverTask.objects.bulk_create(handover_task_details, batch_size=100)

            return handover_record
        finally:
            for lock in locks:
                lock.release()

    def _acquire_handover_task_locks(self, handover_from, handover_task_details):
        """逐个获取对象粒度的分布式锁，任一锁获取失败时回滚已持有的锁并抛出异常"""
        locks = []
        lock_keys = self._gen_handover_task_lock_keys(handover_from, handover_task_details)

        for key in lock_keys:
            lock = gen_permission_handover_lock(key)
            if not lock.acquire():
                for acquired_lock in locks:
                    acquired_lock.release()
                raise error_codes.TASK_EXIST
            locks.append(lock)

        return locks

    def _gen_handover_task_lock_keys(self, handover_from, handover_task_details):
        """生成排序后的锁 key 集合，格式为 handover_from:object_type:object_id，排序以避免死锁"""
        return sorted(
            {"{}:{}:{}".format(handover_from, task.object_type, task.object_id) for task in handover_task_details}
        )

    def _has_running_handover_tasks(self, handover_from, handover_task_details):
        """检查是否已存在相同交接对象的运行中任务，通过 (object_type, object_id) 集合交集判断"""
        new_task_keys = {(task.object_type, str(task.object_id)) for task in handover_task_details}
        if not new_task_keys:
            return False

        running_record_ids = list(
            HandoverRecord.objects.filter(
                handover_from=handover_from, status=HandoverStatus.RUNNING.value
            ).values_list("id", flat=True)
        )
        if not running_record_ids:
            return False

        existing_task_keys = set(
            HandoverTask.objects.filter(handover_record_id__in=running_record_ids).values_list(
                "object_type", "object_id"
            )
        )

        return bool(new_task_keys & existing_task_keys)

    def _gen_handover_tasks(self, handover_from: str, handover_info: Dict) -> List[HandoverTask]:
        """根据交接信息生成子任务列表（未关联 handover_record，由调用方回填）"""
        handover_task_details = []

        for key, value in handover_info.items():
            if not value:
                continue

            # 获取对应的 Provider 并调用 get_info()
            if key in HANDOVER_PROVIDER_MAP:
                provider = HANDOVER_PROVIDER_MAP[key](handover_from, value)  # type: ignore
                infos = provider.get_info()
                for info in infos:
                    handover_task_details.append(
                        HandoverTask(
                            object_type=key,
                            object_id=str(info["id"]),
                            object_detail=json.dumps(info),
                        )
                    )

        return handover_task_details
