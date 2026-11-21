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
from typing import List, Optional, Tuple

from pydantic import parse_obj_as

from backend.apps.policy.models import Policy as PolicyModel
from backend.audit.audit import log_group_event, log_user_event
from backend.audit.constants import AuditSourceType, AuditType
from backend.biz.group import GroupBiz
from backend.biz.policy import PolicyBean, PolicyBeanList
from backend.common.lock import gen_policy_alter_lock
from backend.service.models import Policy, Subject
from backend.service.policy.operation import PolicyOperationService

logger = logging.getLogger("app")


class SubjectGroupPermissionCleanupBiz:
    """清理用户的用户组权限"""

    group_biz = GroupBiz()

    def clean(self, subject: Subject, group_ids: List[int]) -> Tuple[List[int], List[int]]:
        """
        将subject移出用户组, 返回移出成功与失败的用户组ID
        """
        removed: List[int] = []
        failed: List[int] = []
        for group_id in group_ids:
            try:
                self.group_biz.remove_members(str(group_id), [subject])
            except Exception:  # pylint: disable=broad-except
                logger.exception("cleanup user group member fail, username=%s, group_id=%s", subject.id, group_id)
                failed.append(group_id)
                continue
            removed.append(group_id)

        if removed:
            try:
                # NOTE: 不传username, 事件username即为被清理的用户, 保证审计接口可按照用户查询到清理记录
                log_group_event(
                    AuditType.GROUP_MEMBER_DELETE.value,
                    subject,
                    removed,
                    source_type=AuditSourceType.OPENAPI.value,
                )
            except Exception:  # pylint: disable=broad-except
                logger.exception("save audit event fail, username=%s, group_ids=%s", subject.id, removed)

        return removed, failed


class SubjectPolicyPermissionCleanupBiz:
    """清理用户的自定义权限"""

    svc = PolicyOperationService()

    def clean(
        self, subject: Subject, system_id: str, policy_ids: Optional[List[int]] = None, action_id: str = ""
    ) -> Tuple[List[int], List[int]]:
        """
        按policy_ids或action_id删除subject的自定义权限, 返回删除成功与失败的策略ID
        """
        # 自定义权限锁, template_id为0
        with gen_policy_alter_lock(0, system_id, subject.type, subject.id):
            qs = PolicyModel.objects.filter(system_id=system_id, subject_type=subject.type, subject_id=subject.id)
            qs = qs.filter(id__in=policy_ids) if policy_ids else qs.filter(action_id=action_id)
            db_policies = list(qs)
            if not db_policies:
                return [], []

            valid_policy_ids = [p.id for p in db_policies]
            try:
                self.svc.delete_by_ids(system_id, subject, valid_policy_ids)
            except Exception:  # pylint: disable=broad-except
                logger.exception(
                    "cleanup user policies fail, username=%s, system_id=%s, policy_ids=%s",
                    subject.id,
                    system_id,
                    valid_policy_ids,
                )
                return [], valid_policy_ids

        self._log_audit_event(subject, system_id, db_policies)
        return valid_policy_ids, []

    def _log_audit_event(self, subject: Subject, system_id: str, db_policies: List[PolicyModel]):
        """
        根据已删除的DB策略记录审计
        """
        try:
            policies = parse_obj_as(List[PolicyBean], [Policy.from_db_model(p, 0) for p in db_policies])
            policy_list = PolicyBeanList(system_id, policies, need_fill_empty_fields=True)
            log_user_event(
                AuditType.USER_POLICY_DELETE.value,
                subject,
                system_id,
                [p.dict() for p in policy_list.policies],
                source_type=AuditSourceType.OPENAPI.value,
            )
        except Exception:  # pylint: disable=broad-except
            logger.exception(
                "save audit event fail, username=%s, system_id=%s, policy_ids=%s",
                subject.id,
                system_id,
                [p.id for p in db_policies],
            )
