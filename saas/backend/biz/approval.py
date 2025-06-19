#!/usr/bin/env python3
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

from typing import Dict, List

from pydantic import BaseModel

from backend.service.approval import ApprovalProcessService
from backend.service.constants import ApplicationType
from backend.service.models import ApprovalProcess


class ApprovalProcessBean(ApprovalProcess):
    pass


class ApprovalProcessWithNodeNamesBean(ApprovalProcess):
    node_names: List[str]


class DefaultProcessBean(BaseModel):
    type: str
    process_id: str
    process_name: str


class ActionApprovalProcessRelationDictBean(BaseModel):
    relation: Dict[str, ApprovalProcessBean]

    def get_process(self, action_id: str) -> ApprovalProcessBean:
        return self.relation[action_id]


class GroupApprovalProcessRelationDictBean(BaseModel):
    relation: Dict[int, ApprovalProcessBean]

    def get_process(self, group_id: int) -> ApprovalProcessBean:
        return self.relation[group_id]


class ApprovalProcessBiz:
    svc = ApprovalProcessService()

    def list_with_node_names(self, application_type: ApplicationType) -> List[ApprovalProcessWithNodeNamesBean]:
        """查询某个类型可配置的流程，用于展示，需要带上流程节点名称"""
        processes_with_nodes = self.svc.list_with_nodes(application_type)
        return [
            ApprovalProcessWithNodeNamesBean(id=p.id, name=p.name, node_names=[n.name for n in p.nodes])
            for p in processes_with_nodes
        ]

    def list_default_process(self) -> List[DefaultProcessBean]:
        """查询默认流程"""
        processes = self.svc.list_default_process()
        return [
            DefaultProcessBean(type=dp.application_type, process_id=dp.process.id, process_name=dp.process.name)
            for dp in processes
        ]

    def create_or_update_default_process(self, application_type: ApplicationType, process_id: int, operator: str):
        """更新或创建默认流程配置"""
        self.svc.create_or_update_default_process(application_type, process_id, operator)

    def get_action_process_relation_dict(
        self, system_id: str, action_ids: List[str]
    ) -> ActionApprovalProcessRelationDictBean:
        """获取操作对应流程"""
        action_processes = self.svc.list_action_process(system_id, action_ids)
        return ActionApprovalProcessRelationDictBean(relation={ap.action_id: ap.process for ap in action_processes})

    def batch_create_or_update_action_process(
        self, system_id: str, action_ids: List[str], process_id: int, operator: str
    ):
        """批量更新或者创建操作的审批流程"""
        self.svc.batch_create_or_update_action_process(system_id, action_ids, process_id, operator)

    def batch_create_or_update_action_sensitivity_level(
        self, system_id: str, action_ids: List[str], sensitivity_level: str, operator: str
    ):
        """批量更新或者创建操作的敏感等级"""
        self.svc.batch_create_or_update_action_sensitivity_level(system_id, action_ids, sensitivity_level, operator)

    def get_group_process_relation_dict(self, group_ids: List[int]) -> GroupApprovalProcessRelationDictBean:
        """获取用户组对应的流程"""
        group_processes = self.svc.list_group_process(group_ids)
        return GroupApprovalProcessRelationDictBean(relation={gp.group_id: gp.process for gp in group_processes})

    def batch_create_or_update_group_process(self, group_ids: List[int], process_id: int, operator: str):
        """批量更新或创建用户组的审批流程"""
        self.svc.batch_create_or_update_group_process(group_ids, process_id, operator)
