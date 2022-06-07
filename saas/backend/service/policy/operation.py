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
import itertools
from typing import Dict, Iterable, List, Optional, Tuple

from django.db import transaction

from backend.apps.policy.models import Policy as PolicyModel
from backend.apps.temporary_policy.models import TemporaryPolicy
from backend.common.time import PERMANENT_SECONDS
from backend.component import iam
from backend.service.action import ActionList
from backend.util.json import json_dumps

from ..constants import AbacPolicyChangeType, AuthTypeEnum, SubjectType
from ..models import (
    AbacPolicyChangeContent,
    Policy,
    PolicyIDExpiredAt,
    RbacPolicyChangeContent,
    Subject,
    UniversalPolicy,
    UniversalPolicyChangedContent,
)
from .backend import BackendPolicyOperationService
from .query import PolicyList, new_backend_policy_list_by_subject


class PolicyCommonDBOperationService:
    """rbac和abac都需要使用到的"""

    def _create_db_policies(self, system_id: str, subject: Subject, policies: List[Policy]) -> None:
        """
        创建新的策略
        """
        db_policies = [p.to_db_model(system_id, subject) for p in policies]
        PolicyModel.objects.bulk_create(db_policies, batch_size=100)

    def update_db_policies(self, system_id: str, subject: Subject, policies: List[Policy]) -> None:
        """
        更新已有的策略
        """
        policy_list = PolicyList(policies)

        db_policies = PolicyModel.objects.filter(
            subject_id=subject.id, subject_type=subject.type, system_id=system_id, policy_id__in=policy_list.ids
        ).only("id", "action_id")

        # 使用主键更新, 避免死锁
        for p in db_policies:
            update_policy = policy_list.get(p.action_id)
            if not update_policy:
                continue
            PolicyModel.objects.filter(id=p.id).update(_resources=json_dumps(update_policy.resource_groups.dict()))

    def _delete_db_policies(self, system_id: str, subject: Subject, policy_ids: List[int]):
        """
        删除db Policies
        """
        PolicyModel.objects.filter(
            system_id=system_id, subject_type=subject.type, subject_id=subject.id, policy_id__in=policy_ids
        ).delete()

    def _sync_db_policy_id(self, system_id: str, subject: Subject, action_ids: List[str]) -> None:
        """
        同步SaaS-后端策略的policy_id
        """
        db_policies = PolicyModel.objects.filter(
            system_id=system_id,
            subject_type=subject.type,
            subject_id=subject.id,
            action_id__in=action_ids,
        ).defer("_resources")

        if len(db_policies) == 0:
            return

        backend_policy_list = new_backend_policy_list_by_subject(system_id, subject)
        for p in db_policies:
            backend_policy = backend_policy_list.get(p.action_id)
            # Note: 对于只有RBAC权限，则policy_id存储为 SaaS Policy表记录的ID的负数，这样可以避免与后台PolicyID冲突
            p.policy_id = backend_policy.id if backend_policy else -p.id

        PolicyModel.objects.bulk_update(db_policies, fields=["policy_id"], batch_size=100)


class UniversalPolicyOperationService(PolicyCommonDBOperationService, BackendPolicyOperationService):
    """专门用于处理包含RBAC策略的"""

    def delete_backend_policy_by_action(self, system_id: str, action_id: str):
        """删除指定操作的后台策略"""
        # TODO: 该函数是用于删除某个Action所有的操作，对于RBAC,需要后台单独提供接口，同时删除RBAC和ABAC策略？？？
        pass

    def delete_by_ids(self, system_id: str, subject: Subject, policy_ids: List[int]):
        """
        删除指定policy_id的策略
        """
        # 1. 查询策略
        qs = PolicyModel.objects.filter(
            system_id=system_id, subject_type=subject.type, subject_id=subject.id, policy_id__in=policy_ids
        )
        policies = [Policy.from_db_model(p, PERMANENT_SECONDS) for p in qs]

        # 2. 转换为UniversalPolicy结构，然后拆分出rbac和abac权限
        changed_policies = []
        for p in policies:
            up = UniversalPolicy.from_policy(p)
            policy_changed_content = UniversalPolicyChangedContent(
                action_id=p.action_id, auth_type=AuthTypeEnum.NONE.value
            )
            if len(up.expression_resource_groups) > 0:
                policy_changed_content.abac = AbacPolicyChangeContent(
                    change_type=AbacPolicyChangeType.DELETED.value, id=p.policy_id
                )
            if len(up.instances) > 0:
                policy_changed_content.rbac = RbacPolicyChangeContent(deleted=up.instances)

            changed_policies.append(policy_changed_content)

        # 3. 变更DB,并进行后台变更
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
        action_list: Optional[ActionList] = None,
    ):
        pass


