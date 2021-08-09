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
import time
from copy import copy, deepcopy
from itertools import chain
from typing import Any, Dict, List, Tuple

from django.conf import settings
from django.core.cache import cache
from django.db import transaction

from backend.apps.policy.models import Policy as PolicyModel
from backend.common.error_codes import error_codes
from backend.common.time import PERMANENT_SECONDS, generate_default_expired_at
from backend.component import iam
from backend.service.constants import ADMIN_USER, Operate, SelectionMode, SubjectType
from backend.service.models import Action, Attribute, Policy, RelatedResource, ResourceInstance, Subject
from backend.util.json import json_dumps

from ..action import ActionList, ActionService
from ..resource_type import ResourceTypeService

permission_logger = logging.getLogger("permission")

# TODO 需要删除这个文件


class PolicyQueryMixin:
    # TODO 授权后查询表达式, 非查询类接口
    def get_policy(self, system_id: str, subject: Subject, action_id: str) -> Dict:
        """
        获取policy表达式
        """
        return iam.get_backend_expression(system_id, subject.dict(), action_id)

    # TODO 前端展示用的, 包含所有的信息/授权时需要取已有的策略, 做比较, 筛选等等操作, 填充等等操作
    # TODO 模型分离, 用于前端展示的模型, 用于比较/校验/筛选的模型
    # TODO service 只处理模型的查询, 对于名称的填充由biz处理, service的查询模型相对来说需要固定, 不做兼容, 上层biz来处理不同的模型字段
    def list_system_policy_by_subject(self, system_id: str, subject: Subject, fill_name: bool = True) -> List[Policy]:
        """
        获取subject的所有policy
        """
        # 查询用户有权限的policy列表
        policy_dict = self._get_backend_policy_dict(system_id, subject)

        # 从db查询
        qs = PolicyModel.objects.filter(
            system_id=system_id,
            subject_type=subject.type,
            subject_id=subject.id,
            policy_id__in=list(policy_dict.keys()),
        )
        policies = [Policy.from_db_model(p) for p in qs]

        # 组装数据
        for p in policies:
            p.set_expired_at(policy_dict[p.policy_id]["expired_at"])
            p.set_tag_unchanged()  # TODO service不管这个, 由biz填充

        if fill_name:
            self.fill_policies_name_by_system(system_id, policies)  # TODO 由biz填充

        return policies

    # TODO 针对backend返回的policy可以订一个结构, 封装相关的方法
    def _get_backend_policy_dict(self, system_id: str, subject: Subject) -> Dict:
        backend_policies = iam.list_system_policy(system_id, subject.type, subject.id)
        return {p["id"]: p for p in backend_policies}

    # TODO 分上层的用途分割模型, fill相关的操作放到biz
    def fill_policies_name(self, policies: List[Policy], actions: List[Action]) -> None:
        """
        填充policies的名称字段
        """
        action_list = ActionList(actions)

        # 获取policies中所有的system_id信息
        system_ids = set.union(*[policy.get_system_set() for policy in policies])

        # 获取所有相关的资源类型信息
        resource_type_dict = ResourceTypeService().get_resource_type_dict(list(system_ids))

        # 填充policy中的涉及到的需要的Name字段
        for policy in policies:
            action = action_list.get(policy.id)
            if not action:
                continue

            policy.fill_name(action, resource_type_dict)

    # TODO 上提到biz
    def fill_policies_name_by_system(self, system_id: str, policies: List[Policy]):
        """
        使用system_id查询并填充policies的字段
        """
        if not policies:
            return
        actions = ActionService().list(system_id)
        self.fill_policies_name(policies, actions)


