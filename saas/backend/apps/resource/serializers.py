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


class ResourceQuerySLZ(serializers.Serializer):
    system_id = serializers.CharField()
    type = serializers.CharField(label="资源类型")
    parent_type = serializers.CharField(label="父资源类型", allow_blank=True)
    parent_id = serializers.CharField(label="父资源ID", allow_blank=True)
    keyword = serializers.CharField(label="搜索关键词", required=False, allow_blank=True, allow_null=True)
    limit = serializers.IntegerField(label="分页Limit", min_value=1, max_value=100)
    offset = serializers.IntegerField(label="分页offset", min_value=0)


class BaseInfoSLZ(serializers.Serializer):
    id = serializers.CharField(label="ID")
    display_name = serializers.CharField(label="展示名称")
    child_type = serializers.CharField(label="子资源类型")


class ResourceAttributeQuerySLZ(serializers.Serializer):
    system_id = serializers.CharField()
    type = serializers.CharField(label="资源类型")
    limit = serializers.IntegerField(label="分页Limit", min_value=1)
    offset = serializers.IntegerField(label="分页offset", min_value=0)


class ResourceAttributeValueQuerySLZ(serializers.Serializer):
    system_id = serializers.CharField()
    type = serializers.CharField(label="资源类型")
    attribute = serializers.CharField()
    keyword = serializers.CharField(label="搜索关键词", required=False)
    limit = serializers.IntegerField(label="分页Limit", min_value=1, max_value=100)
    offset = serializers.IntegerField(label="分页offset", min_value=0)
