# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云 - 权限中心 (BlueKing-IAM) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

审批流程
"""

from typing import Dict, List

from django.utils import timezone
from django.utils.translation import gettext as _

from backend.apps.approval.models import ActionProcessRelation, ApprovalProcessGlobalConfig, GroupProcessRelation
from backend.common.error_codes import error_codes
from backend.plugins.approval_process.base import ApprovalProcessProvider
from backend.plugins.approval_process.itsm import ITSMApprovalProcessProvider

from .constants import DEFAULT_PROCESS_SUPPORT_APPLICATION_TYPES, ApplicationType
from .models import (
    ActionApprovalProcess,
    ApprovalProcess,
    ApprovalProcessNode,
    ApprovalProcessWithNode,
    DefaultApprovalProcess,
    GroupApprovalProcess,
)


class ApprovalProcessService:
    """审批流程抽象类，主要包括以下功能：
    1. 提供流程查询功能
    2. 提供流程设置功能
    """

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self._provider: ApprovalProcessProvider | None = None

    @property
    def provider(self) -> ApprovalProcessProvider:
        """初始化：流程提供者"""
        # 避免多次读取（实际可以使用 django 的 cache_property 装饰器）
        if self._provider is not None:
            return self._provider
        # TODO：动态读取并加载配置文件设置的流程提供方，这里暂时默认读取 ITSM 的
        self._provider = ITSMApprovalProcessProvider(self.tenant_id)
        return self._provider

    def list_with_nodes(self, application_type: ApplicationType) -> List[ApprovalProcessWithNode]:
        """审批流程列表，查询指定申请类型的流程列表，并附带流程节点"""
        return self.provider.list_with_nodes(application_type)

    def get_process_nodes(self, process_id: str) -> List[ApprovalProcessNode]:
        """获取审批流程节点"""
        return self.provider.get_process_nodes(process_id)

    def _get_process_id_name_dict(self) -> Dict[str, str]:
        """获取流程 ID 与 Name 的映射"""
        processes = self.provider.list()
        return {p.id: p.name for p in processes}

    def get_process_name(self, process_id: str) -> str:
        """获取流程名称，如果没查询到，则默认返回流程 id 字符串
        这里虽然可能存在多次调用查询全部流程，但是由于短时间内存在缓存，所以不影响
        """
        return self._get_process_id_name_dict().get(process_id) or str(process_id)

    def get_default_process(self, application_type: ApplicationType) -> DefaultApprovalProcess:
        """获取某种申请类型的默认流程"""
        # 检查是否该申请类型支持配置审批流程
        if application_type not in DEFAULT_PROCESS_SUPPORT_APPLICATION_TYPES:
            raise error_codes.INVALID_ARGS.format(
                _("不支持申请类型为 [{}] 拥有默认审批流程").format(application_type), True
            )

        # 检查是否有默认审批流程
        try:
            process_config = ApprovalProcessGlobalConfig.objects.get(
                tenant_id=self.tenant_id, application_type=application_type
            )
        except ApprovalProcessGlobalConfig.DoesNotExist:
            # 没有默认审批流程，则需要从流程提供方获取并设置
            process = self.provider.get_default_process(application_type)
            process_config = ApprovalProcessGlobalConfig.objects.create(
                tenant_id=self.tenant_id, application_type=application_type, process_id=process.id
            )

        return DefaultApprovalProcess(
            application_type=application_type,
            process=ApprovalProcess(
                id=process_config.process_id, name=self.get_process_name(process_config.process_id)
            ),
        )

    def create_or_update_default_process(self, application_type: ApplicationType, process_id: int, operator: str):
        """更新或创建默认流程配置"""
        ApprovalProcessGlobalConfig.objects.update_or_create(
            tenant_id=self.tenant_id,
            application_type=application_type,
            defaults={
                "creator": operator,
                "updater": operator,
                "process_id": process_id,
                "updated_time": timezone.now(),
            },
        )

    def list_action_process(self, system_id: str, action_ids: List[str]) -> List[ActionApprovalProcess]:
        """获取某个系统下某些操作其对应的审批流程"""
        # 获取所有已配置 Action 的审批流程
        action_process_relations = ActionProcessRelation.objects.filter(
            tenant_id=self.tenant_id, system_id=system_id, action_id__in=action_ids
        )
        action_process_dict = {i.action_id: i.process_id for i in action_process_relations}

        # 默认审批流程
        default_process = self.get_default_process(ApplicationType.GRANT_ACTION.value).process

        action_processes = []
        for action_id in action_ids:
            # 查询是否已配置，没有配置则使用默认流程
            process = default_process
            if action_id in action_process_dict:
                process_id = action_process_dict[action_id]
                process = ApprovalProcess(id=process_id, name=self.get_process_name(process_id))

            action_processes.append(ActionApprovalProcess(action_id=action_id, process=process))

        return action_processes

    def batch_create_or_update_action_process(
        self, system_id: str, action_ids: List[str], process_id: int, operator: str
    ):
        """批量创建或更新操作的审批流程，对已存在的进行更新，对未存在的进行创建
        默认情况下操作与流程的绑定都是存储在权限中心的
        """
        # 查询已存在的
        exist_ids = set(
            ActionProcessRelation.objects.filter(
                tenant_id=self.tenant_id, system_id=system_id, action_id__in=action_ids
            ).values_list("action_id", flat=True)
        )

        # 对不存在的进行创建
        not_exist_ids = set(action_ids) - set(exist_ids)
        if not_exist_ids:
            action_process_relations = [
                ActionProcessRelation(
                    tenant_id=self.tenant_id,
                    system_id=system_id,
                    action_id=aid,
                    process_id=process_id,
                    creator=operator,
                    updater=operator,
                )
                for aid in not_exist_ids
            ]
            ActionProcessRelation.objects.bulk_create(action_process_relations)

        # 对已存在的进行更新
        if exist_ids:
            ActionProcessRelation.objects.filter(
                tenant_id=self.tenant_id, system_id=system_id, action_id__in=exist_ids
            ).update(process_id=process_id, updater=operator, updated_time=timezone.now())

    def batch_create_or_update_action_sensitivity_level(
        self, system_id: str, action_ids: List[str], sensitivity_level: str, operator: str
    ):
        """批量更新操作的敏感级别"""
        # 查询已存在的
        exist_ids = set(
            ActionProcessRelation.objects.filter(
                tenant_id=self.tenant_id, system_id=system_id, action_id__in=action_ids
            ).values_list("action_id", flat=True)
        )

        # 对不存在的进行创建
        default_process = self.get_default_process(ApplicationType.GRANT_ACTION.value).process
        not_exist_ids = set(action_ids) - set(exist_ids)
        if not_exist_ids:
            action_process_relations = [
                ActionProcessRelation(
                    tenant_id=self.tenant_id,
                    system_id=system_id,
                    action_id=aid,
                    process_id=default_process.id,
                    sensitivity_level=sensitivity_level,
                    creator=operator,
                    updater=operator,
                )
                for aid in not_exist_ids
            ]
            ActionProcessRelation.objects.bulk_create(action_process_relations)

        # 对已存在的进行更新
        if exist_ids:
            ActionProcessRelation.objects.filter(
                tenant_id=self.tenant_id, system_id=system_id, action_id__in=exist_ids
            ).update(sensitivity_level=sensitivity_level, updater=operator, updated_time=timezone.now())

    def list_group_process(self, group_ids: List[int]) -> List[GroupApprovalProcess]:
        """批量查询用户组对应的审批流程"""
        # 获取所有已配置的用户组的审批流程
        group_process_relations = GroupProcessRelation.objects.filter(tenant_id=self.tenant_id, group_id__in=group_ids)
        group_process_dict = {i.group_id: i.process_id for i in group_process_relations}

        # 默认审批流程
        default_process = self.get_default_process(ApplicationType.JOIN_GROUP.value).process

        group_processes = []
        for group_id in group_ids:
            # 查询是否已配置，没有配置则使用默认流程
            process = default_process
            if group_id in group_process_dict:
                process_id = group_process_dict[group_id]
                process = ApprovalProcess(id=process_id, name=self.get_process_name(process_id))

            group_processes.append(GroupApprovalProcess(group_id=group_id, process=process))

        return group_processes

    def batch_create_or_update_group_process(self, group_ids: List[int], process_id: int, operator: str):
        """批量创建或更新用户组的审批流程，对已存在的进行更新，对未存在的进行创建
        默认情况下操作与流程的绑定都是存储在权限中心的
        """
        # 查询已存在
        exist_ids = set(
            GroupProcessRelation.objects.filter(tenant_id=self.tenant_id, group_id__in=group_ids).values_list(
                "group_id", flat=True
            )
        )

        # 对不存在的进行创建
        not_exist_ids = set(group_ids) - exist_ids
        if not_exist_ids:
            group_process_relations = [
                GroupProcessRelation(
                    tenant_id=self.tenant_id, group_id=gid, process_id=process_id, creator=operator, updater=operator
                )
                for gid in not_exist_ids
            ]
            GroupProcessRelation.objects.bulk_create(group_process_relations)

        # 对已存在的进行更新
        if exist_ids:
            GroupProcessRelation.objects.filter(tenant_id=self.tenant_id, group_id__in=exist_ids).update(
                process_id=process_id, updater=operator, updated_time=timezone.now()
            )

    def list_default_process(self) -> List[DefaultApprovalProcess]:
        """查询所有默认流程"""
        return [
            self.get_default_process(application_type)
            for application_type in DEFAULT_PROCESS_SUPPORT_APPLICATION_TYPES
        ]
