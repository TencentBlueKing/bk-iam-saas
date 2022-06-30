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

from django.db import transaction
from django.db.models import Count, F
from django.utils.translation import gettext as _
from pydantic import BaseModel

from backend.apps.template.models import PermTemplate, PermTemplatePolicyAuthorized, PermTemplatePreGroupSync
from backend.common.error_codes import error_codes
from backend.common.time import PERMANENT_SECONDS
from backend.component import iam

from .action import ActionList
from .models import Policy, Subject, SystemCounter
from .policy.backend import BackendPolicyOperationService
from .policy.common import PolicyTypeAnalyzer, UniversalPolicyChangedContentCalculator
from .policy.query import PolicyList, new_backend_policy_list_by_subject


class TemplateGroupPreCommit(BaseModel):
    group_id: str
    policies: List[Policy]

    def convert_policies_to_dict(self) -> List[Dict[str, Any]]:
        return [one.dict() for one in self.policies]


class UniversalTemplateService(BackendPolicyOperationService):
    """专门用于处理用户组模板权限的RBAC策略"""

    calculator = UniversalPolicyChangedContentCalculator()

    def alter(
        self,
        system_id: str,
        template_id: int,
        subject: Subject,
        create_policies: List[Policy],
        delete_policies: List[Policy],
        update_pair_policies: List[Tuple[Policy, Policy]],  # List[(new, old)]
    ):
        # Note: 必须先计算出策略的变更内容，否则先变更DB后，则查询不到老策略，无法进行新老策略对比
        changed_policies = []
        # 1. 新增策略
        changed_policies.extend(self.calculator.cal_for_created(system_id, create_policies))
        # 2. 删除策略
        changed_policies.extend(self.calculator.cal_for_deleted(delete_policies))
        # 3. 更新
        changed_policies.extend(self.calculator.cal_for_updated(system_id, update_pair_policies))

        # 4. 变更
        self.alter_backend_policies(subject, template_id, system_id, changed_policies)


