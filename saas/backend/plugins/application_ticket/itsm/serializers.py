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

from rest_framework import serializers

from .constants import TicketStatus


class TicketSLZ(serializers.Serializer):
    id = serializers.CharField(label="申请的单据单据 id")
    status = serializers.ChoiceField(label="单据当前状态", choices=TicketStatus.get_choices())
    approve_result = serializers.BooleanField(label="审批结果")
    end_at = serializers.CharField(label="单据结束时间", default=None)


class ApprovalSLZ(serializers.Serializer):
    callback_token = serializers.CharField(label="回调 token")
    ticket = TicketSLZ(label="单据信息")
