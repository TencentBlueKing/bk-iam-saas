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

from backend.apps.group.models import Group
from backend.service.constants import GroupMemberType


class AdminGroupBasicSLZ(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ("id", "name", "description")


class AdminGroupMemberSLZ(serializers.Serializer):
    type = serializers.ChoiceField(label="成员类型", choices=GroupMemberType.get_choices())
    id = serializers.CharField(label="成员id")
    name = serializers.CharField(label="名称")
    expired_at = serializers.IntegerField(label="过期时间戳(单位秒)")


class AdminSubjectGroupSLZ(serializers.Serializer):
    id = serializers.CharField(label="用户组id")
    name = serializers.CharField(label="用户组名称")
    expired_at = serializers.IntegerField(label="过期时间戳(单位秒)")
