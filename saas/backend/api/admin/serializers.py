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
from celery.schedules import ParseException
from rest_framework import serializers

from backend.api.admin.constants import SUBJECT_GROUP_CLEANUP_MAX_GROUP_IDS, SUBJECT_POLICY_CLEANUP_MAX_POLICY_IDS
from backend.api.management.v2.serializers import ManagementGradeManagerGroupCreateSLZ
from backend.apps.group.models import Group
from backend.apps.group.serializers import GroupAddMemberSLZ, GroupAuthorizationSLZ
from backend.apps.policy.serializers import ResourceGroupSLZ
from backend.apps.role.models import Role
from backend.apps.role.serializers import BaseGradeMangerSLZ
from backend.apps.template.serializers import TemplateCreateSLZ, TemplateIdSLZ, TemplateListSchemaSLZ, TemplateListSLZ
from backend.common.serializers import GroupMemberSLZ
from backend.service.constants import GroupMemberType, RoleType
from backend.util.crontab import crontab_from_string


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


class AdminGroupPolicyQuerySLZ(serializers.Serializer):
    system_id = serializers.CharField(label="系统ID")


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
    before_at = serializers.IntegerField(label="清理时间戳", required=False, default=None)

    class Meta:
        ref_name = "AdminSubjectSLZ"


class AdminOrganizationSyncConfigSLZ(serializers.Serializer):
    """组织架构同步配置"""

    sync_crontab = serializers.CharField(
        label="同步周期(crontab)",
        required=False,
        help_text="crontab 格式，如 '0 2 * * *' 表示每天凌晨2点。如不传则只触发同步",
    )

    def validate_sync_crontab(self, value):
        try:
            return crontab_from_string(value)
        except (ParseException, ValueError) as e:
            raise serializers.ValidationError(f"invalid crontab expression: {str(e)}")


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


class AdminGradeManagerTemplateBatchCreateSLZ(TemplateCreateSLZ):
    role_ids = serializers.ListField(label="角色ID列表", child=serializers.IntegerField(label="角色ID"), allow_empty=False)


class AdminSubjectPolicyQuerySLZ(serializers.Serializer):
    system_id = serializers.CharField(label="系统ID")
    action_id = serializers.CharField(label="操作ID", required=False)


class AdminSubjectPolicySLZ(serializers.Serializer):
    """Subject的自定义权限（输出）"""

    id = serializers.CharField(label="操作ID", source="action_id")
    policy_id = serializers.IntegerField(label="策略ID")
    type = serializers.CharField(label="操作类型")
    name = serializers.CharField(label="操作名称", allow_blank=True)
    name_en = serializers.CharField(label="操作名称(英文)", allow_blank=True)
    description = serializers.CharField(label="操作描述", allow_blank=True)
    description_en = serializers.CharField(label="操作描述(英文)", allow_blank=True)
    expired_at = serializers.IntegerField(label="过期时间戳(单位秒)")
    expired_display = serializers.CharField(label="过期时间展示")
    resource_groups = serializers.ListField(label="资源条件组", child=ResourceGroupSLZ(label="资源条件组"))


class AdminSubjectGroupCleanupSLZ(serializers.Serializer):
    username = serializers.CharField(label="用户名")
    group_ids = serializers.ListField(
        label="用户组ID列表",
        child=serializers.IntegerField(label="用户组ID", min_value=1),
        allow_empty=False,
        max_length=SUBJECT_GROUP_CLEANUP_MAX_GROUP_IDS,
    )

    def validate_group_ids(self, value):
        # 去重
        return list(dict.fromkeys(value))


class AdminSubjectPolicyCleanupSLZ(serializers.Serializer):
    username = serializers.CharField(label="用户名")
    system_id = serializers.CharField(label="系统ID")
    action_id = serializers.CharField(label="操作ID", required=False)
    policy_ids = serializers.ListField(
        label="策略ID列表",
        child=serializers.IntegerField(label="策略ID", min_value=1),
        required=False,
        allow_empty=False,
        max_length=SUBJECT_POLICY_CLEANUP_MAX_POLICY_IDS,
    )

    def validate(self, attrs):
        # action_id 与 policy_ids 必须且只能传递其中一个
        if ("action_id" in attrs) == ("policy_ids" in attrs):
            raise serializers.ValidationError("action_id 与 policy_ids 必须且只能传递其中一个")
        return attrs


class AdminSubjectCleanupResultSLZ(serializers.Serializer):
    removed = serializers.ListField(label="清理成功的ID列表", child=serializers.IntegerField())
    failed = serializers.ListField(label="清理失败的ID列表", child=serializers.IntegerField())
