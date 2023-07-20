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


class SystemInfoSLZ(serializers.Serializer):
    id = serializers.CharField(label="系统ID")


class AggResourceInstance(serializers.Serializer):
    id = serializers.CharField(label="实例ID", max_length=settings.MAX_LENGTH_OF_RESOURCE_ID)
    name = serializers.CharField(label="实例名称", trim_whitespace=False)


class AggResourceTypeSLZ(serializers.Serializer):
    system_id = serializers.CharField(label="系统ID")
    id = serializers.CharField(label="资源类型ID")
    instances = serializers.ListField(label="资源实例", child=AggResourceInstance(label="资源实例"), allow_empty=False)


class AggActionSLZ(serializers.Serializer):
    system_id = serializers.CharField(label="系统ID")
    id = serializers.CharField(label="操作ID")


class BaseAggActionListSLZ(serializers.Serializer):
    actions = serializers.ListField(label="操作策略", child=AggActionSLZ(label="策略"), allow_empty=False)
    aggregate_resource_types = serializers.ListField(
        label="聚合资源类型列表", child=AggResourceTypeSLZ(label="聚合资源类型"), allow_empty=True
    )


def validate_action_repeat(data):
    """
    检查操作是否重复
    """
    action_id_set = {a["id"] for a in data["actions"]}

    # 判断操作是否有重复
    repeat_err = serializers.ValidationError("actions must not repeat")

    if len(action_id_set) != len(data["actions"]):
        raise repeat_err

    for agg in data["aggregations"]:
        agg_action_id_set = {a["id"] for a in agg["actions"]}
        if len(agg_action_id_set) != len(agg["actions"]):
            raise repeat_err

        # 如果有交集就是有重复
        if agg_action_id_set & action_id_set:
            raise repeat_err

        action_id_set |= agg_action_id_set
