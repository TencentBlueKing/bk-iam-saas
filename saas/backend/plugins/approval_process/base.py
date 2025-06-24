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

import abc
from typing import List

from backend.service.constants import ApplicationType
from backend.service.models import ApprovalProcess, ApprovalProcessNode, ApprovalProcessWithNode


class ApprovalProcessProvider(metaclass=abc.ABCMeta):
    """流程提供方的抽象类"""

    @abc.abstractmethod
    def list(self) -> List[ApprovalProcess]:
        """查询审批流程列表，所有流程"""

    @abc.abstractmethod
    def list_with_nodes(self, application_type: ApplicationType) -> List[ApprovalProcessWithNode]:
        """审批流程列表，查询指定申请类型的流程列表，并附带流程节点"""

    @abc.abstractmethod
    def get_default_process(self, application_type: ApplicationType) -> ApprovalProcess:
        """获取某种申请类型的默认流程
        application_type只需要实现两种，（1）加入用户组（2）申请自定义权限
        """

    @abc.abstractmethod
    def get_process_nodes(self, process_id: str) -> List[ApprovalProcessNode]:
        """查询流程的节点"""
