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
import time

from rest_framework import serializers

from backend.apps.application.base_serializers import BaseAggActionListSLZ, SystemInfoSLZ, validate_action_repeat
from backend.apps.policy.serializers import ConditionSLZ, InstanceSLZ, ResourceGroupSLZ, ResourceSLZ, ResourceTypeSLZ
from backend.apps.role.models import Role, RoleCommonAction, RoleUser
from backend.biz.role import RoleBiz
from backend.biz.subject import SubjectInfoList
from backend.common.time import PERMANENT_SECONDS
from backend.service.constants import (
    ADMIN_USER,
    ANY_ID,
    SUBJECT_ALL,
    SUBJECT_TYPE_ALL,
    GroupMemberType,
    RoleScopeSubjectType,
    SubjectType,
)

from .constants import PermissionTypeEnum


class RoleScopeSubjectSLZ(serializers.Serializer):
    type = serializers.ChoiceField(label="成员类型", choices=RoleScopeSubjectType.get_choices())
    id = serializers.CharField(label="成员id")

    def validate(self, attrs):
        """校验type和id"""
        _id, _type = attrs["id"], attrs["type"]
        # 当id为*时，type必须为*
        if _id == SUBJECT_ALL and _type != SUBJECT_TYPE_ALL:
            raise serializers.ValidationError("type must be * when id is *")
        # 当type为部门时，id必须是数字字符串或*
        if _type == RoleScopeSubjectType.DEPARTMENT.value and _id != SUBJECT_ALL:
            if not _id.isdigit():
                raise serializers.ValidationError("department id can only be a string consisting of numbers only")

        return attrs


class RoleResourceSLZ(ResourceSLZ):
    child_type = serializers.CharField(label="子资源类型", required=False, allow_blank=True, default="")


class RoleInstanceSLZ(InstanceSLZ):
    path = serializers.ListField(
        label="层级链路",
        child=serializers.ListField(label="链路", child=RoleResourceSLZ(label="节点"), allow_empty=False),
        required=True,
        allow_empty=False,
    )

    def validate(self, data):
        """
        分级管理员的auth scope资源链路的最后一级忽略任意
        """
        paths = data["path"]
        for i in range(len(paths)):
            path = paths[i]
            if len(path) > 1 and path[-1]["id"] == ANY_ID:
                paths[i] = path[:-1]

        data["path"] = paths
        return data


class RoleConditionSLZ(ConditionSLZ):
    instances = serializers.ListField(label="拓扑选择", child=RoleInstanceSLZ(label="拓扑实例"))


class RoleResourceTypeSLZ(ResourceTypeSLZ):
    condition = serializers.ListField(label="生效条件", child=RoleConditionSLZ(label="条件"))


class RoleResourceGroupSLZ(ResourceGroupSLZ):
    related_resource_types = serializers.ListField(label="资源类型条件", child=RoleResourceTypeSLZ(label="资源类型"))


class GradeManagerActionSLZ(serializers.Serializer):
    id = serializers.CharField(label="操作ID")
    resource_groups = serializers.ListField(label="资源条件组", child=RoleResourceGroupSLZ(label="资源条件组"))


class RoleScopeAuthorizationSLZ(serializers.Serializer):
    system_id = serializers.CharField(label="系统id", max_length=32)
    actions = serializers.ListField(label="操作策略", child=GradeManagerActionSLZ(label="策略"))
    aggregations = serializers.ListField(
        label="聚合操作", child=BaseAggActionListSLZ(label="聚合操作"), required=False, default=list
    )

    def validate(self, data):
        # 检查操作是否重复
        validate_action_repeat(data)

        if len(data["actions"]) == 0 and len(data["aggregations"]) == 0:
            raise serializers.ValidationError("actions must not be empty")
        return data


class RatingMangerBaseInfoSZL(serializers.Serializer):
    name = serializers.CharField(label="分级管理员名称", max_length=128)
    description = serializers.CharField(label="描述", allow_blank=True)
    members = serializers.ListField(label="成员列表", child=serializers.CharField(label="用户ID", max_length=64))


