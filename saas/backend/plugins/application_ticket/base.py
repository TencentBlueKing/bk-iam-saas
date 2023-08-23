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
from typing import Dict, List, Optional

from rest_framework.request import Request

from backend.service.models import (
    ApplicationTicket,
    ApprovalProcessWithNodeProcessor,
    GradeManagerApplicationData,
    GrantActionApplicationData,
    GroupApplicationData,
)


class ApplicationTicketProvider(metaclass=abc.ABCMeta):
    """申请单据提供方的抽象类"""

    @abc.abstractmethod
    def list_by_sns(self, sns: List[str]) -> List[ApplicationTicket]:
        """批量根据单据号查询单据信息"""
        pass

    @abc.abstractmethod
    def get_ticket(self, sn: str) -> ApplicationTicket:
        """获取单据信息"""
        pass

    @abc.abstractmethod
    def create_for_policy(
        self, data: GrantActionApplicationData, process: ApprovalProcessWithNodeProcessor, callback_url: str
    ) -> str:
        """创建 - 申请或续期自定义权限单据"""
        pass

    @abc.abstractmethod
    def create_for_group(
        self,
        data: GroupApplicationData,
        process: ApprovalProcessWithNodeProcessor,
        callback_url: str,
        tag: str = "",
        approval_title_prefix: str = "",
        approval_content: Optional[Dict] = None,
    ) -> str:
        """创建 - 申请加入或续期用户组单据"""
        pass

    @abc.abstractmethod
    def create_for_grade_manager(
        self,
        data: GradeManagerApplicationData,
        process: ApprovalProcessWithNodeProcessor,
        callback_url: str,
        approval_title: str = "",
        approval_content: Optional[Dict] = None,
        tag: str = "",
    ) -> str:
        """创建 - 创建或更新分级管理员"""
        pass

    @abc.abstractmethod
    def get_approval_ticket_from_callback_request(self, request: Request) -> ApplicationTicket:
        """处理审批回调结果"""
        pass

    @abc.abstractmethod
    def cancel_ticket(self, sn: str, operator: str):
        """撤销单据"""
        pass
