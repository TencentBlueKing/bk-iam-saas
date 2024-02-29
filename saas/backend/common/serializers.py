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

from backend.service.constants import GroupMemberType


class SystemQuerySLZ(serializers.Serializer):
    system_id = serializers.CharField(required=True)


class ActionQuerySLZ(SystemQuerySLZ):
    cache_id = serializers.CharField(label="申请缓存的id", required=False, default="", allow_blank=True)


class BaseAction(serializers.Serializer):
    system_id = serializers.CharField(label="系统ID")
    id = serializers.CharField(label="操作id")


class HiddenSLZ(serializers.Serializer):
    hidden = serializers.BooleanField(label="操作id", required=False, default=True)


class ResourceInstancePathSLZ(serializers.Serializer):
    id = serializers.CharField(label="资源实例ID", max_length=settings.MAX_LENGTH_OF_RESOURCE_ID)
    type = serializers.CharField(label="资源实例类型")
    name = serializers.CharField(label="资源实例名")


class ResourceInstancesSLZ(serializers.Serializer):
    system_id = serializers.CharField(label="系统ID", required=True)
    id = serializers.CharField(label="资源实例ID", required=True, max_length=settings.MAX_LENGTH_OF_RESOURCE_ID)
    type = serializers.CharField(label="资源实例类型", required=True)
    name = serializers.CharField(label="资源实例名", required=True)
    path = serializers.ListField(
        label="资源实例路径", required=False, child=ResourceInstancePathSLZ(label="资源实例路径"), default=list
    )


class GroupMemberSLZ(serializers.Serializer):
    type = serializers.ChoiceField(label="成员类型", choices=GroupMemberType.get_choices())
    id = serializers.CharField(label="成员id")


class GroupSearchSLZ(serializers.Serializer):
    name = serializers.CharField(label="用户组名称", required=False, default="", allow_blank=True)
    id = serializers.IntegerField(label="ID", required=False, default=0)
    description = serializers.CharField(label="描述", required=False, default="", allow_blank=True)
    system_id = serializers.CharField(label="系统ID", required=False, default="", allow_blank=True)
    action_id = serializers.CharField(label="操作ID", required=False, default="", allow_blank=True)
    resource_instances = serializers.ListField(
        label="资源实例", required=False, child=ResourceInstancesSLZ(label="资源实例信息"), default=list
    )
    apply_disable = serializers.BooleanField(label="是否不可申请", required=False)
    hidden = serializers.BooleanField(label="是否隐藏", default=True)
