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
from typing import Any, Dict, List, Optional, Tuple

from django.conf import settings
from django.db import transaction
from django.db.models import Count, F
from pydantic import BaseModel

from backend.apps.template.models import PermTemplate, PermTemplatePolicyAuthorized, PermTemplatePreGroupSync
from backend.common.lock import gen_policy_alter_lock
from backend.common.time import PERMANENT_SECONDS

from .action import ActionList
from .constants import AuthType
from .models import Policy, Subject, SystemCounter, UniversalPolicyChangedContent
from .policy.backend import BackendPolicyOperationService
from .policy.common import UniversalPolicyChangedContentAnalyzer
from .policy.query import PolicyList, new_backend_policy_list_by_subject


class TemplateGroupPreCommit(BaseModel):
    group_id: str
    policies: List[Policy]

    def convert_policies_to_dict(self) -> List[Dict[str, Any]]:
        return [one.dict() for one in self.policies]


class TemplateService:
    backend_svc = BackendPolicyOperationService()
    analyzer = UniversalPolicyChangedContentAnalyzer()

    def _cal_changed_policies(
        self,
        system_id: str,
        create_policies: List[Policy],
        delete_policies: List[Policy],
        update_pair_policies: List[Tuple[Policy, Policy]],  # List[(new, old)]
    ) -> List[UniversalPolicyChangedContent]:
        """计算出要变更的策略 和 策略对应的ActionAuthType"""
        # Note: 必须先计算出策略的变更内容，否则先变更DB后，则查询不到老策略，无法进行新老策略对比
        changed_policies = []
        # 1. 新增策略
        changed_policies.extend(self.analyzer.cal_for_created(system_id, create_policies))
        # 2. 删除策略
        changed_policies.extend(self.analyzer.cal_for_deleted(system_id, delete_policies))
        # 3. 更新
        changed_policies.extend(self.analyzer.cal_for_updated(system_id, update_pair_policies))

        return changed_policies

    # Template Auth
    def revoke_subject(self, system_id: str, template_id: int, subject: Subject):
        """
        移除模板成员
        """
        # 获取已有的授权信息
        authorized_template = PermTemplatePolicyAuthorized.objects.get_by_subject_template(subject, template_id)
        assert system_id == authorized_template.system_id
        policy_list = self._convert_template_actions_to_policy_list(authorized_template.data["actions"])

        # Note: 由于后台删除时需要用到后台PolicyID，这里先进行填充
        # 查询subject的后端权限信息
        backend_policy_list = new_backend_policy_list_by_subject(system_id, subject, template_id)
        # 填充Backend Policy ID
        for p in policy_list.policies:
            if not backend_policy_list.get(p.action_id):
                continue
            p.backend_policy_id = backend_policy_list.get(p.action_id).id  # type: ignore

        # 计算变更策略内容
        changed_policies = self._cal_changed_policies(system_id, [], policy_list.policies, [])

        with gen_policy_alter_lock(template_id, system_id, subject.type, subject.id):
            # 变更
            with transaction.atomic():
                count, _ = PermTemplatePolicyAuthorized.objects.filter(
                    template_id=template_id, subject_type=subject.type, subject_id=subject.id
                ).delete()

                if count != 0:
                    # 更新冗余count
                    PermTemplate.objects.filter(id=template_id).update(subject_count=F("subject_count") - count)
                    # 后端处理
                    self.backend_svc.alter_backend_policies(subject, template_id, system_id, changed_policies)

    def grant_subject(
        self,
        system_id: str,
        template_id: int,
        subject: Subject,
        policies: List[Policy],
        action_list: Optional[ActionList] = None,
    ):
        """
        模板增加成员
        """
        authorized_template = PermTemplatePolicyAuthorized(
            template_id=template_id, subject_type=subject.type, subject_id=subject.id, system_id=system_id
        )
        authorized_template.data = {"actions": [p.dict() for p in policies]}

        # 处理忽略路径
        self._ignore_path(policies, action_list)

        # 计算变更策略内容
        changed_policies = self._cal_changed_policies(system_id, policies, [], [])
        # 设置的ActionAuthType
        authorized_template.auth_types = {cp.action_id: cp.auth_type for cp in changed_policies}

        with gen_policy_alter_lock(template_id, system_id, subject.type, subject.id):
            # 模板授权
            with transaction.atomic():
                authorized_template.save(force_insert=True)
                PermTemplate.objects.filter(id=template_id).update(subject_count=F("subject_count") + 1)

                # 后端处理
                self.backend_svc.alter_backend_policies(subject, template_id, system_id, changed_policies)

    def alter_template_auth(
        self, subject: Subject, template_id: int, create_policies: List[Policy], delete_action_ids: List[str]
    ):
        """
        变更subject的模板授权信息 [action级别的新增和删除，并不涉及resource级别的变更]
        """
        # 获取已有的授权信息
        authorized_template = PermTemplatePolicyAuthorized.objects.get_by_subject_template(subject, template_id)
        system_id = authorized_template.system_id
        policy_list = self._convert_template_actions_to_policy_list(authorized_template.data["actions"])

        # 1. 将[Saas]已有授权信息policy_list，进行增删
        # 1.1 移除需要删除的策略
        delete_policies = policy_list.pop_by_action_ids(delete_action_ids)
        # Note: 由于后台删除时需要用到后台PolicyID，这里先进行填充
        if len(delete_policies) > 0:
            # 查询subject的后端权限信息
            backend_policy_list = new_backend_policy_list_by_subject(system_id, subject, template_id)
            # 填充Backend Policy ID
            for p in delete_policies:
                if not backend_policy_list.get(p.action_id):
                    continue
                p.backend_policy_id = backend_policy_list.get(p.action_id).id  # type: ignore
        # 1.2 添加需要新增的策略
        create_policies = policy_list.extend_without_repeated(create_policies)

        # 2. 计算要变更的策略内容
        changed_policies = self._cal_changed_policies(system_id, create_policies, delete_policies, [])

        # 3. 重新计算action_auth_types
        action_auth_types = authorized_template.auth_types
        # 3.1 移除被删除的策略的AuthType
        for action_id in delete_action_ids:
            action_auth_types.pop(action_id, None)
        # 3.2 添加新增的策略的AuthType
        action_auth_types.update(
            {
                cp.action_id: cp.auth_type
                for cp in changed_policies
                # Note: 变更后策略的AuthType为None，说明是策略变删除，不需要记录了，只取未被删除的
                if cp.auth_type != AuthType.NONE.value
            }
        )

        # 执行变更
        self._execute_changed_template_auth(
            authorized_template.id,
            subject,
            template_id,
            system_id,
            policy_list.policies,
            changed_policies,
            action_auth_types,
        )

    def update_template_auth(
        self, subject: Subject, template_id: int, policies: List[Policy], action_list: Optional[ActionList] = None
    ):
        """
        更新subject的模板授权信息 [不涉及Action的新增和删除，只涉及Action里Resource的变更]
        """
        authorized_template = PermTemplatePolicyAuthorized.objects.get_by_subject_template(subject, template_id)
        system_id = authorized_template.system_id
        policy_list = self._convert_template_actions_to_policy_list(authorized_template.data["actions"])
        # 查询subject的后端权限信息
        backend_policy_list = new_backend_policy_list_by_subject(system_id, subject, template_id)

        # Note: 这里并非直接在policy_list上更新，而是先删后增，原因是SaaS Policy和后台Policy有差别，避免多次deepcopy的性能问题
        # 1. 先将老的原始SaaS Policy 移除
        old_policies = policy_list.pop_by_action_ids([p.action_id for p in policies])

        # 2. 将新策略添加到SaaS Policy
        affected_policies = policy_list.extend_without_repeated(policies)
        # Note: 后面将会进行忽略路径处理，所以这里必须用deepcopy，否则会导致直接修改到了SaaS Policy - policy_list的内容
        new_policies = [p.copy(deep=True) for p in affected_policies]

        # 3. 后台策略变更前，需要给旧策略添加上PolicyID
        for p in old_policies:
            # 后台策略ID, 对于只有RBAC策略，则没有PolicyID
            backend_policy_id = 0
            if backend_policy_list.get(p.action_id):
                backend_policy_id = backend_policy_list.get(p.action_id).id  # type: ignore

            # 填充backend policy id
            p.backend_policy_id = backend_policy_id

        # 4. 计算要变更的策略内容
        # 后台策略需要处理忽略路径
        self._ignore_path(old_policies, action_list)
        self._ignore_path(new_policies, action_list)
        # 计算变更内容
        assert len(old_policies) == len(new_policies)
        update_pair_policies = list(zip(new_policies, old_policies))
        changed_policies = self._cal_changed_policies(system_id, [], [], update_pair_policies)

        # 5. 重新计算action_auth_types
        action_auth_types = authorized_template.auth_types
        for cp in changed_policies:
            action_auth_types[cp.action_id] = cp.auth_type

        # 执行变更
        self._execute_changed_template_auth(
            authorized_template.id,
            subject,
            template_id,
            system_id,
            policy_list.policies,
            changed_policies,
            action_auth_types,
        )

    def _execute_changed_template_auth(
        self,
        authorized_template_id: int,
        subject: Subject,
        template_id: int,
        system_id: str,
        saas_policies: List[Policy],
        changed_policies: List[UniversalPolicyChangedContent],
        action_auth_types: Dict[str, str],
    ):
        """执行模板授权的更新"""
        with gen_policy_alter_lock(template_id, system_id, subject.type, subject.id):
            with transaction.atomic():
                authorized_template = PermTemplatePolicyAuthorized.objects.select_for_update().get(
                    id=authorized_template_id,
                )
                authorized_template.data = {"actions": [p.dict() for p in saas_policies]}
                authorized_template.auth_types = action_auth_types
                authorized_template.save(update_fields=["_data", "_auth_types"])

                # 后端策略变更
                self.backend_svc.alter_backend_policies(subject, template_id, system_id, changed_policies)

    def _ignore_path(self, policies: List[Policy], action_list: Optional[ActionList]):
        """policies忽略路径"""
        if action_list is not None:
            for p in policies:
                action = action_list.get(p.action_id)
                if not action:
                    continue
                p.ignore_path(action)

    def direct_update_db_template_auth(self, subject: Subject, template_id: int, policies: List[Policy]):
        """
        直接更新Subject的模板授权信息，这里只更新DB，不更新后台
        一般用于更新name等，与鉴权无关的信息
        """
        authorized_template = PermTemplatePolicyAuthorized.objects.get_by_subject_template(subject, template_id)
        with transaction.atomic():
            authorized_template = PermTemplatePolicyAuthorized.objects.select_for_update().get(
                id=authorized_template.id
            )
            authorized_template.data = {"actions": [p.dict() for p in policies]}
            authorized_template.save(update_fields=["_data"])

    def _convert_template_actions_to_policy_list(self, actions: List[Dict]) -> PolicyList:
        """转换模板的授权的actions到PolicyList, 兼容过期时间为空的情况"""
        policies = []
        for action in actions:
            if "expired_at" not in action or not action["expired_at"]:
                action["expired_at"] = PERMANENT_SECONDS
            policies.append(Policy.parse_obj(action))
        return PolicyList(policies)

    def list_system_counter_by_subject(self, subject: Subject, hidden: bool = True) -> List[SystemCounter]:
        """
        查询subject有权限的系统-模板数量信息
        """
        qs = (
            PermTemplatePolicyAuthorized.objects.filter_by_subject(subject)
            .values("system_id")
            .annotate(count=Count("system_id"))
            .order_by()
        )

        if hidden:
            return [
                SystemCounter(id=one["system_id"], count=one["count"])
                for one in qs
                if one["system_id"] not in settings.HIDDEN_SYSTEM_LIST
            ]  # NOTE: 屏蔽掉需要隐藏的系统

        return [SystemCounter(id=one["system_id"], count=one["count"]) for one in qs]

    def create_or_update_group_pre_commit(self, template_id: int, pre_commits: List[TemplateGroupPreCommit]):
        """
        创建或更新用户组预更新信息
        """
        group_ids = [one.group_id for one in pre_commits]
        exists_db_per_commits = PermTemplatePreGroupSync.objects.filter(
            template_id=template_id, group_id__in=group_ids
        ).defer("data")
        exists_db_per_commit_dict = {one.group_id: one for one in exists_db_per_commits}

        create_pre_commits, update_pre_commits = [], []
        for pre_commit in pre_commits:
            group_id = pre_commit.group_id

            if group_id in exists_db_per_commit_dict:
                db_pre_commit = exists_db_per_commit_dict[group_id]
                db_pre_commit.data = {"actions": pre_commit.convert_policies_to_dict()}
                update_pre_commits.append(db_pre_commit)
            else:
                db_pre_commit = PermTemplatePreGroupSync(template_id=template_id, group_id=group_id)
                db_pre_commit.data = {"actions": pre_commit.convert_policies_to_dict()}
                create_pre_commits.append(db_pre_commit)

        with transaction.atomic():
            if create_pre_commits:
                PermTemplatePreGroupSync.objects.bulk_create(create_pre_commits, batch_size=100)

            if update_pre_commits:
                PermTemplatePreGroupSync.objects.bulk_update(update_pre_commits, ["data"], batch_size=100)

    def _get_template_id_by_group_system(self, group: Subject, system_id: str) -> int:
        """
        查询用户组有权限的模板ID列表
        """
        return (
            PermTemplatePolicyAuthorized.objects.filter_by_subject(group)
            .filter(system_id=system_id)
            .values_list("template_id", flat=True)
            .first()
        )

    def get_actions_by_group_system(self, group: Subject, system_id: str) -> List[str]:
        """查询用户组有权限的模板的操作列表"""
        template_id = self._get_template_id_by_group_system(group, system_id)
        return PermTemplate.objects.get(id=template_id).action_ids
