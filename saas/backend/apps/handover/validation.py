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

import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List

from django.utils.functional import cached_property
from rest_framework import serializers

from backend.apps.role.models import RoleUser
from backend.apps.subject_template.models import SubjectTemplateRelation
from backend.service.constants import SubjectType
from backend.service.group import GroupService
from backend.service.models.policy import Policy
from backend.service.models.subject import Subject
from backend.service.policy.query import PolicyQueryService


class BaseHandoverDataProcessor(ABC):
    """交接数据合法性校验器基类: 仅做对前端提交 ID 的合法性校验, 不涉及业务详情查询"""

    def __init__(self, handover_from: str, *args, **kwargs):
        """
        Args:
            handover_from: 交接来源用户
            *args: 其他参数, 由子类定义
            **kwargs: 其他关键字参数
        """
        self.handover_from = handover_from

    @abstractmethod
    def validate(self):
        pass


class GroupInfoProcessor(BaseHandoverDataProcessor):
    group_svc = GroupService()

    def __init__(self, handover_from: str, group_ids: List[int]) -> None:
        super().__init__(handover_from)
        self.group_ids = group_ids

    def validate(self):
        # 校验用户是否在属于用户组
        now_ts = int(time.time())
        subject_group_id_set = {int(g.id) for g in self._subject_groups if g.expired_at > now_ts}

        for _id in self.group_ids:
            if _id not in subject_group_id_set:
                raise serializers.ValidationError("用户组: {} 不在当前用户的可交接范围内!".format(_id))

    @cached_property
    def _subject_groups(self):
        subject = Subject.from_username(self.handover_from)
        # NOTE: 可能会有性能问题, 这里需要查询用户的所有组列表
        return self.group_svc.list_all_subject_group_before_expired_at(subject, expired_at=0)


class GustomPolicyProcessor(BaseHandoverDataProcessor):
    policy_query_svc = PolicyQueryService()

    def __init__(self, handover_from: str, custom_policies: List[Dict[str, Any]]) -> None:
        super().__init__(handover_from)
        self.custom_policies = custom_policies

    def validate(self):
        """
        1. 查询用户的每个系统的自定义权限
        2. 校验 id 是否在自定义权限中
        """
        now_ts = int(time.time())
        subject = Subject.from_username(self.handover_from)
        for system_policy in self.custom_policies:
            policies: List[Policy] = self.policy_query_svc.list_by_subject(system_policy["system_id"], subject)
            subject_policy_id_set = {p.policy_id for p in policies if p.expired_at > now_ts}
            for _id in system_policy["policy_ids"]:
                if _id not in subject_policy_id_set:
                    raise serializers.ValidationError(
                        "自定义权限: {}{} 不在当前用户的可交接范围内!".format(system_policy["system_id"], _id)
                    )


class RoleInfoProcessor(BaseHandoverDataProcessor):
    def __init__(self, handover_from: str, role_ids: List[int]) -> None:
        super().__init__(handover_from)
        self.role_ids = role_ids

    def validate(self):
        for _id in self.role_ids:
            if not RoleUser.objects.user_role_exists(self.handover_from, _id):
                raise serializers.ValidationError("角色: {} 不在当前用户的可交接范围内!".format(_id))


class SubjectTemplateProcessor(BaseHandoverDataProcessor):
    def __init__(self, handover_from: str, subject_template_ids: List[int]) -> None:
        super().__init__(handover_from)
        self.subject_template_ids = subject_template_ids

    def validate(self):
        for _id in self.subject_template_ids:
            if not SubjectTemplateRelation.objects.filter(
                template_id=_id, subject_id=self.handover_from, subject_type=SubjectType.USER.value
            ).exists():
                raise serializers.ValidationError("角色: {} 不在当前用户的可交接范围内!".format(_id))
