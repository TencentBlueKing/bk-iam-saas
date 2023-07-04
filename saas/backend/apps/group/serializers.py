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
from typing import List

from django.conf import settings
from django.db.models import QuerySet
from django.utils.translation import gettext as _
from pydantic import parse_obj_as
from rest_framework import serializers

from backend.apps.application.base_serializers import BaseAggActionListSLZ, validate_action_repeat
from backend.apps.application.serializers import ExpiredAtSLZ, SystemInfoSLZ
from backend.apps.group.models import Group
from backend.apps.policy.serializers import BasePolicyActionSLZ, ResourceTypeSLZ
from backend.apps.role.models import Role, RoleRelatedObject, RoleRelation, RoleUser
from backend.apps.role.serializers import ResourceInstancesSLZ
from backend.apps.template.models import PermTemplatePolicyAuthorized
from backend.biz.group import GroupBiz
from backend.biz.policy import PolicyBean, PolicyBeanList
from backend.biz.system import SystemBiz
from backend.biz.template import TemplateBiz
from backend.common.time import PERMANENT_SECONDS
from backend.service.constants import ADMIN_USER, GroupMemberType, RoleRelatedObjectType
from backend.service.group_saas_attribute import GroupAttributeService


class GroupMemberSLZ(serializers.Serializer):
    type = serializers.ChoiceField(label="成员类型", choices=GroupMemberType.get_choices())
    id = serializers.CharField(label="成员id")


class SearchMemberSLZ(serializers.Serializer):
    keyword = serializers.CharField(label="搜索关键词", min_length=3, allow_null=False, required=False)


class GroupIdSLZ(serializers.Serializer):
    """
    用户ID
    """

    id = serializers.IntegerField(label="用户ID")


