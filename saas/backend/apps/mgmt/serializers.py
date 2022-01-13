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

from backend.api.management.constants import ManagementAPIEnum

from .constants import ApiType


class QueryApiSLZ(serializers.Serializer):
    api_type = serializers.ChoiceField(label="API类型", choices=ApiType.get_choices())


class ApiSLZ(serializers.Serializer):
    api = serializers.CharField(label="API")
    name = serializers.CharField(label="API名称")


class ManagementApiWhiteListSLZ(serializers.Serializer):
    id = serializers.IntegerField(label="白名单记录ID")
    api = serializers.ChoiceField(label="管理类API", choices=ManagementAPIEnum.get_choices())
    system_id = serializers.CharField(label="系统ID")


class ManagementApiAddWhiteListSLZ(serializers.Serializer):
    system_id = serializers.CharField(label="系统ID")
    api = serializers.ChoiceField(label="管理类API", choices=ManagementAPIEnum.get_choices())