class ABACPolicyOperationService(PolicyCommonDBOperationService):
    """用于处理ABAC策略的"""

    def delete_backend_policy_by_action(self, system_id: str, action_id: str):
        """删除指定操作的后台策略"""
        iam.delete_action_policies(system_id, action_id)

    def delete_by_ids(self, system_id: str, subject: Subject, policy_ids: List[int]):
        """
        删除指定policy_id的策略
        """
        with transaction.atomic():
            self._delete_db_policies(system_id, subject, policy_ids)
            iam.delete_policies(system_id, subject.type, subject.id, policy_ids)

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
        变更subject的Policies
        """
        with transaction.atomic():
            if create_policies:
                self._create_db_policies(system_id, subject, create_policies)

            if update_policies:
                self.update_db_policies(system_id, subject, update_policies)

            if delete_policy_ids:
                self._delete_db_policies(system_id, subject, delete_policy_ids)

            if create_policies or update_policies or delete_policy_ids:
                self._alter_backend_policies(
                    system_id, subject, create_policies, update_policies, delete_policy_ids, action_list
                )

        if create_policies:
            self._sync_db_policy_id(system_id, subject, [p.action_id for p in create_policies])

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
        执行对policies的创建, 更新, 删除操作, 调用后端批量操作接口
        """
        # 处理忽略路径
        if action_list is not None:
            for p in itertools.chain(create_policies, update_policies):
                action = action_list.get(p.action_id)
                if not action:
                    continue
                p.ignore_path(action)

        # 组装backend变更策略的数据
        backend_create_policies = [p.to_backend_dict(system_id) for p in create_policies]
        backend_update_policies = [p.to_backend_dict(system_id) for p in update_policies]

        return iam.alter_policies(
            system_id, subject.type, subject.id, backend_create_policies, backend_update_policies, delete_policy_ids
        )

    def renew(self, subject: Subject, thin_policies: List[PolicyIDExpiredAt]):
        """
        权策续期
        """
        iam.update_policy_expired_at(subject.type, subject.id, [one.dict() for one in thin_policies])

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
        db_policies = [p.to_db_model(system_id, subject, model=TemporaryPolicy) for p in policies]

        # 处理忽略路径
        if action_list is not None:
            for p in policies:
                action = action_list.get(p.action_id)
                if not action:
                    continue
                p.ignore_path(action)

        # NOTE: 这里为了先拿到后端的id, 需要先创建后端权限, 没有使用事务

        # 创建后端策略
        data = iam.create_temporary_policies(
            system_id, subject.type, subject.id, [p.to_backend_dict(system_id) for p in policies]
        )

        # 写入后端policy_ids
        for p, id in zip(db_policies, data["ids"]):
            p.policy_id = id

        # 创建db权限
        TemporaryPolicy.objects.bulk_create(db_policies, batch_size=100)

    def delete_temporary_policies_by_ids(self, system_id: str, subject: Subject, policy_ids: List[int]):
        """
        删除指定policy_id的临时策略
        """
        with transaction.atomic():
            TemporaryPolicy.objects.filter(
                system_id=system_id, subject_type=subject.type, subject_id=subject.id, policy_id__in=policy_ids
            ).delete()
            iam.delete_temporary_policies(system_id, subject.type, subject.id, policy_ids)