class RatingMangerCreateSLZ(RatingMangerBaseInfoSZL):
    authorization_scopes = serializers.ListField(
        label="系统操作", child=RoleScopeAuthorizationSLZ(label="系统操作"), allow_empty=False
    )
    subject_scopes = serializers.ListField(label="授权对象", child=RoleScopeSubjectSLZ(label="授权对象"), allow_empty=False)

    def validate(self, data):
        if len(data["authorization_scopes"]) != len({sys["system_id"] for sys in data["authorization_scopes"]}):
            raise serializers.ValidationError({"authorization_scopes": ["system must not repeat"]})
        return data


class RoleIdSLZ(serializers.Serializer):
    """
    角色ID
    """

    id = serializers.IntegerField(label="角色ID")


class RatingMangerListSchemaSLZ(serializers.Serializer):
    members = serializers.ListField(label="成员列表", child=serializers.CharField(label="用户ID", max_length=128))

    class Meta:
        model = Role
        fields = ("id", "name", "description", "updated_time", "creator", "members")


class RoleScopeAuthorizationSchemaSLZ(serializers.Serializer):
    system = SystemInfoSLZ(label="系统信息")
    actions = serializers.ListField(label="操作策略", child=GradeManagerActionSLZ(label="策略"))


class RatingMangerDetailSchemaSLZ(RatingMangerListSchemaSLZ):
    authorization_scopes = serializers.ListField(
        label="系统操作", child=RoleScopeAuthorizationSchemaSLZ(label="系统操作"), allow_empty=False
    )
    subject_scopes = serializers.ListField(label="授权对象", child=RoleScopeSubjectSLZ(label="授权对象"), allow_empty=False)

    class Meta:
        model = Role
        fields = (
            "id",
            "name",
            "description",
            "updated_time",
            "creator",
            "members",
            "authorization_scopes",
            "subject_scopes",
        )


class RatingMangerListSLZ(serializers.ModelSerializer):
    members = serializers.SerializerMethodField(label="成员列表")

    class Meta:
        model = Role
        fields = ("id", "name", "description", "creator", "created_time", "updated_time", "updater", "members")

    def get_members(self, obj):
        return list(RoleUser.objects.filter(role_id=obj.id).values_list("username", flat=True))


class RatingMangerDetailSLZ(RatingMangerListSLZ):
    authorization_scopes = serializers.SerializerMethodField(label="系统操作")
    subject_scopes = serializers.SerializerMethodField(label="授权对象")

    class Meta:
        model = Role
        fields = (
            "id",
            "name",
            "description",
            "updated_time",
            "creator",
            "members",
            "authorization_scopes",
            "subject_scopes",
        )

    def get_authorization_scopes(self, obj):
        # ResourceNameAutoUpdate
        scope_systems = RoleBiz().list_auth_scope_bean(obj.id, should_auto_update_resource_name=True)
        return [one.dict() for one in scope_systems]

    def get_subject_scopes(self, obj):
        subjects = RoleBiz().list_subject_scope(obj.id)
        subject_list = SubjectInfoList(subjects)
        return [one.dict() for one in subject_list.subjects]


class SystemManagerSLZ(RatingMangerListSLZ):
    system_permission_global_enabled = serializers.SerializerMethodField(label="是否拥有系统所有权限")

    class Meta:
        model = Role
        fields = ("id", "name", "name_en", "description", "members", "system_permission_global_enabled")

    def get_system_permission_global_enabled(self, obj):
        return obj.system_permission_enabled_content.global_enabled


class SystemManagerMemberUpdateSLZ(serializers.Serializer):
    members = serializers.ListField(label="成员列表", child=serializers.CharField(label="用户ID", max_length=128))


class MemberSystemPermissionUpdateSLZ(serializers.Serializer):
    system_permission_global_enabled = serializers.BooleanField(label="是否拥有系统所有权限")


