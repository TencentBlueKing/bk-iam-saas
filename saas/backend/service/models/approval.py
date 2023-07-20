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
from typing import List

from pydantic import BaseModel

from ..constants import APPLICATION_SUPPORT_PROCESSOR_ROLE_MAP, ApplicationType, ProcessorNodeType, ProcessorSource


class ApprovalProcess(BaseModel):
    id: int
    name: str


class ApprovalProcessNode(BaseModel):
    """流程节点
    包含字段：唯一标识、节点名称、流程处理者来源、流程者类型
    流程处理者来源：有IAM 和其他，目前默认非IAM都是其他，若后续IAM内置审批，则进行扩展
    流程处理者类型：
    1. 若来源是IAM,则包括IAM超级管理员、IAM分级管理员等，即[]
    2. 若来源非IAM,则可能是第三方审批系统定义的角色，比如Leader/指定审批人等
    """

    id: int
    name: str
    processor_source: str
    processor_type: str

    # 申请审批在合并单据时需要对流程进行判断是否相同
    def __hash__(self):
        return hash((self.id, self.processor_source, self.processor_type))

    def __eq__(self, other):
        return (
            self.id == other.id
            and self.processor_source == other.processor_source
            and self.processor_type == other.processor_type
        )

    def is_application_type_supported(self, application_type: ApplicationType) -> bool:
        """是否支持配置为某种申请类型的流程节点"""
        # 非IAM来源的默认支持被所有类型的申请配置为审批流程的节点
        if not self.is_iam_source():
            return True

        # 查看是否申请类型支持的节点处理者类型
        if self.processor_type not in APPLICATION_SUPPORT_PROCESSOR_ROLE_MAP[application_type]:
            return False

        return True

    def is_iam_source(self) -> bool:
        return self.processor_source == ProcessorSource.IAM.value


class ApprovalProcessWithNode(ApprovalProcess):
    """附带流程里的每个节点名称"""

    nodes: List[ApprovalProcessNode] = []

    def is_match_application_type(self, application_type: ApplicationType) -> bool:
        """判断流程与审批类型是否匹配"""
        # 检查所有节点是否都支持当前的申请类型，只要有一个节点不支持，则表示整个流程都不能匹配该申请类型
        for node in self.nodes:
            if not node.is_application_type_supported(application_type):
                return False
        return True


class DefaultApprovalProcess(BaseModel):
    application_type: str
    process: ApprovalProcess


class ActionApprovalProcess(BaseModel):
    action_id: str
    process: ApprovalProcess


class GroupApprovalProcess(BaseModel):
    group_id: int
    process: ApprovalProcess


class ApprovalProcessNodeWithProcessor(ApprovalProcessNode):
    """流程节点，并附带节点的处理者"""

    processors: List[str] = []

    # 申请审批在合并单据时需要对流程进行判断是否相同
    def __hash__(self):
        return hash((self.id, self.processor_source, self.processor_type, ",".join(self.processors)))

    def __eq__(self, other):
        return (
            self.id == other.id
            and self.processor_source == other.processor_source
            and self.processor_type == other.processor_type
            and self.processors == other.processors
        )


class ApprovalProcessWithNodeProcessor(ApprovalProcessWithNode):
    """附带流程里的每个节点, 且每个节点都附带具体处理人"""

    nodes: List[ApprovalProcessNodeWithProcessor] = []

    # 申请审批在合并单据时需要对流程进行判断是否相同
    def __hash__(self):
        return hash((self.id, tuple(self.nodes)))

    def __eq__(self, other):
        return self.id == other.id and self.nodes == other.nodes

    def set_node_approver(self, node_type: str, approver: List[str]):
        for node in self.nodes:
            if node.is_iam_source() and node.processor_type == node_type:
                node.processors = approver

    def has_instance_approver_node(self, judge_empty=False) -> bool:
        """
        是否包含资源审批人节点

        judge_empty: 是否判断节点的审批人为空
        """
        for node in self.nodes:
            if node.is_iam_source() and node.processor_type == ProcessorNodeType.INSTANCE_APPROVER.value:
                # 判断节点审批人是否为空
                if judge_empty and len(node.processors) == 0:
                    return False

                return True
        return False

    def has_grade_manager_node(self) -> bool:
        """
        是否包含分级管理员节点
        """
        for node in self.nodes:
            if node.is_iam_source() and node.processor_type == ProcessorNodeType.GRADE_MANAGER.value:
                return True
        return False
