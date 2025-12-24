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
from django.conf import settings
from rest_framework import serializers

from backend.apps.organization.models import DepartmentMember


class UnsignedIntegerField(serializers.IntegerField):
    """
    无符号整数字段
    支持各种无符号整数范围
    """

    def __init__(self, max_value=2 ** 32 - 1, **kwargs):
        # 设置默认的最大值（32位无符号整数）
        kwargs["max_value"] = min(kwargs.get("max_value", max_value), max_value)
        kwargs["min_value"] = 0  # 无符号整数不能为负数

        super().__init__(**kwargs)

    def to_internal_value(self, data):
        try:
            value = int(data)
        except (TypeError, ValueError):
            raise serializers.ValidationError("Must be a valid integer")

        if value < 0:
            raise serializers.ValidationError("Unsigned integer cannot be negative")

        if hasattr(self, "max_value") and value > self.max_value:
            raise serializers.ValidationError(f"Value cannot exceed {self.max_value}")

        return value


class Unsigned32Field(UnsignedIntegerField):
    """32位无符号整数 (0-4294967295)"""

    def __init__(self, **kwargs):
        kwargs["max_value"] = 4294967295
        super().__init__(**kwargs)


class RtxSLZ(serializers.Serializer):
    rtx = serializers.CharField(required=True)

    def validate_rtx(self, value):
        if not value:
            raise serializers.ValidationError("rtx不能为空")
        for department in settings.PCG_DEPARTMENT_IDS_SET:
            if not DepartmentMember.objects.filter(department_id=department, member_id=value).exists():
                raise serializers.ValidationError("rtx不在部门内")
        return value


class AssetSLZ(serializers.Serializer):
    id = Unsigned32Field()
    info = serializers.CharField(required=True)
    role_type = serializers.CharField(required=True)
    remark = serializers.CharField(required=False, allow_blank=True)
    info_key = serializers.CharField(required=False, allow_blank=True)
    info_url = serializers.CharField(required=False, allow_blank=True)


class ActivityRtxSLZ(serializers.Serializer):
    activity_rtx = serializers.CharField(required=True)

    def validate_activity_rtx(self, value):
        if not value:
            raise serializers.ValidationError("rtx不能为空")
        for department in settings.PCG_DEPARTMENT_IDS_SET:
            if not DepartmentMember.objects.filter(department_id=department, member_id=value).exists():
                raise serializers.ValidationError("rtx不在部门内")
        return value


class HandoverRtxSLZ(serializers.Serializer):
    handover_rtx = serializers.CharField(required=True)

    def validate_handover_rtx(self, value):
        if not value:
            raise serializers.ValidationError("rtx不能为空")
        for department in settings.PCG_DEPARTMENT_IDS_SET:
            if not DepartmentMember.objects.filter(department_id=department, member_id=value).exists():
                raise serializers.ValidationError("rtx不在部门内")
        return value


class ResignHandoverSLZ(ActivityRtxSLZ, HandoverRtxSLZ):
    assets = serializers.ListField(child=AssetSLZ(), required=True)


class RecycleSLZ(ActivityRtxSLZ):
    assets = serializers.ListField(child=AssetSLZ(), required=True)


class AssetStatusSLZ(serializers.Serializer):
    fail_reason = serializers.CharField(required=False, allow_blank=True, default="")
    info = AssetSLZ(required=False, default={})


class HandoverResultSLZ(serializers.Serializer):
    err_list = serializers.ListField(child=AssetStatusSLZ(), required=False, default=[])
