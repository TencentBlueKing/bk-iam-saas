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

from backend.apps.handover.constants import HandoverStatus, HandoverTaskStatus


class HandOverSLZ(serializers.Serializer):
    handover_to = serializers.CharField(label="目标交接人")
    reason = serializers.CharField(label="交接原因")
    handover_info = serializers.DictField(label="交接信息")


class HandOverRecordSLZ(serializers.Serializer):
    id = serializers.IntegerField(label="交接记录ID")
    created_time = serializers.CharField(label="时间")
    handover_to = serializers.CharField(label="目标交接人")
    status = serializers.CharField(label="交接状态", help_text=f"{HandoverStatus.get_choices()}")


class HandOverTaskSLZ(serializers.Serializer):
    object_type = serializers.CharField(label="交接类型")
    created_time = serializers.CharField(label="时间")
    status = serializers.CharField(label="交接状态", help_text=f"{HandoverTaskStatus.get_choices()}")
    object_detail = serializers.CharField(label="交接权限详情")
    error_info = serializers.CharField(label="交接异常信息")

