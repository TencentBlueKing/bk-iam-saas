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

from backend.apps.handover.models import HandoverRecord, HandoverTask
from backend.service.constants import ADMIN_USER


class CustomPolicySLZ(serializers.Serializer):
    system_id = serializers.CharField(label="系统ID")
    policy_ids = serializers.ListField(label="ids", child=serializers.IntegerField(), allow_empty=False)


class HandoverInfoSLZ(serializers.Serializer):
    group_ids = serializers.ListField(label="用户ids", child=serializers.IntegerField(), required=False, default=list)
    custom_policies = serializers.ListField(
        label="用户ids", child=CustomPolicySLZ(label="自定权限"), required=False, default=list
    )
    role_ids = serializers.ListField(label="管理员ids", child=serializers.IntegerField(), required=False, default=list)
    subject_template_ids = serializers.ListField(
        label="人员模板ids", child=serializers.IntegerField(), required=False, default=list
    )

    def validate(self, data):
        if all(not value for value in data.values()):
            raise serializers.ValidationError("交接的权限内容不可为空")
        return data


class HandoverSLZ(serializers.Serializer):
    handover_to = serializers.CharField(label="目标交接人")
    reason = serializers.CharField(label="交接原因")
    handover_info = HandoverInfoSLZ(label="交接信息")

    def validate_handover_to(self, value):
        if value == ADMIN_USER:
            raise serializers.ValidationError("Can not hand over to admin!")
        return value


class HandoverRecordSLZ(serializers.ModelSerializer):
    class Meta:
        model = HandoverRecord
        fields = ("id", "handover_to", "created_time", "status")


class HandoverTaskSLZ(serializers.ModelSerializer):
    object_detail = serializers.SerializerMethodField(label="交接权限详情")

    class Meta:
        model = HandoverTask
        fields = ("id", "object_type", "created_time", "status", "object_detail", "error_info")

    def get_object_detail(self, obj):
        return json.loads(obj.object_detail)
