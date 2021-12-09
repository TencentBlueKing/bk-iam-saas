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
import json

from rest_framework import serializers

from backend.apps.handover.constants import HandoverStatus, HandoverTaskStatus
from backend.service.constants import ADMIN_USER


class CustomPolicy(serializers.Serializer):
    system_id = serializers.CharField(label="系统ID")
    policy_ids = serializers.ListField(label="ids", child=serializers.IntegerField(), allow_empty=False)


class HandoverInfo(serializers.Serializer):
    group_ids = serializers.ListField(label="用户ids", child=serializers.IntegerField(), required=False, default=list)
    custom_policies = serializers.ListField(
        label="用户ids", child=CustomPolicy(label="自定权限"), required=False, default=list
    )
    role_ids = serializers.ListField(label="管理员ids", child=serializers.IntegerField(), required=False, default=list)

    def validate(self, data):
        if all([not value for value in data.values()]):
            raise serializers.ValidationError("交接的权限内容不可为空")
        return data


class HandoverSLZ(serializers.Serializer):
    handover_to = serializers.CharField(label="目标交接人")
    reason = serializers.CharField(label="交接原因")
    handover_info = HandoverInfo(label="交接信息")

    def validate_handover_to(self, value):
        if value == ADMIN_USER:
            raise serializers.ValidationError("Can not hand over to admin!")
        return value


class HandoverRecordSLZ(serializers.Serializer):
    id = serializers.IntegerField(label="交接记录ID")
    created_time = serializers.CharField(label="时间")
    handover_to = serializers.CharField(label="目标交接人")
    status = serializers.CharField(label="交接状态", help_text=f"{HandoverStatus.get_choices()}")


class HandoverTaskSLZ(serializers.Serializer):
    object_type = serializers.CharField(label="交接类型")
    created_time = serializers.CharField(label="时间")
    status = serializers.CharField(label="交接状态", help_text=f"{HandoverTaskStatus.get_choices()}")
    object_detail = serializers.SerializerMethodField(label="交接权限详情")
    error_info = serializers.CharField(label="交接异常信息")

    def get_object_detail(self, obj):
        return json.loads(obj.object_detail)
