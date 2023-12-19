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
from datetime import datetime

from rest_framework import serializers

from backend.apps.group.models import Group
from backend.apps.subject_template.models import SubjectTemplate
from backend.common.time import PERMANENT_SECONDS, expired_at_display
from backend.service.constants import SubjectTemplateMemberType


class SubjectTemplateSubjectSLZ(serializers.Serializer):
    type = serializers.ChoiceField(label="成员类型", choices=SubjectTemplateMemberType.get_choices())
    id = serializers.CharField(label="成员id")


class BaseSubjectTemplateSLZ(serializers.Serializer):
    name = serializers.CharField(label="名称", max_length=128)
    description = serializers.CharField(label="描述", allow_blank=True)


class SubjectTemplateMemberSLZ(serializers.Serializer):
    subjects = serializers.ListField(label="成员列表", child=SubjectTemplateSubjectSLZ(), max_length=1000)


class SubjectTemplateCreateSLZ(BaseSubjectTemplateSLZ, SubjectTemplateMemberSLZ):
    pass


class SubjectTemplateListSLZ(serializers.ModelSerializer):
    group_count = serializers.SerializerMethodField(label="用户组数量")

    class Meta:
        model = SubjectTemplate
        fields = ("id", "name", "description", "readonly", "group_count", "creator", "created_time")

    # 关联的用户组数量
    def get_group_count(self, obj):
        return self.context["group_count_dict"].get(obj.id, 0)


class SubjectTemplateMemberListSLZ(serializers.Serializer):
    type = serializers.ChoiceField(label="成员类型", choices=SubjectTemplateMemberType.get_choices())
    id = serializers.CharField(label="成员id")
    name = serializers.CharField(label="名称")
    full_name = serializers.CharField(label="全名(仅部门有)")
    member_count = serializers.IntegerField(label="成员数量(仅部门用)")
    user_departments = serializers.ListField(label="用户部门", child=serializers.CharField())
    created_time = serializers.DateTimeField(label="添加时间")


class SubjectTemplateGroupSLZ(serializers.Serializer):
    id = serializers.CharField(label="用户组ID")
    name = serializers.CharField(label="用户组名称")
    expired_at = serializers.IntegerField(label="过期时间", max_value=PERMANENT_SECONDS)
    expired_at_display = serializers.CharField(label="过期时间显示")
    created_time = serializers.CharField(label="加入时间")


class SubjectTemplateIdSLZ(serializers.Serializer):
    """
    人员模版ID
    """

    id = serializers.IntegerField(label="人员模版ID")


class SubjectTemplatesAddMemberSLZ(SubjectTemplateMemberSLZ):
    template_ids = serializers.ListField(label="人员模版ID列表", child=serializers.IntegerField())


class SubjectTemplateGroupIdSLZ(serializers.Serializer):
    """
    人员模版组ID
    """

    group_id = serializers.IntegerField(label="用户组ID")


class SubjectTemplateGroupOutputSLZ(serializers.ModelSerializer):
    expired_at = serializers.SerializerMethodField(label="过期时间")
    expired_at_display = serializers.SerializerMethodField(label="过期时间显示")
    created_time = serializers.SerializerMethodField(label="创建时间")

    class Meta:
        model = Group
        fields = ("id", "name", "expired_at", "expired_at_display", "created_time")

    def get_expired_at(self, obj):
        return self.context["template_dict"].get(obj.id, {}).get("expired_at", 0)

    def get_expired_at_display(self, obj):
        return expired_at_display(self.get_expired_at(obj))

    def get_created_time(self, obj):
        t = self.context["template_dict"].get(obj.id, {}).get("created_time", "")
        if not isinstance(t, datetime):
            return t

        return serializers.DateTimeField().to_representation(t)
