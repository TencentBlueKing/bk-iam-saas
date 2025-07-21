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

import itertools
import logging
from typing import Dict, List, Optional

from django.db import transaction

from backend.apps.policy.models import Policy as PolicyModel
from backend.apps.temporary_policy.models import TemporaryPolicy
from backend.common.time import PERMANENT_SECONDS
from backend.component import iam
from backend.service.action import ActionList
from backend.service.constants import SubjectType
from backend.service.models import Policy, Subject, UniversalPolicyChangedContent
from backend.util.json import json_dumps

from .backend import BackendPolicyOperationService
from .common import UniversalPolicyChangedContentAnalyzer
from .query import new_backend_policy_list_by_subject

logger = logging.getLogger("app")


class PolicyCommonDBOperationService:
    """rbac 和 abac 都需要使用到的"""

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id

    def _create_db_policies(self, system_id: str, subject: Subject, policies: List[Policy]) -> None:
        """
        创建新的策略
        """
        db_policies = [p.to_db_model(self.tenant_id, system_id, subject) for p in policies]
        PolicyModel.objects.bulk_create(db_policies, batch_size=100)

    def update_db_policies(self, system_id: str, subject: Subject, policies: List[Policy]):
        """
        更新已有的策略
        """
        # 使用主键更新，避免死锁
        for p in policies:
            PolicyModel.objects.filter(
                id=p.policy_id,
                subject_id=subject.id,
                subject_type=subject.type,
                system_id=system_id,
            ).update(
                _resources=json_dumps(p.resource_groups.dict()),
                auth_type=p.auth_type,
            )

    def _delete_db_policies(self, system_id: str, subject: Subject, policy_ids: List[int]):
        """
        删除 db Policies
        """
        PolicyModel.objects.filter(
            system_id=system_id, subject_type=subject.type, subject_id=subject.id, id__in=policy_ids
        ).delete()


