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

from backend.common.serializers import HiddenSLZ


class SystemSLZ(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField()
    is_favorite = serializers.BooleanField(default=False)


class NodeSLZ(serializers.Serializer):
    id = serializers.CharField(label="操作ID")
    name = serializers.CharField()
    name_en = serializers.CharField()


class TopologySLZ(NodeSLZ):
    related_actions = serializers.ListField(label="关联普通操作", child=NodeSLZ(label="普通操作"))
    sub_actions = serializers.ListField(label="关联子操作", child=NodeSLZ(label="子操作"))


class QueryResourceTypeSLZ(serializers.Serializer):
    system_id = serializers.CharField(label="系统ID")


class SystemResourceTypeSLZ(serializers.Serializer):
    id = serializers.CharField(label="资源类别ID")
    name = serializers.CharField(label="资源类别名称")


class SystemQuerySLZ(HiddenSLZ):
    all = serializers.BooleanField(label="查询所有的系统", default=False)