class PolicyService(PolicyQueryMixin):
    """
    策略授权对象

    application_authorize 自定义申请单在审批后授权
    delete_partial policy中条件部分删除
    delete_by_ids 删除策略
    """

    # TODO 操作类
    def alter_subject_policies(self, system_id: str, subject: Subject, policies: List[Policy]) -> List[Policy]:
        """
        变更用户的策略
        """
        if not policies:
            return []

        # 加system+subject锁, 避免并发引发数据不一致
        with cache.lock(self._get_authorization_lock_key(system_id, subject), timeout=10):
            # 查询用户已有的权限
            old_policies = self.list_system_policy_by_subject(system_id, subject)

            # TODO 相关的diff方法, 检查方法全部放到biz
            # 对比申请权限与已有权限的差异
            create_policies, update_policies, _ = self._diff_policies(policies, old_policies, True)

            # 如果老策略已经覆盖要变更的策略，则直接返回
            if not create_policies and not update_policies:
                return []

            # 检查更新的policy, 实例数据不超过1万
            for p in update_policies:
                self.check_policy_instance_count(p)

            # 开启事务
            with transaction.atomic():
                # 1. 创建SaaS策略
                self._create_db_policies(system_id, subject, create_policies)

                # 2. 更新SaaS策略
                self._update_db_policies(system_id, subject, update_policies)

                # 5. 变更后端权限
                self._alter_backend_policies(system_id, subject, create_policies, update_policies, [])

            # 6. 更新SaaS策略policy_id
            self._sync_subject_policy_id(system_id, subject)

        # 返回授权的策略
        return self._compare_grant_policies(
            system_id, create_policies, update_policies, {p.id: p for p in old_policies}
        )

    # TODO biz层封装相关的方法
    def _diff_policies(
        self, new_policies: List[Policy], old_policies: List[Policy], merge=False
    ) -> Tuple[List[Policy], List[Policy], List[Policy]]:
        """
        对比出需要创建的policy, 需要更新的policy
        """
        create_policies = []  # 需要创建的policies
        update_policies = []  # 需要更新的policies
        unchanged_policies = []  # 不变的policies

        old_policies_dict = {p.id: p for p in old_policies}
        for p in new_policies:
            # 不在已有的操作中的新操作
            if p.id not in old_policies_dict:
                create_policies.append(p)
            else:
                old_policy = old_policies_dict[p.id]
                p.policy_id = old_policy.policy_id

                # 对比过期时间, 申请的时间小于已有权限的过期时间, 过期时间不变
                if (old_policy.expired_at or 0) > (p.expired_at or 0):
                    p.expired_at = old_policy.expired_at

                # 如果老策略已经包含了新策略里，则不需要更新
                if old_policy.has(p) and old_policy.compare_expired_at(p):
                    unchanged_policies.append(old_policy)
                    continue

                # 合并数据
                p.merge(old_policy)
                update_policies.append(p)

        # 其它未变更的操作
        other_action_set = set(old_policies_dict.keys()) - set({p.id for p in new_policies})
        for action_id in list(other_action_set):
            unchanged_policies.append(old_policies_dict[action_id])

        return create_policies, update_policies, unchanged_policies

    # TODO 操作类接口
    def _create_db_policies(self, system_id: str, subject: Subject, policies: List[Policy]) -> None:
        """
        创建新的策略
        """
        db_policies = [p.to_db_model(system_id, subject) for p in policies]

        PolicyModel.objects.bulk_create(db_policies, batch_size=100)

    def _update_db_policies(self, system_id: str, subject: Subject, policies: List[Policy]) -> None:
        """
        更新已有的策略
        """
        policies_dict = {p.policy_id: p for p in policies}

        db_policies = PolicyModel.objects.filter(
            subject_id=subject.id,
            subject_type=subject.type,
            system_id=system_id,
            policy_id__in=list(policies_dict.keys()),
        ).only("id", "policy_id")

        # 使用主键更新, 避免死锁
        for p in db_policies:
            new_policy = policies_dict[p.policy_id]

            PolicyModel.objects.filter(id=p.id).update(
                _resources=json_dumps([rt.dict() for rt in new_policy.related_resource_types]),
                _environment=json_dumps(new_policy.environment),
            )

    def _alter_backend_policies(
        self,
        system_id: str,
        subject: Subject,
        create_policies: List[Policy],
        update_policies: List[Policy],
        delete_policy_ids: List[int],
    ):
        """
        执行对policies的创建, 更新, 删除操作, 调用后端批量操作接口
        """
        # 组装backend变更策略的数据
        backend_create_policies = [p.to_backend_dict() for p in create_policies]

        backend_update_policies = [p.to_backend_dict() for p in update_policies]

        return iam.alter_policies(
            system_id, subject.type, subject.id, backend_create_policies, backend_update_policies, delete_policy_ids
        )

    def _sync_subject_policy_id(self, system_id: str, subject: Subject) -> None:
        """
        同步SaaS-后端策略的policy_id
        """
        policies = PolicyModel.objects.filter(
            system_id=system_id, subject_type=subject.type, subject_id=subject.id, policy_id=0
        )

        if len(policies) > 0:
            backend_policies = iam.list_system_policy(system_id, subject.type, subject.id)
            policy_id_dict = {p["action_id"]: p["id"] for p in backend_policies}
            for p in policies:
                p.policy_id = policy_id_dict.get(p.action_id, 0)
            PolicyModel.objects.bulk_update(policies, fields=["policy_id"], batch_size=100)

    @staticmethod
    def _get_authorization_lock_key(system_id: str, subject: Subject):
        """
        生成 system + action + subject 锁 key
        """
        return f"bk_iam:lock:{system_id}:{subject.type}:{subject.id}"

    def _alter_policies(self, subject, system_id, create_policies, update_policies):
        """
        策略调整
        """
        # 开启事务
        with transaction.atomic():
            if update_policies:
                self._update_db_policies(system_id, subject, update_policies)

            if create_policies:
                self._create_db_policies(system_id, subject, create_policies)

            if update_policies or create_policies:
                self._alter_backend_policies(system_id, subject, create_policies, update_policies, [])
        if create_policies:
            self._sync_subject_policy_id(system_id, subject)

    # TODO 放到biz的小方法中, 不必放到biz class中
    def generate_expired_at(self, expired_at: int = 0):
        """生成过期时间"""
        # 如果传入设置的过期时间, 大于当前时间，且小于或等于永久，则使用它
        if time.time() < expired_at <= PERMANENT_SECONDS:
            return expired_at

        return generate_default_expired_at()

    def _grant_resources_instance(
        self,
        system_id: str,
        actions: List[Action],
        subject: Subject,
        resources: List[ResourceInstance],
        expired_at: int = 0,
    ) -> List[Policy]:
        """
        资源实例授权
        """
        new_policy_expired_at = self.generate_expired_at(expired_at)
        # 加 system + subject 锁
        with cache.lock(self._get_authorization_lock_key(system_id, subject), timeout=10):

            policies = self.list_system_policy_by_subject(system_id, subject)
            policies_dict = {p.id: p for p in policies}

            # 遍历actions, 如果已有policy则更新, 如果不存在则创建
            # TODO 应该提供相关的数据结构转换方法, 全部转成policies再处理
            create_policies, update_policies = [], []
            for action in actions:
                if action.id in policies_dict:
                    # 对于与资源实例无关的Action，直接跳过
                    if len(action.related_resource_types) == 0:
                        continue
                    policy = deepcopy(policies_dict[action.id])
                    # TODO: 参数有效期, 大于已有有效期, 是否更新???
                    if policy.add_resources_instance(resources):  # TODO 做成数据转换, 全部转换为policy, 再通过policy复用相关的方法
                        # 检查整个policy的path数量没有超过1万
                        self.check_policy_instance_count(policy)

                        # 需要更新的policy
                        update_policies.append(policy)
                    continue

                # 创建新的policy
                related_resource_types = []
                if len(action.related_resource_types) > 0:
                    related_resource_types = [RelatedResource.from_resource_instance(r) for r in resources]
                policy = Policy(
                    id=action.id,
                    related_resource_types=related_resource_types,
                    environment={},
                    expired_at=new_policy_expired_at,
                    type=action.type,
                )
                create_policies.append(policy)

            self._alter_policies(subject, system_id, create_policies, update_policies)

        # 返回授权的策略信息
        return self._compare_grant_policies(system_id, create_policies, update_policies, policies_dict)

    # TODO 不需要了, 审计以实际传入的数据为准
    def _compare_grant_policies(
        self,
        system_id,
        create_policies: List[Policy],
        update_policies: List[Policy],
        old_policy_dict: Dict[str, Policy],
    ) -> List[Policy]:
        """
        对比出实际授权的策略
        """
        grant_policies = copy(create_policies)
        for policy in update_policies:
            policy.diff(old_policy_dict[policy.id])
            grant_policies.append(policy)

        self.fill_policies_name_by_system(system_id, grant_policies)

        return grant_policies

    # TODO 结构转换为policies后, 统一使用policyList的相关方法处理
    def _revoke_resources_instance(
        self, system_id: str, actions: List[Action], subject: Subject, resources: List[ResourceInstance]
    ):
        # 加 system + subject 锁
        # TODO 结构转换后, 通过policy相关的方法处理
        with cache.lock(self._get_authorization_lock_key(system_id, subject), timeout=10):

            policies = self.list_system_policy_by_subject(system_id, subject)
            policies_dict = {p.id: p for p in policies}

            update_policies, delete_policies = [], []
            for action in actions:
                if action.id in policies_dict:
                    policy = deepcopy(policies_dict[action.id])
                    if policy.remove_resources_instance(resources):
                        if all([r.is_empty() for r in policy.related_resource_types]):
                            delete_policies.append(policy)
                        else:
                            update_policies.append(policy)

            with transaction.atomic():
                delete_ids = [p.policy_id for p in delete_policies]
                if update_policies:
                    self._update_db_policies(system_id, subject, update_policies)

                if delete_policies:
                    PolicyModel.objects.filter(
                        system_id=system_id, subject_type=subject.type, subject_id=subject.id, policy_id__in=delete_ids
                    ).delete()

                if update_policies or delete_policies:
                    self._alter_backend_policies(system_id, subject, [], update_policies, delete_ids)

            # 返回被回收的策略
            revoke_policies = [policies_dict[p.id] for p in delete_policies]
            for p in update_policies:
                old_policy = policies_dict[p.id]
                old_policy.diff(p)
                revoke_policies.append(old_policy)
            self.fill_policies_name_by_system(system_id, revoke_policies)

            return update_policies, delete_policies, revoke_policies

    def grant_or_revoke_instance(
        self,
        operate: str,
        system_id: str,
        action: Action,
        subject: Subject,
        resource_instances: List[ResourceInstance],
        expired_at: int = 0,
    ) -> Tuple[Dict, List[Policy]]:
        """
        单个资源实例授权或回收
        """
        if subject.type == SubjectType.USER.value and subject.id == ADMIN_USER:
            return {}, []

        permission_logger.info("open api %s by system: %s", operate, system_id)

        if operate == Operate.GRANT.value:
            grant_policies = self._grant_resources_instance(
                system_id, [action], subject, resource_instances, expired_at
            )
            return self.get_policy(system_id, subject, action.id), grant_policies

        if operate == Operate.REVOKE.value:
            update_policies, delete_policies, revoke_policies = self._revoke_resources_instance(
                system_id, [action], subject, resource_instances
            )
            if update_policies:
                return self.get_policy(system_id, subject, action.id), revoke_policies
            if delete_policies:
                policy = delete_policies[0]
                return {"policy_id": policy.policy_id, "expression": {}}, revoke_policies

        return {}, []

    def grant_or_revoke_batch_instance(
        self,
        operate: str,
        system_id: str,
        actions: List[Action],
        subject: Subject,
        resource_instances: List[ResourceInstance],
        expired_at: int = 0,
    ) -> Tuple[List[Any], List[Policy]]:
        """
        批量资源实例授权或回收
        """
        if subject.type == SubjectType.USER.value and subject.id == ADMIN_USER:
            return [], []

        permission_logger.info("open api %s by system: %s", operate, system_id)

        if operate == Operate.GRANT.value:
            grant_policies = self._grant_resources_instance(
                system_id, actions, subject, resource_instances, expired_at
            )
            policies = self.list_system_policy_by_subject(system_id, subject, False)
            return (
                [
                    {"action": {"id": p.id}, "policy_id": p.policy_id}
                    for p in policies
                    if p.id in {ac.id for ac in actions}
                ],
                grant_policies,
            )

        if operate == Operate.REVOKE.value:
            update_policies, delete_policies, revoke_policies = self._revoke_resources_instance(
                system_id, actions, subject, resource_instances
            )  # 批量回收
            return (
                [{"action": {"id": p.id}, "policy_id": p.policy_id} for p in chain(update_policies, delete_policies)],
                revoke_policies,
            )

        return [], []

    def grant_attribute(
        self, system_id: str, action_ids: List[str], subject: Subject, attributes: List[Attribute]
    ) -> Tuple[List[Any], List[Policy]]:
        """
        属性授权
        其中attributes 并非批量属性授权，而是属性之间有逻辑And关系
        注意：仅仅支持
        """
        # 查询Action，并且其关联的资源类型Name/NameEn
        actions = [a for a in ActionService().list(system_id) if a.id in set(action_ids)]
        # 遍历每个Action，转换出需要赋予权限的策略
        policies = []
        for action in actions:
            # 对于与资源实例无关的Action，直接生成权限
            if len(action.related_resource_types) == 0:
                policies.append(
                    Policy(
                        id=action.id,
                        related_resource_types=[],
                        environment={},
                        expired_at=generate_default_expired_at(),
                        type=action.type,
                    )
                )
                continue
            # 目前仅仅支持一种依赖资源类型的Action，多种则直接忽略
            if len(action.related_resource_types) != 1:
                continue

            rrt = action.related_resource_types[0]
            # Action不支持属性授权，也直接忽略
            if rrt.selection_mode not in [SelectionMode.ATTRIBUTE.value, SelectionMode.ALL.value]:
                continue

            related_resource_types = [
                RelatedResource.from_attributes(rrt.system_id, rrt.id, rrt.name, rrt.name_en, attributes)
            ]
            policies.append(
                Policy(
                    id=action.id,
                    related_resource_types=related_resource_types,
                    environment={},
                    expired_at=generate_default_expired_at(),
                    type=action.type,
                )
            )
        # 变更权限
        grant_policies = self.alter_subject_policies(system_id, subject, policies)

        subject_policies = self.list_system_policy_by_subject(system_id, subject, False)
        return (
            [{"action": {"id": p.id}, "policy_id": p.policy_id} for p in subject_policies if p.id in set(action_ids)],
            grant_policies,
        )

    # TODO: [重构] 迁移拆分svc.Policy.get_instances() 、 biz.Policy.check_instance_count
    def check_policy_instance_count(self, policy: Policy):
        """
        检查策略的实例数量不超过限制
        """
        for rrt in policy.related_resource_types:
            if rrt.instances_count() > settings.SINGLE_POLICY_MAX_INSTANCES_LIMIT:
                raise error_codes.VALIDATE_ERROR.format(
                    "操作[{}]关联的[{}]的实例数已达上限{}个，请改用范围或者属性授权。".format(
                        policy.name, rrt.name, settings.SINGLE_POLICY_MAX_INSTANCES_LIMIT
                    )
                )
