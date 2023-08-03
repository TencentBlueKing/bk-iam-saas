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
from backend.apps.role.models import RoleUser
from backend.apps.subject.serializers import SubjectGroupSLZ
from backend.biz.group import GroupBiz
from backend.service.group_saas_attribute import GroupAttributeService

from .constants import NewbieSceneEnum


class UserNewbieSLZ(serializers.Serializer):
    scene = serializers.ChoiceField(label="场景", choices=NewbieSceneEnum.get_choices())
    status = serializers.BooleanField(label="状态")


class UserNewbieUpdateSLZ(serializers.Serializer):
    scene = serializers.ChoiceField(label="场景", choices=NewbieSceneEnum.get_choices())


class GroupSLZ(SubjectGroupSLZ):
    role = serializers.SerializerMethodField()
    role_members = serializers.SerializerMethodField()
    attributes = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group_role_dict = None
        self.group_attrs_dict = None
        if isinstance(self.instance, list) and self.instance:
            group_ids = [int(group.id) for group in self.instance]

            self.group_role_dict = GroupBiz().get_group_role_dict_by_ids(group_ids)
            # 查询涉及到的用户组的属性
            self.group_attrs_dict = GroupAttributeService().batch_get_attributes(group_ids)
        elif isinstance(self.instance, Group):
            self.group_attrs_dict = GroupAttributeService().batch_get_attributes([self.instance.id])

    def get_role(self, obj):
        if not self.group_role_dict:
            return {}
        role = self.group_role_dict.get(obj.id)
        if not role:
            return {}

        return role.dict()

    def get_attributes(self, obj):
        if not self.group_attrs_dict:
            return {}

        group_attributes = self.group_attrs_dict.get(obj.id)
        if group_attributes:
            return group_attributes.get_attributes()
        return {}

    def get_role_members(self, obj):
        if not self.group_role_dict:
            return []
        role = self.group_role_dict.get(obj.id)
        if not role:
            return []

        return list(RoleUser.objects.filter(role_id=role.id).values_list("username", flat=True))


class QueryRoleSLZ(serializers.Serializer):
    with_perm = serializers.BooleanField(label="角色是否带权限")


class QueryGroupSLZ(serializers.Serializer):
    system_id = serializers.CharField(label="系统id", required=False, allow_blank=True, default="")