class SuperManagerMemberSLZ(serializers.Serializer):
    username = serializers.CharField(label="用户名")
    system_permission_enabled = serializers.BooleanField(label="是否拥有系统所有权限")


class SuperManagerMemberDeleteSLZ(serializers.Serializer):
    username = serializers.CharField(label="用户名")

    def validate_username(self, value):
        if value == ADMIN_USER:
            raise serializers.ValidationError("admin cannot be deleted")
        return value


class RoleCommonActionSLZ(serializers.ModelSerializer):
    class Meta:
        model = RoleCommonAction
        fields = ("id", "system_id", "name", "name_en", "action_ids")


class RoleCommonCreateSLZ(serializers.Serializer):
    system_id = serializers.CharField(label="系统id", max_length=32)
    name = serializers.CharField(label="名称", max_length=128)
    action_ids = serializers.ListField(label="操作ID", child=serializers.CharField(), allow_empty=False)

    def validate(self, data):
        action_id_set = set(data["action_ids"])
        # 判断操作是否有重复
        if len(action_id_set) != len(data["action_ids"]):
            raise serializers.ValidationError({"action_ids": ["action_ids must not repeat"]})
        return data

    def create(self, validated_data):
        action_ids = validated_data.pop("action_ids")
        instance = RoleCommonAction(**validated_data)
        instance.action_ids = action_ids
        instance.save()
        return instance


class RoleGroupMemberRenewSLZ(serializers.Serializer):
    type = serializers.ChoiceField(label="成员类型", choices=GroupMemberType.get_choices())
    id = serializers.CharField(label="成员id")
    parent_type = serializers.ChoiceField(label="父级类型", choices=[(SubjectType.GROUP.value, "用户组")])
    parent_id = serializers.CharField(label="父级ID")
    expired_at = serializers.IntegerField(label="过期时间", max_value=PERMANENT_SECONDS)

    def validate_expired_at(self, value):
        """
        验证过期时间
        """
        if value <= (time.time()):
            raise serializers.ValidationError("expired_at must greater than now timestamp")
        return value


class RoleGroupMembersRenewSLZ(serializers.Serializer):
    members = serializers.ListField(label="续期成员", child=RoleGroupMemberRenewSLZ(), allow_empty=False)


class ResourceInstancePathSLZ(serializers.Serializer):
    id = serializers.CharField(label="资源实例ID")
    type = serializers.CharField(label="资源实例类型")
    name = serializers.CharField(label="资源实例名")


class ResourceInstancesSLZ(serializers.Serializer):
    system_id = serializers.CharField(label="系统ID", required=True)
    id = serializers.CharField(label="资源实例ID", required=True)
    type = serializers.CharField(label="资源实例类型", required=True)
    name = serializers.CharField(label="资源实例名", required=True)
    path = serializers.ListField(
        label="资源实例路径", required=False, child=ResourceInstancePathSLZ(label="资源实例路径"), default=list
    )


class QueryAuthorizedSubjectsSLZ(serializers.Serializer):
    system_id = serializers.CharField(label="系统ID")
    action_id = serializers.CharField(label="操作ID")
    limit = serializers.IntegerField(label="返回结果数", min_value=10, max_value=1000)
    resource_instances = serializers.ListField(
        label="资源实例", required=False, child=ResourceInstancesSLZ(label="资源实例信息"), default=list
    )
    permission_type = serializers.ChoiceField(label="权限类型", choices=PermissionTypeEnum.get_choices())

    def validate(self, data):
        if data["permission_type"] == PermissionTypeEnum.RESOURCE_INSTANCE.value:
            if not data.get("resource_instances"):
                data["resource_instances"] = []
            return data

        return data


class AuthorizedSubjectsSLZ(serializers.Serializer):
    type = serializers.CharField(label="Subject对象类型")
    id = serializers.CharField(label="Subject对象ID")
    name = serializers.CharField(label="Subject对象名称")
