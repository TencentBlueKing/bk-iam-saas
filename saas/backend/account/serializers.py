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

from rest_framework import serializers

from backend.service.constants import RoleType


class AccountRoleSLZ(serializers.Serializer):
    id = serializers.IntegerField(label="角色唯一标识")
    type = serializers.CharField(label="角色类型", help_text=f"{RoleType.get_choices()}")
    name = serializers.CharField()
    description = serializers.CharField()
    is_member = serializers.BooleanField(label="登录用户是否是角色成员")
    sub_roles = serializers.ListField(label="子集管理员列表", child=serializers.CharField(label="子集管理员"))


class AccountUserSLZ(serializers.Serializer):
    username = serializers.CharField(label="用户名")
    name = serializers.CharField(label="名称")
    role = AccountRoleSLZ(label="角色")


class AccountRoleSwitchSLZ(serializers.Serializer):
    id = serializers.IntegerField(label="角色唯一标识")
