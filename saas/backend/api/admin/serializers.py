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

from backend.api.management.v2.serializers import ManagementGradeManagerGroupCreateSLZ
from backend.apps.group.models import Group
from backend.apps.group.serializers import GroupAddMemberSLZ, GroupAuthorizationSLZ
from backend.apps.role.models import Role
from backend.apps.role.serializers import BaseGradeMangerSLZ
from backend.apps.template.serializers import TemplateCreateSLZ, TemplateIdSLZ, TemplateListSchemaSLZ, TemplateListSLZ
from backend.common.serializers import GroupMemberSLZ
from backend.service.constants import GroupMemberType, RoleType


class AdminGroupBasicSLZ(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ("id", "name", "description")


class AdminGroupCreateSLZ(ManagementGradeManagerGroupCreateSLZ):
    pass


class AdminGroupMemberSLZ(serializers.Serializer):
    type = serializers.ChoiceField(label="成员类型", choices=GroupMemberType.get_choices())
    id = serializers.CharField(label="成员id")
    name = serializers.CharField(label="名称")
    expired_at = serializers.IntegerField(label="过期时间戳(单位秒)")


class AdminGroupAddMemberSLZ(GroupAddMemberSLZ):
    pass


class AdminGroupRemoveMemberSLZ(serializers.Serializer):
    members = serializers.ListField(label="成员列表", child=GroupMemberSLZ(label="成员"), allow_empty=False)


class AdminSubjectGroupSLZ(serializers.Serializer):
    id = serializers.CharField(label="用户组id")
    name = serializers.CharField(label="用户组名称")
    expired_at = serializers.IntegerField(label="过期时间戳(单位秒)")


class AdminGroupAuthorizationSLZ(GroupAuthorizationSLZ):
    pass


class AdminSystemProviderConfigSLZ(serializers.Serializer):
    token = serializers.CharField(label="回调token")
    host = serializers.CharField(label="回调地址")


class SystemManageSLZ(serializers.Serializer):
    managers = serializers.ListField(child=serializers.CharField(label="成员"), max_length=100)


class SuperManagerMemberSLZ(serializers.Serializer):
    username = serializers.CharField(label="用户名")
    has_system_permission = serializers.BooleanField(label="是否拥有系统所有权限")

    class Meta:
        ref_name = "AdminSuperManagerMemberSLZ"


class SystemManagerWithMembersSLZ(BaseGradeMangerSLZ):
    has_system_permission = serializers.SerializerMethodField(label="是否拥有系统所有权限")

    class Meta:
        model = Role
        fields = ("id", "name", "name_en", "description", "members", "has_system_permission")

    def get_has_system_permission(self, obj):
        return obj.system_permission_enabled_content.global_enabled


class SubjectRoleSLZ(serializers.Serializer):
    id = serializers.IntegerField(label="角色唯一标识")
    type = serializers.CharField(label="角色类型", help_text=f"{RoleType.get_choices()}")
    name = serializers.CharField()


class SubjectSLZ(serializers.Serializer):
    # 注意, 当前只支持冻结用户, 不支持其他类型
    type = serializers.ChoiceField(label="Subject类型", choices=[("user", "用户")])
    id = serializers.CharField(label="SubjectID")


class FreezeSubjectResponseSLZ(serializers.Serializer):
    type = serializers.CharField(label="SubjectType")
    id = serializers.CharField(label="SubjectID")


class AdminTemplateListSchemaSLZ(TemplateListSchemaSLZ):
    pass


class AdminTemplateListSLZ(TemplateListSLZ):
    pass


class AdminTemplateCreateSLZ(TemplateCreateSLZ):
    pass


class AdminTemplateIdSLZ(TemplateIdSLZ):
    pass


class ActionSLZ(serializers.Serializer):
    name = serializers.CharField(label="操作名称")
    action_id = serializers.CharField(label="操作ID")
    expired_at = serializers.IntegerField(label="过期时间戳(单位秒)", allow_null=True)
    expired_at_display = serializers.CharField(label="过期时间显示", allow_null=True)


class SystemSLZ(serializers.Serializer):
    name = serializers.CharField(label="系统名称")
    system_id = serializers.CharField(label="系统ID")


class SystemActionSLZ(SystemSLZ):
    action = serializers.ListField(label="操作列表", child=ActionSLZ(label="操作"))


class GradeManagementSLZ(serializers.Serializer):
    id = serializers.IntegerField(label="分级管理空间ID")
    name = serializers.CharField(label="分级管理空间名称")


class GroupPermissionSLZ(serializers.Serializer):
    id = serializers.IntegerField(label="用户组ID")
    name = serializers.CharField(label="用户组名称")
    grade_management = GradeManagementSLZ(label="分级管理空间")
    description = serializers.CharField(label="用户组描述", default="")
    expired_at = serializers.IntegerField(label="过期时间戳(单位秒)")
    expired_at_display = serializers.CharField(label="过期时间显示")
    permissions = serializers.ListField(label="权限列表", child=SystemActionSLZ(label="系统"))


class SubjectGroupPermissionSLZ(serializers.Serializer):
    groups = serializers.ListField(label="用户组列表", child=GroupPermissionSLZ(label="用户组"))
