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
from django.conf import settings
from rest_framework import serializers

from backend.apps.organization.models import User


def validate_rtx(value):
    user = User.objects.filter(username=value).first()
    if not user:
        raise serializers.ValidationError("rtx not exists")
    if len(set(settings.PCG_DEPARTMENT_IDS) & set(user.ancestor_department_ids())) == 0:
        raise serializers.ValidationError("rtx is not in the specified organization")
    return value


class RtxSLZ(serializers.Serializer):
    rtx = serializers.CharField(required=True)

    def validate_rtx(self, value):
        return validate_rtx(value)


class AssetSLZ(serializers.Serializer):
    id = serializers.IntegerField(max_value=2 ** 32 - 1, min_value=0)
    info = serializers.CharField(required=True)
    role_type = serializers.CharField(required=True)
    remark = serializers.CharField(required=False, allow_blank=True)
    info_key = serializers.CharField(required=False, allow_blank=True)
    info_url = serializers.CharField(required=False, allow_blank=True)


class ActivityRtxSLZ(serializers.Serializer):
    activity_rtx = serializers.CharField(required=True)

    def validate_activity_rtx(self, value):
        return validate_rtx(value)


class HandoverRtxSLZ(serializers.Serializer):
    handover_rtx = serializers.CharField(required=True)

    def validate_handover_rtx(self, value):
        return validate_rtx(value)


class ResignHandoverSLZ(ActivityRtxSLZ, HandoverRtxSLZ):
    assets = serializers.ListField(child=AssetSLZ(), required=True)


class RecycleSLZ(ActivityRtxSLZ):
    assets = serializers.ListField(child=AssetSLZ(), required=True)


class AssetStatusSLZ(serializers.Serializer):
    fail_reason = serializers.CharField(required=False, allow_blank=True, default="")
    info = AssetSLZ(required=False, default={})


class HandoverResultSLZ(serializers.Serializer):
    err_list = serializers.ListField(child=AssetStatusSLZ(), required=False, default=[])
