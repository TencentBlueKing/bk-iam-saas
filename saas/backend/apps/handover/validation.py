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
from collections import defaultdict
from typing import Any, Dict, List

from django.utils.functional import cached_property
from pydantic import parse_obj_as
from rest_framework import serializers

from backend.apps.approval.models import ActionProcessRelation
from backend.apps.group.models import Group
from backend.apps.policy.models import Policy
from backend.apps.role.models import Role, RoleRelatedObject, RoleUser
from backend.apps.subject_template.models import SubjectTemplate, SubjectTemplateRelation
from backend.biz.group import GroupBiz, SubjectGroupBean
from backend.biz.policy import PolicyQueryBiz
from backend.biz.system import SystemBiz
from backend.service.constants import RoleRelatedObjectType, SensitivityLevel, SubjectType
from backend.service.models.application import ApplicationPolicyInfo
from backend.service.models.subject import Subject


class BaseHandoverDataProcessor(ABC):
    @abstractmethod
    def validate(self):
        pass

    @abstractmethod
    def get_info(self):
        pass


class GroupInfoProcessor(BaseHandoverDataProcessor):
    biz = GroupBiz()

    def __init__(self, handover_from: str, group_ids: List[int]) -> None:
        self.handover_from = handover_from
        self.group_ids = group_ids

    def validate(self):
        # 校验用户是否在属于用户组
        now_ts = int(time.time())
        subject_group_id_set = {g.id for g in self.subject_groups if g.expired_at > now_ts}

        for _id in self.group_ids:
            if _id not in subject_group_id_set:
                raise serializers.ValidationError("用户组: {} 不在当前用户的可交接范围内!".format(_id))

    def get_info(self):
        groups = Group.objects.filter(id__in=self.group_ids)
        group_expired_at = {g.id: g.expired_at for g in self.subject_groups}

        # 查询用户组所属的管理空间名称
        group_role_map = {
            one["object_id"]: one["role_id"]
            for one in RoleRelatedObject.objects.filter(
                object_type=RoleRelatedObjectType.GROUP.value, object_id__in=self.group_ids
            ).values("role_id", "object_id")
        }
        role_name_map: Dict[int, str] = {}
        if group_role_map:
            role_name_map = {
                one["id"]: one["name"]
                for one in Role.objects.filter(id__in=set(group_role_map.values())).values("id", "name")
            }

        # 查询每个用户组的最高敏感等级（基于其所有权限模板/自定义权限的策略敏感等级）
        highest_sensitivity_level_map = self._get_groups_highest_sensitivity_level(self.group_ids)

        return [
            {
                "id": group.id,
                "name": group.name,
                "description": group.description,
                "expired_at": group_expired_at[group.id],
                "role_name": role_name_map.get(group_role_map.get(group.id, 0), ""),
                "highest_sensitivity_level": highest_sensitivity_level_map.get(group.id, SensitivityLevel.L1.value),
            }
            for group in groups
        ]

    @staticmethod
    def _get_groups_highest_sensitivity_level(group_ids: List[int]) -> Dict[int, str]:
        """计算用户组的最高敏感等级

        取每个用户组下所有自定义权限策略的最高敏感等级。
        """
        if not group_ids:
            return {}

        # 1. 查询所有用户组的 (system_id, action_id) 关系
        group_actions = list(
            Policy.objects.filter(
                subject_type=SubjectType.GROUP.value,
                subject_id__in=[str(gid) for gid in group_ids],
            ).values("subject_id", "system_id", "action_id")
        )
        if not group_actions:
            return {gid: SensitivityLevel.L1.value for gid in group_ids}

        # 2. 查询所涉及系统的 (system_id, action_id) -> sensitivity_level 映射
        involved_systems = {ga["system_id"] for ga in group_actions}
        sensitivity_map = {
            (rel["system_id"], rel["action_id"]): rel["sensitivity_level"]
            for rel in ActionProcessRelation.objects.filter(system_id__in=involved_systems).values(
                "system_id", "action_id", "sensitivity_level"
            )
        }

        # 3. 聚合每个用户组的最高敏感等级
        group_levels: Dict[int, List[str]] = defaultdict(list)
        for ga in group_actions:
            level = sensitivity_map.get((ga["system_id"], ga["action_id"]), SensitivityLevel.L1.value)
            group_levels[int(ga["subject_id"])].append(level)

        return {
            gid: (max(group_levels[gid]) if group_levels.get(gid) else SensitivityLevel.L1.value) for gid in group_ids
        }

    @cached_property
    def subject_groups(self) -> List[SubjectGroupBean]:
        subject = Subject.from_username(self.handover_from)
        # NOTE: 可能会有性能问题, 这里需要查询用户的所有组列表
        return self.biz.list_all_subject_group(subject)