class UniversalPolicyOperationService(PolicyCommonDBOperationService, BackendPolicyOperationService):
    """专门用于处理包含 RBAC 策略的"""

    analyzer = UniversalPolicyChangedContentAnalyzer()

    def delete_backend_policy_by_action(self, system_id: str, action_id: str):
        """删除指定操作的后台策略"""
        # TODO: 该函数是用于删除某个 Action 所有的操作，
        #       对于 RBAC，需要后台单独提供接口，同时删除 RBAC 和 ABAC 策略？？？
        # TODO: 对于 RBAC，需要后台单独提供接口，但是后台 RBAC 策略 action_pks 是一个字段，不好删除
        # TODO: 可以先根据 action_id 判断是否会有 RBAC 策略，如果不会，则不需要执行

    def delete_by_ids(self, system_id: str, subject: Subject, policy_ids: List[int]):
        """
        删除指定 policy_id 的策略
        """
        # 1. 计算变更的后台策略内容
        changed_policies = self._cal_policy_change_contents_by_deleted(system_id, subject, policy_ids)

        # 2. 变更 DB，并进行后台变更
        with transaction.atomic():
            self._delete_db_policies(system_id, subject, policy_ids)
            self.alter_backend_policies(subject, 0, system_id, changed_policies)

    def alter(
        self,
        system_id: str,
        subject: Subject,
        create_policies: List[Policy],
        update_policies: List[Policy],
        delete_policy_ids: List[int],
    ):
        # Note: 必须先计算出策略的变更内容，否则先变更 DB 后，则查询不到老策略，无法进行新老策略对比
        changed_policies = []
        # 1. 新增策略
        changed_policies.extend(self.analyzer.cal_for_created(system_id, create_policies))

        # 2. 删除策略
        changed_policies.extend(self._cal_policy_change_contents_by_deleted(system_id, subject, delete_policy_ids))

        # 3. 更新
        changed_policies.extend(self._cal_policy_change_contents_by_updated(system_id, subject, update_policies))

        # 4. 设置 Policy 的 AuthType
        action_auth_types = {cp.action_id: cp.auth_type for cp in changed_policies}
        # 只需要新建和更新的策略设置对应的 AuthType，删除的策略不需要
        for p in create_policies:
            p.auth_type = action_auth_types[p.action_id]
        for p in update_policies:
            p.auth_type = action_auth_types[p.action_id]

        # 5. 变更 DB，并变更后台
        with transaction.atomic():
            if create_policies:
                self._create_db_policies(system_id, subject, create_policies)

            if update_policies:
                self.update_db_policies(system_id, subject, update_policies)

            if delete_policy_ids:
                self._delete_db_policies(system_id, subject, delete_policy_ids)

            if changed_policies:
                self.alter_backend_policies(subject, 0, system_id, changed_policies)

    def _cal_policy_change_contents_by_deleted(
        self, system_id: str, subject: Subject, delete_policy_ids: List[int]
    ) -> List[UniversalPolicyChangedContent]:
        """根据要删除的策略 ID，组装计算出要变更的策略内容"""
        if len(delete_policy_ids) == 0:
            return []

        # 查询策略
        qs = PolicyModel.objects.filter(
            system_id=system_id, subject_type=subject.type, subject_id=subject.id, id__in=delete_policy_ids
        )
        policies = [Policy.from_db_model(p, PERMANENT_SECONDS) for p in qs]

        # 填充后台 PolicyID
        backend_policy_list = new_backend_policy_list_by_subject(system_id, subject)
        for p in policies:
            # 对于纯 RBAC 策略，不存在 Backend PolicyID
            if not backend_policy_list.get(p.action_id):
                continue

            p.backend_policy_id = backend_policy_list.get(p.action_id).id  # type: ignore

        return self.analyzer.cal_for_deleted(system_id, policies)

    def _cal_policy_change_contents_by_updated(
        self, system_id: str, subject: Subject, update_policies: List[Policy]
    ) -> List[UniversalPolicyChangedContent]:
        """根据更新的策略，组装计算出要变更的策略内容"""
        if len(update_policies) == 0:
            return []

        # 1 根据 ActionID 查询旧策略内容
        qs = PolicyModel.objects.filter(
            system_id=system_id,
            subject_type=subject.type,
            subject_id=subject.id,
            action_id__in=[p.action_id for p in update_policies],
        )
        old_policies = {p.action_id: Policy.from_db_model(p, PERMANENT_SECONDS) for p in qs}

        # 2. 填充后台 PolicyID
        backend_policy_list = new_backend_policy_list_by_subject(system_id, subject)
        for p in old_policies.values():
            # 对于纯 RBAC 策略，不存在 Backend PolicyID
            if not backend_policy_list.get(p.action_id):
                continue
            p.backend_policy_id = backend_policy_list.get(p.action_id).id  # type: ignore

        # 3 遍历组装每个新旧策略对
        update_pair_policies = [(p, old_policies[p.action_id]) for p in update_policies]

        return self.analyzer.cal_for_updated(system_id, update_pair_policies)


