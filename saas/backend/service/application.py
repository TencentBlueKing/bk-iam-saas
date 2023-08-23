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
from typing import Callable, Dict, List, Optional, Tuple

from django.conf import settings
from rest_framework.request import Request

from backend.apps.application.models import Application
from backend.plugins.application_ticket.base import ApplicationTicketProvider
from backend.plugins.application_ticket.itsm import ITSMApplicationTicketProvider
from backend.util.json import json_dumps
from backend.util.url import url_join
from backend.util.uuid import gen_uuid

from .models import (
    ApplicationTicket,
    ApprovalProcessWithNodeProcessor,
    GradeManagerApplicationData,
    GrantActionApplicationData,
    GroupApplicationData,
    TypeUnionApplicationData,
)


class ApplicationService:
    """申请单据重新类，包括以下功能：
    1. 创建单据
    2. 单据更新
    """

    def __init__(self):
        self._provider = None

    @property
    def provider(self) -> ApplicationTicketProvider:
        """初始化：单据提供者"""
        # 避免多次读取（实际可以使用django的cache_property装饰器）
        if self._provider is not None:
            return self._provider
        # TODO：动态读取并加载配置文件设置的流程提供方，这里暂时默认读取ITSM的
        self._provider = ITSMApplicationTicketProvider()
        return self._provider

    def _generate_callback_info(self) -> Tuple[str, str]:
        """生成回调信息"""
        callback_id = gen_uuid()
        callback_url = url_join(settings.APP_API_URL, f"/api/v1/applications/{callback_id}/approve/")
        return callback_id, callback_url

    def _create(
        self,
        data: TypeUnionApplicationData,
        create_ticket_func: Callable[[str], str],
        source_system_id: str = "",
        callback_id: str = "",
        callback_url: str = "",
    ) -> Application:
        """创建申请逻辑"""
        # NOTE: 兼容申请自定义callback
        if not callback_id or not callback_url:
            callback_id, callback_url = self._generate_callback_info()

        # 调用第三方插件进行单据创建
        ticket_sn = create_ticket_func(callback_url)
        application = Application.objects.create(
            sn=ticket_sn,
            type=data.type,
            applicant=data.applicant_info.username,
            reason=data.reason,
            _data=json_dumps(data.raw_content()),
            callback_id=callback_id,
            source_system_id=source_system_id,
            hidden=source_system_id in settings.HIDDEN_SYSTEM_LIST if source_system_id else False,
        )
        return application

    def create_for_policy(
        self, data: GrantActionApplicationData, process: ApprovalProcessWithNodeProcessor
    ) -> Application:
        """创建或续期自定义权限申请单"""
        return self._create(data, lambda callback_url: self.provider.create_for_policy(data, process, callback_url))

    def create_for_group(
        self,
        data: GroupApplicationData,
        process: ApprovalProcessWithNodeProcessor,
        source_system_id: str = "",
        approval_title_prefix: str = "",
        approval_content: Optional[Dict] = None,
    ) -> Application:
        """创建加入或续期用户组申请单"""
        return self._create(
            data,
            lambda callback_url: self.provider.create_for_group(
                data,
                process,
                callback_url,
                tag=source_system_id,
                approval_title_prefix=approval_title_prefix,
                approval_content=approval_content,
            ),
            source_system_id=source_system_id,
        )

    def create_for_grade_manager(
        self,
        data: GradeManagerApplicationData,
        process: ApprovalProcessWithNodeProcessor,
        source_system_id: str = "",
        callback_id: str = "",
        callback_url: str = "",
        approval_title: str = "",
        approval_content: Optional[Dict] = None,
    ) -> Application:
        """创建变更分级管理员申请单"""
        return self._create(
            data,
            lambda callback_url: self.provider.create_for_grade_manager(
                data,
                process,
                callback_url,
                approval_title=approval_title,
                approval_content=approval_content,
                tag=source_system_id,
            ),
            source_system_id=source_system_id,
            callback_id=callback_id,
            callback_url=callback_url,
        )

    def get_approval_ticket_from_callback_request(self, request: Request) -> ApplicationTicket:
        """处理审批回调请求的单据"""
        return self.provider.get_approval_ticket_from_callback_request(request)

    def query_ticket_approval_status(self, sns: List[str]) -> List[ApplicationTicket]:
        """查询单据审批状态"""
        # 容错处理
        if len(sns) == 0:
            return []

        # 使用单据号查询状态
        return self.provider.list_by_sns(sns)

    def cancel_ticket(self, sn: str, operator: str):
        """撤销单据"""
        self.provider.cancel_ticket(sn, operator)

    def get_ticket(self, sn: str) -> ApplicationTicket:
        """查询单据"""
        return self.provider.get_ticket(sn)