class GroupSLZ(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    attributes = serializers.SerializerMethodField()
    role_members = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = (
            "id",
            "name",
            "user_count",
            "department_count",
            "description",
            "creator",
            "created_time",
            "role",
            "attributes",
            "readonly",
            "role_members",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group_role_dict = None
        self.group_attrs_dict = None
        if isinstance(self.instance, (QuerySet, list)) and self.instance:
            group_ids = [group.id for group in self.instance]
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


class MemberSLZ(serializers.Serializer):
    type = serializers.ChoiceField(label="成员类型", choices=GroupMemberType.get_choices())
    id = serializers.CharField(label="成员id")
    name = serializers.CharField(label="名称")
    full_name = serializers.CharField(label="全名(仅部门有)")
    member_count = serializers.IntegerField(label="成员数量(仅部门用)")
    created_time = serializers.DateTimeField(label="添加时间")
    expired_at = serializers.IntegerField(label="过期时间", max_value=PERMANENT_SECONDS)
    expired_at_display = serializers.CharField(label="过期时间显示")


class GroupAddMemberSLZ(serializers.Serializer):
    members = serializers.ListField(label="成员列表", child=GroupMemberSLZ(label="成员"), allow_empty=False)
    expired_at = serializers.IntegerField(label="过期时间", max_value=PERMANENT_SECONDS)

    def validate_expired_at(self, value):
        if value <= int(time.time()):
            raise serializers.ValidationError("expired_at must more then now")
        return value

    def validate_members(self, value):
        # 屏蔽admin授权
        return [m for m in value if not (m["type"] == GroupMemberType.USER.value and m["id"] == ADMIN_USER)]


class GroupsAddMemberSLZ(GroupAddMemberSLZ):
    group_ids = serializers.ListField(label="用户组ID列表")


class GroupUpdateSLZ(serializers.Serializer):
    name = serializers.CharField(label="用户组名称", min_length=2, max_length=128)
    description = serializers.CharField(label="描述", allow_blank=True)

    def validate(self, data):
        """
        校验名称
        """
        if self.instance:
            if Group.objects.exclude(id=self.instance.id).filter(name=data["name"]).exists():
                raise serializers.ValidationError({"name": [_("存在同名用户组")]})

        return data


class GroupDeleteMemberSLZ(serializers.Serializer):
    members = serializers.ListField(label="成员列表", child=GroupMemberSLZ(label="成员"), allow_empty=False)


class GroupTemplateSchemaSLZ(serializers.Serializer):
    id = serializers.CharField(label="权限模板ID")
    name = serializers.CharField(label="权限模板名称")
    system = SystemInfoSLZ(label="系统信息")
    updated_time = serializers.CharField(label="更新时间")


class GroupTemplateSLZ(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(label="权限模板ID", source="template_id")
    system = serializers.SerializerMethodField(label="系统信息")
    name = serializers.SerializerMethodField(label="模板名称")

    class Meta:
        model = PermTemplatePolicyAuthorized
        fields = ("id", "system", "name", "updated_time")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        template_ids = [tmp.template_id for tmp in args[0]]
        self._template_name_dict = TemplateBiz().get_template_name_dict_by_ids(template_ids)
        self._system_list = SystemBiz().new_system_list()

    def get_system(self, obj):
        system_id = obj.system_id
        system = self._system_list.get(system_id)

        return {
            "id": system_id,
            "name": system.name if system else "",
            "name_en": system.name_en if system else "",
        }

    def get_name(self, obj):
        return self._template_name_dict.get(obj.template_id, "")


class GroupTemplateDetailSLZ(GroupTemplateSLZ):
    actions = serializers.SerializerMethodField(label="授权信息")

    def __init__(self, *args, **kwargs):
        serializers.ModelSerializer.__init__(self, *args, **kwargs)
        self._template_name_dict = TemplateBiz().get_template_name_dict_by_ids([self.instance.id])
        self._system_list = SystemBiz().new_system_list()

    class Meta:
        model = PermTemplatePolicyAuthorized
        fields = ("id", "system", "name", "actions", "updated_time")

    def get_actions(self, obj):
        policy_list = PolicyBeanList(
            obj.system_id, parse_obj_as(List[PolicyBean], obj.data["actions"]), need_fill_empty_fields=True
        )

        # ResourceNameAutoUpdate
        updated_policies = GroupBiz().update_template_due_to_renamed_resource(
            int(obj.subject_id), obj.template_id, policy_list
        )

        return [p.dict() for p in updated_policies]


class GroupTemplateDetailSchemaSLZ(GroupTemplateDetailSLZ):
    def __init__(self, *args, **kwargs):
        serializers.ModelSerializer.__init__(self, *args, **kwargs)


class GroupTransferSLZ(serializers.Serializer):
    group_ids = serializers.ListField(label="用户组ID列表", child=serializers.IntegerField(label="用户组ID"))
    role_id = serializers.IntegerField(label="角色唯一标识")

    def validate_role_id(self, value):
        if not Role.objects.filter(pk=value).exists():
            raise serializers.ValidationError(f"role id {value} not exists")
        return value

    def validate_group_ids(self, value):
        role = self.context["role"]

        exists_group_ids = RoleRelatedObject.objects.filter(
            role_id=role.id, object_type=RoleRelatedObjectType.GROUP.value, object_id__in=value
        ).values_list("object_id", flat=True)

        if len(value) != len(exists_group_ids):
            raise serializers.ValidationError(
                f"role cannot manage group ids {[_id for _id in value if _id not in set(exists_group_ids)]}"
            )

        return value


class GroupMemberExpiredAtSLZ(GroupMemberSLZ, ExpiredAtSLZ):
    pass


class GroupMemberUpdateExpiredAtSLZ(serializers.Serializer):
    members = serializers.ListField(label="成员列表", child=GroupMemberExpiredAtSLZ(label="成员"), allow_empty=False)


class GroupPolicyUpdateSLZ(serializers.Serializer):
    system_id = serializers.CharField(label="系统ID")
    template_id = serializers.IntegerField(label="模板ID", required=False, default=0)
    actions = serializers.ListField(label="操作策略", child=BasePolicyActionSLZ(label="策略"), allow_empty=False)


class TemplateAuthorizationSLZ(serializers.Serializer):
    system_id = serializers.CharField(label="系统ID")
    template_id = serializers.IntegerField(label="模板ID", required=False, default=0)
    actions = serializers.ListField(label="操作策略", child=BasePolicyActionSLZ(label="策略"), required=False, default=list)
    aggregations = serializers.ListField(
        label="聚合操作", child=BaseAggActionListSLZ(label="聚合操作"), required=False, default=list
    )

    def validate(self, data):
        # 检查操作是否重复
        validate_action_repeat(data)

        if len(data["actions"]) == 0 and len(data["aggregations"]) == 0:
            raise serializers.ValidationError("all actions expired")
        return data


class GroupAuthorizationSLZ(serializers.Serializer):
    templates = serializers.ListField(label="授权信息", child=TemplateAuthorizationSLZ(label="模板授权"), allow_empty=False)

    def validate(self, data):
        # 单次授权限制
        validate_template_authorization(data["templates"])
        return data


# TODO: [重构] 所有与settings配置或需要复用的validate方法统一到biz.validation
def validate_template_authorization(templates):
    template_ids = [t["template_id"] for t in templates if t["template_id"] != 0]
    if len(template_ids) != len(set(template_ids)):
        raise serializers.ValidationError(_("授权的模板有重复"))

    template_limit = settings.SUBJECT_AUTHORIZATION_LIMIT["group_auth_template_once_limit"]
    if len(template_ids) > template_limit:
        raise serializers.ValidationError(_("单次授权模板数最多{}个").format(template_limit))

    custom_system_ids = [t["system_id"] for t in templates if t["template_id"] == 0]
    if len(custom_system_ids) != len(set(custom_system_ids)):
        raise serializers.ValidationError(_("授权的自定义权限系统有重复"))

    system_limit = settings.SUBJECT_AUTHORIZATION_LIMIT["group_auth_system_once_limit"]
    if len(custom_system_ids) > system_limit:
        raise serializers.ValidationError(_("单次授权自定义系统数最多{}个").format(system_limit))


class GroupCreateSLZ(serializers.Serializer):
    name = serializers.CharField(label="用户组名称", min_length=2, max_length=128)
    description = serializers.CharField(label="描述", allow_blank=True)
    members = serializers.ListField(label="成员列表", child=GroupMemberSLZ(label="成员"))
    expired_at = serializers.IntegerField(label="过期时间", max_value=PERMANENT_SECONDS)
    templates = serializers.ListField(label="授权信息", child=TemplateAuthorizationSLZ(label="模板授权"), allow_empty=True)

    def validate(self, data):
        """
        如果有成员, 过期时间不能小于当前时间
        """
        # 单次授权限制
        validate_template_authorization(data["templates"])

        if data["members"]:
            # 过期时间不能小于当前时间
            if data["expired_at"] <= int(time.time()):
                raise serializers.ValidationError({"expired_at": ["greater than now timestamp"]})

        return data


class GroupAuthorizedConditionSLZ(serializers.Serializer):
    action_id = serializers.CharField(label="操作ID")
    resource_group_id = serializers.CharField(label="资源条件组ID")
    related_resource_type = ResourceTypeSLZ(label="资源类型")


class GradeManagerGroupTransferSLZ(serializers.Serializer):
    subset_manager_id = serializers.IntegerField(label="子集管理员id")

    def validate_subset_manager_id(self, value):
        role = self.context["role"]
        if not RoleRelation.objects.filter(parent_id=role.id, role_id=value).exists():
            raise serializers.ValidationError(f"subset manager id {value} not exists")
        return value


class GroupSearchSLZ(serializers.Serializer):
    name = serializers.CharField(label="用户组名称", required=False, default="", allow_blank=True)
    id = serializers.IntegerField(label="ID", required=False, default=0)
    description = serializers.CharField(label="描述", required=False, default="", allow_blank=True)
    system_id = serializers.CharField(label="系统ID")
    action_id = serializers.CharField(label="操作ID")
    resource_instances = serializers.ListField(
        label="资源实例", required=False, child=ResourceInstancesSLZ(label="资源实例信息"), default=list
    )
