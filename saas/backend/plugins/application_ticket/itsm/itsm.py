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
from typing import Dict, List, Optional

from rest_framework.request import Request

from backend.component import itsm
from backend.service.constants import ApplicationStatus, ApplicationType, ProcessorSource, SubjectType
from backend.service.models import (
    ApplicationTicket,
    ApprovalProcessWithNodeProcessor,
    GradeManagerApplicationData,
    GrantActionApplicationData,
    GroupApplicationData,
    TypeUnionApplicationData,
)

from ..base import ApplicationTicketProvider
from .constants import TicketStatus
from .serializers import ApprovalSLZ
from .ticket_content import ActionTable, GradeManagerForm, GroupTable
from .ticket_content_tpl import FORM_SCHEMES


class ITSMApplicationTicketProvider(ApplicationTicketProvider):
    def list_by_sns(self, sns: List[str]) -> List[ApplicationTicket]:
        """批量根据单据号查询单据信息"""
        data = itsm.batch_query_ticket_result(sns)
        tickets = [
            ApplicationTicket(
                sn=i["sn"], url=i["ticket_url"], status=self._convert_status(i["current_status"], i["approve_result"])
            )
            for i in data
        ]
        return tickets

    def get_ticket(self, sn: str) -> ApplicationTicket:
        """获取单据信息"""
        return self.list_by_sns([sn])[0]

    def _generate_ticket_common_params(
        self, data: TypeUnionApplicationData, process: ApprovalProcessWithNodeProcessor, callback_url: str
    ) -> Dict:
        """生成Ticket的通用参数"""
        # 对于ITSM，只需要IAM角色相关的处理者
        node_processors_dict = {
            node.id: ",".join(node.processors)
            for node in process.nodes
            if node.processor_source == ProcessorSource.IAM.value
        }

        # 申请人的组织架构
        departments = data.applicant_info.organization
        # 容错处理：组织可能未空
        organization_names = "\n".join([d.full_name for d in departments]) or "--"

        return {
            "process_id": process.id,
            "creator": data.applicant_info.username,
            "callback_url": callback_url,
            "node_processors": node_processors_dict,
            "application_type_display": ApplicationType.get_choice_label(data.type),
            "organization_names": organization_names,
            "reason": data.reason,
        }

    def create_for_policy(
        self, data: GrantActionApplicationData, process: ApprovalProcessWithNodeProcessor, callback_url: str
    ) -> str:
        """创建 - 申请或续期自定义权限单据"""
        params = self._generate_ticket_common_params(data, process, callback_url)
        params["title"] = f"申请{data.content.system.name}{len(data.content.policies)}个操作权限"
        params["content"] = {
            "schemes": FORM_SCHEMES,
            "form_data": [ActionTable.from_application(data.content).dict()],
        }  # 真正生成申请内容的核心入口点

        # 如果审批流程中包含资源审批人, 并且资源审批人不为空
        # 增加 has_instance_approver 字段, 用于itsm审批流程走分支
        if process.has_instance_approver_node():
            params["has_instance_approver"] = int(process.has_instance_approver_node(judge_empty=True))

        # 在params中加上权限获得者
        params["dynamic_fields"] = [
            {
                "name": "权限获得者",
                "type": "STRING",
                "value": ", ".join(
                    [
                        "{}: {}({})".format("用户" if u.type == SubjectType.USER.value else "部门", u.display_name, u.id)
                        for u in data.content.applicants
                    ]
                ),
                "meta": {"language": {"en": "recipient of permissions"}},
            }
        ]

        ticket = itsm.create_ticket(**params)
        return ticket["sn"]

    def create_for_group(
        self, data: GroupApplicationData, process: ApprovalProcessWithNodeProcessor, callback_url: str, tag: str = ""
    ) -> str:
        """创建 - 申请加入或续期用户组单据"""
        params = self._generate_ticket_common_params(data, process, callback_url)

        title_prefix = (
            f"申请加入 {len(data.content.groups)} 个用户组"
            if data.type == ApplicationType.JOIN_GROUP
            else f"申请续期 {len(data.content.groups)} 个用户组"
        )
        params["title"] = "{}：{}".format(title_prefix, "、".join([one.name for one in data.content.groups]))

        params["content"] = {"schemes": FORM_SCHEMES, "form_data": [GroupTable.from_application(data.content).dict()]}

        # 在params中加上权限获得者
        params["dynamic_fields"] = [
            {
                "name": "权限获得者",
                "type": "STRING",
                "value": ", ".join(
                    [
                        "{}: {}({})".format("用户" if u.type == SubjectType.USER.value else "部门", u.display_name, u.id)
                        for u in data.content.applicants
                    ]
                ),
                "meta": {"language": {"en": "recipient of permissions"}},
            }
        ]

        params["tag"] = tag
        ticket = itsm.create_ticket(**params)
        return ticket["sn"]

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
        params = self._generate_ticket_common_params(data, process, callback_url)

        if approval_title:
            params["title"] = approval_title
        else:
            title_prefix = "申请创建管理空间" if data.type == ApplicationType.CREATE_GRADE_MANAGER.value else "申请编辑管理空间"
            params["title"] = f"{title_prefix}：{data.content.name}"

        if approval_content:
            params["content"] = approval_content
        else:
            params["content"] = {
                "schemes": FORM_SCHEMES,
                "form_data": GradeManagerForm.from_application(data.content).form_data,
            }

        params["tag"] = tag
        ticket = itsm.create_ticket(**params)
        return ticket["sn"]

    def _convert_status(self, ticket_status: TicketStatus, approve_result: bool) -> ApplicationStatus:
        """将ITSM单据状态和结果转换为权限中心定义的单据状态"""
        status = ApplicationStatus.PENDING.value
        if ticket_status == TicketStatus.FINISHED.value:
            status = ApplicationStatus.PASS.value if approve_result else ApplicationStatus.REJECT.value
        elif ticket_status in [TicketStatus.TERMINATED.value, TicketStatus.REVOKED.value]:
            status = ApplicationStatus.CANCELLED.value

        return status

    def get_approval_ticket_from_callback_request(self, request: Request) -> ApplicationTicket:
        """处理审批回调结果"""
        serializer = ApprovalSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        sn = serializer.validated_data["sn"]
        ticket_status = serializer.validated_data["current_status"]
        approve_result = serializer.validated_data["approve_result"]

        status = self._convert_status(ticket_status, approve_result)

        return ApplicationTicket(sn=sn, status=status)

    def cancel_ticket(self, sn: str, operator: str):
        """撤销单据"""
        itsm.withdraw_ticket(sn, operator)
