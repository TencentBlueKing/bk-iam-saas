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

from backend.apps.group.models import Group
from backend.apps.subject.serializers import SubjectGroupSLZ
from backend.apps.subject_template.models import SubjectTemplate
from backend.biz.group import GroupBiz
from backend.biz.subject_template import SubjectTemplateBiz
from backend.common.serializers import ResourceInstancesSLZ
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
    subject_template_count = serializers.SerializerMethodField()

    class Meta:
        ref_name = "UserGroupSLZ"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        tenant_id = self.context["tenant_id"]
        self.group_role_dict = None
        self.group_attrs_dict = None
        self.subject_template_count_dict = None
        if isinstance(self.instance, list) and self.instance:
            group_ids = [int(group.id) for group in self.instance]
            self.group_role_dict = GroupBiz(tenant_id).get_group_role_dict_by_ids(group_ids)
            # 查询涉及到的用户组的属性
            self.group_attrs_dict = GroupAttributeService(tenant_id).batch_get_attributes(group_ids)
            # 人员模版数量
            self.subject_template_count_dict = SubjectTemplateBiz(tenant_id).get_group_template_count_dict(group_ids)
        elif isinstance(self.instance, Group):
            self.group_attrs_dict = GroupAttributeService(tenant_id).batch_get_attributes([self.instance.id])
            # 人员模版数量
            self.subject_template_count_dict = SubjectTemplateBiz(tenant_id).get_group_template_count_dict(
                [self.instance.id]
            )

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
        if not role or not role.members:
            return []

        return role.members

    def get_subject_template_count(self, obj):
        if not self.subject_template_count_dict:
            return 0
        return self.subject_template_count_dict.get(obj.id, 0)


class QueryRoleSLZ(serializers.Serializer):
    with_perm = serializers.BooleanField(label="角色是否带权限")


class QueryGroupSLZ(serializers.Serializer):
    system_id = serializers.CharField(label="系统 id", required=False, allow_blank=True, default="")


class UserPolicySearchSLZ(serializers.Serializer):
    system_id = serializers.CharField(label="系统 ID")
    action_id = serializers.CharField(label="操作 ID", required=False, default="", allow_blank=True)
    resource_instances = serializers.ListField(
        label="资源实例", required=False, child=ResourceInstancesSLZ(label="资源实例信息"), default=list
    )


class SubjectTemplateGroupSLZ(GroupSLZ):
    template_id = serializers.IntegerField(label="模板 ID")
    template_name = serializers.SerializerMethodField(label="模板名称")
    created_time = serializers.SerializerMethodField(label="创建时间")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subject_template_dict = None
        if isinstance(self.instance, list) and self.instance:
            template_ids = [group.template_id for group in self.instance]
            self.subject_template_dict = {one.id: one for one in SubjectTemplate.objects.filter(id__in=template_ids)}

    def get_template_name(self, obj):
        if not self.subject_template_dict or not self.subject_template_dict.get(obj.template_id):
            return ""

        return self.subject_template_dict.get(obj.template_id).name

    def get_created_time(self, obj):
        return serializers.DateTimeField().to_representation(obj.created_time)


class SubjectTemplateGroupQuerySLZ(serializers.Serializer):
    system_id = serializers.CharField(label="系统 ID", required=False, allow_blank=True, default="")
    limit = serializers.IntegerField(label="分页 Limit", required=False, default=10, min_value=1, max_value=100)
    offset = serializers.IntegerField(label="分页 offset", required=False, default=0, min_value=0)