class ABACPolicyOperationService(PolicyCommonDBOperationService):
    """用于处理 ABAC 策略的"""

    def delete_backend_policy_by_action(self, system_id: str, action_id: str):
        """删除指定操作的后台策略"""
        iam.delete_action_policies(system_id, action_id)

    def delete_by_ids(self, system_id: str, subject: Subject, policy_ids: List[int]):
        """
        删除指定 policy_id 的策略
        """
        # 查询要删除的策略对应的后台 PolicyID
        policy_id_map = self._query_backend_policy_id(system_id, subject, policy_ids)
        backend_policy_ids = [policy_id_map[_id] for _id in policy_ids if _id in policy_id_map]

        # 4. 过滤出要删除策略的
        with transaction.atomic():
            self._delete_db_policies(system_id, subject, policy_ids)
            iam.delete_policies(system_id, subject.type, subject.id, backend_policy_ids)

    def alter(
        self,
        system_id: str,
        subject: Subject,
        create_policies: List[Policy],
        update_policies: List[Policy],
        delete_policy_ids: List[int],
        action_list: Optional[ActionList] = None,
    ):
        """
        变更 subject 的 Policies
        """
        delete_backend_policy_ids = []
        # 更新或删除，需要查询对应的后台策略 ID
        if update_policies or delete_policy_ids:
            # 查询更新和要删除策略对应的后台 PolicyID
            policy_ids = [p.policy_id for p in update_policies] + delete_policy_ids
            policy_id_map = self._query_backend_policy_id(system_id, subject, policy_ids)

            # 2. 填充要更新的策略的后台 PolicyID
            for p in update_policies:
                p.backend_policy_id = policy_id_map[p.policy_id]

            # 3. 计算出要删除的后台策略
            delete_backend_policy_ids = [policy_id_map[_id] for _id in delete_policy_ids]

        with transaction.atomic():
            if create_policies:
                self._create_db_policies(system_id, subject, create_policies)

            if update_policies:
                self.update_db_policies(system_id, subject, update_policies)

            if delete_policy_ids:
                self._delete_db_policies(system_id, subject, delete_policy_ids)

            if create_policies or update_policies or delete_backend_policy_ids:
                self._alter_backend_policies(
                    system_id, subject, create_policies, update_policies, delete_backend_policy_ids, action_list
                )

    def _query_backend_policy_id(self, system_id: str, subject: Subject, policy_ids: List[int]) -> Dict[int, int]:
        """根据 SaaS PolicyIDs 查询对应的后台策略"""
        # 1. 查询后台 PolicyID
        backend_policy_list = new_backend_policy_list_by_subject(system_id, subject)
        action_to_backend_policy_id_map = {p.action_id: p.id for p in backend_policy_list.policies}

        # 2. 查询策略对应的 Action
        db_policies = PolicyModel.objects.filter(
            subject_id=subject.id, subject_type=subject.type, system_id=system_id, id__in=policy_ids
        ).only("id", "action_id")

        # 3. 计算出 SaaS PolicyID 与 Backend PolicyID 的映射
        return {p.id: action_to_backend_policy_id_map[p.action_id] for p in db_policies}

    def _alter_backend_policies(
        self,
        system_id: str,
        subject: Subject,
        create_policies: List[Policy],
        update_policies: List[Policy],
        delete_policy_ids: List[int],
        action_list: Optional[ActionList] = None,
    ):
        """
        执行对 policies 的创建，更新，删除操作，调用后端批量操作接口
        """
        # 处理忽略路径
        if action_list is not None:
            for p in itertools.chain(create_policies, update_policies):
                action = action_list.get(p.action_id)
                if not action:
                    continue
                p.ignore_path(action)

        # 组装 backend 变更策略的数据
        backend_create_policies = [p.to_backend_dict(system_id) for p in create_policies]
        backend_update_policies = [p.to_backend_dict(system_id) for p in update_policies]

        return iam.alter_policies(
            system_id, subject.type, subject.id, backend_create_policies, backend_update_policies, delete_policy_ids
        )

    def create_temporary_policies(
        self,
        system_id: str,
        subject: Subject,
        policies: List[Policy],
        action_list: Optional[ActionList] = None,
    ):
        """
        创建临时权限
        """
        # 创建 db model
        db_policies = [p.to_db_model(self.tenant_id, system_id, subject, model=TemporaryPolicy) for p in policies]

        # 处理忽略路径
        if action_list is not None:
            for p in policies:
                action = action_list.get(p.action_id)
                if not action:
                    continue
                p.ignore_path(action)

        # NOTE: 这里为了先拿到后端的 id, 需要先创建后端权限，没有使用事务

        # 创建后端策略
        data = iam.create_temporary_policies(
            system_id, subject.type, subject.id, [p.to_backend_dict(system_id) for p in policies]
        )

        # 写入后端 policy_ids
        for p, _id in zip(db_policies, data["ids"], strict=False):
            p.policy_id = _id

        # 创建 db 权限
        TemporaryPolicy.objects.bulk_create(db_policies, batch_size=100)

    def delete_temporary_policies_by_ids(self, system_id: str, subject: Subject, policy_ids: List[int]):
        """
        删除指定 policy_id 的临时策略
        """
        backend_policy_ids = list(
            TemporaryPolicy.objects.filter(
                system_id=system_id, subject_type=subject.type, subject_id=subject.id, id__in=policy_ids
            ).values_list("policy_id", flat=True)
        )

        with transaction.atomic():
            TemporaryPolicy.objects.filter(
                system_id=system_id, subject_type=subject.type, subject_id=subject.id, id__in=policy_ids
            ).delete()
            iam.delete_temporary_policies(system_id, subject.type, subject.id, backend_policy_ids)