class GustomPolicyProcessor(BaseHandoverDataProcessor):
    biz = PolicyQueryBiz()
    system_biz = SystemBiz()

    def __init__(self, handover_from: str, custom_policies: List[Dict[str, Any]]) -> None:
        self.handover_from = handover_from
        self.custom_policies = custom_policies

    def validate(self):
        """
        1. 查询用户的每个系统的自定义权限
        2. 校验id是否在自定义权限中
        """
        subject = Subject.from_username(self.handover_from)
        for system_policy in self.custom_policies:
            policies = self.biz.list_by_subject(system_policy["system_id"], subject)
            subject_policy_id_set = {p.policy_id for p in policies if not p.is_expired()}
            for _id in system_policy["policy_ids"]:
                if _id not in subject_policy_id_set:
                    raise serializers.ValidationError(
                        "自定义权限: {}{} 不在当前用户的可交接范围内!".format(system_policy["system_id"], _id)
                    )

    def get_info(self):
        system_list = self.system_biz.new_system_list()
        subject = Subject.from_username(self.handover_from)
        infos = []
        for system_policy in self.custom_policies:
            sys = system_list.get(system_policy["system_id"])
            application_policies: List[Dict[str, Any]] = []
            if system_policy["policy_ids"]:
                policies = self.biz.list_by_subject(system_policy["system_id"], subject)
                policy_map = {p.policy_id: p for p in policies if not p.is_expired()}

                hit_policies = [policy_map[pid] for pid in system_policy["policy_ids"] if pid in policy_map]
                if hit_policies:
                    application_policies = [
                        p.dict(by_alias=True) for p in parse_obj_as(List[ApplicationPolicyInfo], hit_policies)
                    ]
            infos.append(
                {
                    "id": system_policy["system_id"],
                    "policy_ids": system_policy["policy_ids"],
                    "name": sys.name if sys else "",
                    "name_en": sys.name_en if sys else "",
                    "policies": application_policies,
                }
            )
        return infos


class RoleInfoProcessor(BaseHandoverDataProcessor):
    def __init__(self, handover_from: str, role_ids: List[int]) -> None:
        self.handover_from = handover_from
        self.role_ids = role_ids

    def validate(self):
        for _id in self.role_ids:
            if not RoleUser.objects.user_role_exists(self.handover_from, _id):
                raise serializers.ValidationError("角色: {} 不在当前用户的可交接范围内!".format(_id))

    def get_info(self):
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


class SubjectTemplateProcessor(BaseHandoverDataProcessor):
    def __init__(self, handover_from: str, subject_template_ids: List[int]) -> None:
        self.handover_from = handover_from
        self.subject_template_ids = subject_template_ids

    def validate(self):
        for _id in self.subject_template_ids:
            if not SubjectTemplateRelation.objects.filter(
                template_id=_id, subject_id=self.handover_from, subject_type=SubjectType.USER.value
            ).exists():
                raise serializers.ValidationError("人员模板: {} 不在当前用户的可交接范围内!".format(_id))

    def get_info(self):
        templates = SubjectTemplate.objects.filter(id__in=self.subject_template_ids)
        return [{"id": t.id, "name": t.name, "description": t.description} for t in templates]
