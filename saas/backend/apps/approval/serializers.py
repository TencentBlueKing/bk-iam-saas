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

from rest_framework import serializers

from backend.service.constants import ApplicationType


class ApporvalProcessQuerySLZ(serializers.Serializer):
    type = serializers.ChoiceField(label="申请审批类型", choices=ApplicationType.get_choices())


class ApprovalProcessSLZ(serializers.Serializer):
    id = serializers.IntegerField(label="流程ID")
    name = serializers.CharField(label="流程名称")
    nodes = serializers.ListField(label="节点列表(仅名称)", child=serializers.CharField(label="节点名称"))


class ApprovalProcessGlobalConfigSLZ(serializers.Serializer):
    type = serializers.ChoiceField(label="申请类型", choices=ApplicationType.get_choices())
    process_id = serializers.IntegerField(label="流程ID")
    process_name = serializers.CharField(label="流程名称")


class ApprovalProcessGlobalConfigModifySLZ(serializers.Serializer):
    type = serializers.ChoiceField(label="申请审批类型", choices=ApplicationType.get_choices())
    process_id = serializers.CharField(label="流程ID")


class ActionApprovalProcessQuerySLZ(serializers.Serializer):
    system_id = serializers.CharField(label="系统ID")
    action_group_id = serializers.IntegerField(label="操作分组ID", required=False, default=0)
    keyword = serializers.CharField(label="搜索关键字", required=False, default="")
    sensitivity_level = serializers.CharField(label="敏感等级", max_length=32, default="")


class ActionApprovalProcessSLZ(serializers.Serializer):
    action_id = serializers.CharField(label="操作ID")
    action_name = serializers.CharField(label="操作名称")
    system_id = serializers.CharField(label="系统ID")
    process_id = serializers.IntegerField(label="流程ID")
    process_name = serializers.CharField(label="流程名称")
    sensitivity_level = serializers.CharField(label="敏感等级")


class BaseActionSLZ(serializers.Serializer):
    id = serializers.CharField(label="操作ID")
    system_id = serializers.CharField(label="系统ID")


class ActionApprovalProcessModifySLZ(serializers.Serializer):
    actions = serializers.ListField(label="操作列表", child=BaseActionSLZ(label="操作"))
    process_id = serializers.CharField(label="流程ID")


class GroupApprovalProcessQuerySLZ(serializers.Serializer):
    keyword = serializers.CharField(label="搜索关键字", required=False, default="")


class GroupApprovalProcessSLZ(serializers.Serializer):
    group_id = serializers.IntegerField(label="用户组ID")
    group_name = serializers.CharField(label="用户组名称")
    group_desc = serializers.CharField(label="用户组描述")
    process_id = serializers.IntegerField(label="流程ID")
    process_name = serializers.CharField(label="流程名称")


class GroupApprovalProcessModifySLZ(serializers.Serializer):
    group_ids = serializers.ListField(label="用户组ID列表", child=serializers.IntegerField(label="用户组ID"))
    process_id = serializers.CharField(label="流程ID")


class SensitivityLevelCountSLZ(serializers.Serializer):
    all = serializers.IntegerField()
    L1 = serializers.IntegerField()
    L2 = serializers.IntegerField()
    L3 = serializers.IntegerField()
    L4 = serializers.IntegerField()


class ActionSensitivityLevelSLZ(serializers.Serializer):
    actions = serializers.ListField(label="操作列表", child=BaseActionSLZ(label="操作"))
    sensitivity_level = serializers.CharField(label="敏感等级", max_length=32)