# Note: 用户组权限相关的操作使用支持 RBAC 的接口，用户权限相关的操作使用 ABAC 接口
class PolicyOperationService:
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.abac_svc = ABACPolicyOperationService(tenant_id)
        self.universal_svc = UniversalPolicyOperationService(tenant_id)

    def delete_backend_policy_by_action(self, system_id: str, action_id: str):
        """删除指定操作的后台策略"""
        # ABAC 处理
        self.abac_svc.delete_backend_policy_by_action(system_id, action_id)

        # RBAC 处理
        self.universal_svc.delete_backend_policy_by_action(system_id, action_id)

    def delete_by_ids(self, system_id: str, subject: Subject, policy_ids: List[int]):
        """
        删除指定 policy_id 的策略
        """
        if subject.type == SubjectType.USER.value:
            self.abac_svc.delete_by_ids(system_id, subject, policy_ids)
            return

        self.universal_svc.delete_by_ids(system_id, subject, policy_ids)

    def alter(
        self,
        system_id: str,
        subject: Subject,
        create_policies: Optional[List[Policy]] = None,
        update_policies: Optional[List[Policy]] = None,
        delete_policy_ids: Optional[List[int]] = None,
        action_list: Optional[ActionList] = None,
    ):
        """
        变更 subject 的 Policies
        """
        create_policies = create_policies or []
        update_policies = update_policies or []
        delete_policy_ids = delete_policy_ids or []

        # Note: type 只有 user 和 group，user 默认走 ABAC 权限
        if subject.type == SubjectType.USER.value:
            self.abac_svc.alter(system_id, subject, create_policies, update_policies, delete_policy_ids, action_list)
            return

        # Note: 下面是对 type=group 的处理
        self.universal_svc.alter(system_id, subject, create_policies, update_policies, delete_policy_ids)

    def only_update_db_policies(self, system_id: str, subject: Subject, policies: List[Policy]) -> None:
        """
        更新已有的 SaaS DB 里策略，一般只用于更新 resource name 之类的，不影响鉴权的，不需要同步后台的数据
        """
        # 使用主键更新，避免死锁，只更新 resource 字段
        for p in policies:
            PolicyModel.objects.filter(
                id=p.policy_id,
                subject_id=subject.id,
                subject_type=subject.type,
                system_id=system_id,
            ).update(_resources=json_dumps(p.resource_groups.dict()))

    def create_temporary_policies(
        self,
        system_id: str,
        subject: Subject,
        policies: List[Policy],
        action_list: Optional[ActionList] = None,
    ):
        """
        创建临时权限
        """
        # 只有用户才有临时权限
        assert subject.type == SubjectType.USER.value
        self.abac_svc.create_temporary_policies(system_id, subject, policies, action_list)

    def delete_temporary_policies_by_ids(self, system_id: str, subject: Subject, policy_ids: List[int]):
        """
        删除指定 policy_id 的临时策略
        """
        # 只有用户才有临时权限
        assert subject.type == SubjectType.USER.value
        self.abac_svc.delete_temporary_policies_by_ids(system_id, subject, policy_ids)
