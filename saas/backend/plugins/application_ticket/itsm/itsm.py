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

from typing import Dict, List, Optional

from rest_framework.request import Request

from backend.component.client.bk_itsm import BkITSMClient
from backend.service.constants import ApplicationStatus, ApplicationType, ProcessorSource
from backend.service.models import (
    ApplicationTicket,
    ApprovalProcessWithNodeProcessor,
    GradeManagerApplicationData,
    GrantActionApplicationData,
    GroupApplicationData,
    TypeUnionApplicationData,
)

from .constants import TicketStatus
from .serializers import ApprovalSLZ
from .ticket_content import ActionTable, GradeManagerForm, GroupTable
from .ticket_content_tpl import FORM_SCHEMES
from ..base import ApplicationTicketProvider


class ITSMApplicationTicketProvider(ApplicationTicketProvider):
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.client = BkITSMClient(tenant_id)

    def list_by_sns(self, sns: List[str]) -> List[ApplicationTicket]:
        """批量根据单据号查询单据信息"""
        data = self.client.batch_query_ticket_result(sns)
        return [
            ApplicationTicket(
                sn=i["id"],
                url=i["frontend_url"],
                status=self._convert_status(i["status"], i["approve_result"], i["end_at"]),
            )
            for i in data
        ]

    def get_ticket(self, sn: str) -> ApplicationTicket:
        """获取单据信息"""
        return self.list_by_sns([sn])[0]

    def _generate_ticket_common_params(
        self,
        data: TypeUnionApplicationData,
        process: ApprovalProcessWithNodeProcessor,
        callback_url: str,
        callback_token: str,
    ) -> Dict:
        """生成 Ticket 的通用参数"""
        # 对于 ITSM，只需要 IAM 角色相关的处理者
        node_processors = {
            node.processor_type: node.processors
            for node in process.nodes
            if node.processor_source == ProcessorSource.IAM.value
        }

        # 申请人的组织架构
        departments = data.applicant_info.organization
        # 容错处理：组织可能未空
        organization_names = "\n".join([d.full_name for d in departments]) or "--"

        return {
            "workflow_key": process.id,
            "operator": data.applicant_info.username,
            "callback_url": callback_url,
            "callback_token": callback_token,
            "form_data": {
                "ticket__title": "",
                "application_type": ApplicationType.get_choice_label(data.type),
                "reason": data.reason,
                "organization": organization_names,
                **{key: value for key, value in node_processors.items() if key != "creator"},
            },
        }

    def create_for_policy(
        self,
        data: GrantActionApplicationData,
        process: ApprovalProcessWithNodeProcessor,
        callback_url: str,
        approval_title_prefix: str = "",
        approval_content: Optional[Dict] = None,
        callback_token: str = "",
    ) -> str:
        """创建 - 申请或续期自定义权限单据"""
        params = self._generate_ticket_common_params(data, process, callback_url, callback_token)

        if approval_title_prefix:
            params["form_data"]["ticket__title"] = f"{approval_title_prefix} {len(data.content.policies)} 个操作权限"
        else:
            params["form_data"]["ticket__title"] = (
                f"申请{data.content.system.name}{len(data.content.policies)}个操作权限"
            )

        if approval_content:
            params["form_data"]["content"] = approval_content
        else:
            params["form_data"]["content"] = {
                "schemes": FORM_SCHEMES,
                "data": [ActionTable.from_application(data.content).dict()],
            }  # 真正生成申请内容的核心入口点

        # 在 params 中加上权限获得者，增加敏感等级提示语句
        params["form_data"]["permission_holder"] = data.get_applicants_field()
        params["form_data"]["sensitivity_level"] = data.get_action_sensitivity_level_field()

        ticket = self.client.create_ticket(**params)
        return ticket["id"]

    def create_for_group(
        self,
        data: GroupApplicationData,
        process: ApprovalProcessWithNodeProcessor,
        callback_url: str,
        tag: str = "",
        approval_title_prefix: str = "",
        approval_content: Optional[Dict] = None,
        callback_token: str = "",
    ) -> str:
        """创建 - 申请加入或续期用户组单据"""
        params = self._generate_ticket_common_params(data, process, callback_url, callback_token)

        if approval_title_prefix:
            title_prefix = approval_title_prefix + f" {len(data.content.groups)} 个用户组"
        else:
            title_prefix = (
                f"申请加入 {len(data.content.groups)} 个用户组"
                if data.type == ApplicationType.JOIN_GROUP
                else f"申请续期 {len(data.content.groups)} 个用户组"
            )
        title = "{}：{}".format(
            title_prefix, "、".join([f"({one.role_name}){one.name}" for one in data.content.groups])
        )
        if len(title) > 64:  # noqa: PLR2004
            title = title[:64] + "..."

        params["form_data"]["ticket__title"] = title

        if approval_content:
            params["form_data"]["content"] = approval_content
        else:
            params["form_data"]["content"] = {
                "schemes": FORM_SCHEMES,
                "data": [GroupTable.from_application(data.content).dict()],
            }

        params["form_data"]["permission_holder"] = data.get_applicants_field()
        params["form_data"]["sensitivity_level"] = data.get_action_sensitivity_level_field()

        ticket = self.client.create_ticket(**params)
        return ticket["id"]

    def create_for_grade_manager(
        self,
        data: GradeManagerApplicationData,
        process: ApprovalProcessWithNodeProcessor,
        callback_url: str,
        approval_title: str = "",
        approval_content: Optional[Dict] = None,
        tag: str = "",
        callback_token: str = "",
    ) -> str:
        """创建 - 创建或更新分级管理员"""
        params = self._generate_ticket_common_params(data, process, callback_url, callback_token)

        if approval_title:
            params["form_data"]["ticket__title"] = approval_title
        else:
            title_prefix = (
                "申请创建管理空间" if data.type == ApplicationType.CREATE_GRADE_MANAGER.value else "申请编辑管理空间"
            )
            params["form_data"]["ticket__title"] = f"{title_prefix}:{data.content.name}"

        if approval_content:
            params["form_data"]["content"] = approval_content
        else:
            params["form_data"]["content"] = {
                "schemes": FORM_SCHEMES,
                "data": GradeManagerForm.from_application(data.content).form_data,
            }

        ticket = self.client.create_ticket(**params)
        return ticket["id"]

    def _convert_status(
        self, ticket_status: TicketStatus, approve_result: bool, end_at: Optional[str] = None
    ) -> ApplicationStatus:
        """将 ITSM 单据状态和结果转换为权限中心定义的单据状态"""
        status = ApplicationStatus.PENDING.value
        if approve_result and end_at is not None:
            status = ApplicationStatus.PASS.value
        elif not approve_result and end_at is not None and ticket_status == TicketStatus.FINISHED.value:
            status = ApplicationStatus.REJECT.value
        elif ticket_status in [TicketStatus.TERMINATION.value, TicketStatus.REVOKED.value]:
            status = ApplicationStatus.CANCELLED.value

        return status

    def get_approval_ticket_from_callback_request(self, request: Request) -> ApplicationTicket:
        """处理审批回调结果"""
        serializer = ApprovalSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        ticket_id = serializer.validated_data["ticket"]["id"]
        ticket_status = serializer.validated_data["ticket"]["status"]
        approve_result = serializer.validated_data["ticket"]["approve_result"]
        end_at = serializer.validated_data["ticket"]["end_at"]

        status = self._convert_status(ticket_status, approve_result, end_at=end_at)

        return ApplicationTicket(sn=ticket_id, status=status)

    def cancel_ticket(self, sn: str):
        """撤销单据"""
        self.client.withdraw_ticket(sn)