class TemplateService:
    analyzer = PolicyTypeAnalyzer()
    universal_svc = UniversalTemplateService()

    # Template Auth
    def revoke_subject(self, system_id: str, template_id: int, subject: Subject):
        """
        移除模板成员
        """
        # 获取已有的授权信息
        authorized_template = PermTemplatePolicyAuthorized.objects.get_by_subject_template(subject, template_id)
        assert system_id == authorized_template.system_id
        policy_list = self._convert_template_actions_to_policy_list(authorized_template.data["actions"])

        # 根据Action分析出删除的RBAC/ABAC策略
        # Note: 这里由于后台直接提供了按模板删除所有ABAC策略接口，所以这里忽略ABAC策略，不需要一条条策略删除
        _, delete_universal_policies = self.analyzer.split_policies_by_auth_type(
            system_id,
            policy_list.policies,
        )

        # Note: 由于后台删除时需要用到后台PolicyID，这里先进行填充
        if len(delete_universal_policies) > 0:
            # 查询subject的后端权限信息
            backend_policy_list = new_backend_policy_list_by_subject(system_id, subject, template_id)
            # 填充Backend Policy ID
            for p in delete_universal_policies:
                if not backend_policy_list.get(p.action_id):
                    continue
                p.policy_id = backend_policy_list.get(p.action_id).id  # type: ignore

        with transaction.atomic():
            count, _ = PermTemplatePolicyAuthorized.objects.filter(
                template_id=template_id, subject_type=subject.type, subject_id=subject.id
            ).delete()

            if count != 0:
                # 更新冗余count
                PermTemplate.objects.filter(id=template_id).update(subject_count=F("subject_count") - count)

                # 调用后端删除权限
                iam.delete_template_policies(system_id, subject.type, subject.id, template_id)

                # RBAC处理
                if delete_universal_policies:
                    self.universal_svc.alter(system_id, template_id, subject, [], delete_universal_policies, [])

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

        # 根据Action分析出新增的RBAC/ABAC策略
        abac_policies, universal_policies = self.analyzer.split_policies_by_auth_type(system_id, policies)

        # 模板授权
        with transaction.atomic():
            authorized_template.save(force_insert=True)
            PermTemplate.objects.filter(id=template_id).update(subject_count=F("subject_count") + 1)

            # ABAC处理
            if abac_policies:
                iam.create_and_delete_template_policies(
                    system_id,
                    subject.type,
                    subject.id,
                    template_id,
                    [p.to_backend_dict(system_id) for p in abac_policies],
                    [],
                )

            # RBAC处理
            if universal_policies:
                self.universal_svc.alter(system_id, template_id, subject, universal_policies, [], [])

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
                p.policy_id = backend_policy_list.get(p.action_id).id  # type: ignore

        # 1.2 添加需要新增的策略
        create_policies = policy_list.extend_without_repeated(create_policies)

        # 2. 根据Action分析出新增、删除的RBAC/ABAC策略
        create_abac_policies, create_universal_policies = self.analyzer.split_policies_by_auth_type(
            system_id,
            create_policies,
        )
        delete_abac_policies, delete_universal_policies = self.analyzer.split_policies_by_auth_type(
            system_id,
            delete_policies,
        )

        # 3. 变更模板授权
        with transaction.atomic():
            # 修改模板授权信息
            authorized_template = PermTemplatePolicyAuthorized.objects.select_for_update().get(
                id=authorized_template.id
            )
            authorized_template.data = {"actions": [p.dict() for p in policy_list.policies]}
            authorized_template.save(update_fields=["_data"])

            # ABAC处理
            if create_abac_policies or delete_abac_policies:
                iam.create_and_delete_template_policies(
                    system_id,
                    subject.type,
                    subject.id,
                    template_id,
                    [p.to_backend_dict(system_id) for p in create_abac_policies],
                    [p.policy_id for p in delete_abac_policies],
                )

            # RBAC处理
            if create_universal_policies or delete_universal_policies:
                self.universal_svc.alter(
                    system_id, template_id, subject, create_universal_policies, delete_universal_policies, []
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

        # 1. 根据Action分析出更新的RBAC/ABAC策略
        update_abac_policies, update_universal_policies = self.analyzer.split_policies_by_auth_type(
            system_id, policies
        )

        # 2. ABAC策略，填充backend policy id ，同时将[SaaS]policy_list进行更新
        for p in update_abac_policies:
            # Note: 对于ABAC策略，后台都有一一对应的策略，如果查询不到，说明此次更新有问题
            if not backend_policy_list.get(p.action_id):
                raise error_codes.VALIDATE_ERROR.format(_("模板{}没有{}操作的权限").format(template_id, p.action_id))

            p.policy_id = backend_policy_list.get(p.action_id).id  # type: ignore
            # 更新SaaS存储的策略内容
            policy_list.update(p)

        # 3. RBAC策略，填充backend policy id，获取老策略，[SaaS]policy_list进行更新
        old_universal_policies = []
        for p in update_universal_policies:
            # 后台策略ID, 对于universal类型的策略，不一定有
            policy_id = 0
            if backend_policy_list.get(p.action_id):
                policy_id = backend_policy_list.get(p.action_id).id  # type: ignore

            # Note: 获取老策略必须在policy_list.update之前，且必须是deepcopy一个新对象，否则会被policy_list.update更新掉的
            old_policy = policy_list.get(p.action_id).copy(deep=True)  # type: ignore

            # 填充backend policy id
            old_policy.policy_id = policy_id
            p.policy_id = policy_id
            old_universal_policies.append(old_policy)

            # 更新[SaaS]policy_list
            policy_list.update(p)

        # 4. 变更
        with transaction.atomic():
            authorized_template = PermTemplatePolicyAuthorized.objects.select_for_update().get(
                id=authorized_template.id
            )
            authorized_template.data = {"actions": [p.dict() for p in policy_list.policies]}
            authorized_template.save(update_fields=["_data"])

            # Note: 必须SaaS DB修改后才可执行忽略路径，否则SaaS DB里保存的数据就缺失了路径（因为Policy都是引用的，不是deepcopy处理的）
            # 处理忽略路径
            self._ignore_path(update_abac_policies, action_list)
            self._ignore_path(update_universal_policies, action_list)

            # ABAC策略
            if update_abac_policies:
                iam.update_template_policies(
                    system_id,
                    subject.type,
                    subject.id,
                    template_id,
                    [p.to_backend_dict(system_id) for p in update_abac_policies],
                )

            # RBAC策略
            if update_universal_policies:
                update_pair_policies = list(zip(update_universal_policies, old_universal_policies))
                self.universal_svc.alter(system_id, template_id, subject, [], [], update_pair_policies)

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

    def list_system_counter_by_subject(self, subject: Subject) -> List[SystemCounter]:
        """
        查询subject有权限的系统-模板数量信息
        """
        qs = (
            PermTemplatePolicyAuthorized.objects.filter_by_subject(subject)
            .values("system_id")
            .annotate(count=Count("system_id"))
            .order_by()
        )

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
