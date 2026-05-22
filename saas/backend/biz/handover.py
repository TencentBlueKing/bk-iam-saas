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
from contextlib import contextmanager
from typing import Dict, Iterable, List, Tuple

from backend.apps.application.models import Application
from backend.apps.handover.constants import HandoverObjectType, HandoverStatus
from backend.apps.handover.models import HandoverRecord, HandoverTask
from backend.apps.role.models import Role
from backend.audit.audit import log_group_event, log_role_event, log_subject_template_event, log_user_event
from backend.audit.constants import AuditSourceType, AuditType
from backend.biz.constants import HandoverTaskStatus
from backend.biz.group import GroupBiz
from backend.biz.helper import RoleWithPermGroupBiz
from backend.biz.policy import PolicyOperationBiz, PolicyQueryBiz
from backend.biz.role import RoleBiz
from backend.biz.subject_template import SubjectTemplateBiz
from backend.common.error_codes import error_codes
from backend.common.lock import RedisLock, gen_permission_handover_lock
from backend.service.constants import ApplicationStatus, ApplicationType, RoleType
from backend.service.models import Subject
from backend.util.json import json_dumps


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

        self.system_id = object_detail["system_id"]
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


class HandoverTaskCheckBiz:
    """权限交接的锁、冲突校验与 HandoverTask 构造"""

    @staticmethod
    def iter_fine_grained_keys(object_type: str, one: Dict) -> Iterable[Tuple[str, str]]:
        """生成最细粒度的 (object_type, fine_grained_id) 元组

        - custom_policies: fine_grained_id = "{system_id}:{policy_id}"
        - 其他类型:        fine_grained_id = str(one["id"])
        """
        if object_type == HandoverObjectType.CUSTOM_POLICIES.value:
            system_id = one.get("system_id")
            for policy_id in one.get("policy_ids") or []:
                yield object_type, "{}:{}".format(system_id, policy_id)
            return

        yield object_type, str(one["id"])

    def _gen_lock_keys(self, handover_from: str, detailed_handover_info: Dict) -> List[str]:
        """生成排序后的锁 key 列表

        格式为 "{handover_from}:{object_type}:{fine_grained_id}", 排序以避免不同请求按不同顺序加锁导致死锁。
        """
        keys = set()
        for object_type, infos in detailed_handover_info.items():
            if not infos:
                continue
            for one in infos:
                for _, fine_id in self.iter_fine_grained_keys(object_type, one):
                    keys.add("{}:{}:{}".format(handover_from, object_type, fine_id))
        return sorted(keys)

    @contextmanager
    def acquire_locks(self, handover_from: str, detailed_handover_info: Dict):
        """按对象粒度逐个获取分布式锁的上下文管理器

        任一锁获取失败时回滚已持有的锁并抛出 TASK_EXIST; with 块退出时自动释放全部锁。
        """
        locks: List[RedisLock] = []
        try:
            for key in self._gen_lock_keys(handover_from, detailed_handover_info):
                lock = gen_permission_handover_lock(key)
                if not lock.acquire():
                    for acquired_lock in locks:
                        acquired_lock.release()
                    locks = []
                    raise error_codes.TASK_EXIST.format(message="请勿重复提交")
                locks.append(lock)
            yield
        finally:
            for lock in locks:
                lock.release()

    def _collect_new_task_keys(self, detailed_handover_info: Dict) -> set:
        return {
            key
            for object_type, infos in detailed_handover_info.items()
            if infos
            for one in infos
            for key in self.iter_fine_grained_keys(object_type, one)
        }

    def check_running_conflict(self, handover_from: str, detailed_handover_info: Dict) -> None:
        """检查是否已存在运行中且交接对象有重叠的 HandoverRecord

        通过最细粒度 (object_type, fine_grained_id) 集合交集判断, 冲突时抛 TASK_EXIST。
        """
        new_task_keys = self._collect_new_task_keys(detailed_handover_info)
        if not new_task_keys:
            return

        running_record_ids = list(
            HandoverRecord.objects.filter(
                handover_from=handover_from, status=HandoverStatus.RUNNING.value
            ).values_list("id", flat=True)
        )
        if not running_record_ids:
            return

        existing_task_keys = set()
        for object_type, object_id, object_detail in HandoverTask.objects.filter(
            handover_record_id__in=running_record_ids
        ).values_list("object_type", "object_id", "object_detail"):
            if object_type == HandoverObjectType.CUSTOM_POLICIES.value:
                # 自定义权限的 object_id 是 system_id, 需结合 object_detail.policy_ids 展开到 policy 粒度
                try:
                    detail = json.loads(object_detail) if object_detail else {}
                except (TypeError, ValueError):
                    detail = {}
                for policy_id in detail.get("policy_ids") or []:
                    existing_task_keys.add((object_type, "{}:{}".format(object_id, policy_id)))
            else:
                existing_task_keys.add((object_type, str(object_id)))

        conflict_keys = new_task_keys & existing_task_keys
        if conflict_keys:
            conflict_object_pairs = [f"{object_type}:{fine_id}" for object_type, fine_id in conflict_keys]
            raise error_codes.TASK_EXIST.format(
                message=f"存在正在执行的交接任务，冲突对象: {', '.join(conflict_object_pairs)}", replace=True
            )

    def check_pending_application_conflict(self, handover_from: str, detailed_handover_info: Dict) -> None:
        """检查是否已存在审批中且交接对象有重叠的交接申请单, 冲突时抛 TASK_EXIST"""
        new_task_keys = self._collect_new_task_keys(detailed_handover_info)
        if not new_task_keys:
            return

        pending_applications = Application.objects.filter(
            applicant=handover_from,
            type=ApplicationType.HANDOVER.value,
            status=ApplicationStatus.PENDING.value,
        ).only("id", "_data")

        for application in pending_applications:
            existing_handover_info = (application.data or {}).get("handover_info") or {}
            existing_task_keys = {
                key
                for object_type, infos in existing_handover_info.items()
                if infos
                for one in infos
                if isinstance(one, dict)
                for key in self.iter_fine_grained_keys(object_type, one)
            }
            conflict_keys = new_task_keys & existing_task_keys
            if conflict_keys:
                conflict_object_pairs = [f"{object_type}:{fine_id}" for object_type, fine_id in conflict_keys]
                raise error_codes.TASK_EXIST.format(
                    message=f"存在审批中的交接申请，冲突对象: {', '.join(conflict_object_pairs)}", replace=True
                )

    def build_tasks(self, detailed_handover_info: Dict, handover_record_id: int) -> List[HandoverTask]:
        """基于已展开的详细信息构造 HandoverTask 列表

        自定义权限以 system_id 作为 object_id (一个系统聚合为一条 task), 其他类型沿用对象自身 id。
        """
        tasks: List[HandoverTask] = []
        for key, infos in detailed_handover_info.items():
            if not infos:
                continue
            for one in infos:
                raw_object_id = one["system_id"] if key == HandoverObjectType.CUSTOM_POLICIES.value else one["id"]
                tasks.append(
                    HandoverTask(
                        handover_record_id=handover_record_id,
                        object_type=key,
                        object_id=str(raw_object_id),
                        object_detail=json_dumps(one),
                    )
                )
        return tasks