class PolicyOperationService:
    abac_svc = ABACPolicyOperationService()
    universal_svc = UniversalPolicyOperationService()
    common_svc = PolicyCommonDBOperationService()
    action_fields = "id,auth_type"

    def _query_action_auth_types(self, system_id: str, action_ids: Iterable[str]) -> Dict[str, str]:
        """查询操作的AuthType"""
        actions = iam.list_action(system_id, fields=self.action_fields)
        # 只返回要查询的操作的Auth，同时对于auth_type为空的，则默认为ABAC
        return {i["id"]: i["auth_type"] or AuthTypeEnum.ABAC.value for i in actions if i["id"] in action_ids}

    def _query_action_id_by_policy_ids(
        self, system_id: str, subject: Subject, policy_ids: List[int]
    ) -> Dict[int, str]:
        """根据PolicyID查询ActionID"""
        if len(policy_ids) == 0:
            return {}

        # 查询PolicyID为Backend Policy的Action
        db_policies = PolicyModel.objects.filter(
            subject_type=subject.type, subject_id=subject.id, system_id=system_id, policy_id__in=policy_ids
        ).only("policy_id", "action_id")

        return {p.policy_id: p.action_id for p in db_policies}

    def _split_policy_ids_by_auth_type(
        self, system_id: str, subject: Subject, policy_ids: List[int]
    ) -> Tuple[List[int], List[int]]:
        """用于将PolicyID区分出来，是来着RBAC还是ABAC策略"""
        if len(policy_ids) == 0:
            return [], []

        # 查询PolicyID对应的Action，然后再查询Action的AuthType
        policy_action_ids = self._query_action_id_by_policy_ids(system_id, subject, policy_ids)
        action_auth_types = self._query_action_auth_types(system_id, policy_action_ids.values())

        # 根据AuthType拆分为不同的policy_ids
        abac_policy_ids, universal_policy_ids = [], []
        for policy_id in policy_ids:
            action_id = policy_action_ids[policy_id]
            auth_type = action_auth_types[action_id]
            if auth_type == AuthTypeEnum.ABAC.value:
                abac_policy_ids.append(policy_id)
            else:
                universal_policy_ids.append(policy_id)

        return abac_policy_ids, universal_policy_ids

    def _split_policies_by_auth_type(
        self, system_id: str, policies: List[Policy]
    ) -> Tuple[List[Policy], List[Policy]]:
        """将策略列表按照其Action的AuthType进行拆分"""
        if len(policies) == 0:
            return [], []

        # 查询策略Action对应的AuthType
        action_auth_types = self._query_action_auth_types(system_id, [p.action_id for p in policies])

        # 根据AuthType拆分
        abac_policies, universal_policies = [], []
        for p in policies:
            auth_type = action_auth_types[p.action_id]
            if auth_type == AuthTypeEnum.ABAC.value:
                abac_policies.append(p)
            else:
                universal_policies.append(p)

        return abac_policies, universal_policies

    def delete_backend_policy_by_action(self, system_id: str, action_id: str):
        """删除指定操作的后台策略"""
        # 查询Action的AuthType
        auth_type = self._query_action_auth_types(system_id, [action_id])[action_id]

        # ABAC处理
        if auth_type == AuthTypeEnum.ABAC.value:
            self.abac_svc.delete_backend_policy_by_action(system_id, action_id)
            return

        # RBAC处理
        # TODO: 对于RBAC，需要后台单独提供接口，但是后台RBAC策略action_pks是一个字段，不好删除

    def delete_by_ids(self, system_id: str, subject: Subject, policy_ids: List[int]):
        """
        删除指定policy_id的策略
        """
        if subject.type == SubjectType.USER.value:
            self.abac_svc.delete_by_ids(system_id, subject, policy_ids)
            return

        # 将PolicyIDs拆分出RBAC和ABAC处理
        abac_policy_ids, universal_policy_ids = self._split_policy_ids_by_auth_type(system_id, subject, policy_ids)

        # ABAC处理
        if len(abac_policy_ids) > 0:
            self.abac_svc.delete_by_ids(system_id, subject, abac_policy_ids)

        # RBAC处理
        if len(universal_policy_ids) > 0:
            self.universal_svc.delete_by_ids(system_id, subject, universal_policy_ids)

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
        变更subject的Policies
        """
        create_policies = create_policies or []
        update_policies = update_policies or []
        delete_policy_ids = delete_policy_ids or []

        if subject.type == SubjectType.USER.value:
            self.abac_svc.alter(system_id, subject, create_policies, update_policies, delete_policy_ids, action_list)
            return

        # 1. 将创建、更新、删除的策略按照Action的AuthType进行拆分
        create_abac_policies, create_universal_policies = self._split_policies_by_auth_type(system_id, create_policies)
        update_abac_policies, update_universal_policies = self._split_policies_by_auth_type(system_id, update_policies)
        delete_abac_policy_ids, delete_universal_policy_ids = self._split_policy_ids_by_auth_type(
            system_id, subject, delete_policy_ids
        )

        # ABAC 处理
        if create_abac_policies or update_abac_policies or delete_abac_policy_ids:
            self.abac_svc.alter(system_id, subject, create_abac_policies, update_abac_policies, delete_abac_policy_ids)

        # RBAC处理
        if create_universal_policies or update_universal_policies or delete_universal_policy_ids:
            self.universal_svc.alter(
                system_id, subject, create_universal_policies, update_universal_policies, delete_universal_policy_ids
            )

    def update_db_policies(self, system_id: str, subject: Subject, policies: List[Policy]) -> None:
        """
        更新已有的SaaS DB里策略
        """
        self.common_svc.update_db_policies(system_id, subject, policies)

    def renew(self, subject: Subject, thin_policies: List[PolicyIDExpiredAt]):
        """
        权策续期
        """
        # 只有用户的权限可以续期
        assert subject.type == SubjectType.USER.value
        self.abac_svc.renew(subject, thin_policies)

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
        删除指定policy_id的临时策略
        """
        # 只有用户才有临时权限
        assert subject.type == SubjectType.USER.value
        self.abac_svc.delete_temporary_policies_by_ids(system_id, subject, policy_ids)
