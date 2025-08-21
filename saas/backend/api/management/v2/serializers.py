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

from django.conf import settings
from django.db.models import QuerySet
from django.utils.translation import gettext as _
from rest_framework import serializers

from backend.apps.application.serializers import ExpiredAtSLZ, ReasonSLZ
from backend.apps.group.models import Group
from backend.apps.group.serializers import GroupAuthorizationSLZ
from backend.apps.role.models import Role, RoleUser
from backend.apps.role.serializers import GradeMangerBaseInfoSLZ, RoleScopeSubjectSLZ
from backend.apps.subject_template.models import SubjectTemplate
from backend.apps.template.serializers import TemplateCreateSLZ, TemplateIdSLZ, TemplateListSchemaSLZ, TemplateListSLZ
from backend.biz.role import RoleCheckBiz
from backend.biz.subject_template import SubjectTemplateBiz
from backend.common.serializers import GroupMemberSLZ
from backend.common.time import PERMANENT_SECONDS
from backend.service.constants import ADMIN_USER, GroupMemberType
from backend.service.models import Subject
from backend.util.serializer import StringArrayField


class ManagementSourceSystemSLZ(serializers.Serializer):
    system = serializers.CharField(label="调用API的系统id", max_length=32, help_text="用于认证是哪个系统调用了API")


class ManagementActionSLZ(serializers.Serializer):
    id = serializers.CharField(label="操作ID")


class ManagementResourcePathNodeSLZ(serializers.Serializer):
    system = serializers.CharField(label="系统ID")
    type = serializers.CharField(label="资源类型")
    id = serializers.CharField(label="资源实例ID", max_length=settings.MAX_LENGTH_OF_RESOURCE_ID)
    name = serializers.CharField(
        label="资源实例ID名称", allow_blank=True, trim_whitespace=False
    )  # 路径节点存在无限制，当id="*"则name可以为空


class ManagementResourcePathsSLZ(serializers.Serializer):
    system = serializers.CharField(label="系统ID")
    type = serializers.CharField(label="资源类型")
    paths = serializers.ListField(
        label="批量层级",
        child=serializers.ListField(label="拓扑层级", child=ManagementResourcePathNodeSLZ(label="实例"), allow_empty=False),
        allow_empty=True,
    )


class ManagementRoleScopeAuthorizationSLZ(serializers.Serializer):
    system = serializers.CharField(label="授权的系统id", max_length=32)
    actions = serializers.ListField(label="操作", child=ManagementActionSLZ(label="操作"), allow_empty=False)
    resources = serializers.ListField(
        # 如果action是与资源实例无关的，那么resources允许为空列表，但是字段还是要有，保持格式一致
        label="资源拓扑",
        child=ManagementResourcePathsSLZ(label="匹配资源拓扑"),
        allow_empty=True,
    )

    def validate(self, data):
        if len(data["actions"]) != len({a["id"] for a in data["actions"]}):
            raise serializers.ValidationError({"actions": ["must not repeat"]})
        return data


class ManagementGradeManagerCreateApplicationSLZ(GradeMangerBaseInfoSLZ, ReasonSLZ):
    members = serializers.ListField(
        label="成员列表",
        child=serializers.CharField(label="用户ID", max_length=64),
        max_length=settings.SUBJECT_AUTHORIZATION_LIMIT["grade_manager_member_limit"],
    )
    authorization_scopes = serializers.ListField(
        label="可授权的权限范围", child=ManagementRoleScopeAuthorizationSLZ(label="系统操作"), allow_empty=False
    )
    subject_scopes = serializers.ListField(label="授权对象", child=RoleScopeSubjectSLZ(label="授权对象"), allow_empty=False)
    sync_perm = serializers.BooleanField(label="同步分级管理员权限到用户组", required=False, default=False)
    group_name = serializers.CharField(label="同步用户组名称", max_length=512, required=False, allow_blank=True, default="")
    sync_subject_template = serializers.BooleanField(label="是否同步创建人员模板", default=False)
    applicant = serializers.CharField(label="申请者的用户名", max_length=32)
    callback_id = serializers.CharField(label="回调ID", max_length=32, required=False, allow_blank=True, default="")
    callback_url = serializers.CharField(label="回调URL", required=False, allow_blank=True, default="")
    title = serializers.CharField(label="审批单标题", required=False, allow_blank=True, default="")
    content = serializers.DictField(label="审批单内容", required=False, allow_empty=True, default=dict)


class ManagementGradeManagerBasicInfoSLZ(serializers.Serializer):
    id = serializers.IntegerField(label="分级管理员ID")
    name = serializers.CharField(label="分级管理员名称", max_length=128)
    description = serializers.CharField(label="描述", allow_blank=True)


class ManagementGradeManagerMembersSLZ(serializers.Serializer):
    members = serializers.ListField(child=serializers.CharField(label="成员"), max_length=100)

    def validate(self, data):
        """
        校验成员加入的分级管理员数是否超过限制
        """
        role_check_biz = RoleCheckBiz()
        for username in data["members"]:
            # subject加入的分级管理员数量不能超过最大值
            role_check_biz.check_subject_grade_manager_limit(Subject.from_username(username))
        return data


class ManagementGradeManagerMembersDeleteSLZ(serializers.Serializer):
    members = serializers.CharField(label="用户名", help_text="用户名，多个以英文逗号分隔")

    def validate(self, data):
        # 验证 member的合法性，并转化为后续view需要数据格式
        members = data.get("members") or ""
        if members:
            try:
                data["members"] = list(filter(None, members.split(",")))
            except Exception:  # pylint: disable=broad-except
                raise serializers.ValidationError({"members": [f"用户名({members})非法"]})

        if len(data["members"]) == 0:
            raise serializers.ValidationError({"members": "should not be empty"})

        return data


class ManagementGroupBasicInfoSLZ(serializers.Serializer):
    name = serializers.CharField(label="用户组名称", min_length=2, max_length=512)
    description = serializers.CharField(label="描述", allow_blank=True)


class ManagementGroupBasicCreateSLZ(ManagementGroupBasicInfoSLZ):
    readonly = serializers.BooleanField(label="是否只读", default=False, required=False)


class ManagementGradeManagerGroupCreateSLZ(serializers.Serializer):
    groups = serializers.ListField(child=ManagementGroupBasicCreateSLZ(label="用户组"), max_length=10)
    create_attributes = serializers.BooleanField(label="是否创建属性", default=True, required=False)
    sync_subject_template = serializers.BooleanField(label="是否同步创建人员模板", default=False)

    def validate(self, data):
        """
        groups自身数据是否包括用户重名
        """
        groups_data = data["groups"]
        names = set()
        for g in groups_data:
            if g["name"] in names:
                raise serializers.ValidationError({"groups": [_("用户组名称{}不能重复").format(g["name"])]})
            names.add(g["name"])
        return data


class ManagementGroupBasicSLZ(ManagementGroupBasicInfoSLZ):
    id = serializers.IntegerField(label="用户组ID")


class ManagementGroupBaseInfoUpdateSLZ(serializers.Serializer):
    name = serializers.CharField(label="用户组名称", min_length=2, max_length=128, required=False)
    description = serializers.CharField(label="描述", allow_blank=True, required=False)


class ManagementGroupMemberSLZ(serializers.Serializer):
    type = serializers.ChoiceField(label="成员类型", choices=GroupMemberType.get_choices())
    id = serializers.CharField(label="成员id")
    name = serializers.CharField(label="名称")
    expired_at = serializers.IntegerField(label="过期时间戳(单位秒)")
    created_at = serializers.IntegerField(label="创建时间戳(单位秒)")


class ManagementGroupMemberDeleteSLZ(serializers.Serializer):
    type = serializers.ChoiceField(label="成员类型", choices=GroupMemberType.get_choices())
    ids = serializers.CharField(
        label="成员IDs", help_text="成员IDs，多个以英文逗号分隔, 对于type=user，则ID为用户名，对于type=department，则为部门ID"
    )

    def validate(self, data):
        # 验证 ID的合法性，并转化为后续view需要数据格式
        ids = data.get("ids") or ""
        if ids:
            try:
                data["ids"] = list(filter(None, ids.split(",")))
            except Exception:  # pylint: disable=broad-except
                raise serializers.ValidationError({"ids": [f"成员IDS({ids})非法"]})

        if len(data["ids"]) == 0:
            raise serializers.ValidationError({"ids": "should not be empty"})

        return data


class ManagementGroupSubjectTemplateSLZ(serializers.Serializer):
    id = serializers.CharField(label="人员模板 ID", source="template_id")
    name = serializers.SerializerMethodField(label="人员模板名称")
    expired_at = serializers.IntegerField(label="过期时间戳(单位秒)")

    def get_name(self, obj):
        return self.context["subject_template_name_map"].get(obj.template_id) or obj.template_id


class ManagementGradeManagerBasicSLZ(serializers.Serializer):
    id = serializers.IntegerField(label="分级管理员ID")


class ManagementUserQuerySLZ(serializers.Serializer):
    user_id = serializers.CharField(label="用户名", max_length=32)


class ManagementUserGradeManagerQuerySLZ(ManagementUserQuerySLZ, ManagementSourceSystemSLZ):
    pass


class ManagementGroupGrantSLZ(ManagementRoleScopeAuthorizationSLZ):
    system = serializers.CharField(label="授权的系统id", max_length=32, required=False, allow_blank=True, default="")


class ManagementGroupRevokeSLZ(ManagementRoleScopeAuthorizationSLZ):
    system = serializers.CharField(label="授权的系统id", max_length=32, required=False, allow_blank=True, default="")


class ManagementGroupPolicyDeleteSLZ(serializers.Serializer):
    system = serializers.CharField(label="授权的系统id", max_length=32, required=False, allow_blank=True, default="")
    actions = serializers.ListField(label="操作", child=ManagementActionSLZ(label="操作"), allow_empty=False)


class ManagementGroupIDsSLZ(serializers.Serializer):
    group_ids = serializers.ListField(label="用户组ID列表", child=serializers.IntegerField(label="用户组ID"))


class ManagementGroupApplicationSLZ(serializers.Serializer):
    applicant = serializers.CharField(label="申请者的用户名", max_length=32)
    content_template = serializers.DictField(label="审批单内容模板", required=False, allow_empty=True, default=dict)
    group_content = serializers.DictField(label="审批单内容", required=False, allow_empty=True, default=dict)
    title_prefix = serializers.CharField(label="审批单标题前缀", required=False, allow_blank=True, default="")

    def validate(self, data):
        if data["content_template"] and data["group_content"]:
            if "schemes" not in data["content_template"] or "form_data" not in data["content_template"]:
                raise serializers.ValidationError({"content_template": ["content_template中必须包含schemes和form_data"]})
            if (
                not isinstance(data["content_template"]["form_data"], list)
                or len(data["content_template"]["form_data"]) != 1
                or "value" not in data["content_template"]["form_data"][0]
                or not isinstance(data["content_template"]["form_data"][0]["value"], list)
            ):
                raise serializers.ValidationError({"content_template": ["content_template中必须包含form_data且为空数组"]})

            if set(map(str, data["group_ids"])) != set(data["group_content"].keys()):
                raise serializers.ValidationError({"group_content": ["group_content中的key必须与group_ids一致"]})
        else:
            data["content_template"] = None
            data["group_content"] = None
        return data


class ManagementGroupApplicationCreateSLZ(
    ManagementGroupApplicationSLZ, ManagementGroupIDsSLZ, ExpiredAtSLZ, ReasonSLZ
):
    pass


class ManagementApplicationIDSLZ(serializers.Serializer):
    ids = serializers.ListField(label="申请单据ID列表", child=serializers.CharField(label="申请单据ID"))


class ManagementSubjectGroupBelongSLZ(serializers.Serializer):
    group_ids = serializers.CharField(label="用户组ID，多个以英文逗号分隔", max_length=255, required=True)


class ManagementMemberGroupDetailInputInPathSLZ(serializers.Serializer):
    group_member_type = serializers.ChoiceField(help_text="用户组成员类型", choices=GroupMemberType.get_choices())
    member_id = serializers.CharField(help_text="用户组成员 ID", max_length=128)

    def validate(self, attrs):
        # 组织 ID 和 人员模板 ID 都必须是整数
        group_member_type = attrs["group_member_type"]
        member_id = attrs["member_id"]
        if group_member_type in (GroupMemberType.DEPARTMENT.value, GroupMemberType.TEMPLATE.value):
            try:
                int(member_id)
            except ValueError:
                raise serializers.ValidationError(
                    {
                        "member_id": [f"当 group_member_type 为 {group_member_type} 时，member_id({member_id}) 必须为整数"],
                    }
                )

        return attrs


class ManagementMemberGroupDetailInputSLZ(serializers.Serializer):
    group_ids = StringArrayField(help_text="用户组 ID，多个以英文逗号分隔", min_items=1, max_items=100)

    def validate_group_ids(self, value):
        try:
            [int(i) for i in value]
        except ValueError:
            raise serializers.ValidationError({"group_ids": ["用户组 ID 必须为整数"]})

        return value


class ManagementMemberGroupDetailOutputSLZ(serializers.Serializer):
    id = serializers.IntegerField(help_text="用户组 ID")
    name = serializers.CharField(help_text="用户组名称")
    description = serializers.CharField(help_text="用户组描述")
    created_at = serializers.SerializerMethodField(help_text="加入用户组时间戳")
    expired_at = serializers.SerializerMethodField(help_text="过期时间戳")

    def get_created_at(self, obj):
        return self.context["subject_group_map"][obj.id]["created_at"]

    def get_expired_at(self, obj):
        return self.context["subject_group_map"][obj.id]["expired_at"]


class ManagementGradeManagerApplicationResultSLZ(serializers.Serializer):
    id = serializers.CharField(label="申请单据ID")
    sn = serializers.CharField(label="ITSM审批单SN")


class ManagementSubsetMangerCreateSLZ(GradeMangerBaseInfoSLZ):
    members = serializers.ListField(
        label="成员列表",
        child=serializers.CharField(label="用户ID", max_length=64),
        max_length=settings.SUBJECT_AUTHORIZATION_LIMIT["grade_manager_member_limit"],
    )
    authorization_scopes = serializers.ListField(
        label="可授权的权限范围", child=ManagementRoleScopeAuthorizationSLZ(label="系统操作"), allow_empty=False
    )
    subject_scopes = serializers.ListField(label="授权对象", child=RoleScopeSubjectSLZ(label="授权对象"), allow_empty=True)
    inherit_subject_scope = serializers.BooleanField(label="继承分级管理员人员管理范围", required=False, default=False)
    sync_perm = serializers.BooleanField(label="同步分级管理员权限到用户组", required=False, default=False)
    group_name = serializers.CharField(label="同步用户组名称", max_length=512, required=False, allow_blank=True, default="")

    def validate(self, data):
        data = super().validate(data)
        if not data["inherit_subject_scope"] and not data["subject_scopes"]:
            raise serializers.ValidationError({"subject_scopes": ["must not be empty"]})
        return data


class ManagementGroupSLZ(serializers.ModelSerializer):
    subject_template_count = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = (
            "id",
            "name",
            "user_count",
            "department_count",
            "subject_template_count",
            "description",
            "creator",
            "created_time",
            "readonly",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subject_template_count_dict = None
        if isinstance(self.instance, (QuerySet, list)) and self.instance:
            group_ids = [int(group.id) for group in self.instance]
            # 人员模版数量
            self.subject_template_count_dict = SubjectTemplateBiz().get_group_template_count_dict(group_ids)
        elif isinstance(self.instance, Group):
            # 人员模版数量
            self.subject_template_count_dict = SubjectTemplateBiz().get_group_template_count_dict([self.instance.id])

    def get_subject_template_count(self, obj):
        if not self.subject_template_count_dict:
            return 0
        return self.subject_template_count_dict.get(obj.id, 0)


class ManagementQueryGroupSLZ(serializers.Serializer):
    inherit = serializers.BooleanField(label="是否继承子集管理员的用户组", required=False, default=True)
    only_inherit = serializers.BooleanField(label="是否只查询继承子集管理员的用户组", required=False, default=False)


class ManagementGradeManagerCreateSLZ(GradeMangerBaseInfoSLZ):
    members = serializers.ListField(
        label="成员列表",
        child=serializers.CharField(label="用户ID", max_length=64),
        max_length=settings.SUBJECT_AUTHORIZATION_LIMIT["grade_manager_member_limit"],
    )
    authorization_scopes = serializers.ListField(
        label="可授权的权限范围", child=ManagementRoleScopeAuthorizationSLZ(label="系统操作"), allow_empty=False
    )
    subject_scopes = serializers.ListField(label="授权对象", child=RoleScopeSubjectSLZ(label="授权对象"), allow_empty=False)
    sync_perm = serializers.BooleanField(label="同步分级管理员权限到用户组", required=False, default=False)
    group_name = serializers.CharField(label="同步用户组名称", max_length=512, required=False, allow_blank=True, default="")
    sync_subject_template = serializers.BooleanField(label="是否同步创建人员模板", default=False)
    enabled = serializers.BooleanField(label="是否启用", required=False, default=True)


class ManagementGradeMangerDetailSLZ(serializers.ModelSerializer):
    members = serializers.SerializerMethodField(label="成员列表")

    class Meta:
        model = Role
        fields = (
            "id",
            "name",
            "description",
            "creator",
            "created_time",
            "updated_time",
            "updater",
            "members",
            "sync_perm",
            "enabled",
        )

    def get_members(self, obj):
        return [one.username for one in RoleUser.objects.filter(role_id=obj.id)]


class ManagementSubjectTemplateSLZ(serializers.ModelSerializer):
    class Meta:
        model = SubjectTemplate
        fields = ("id", "name", "description", "readonly", "source_group_id", "creator", "created_time")


class ManagementGroupAuthorizationSLZ(GroupAuthorizationSLZ):
    pass


class ManagementTemplateListSchemaSLZ(TemplateListSchemaSLZ):
    pass


class ManagementTemplateListSLZ(TemplateListSLZ):
    pass


class ManagementTemplateCreateSLZ(TemplateCreateSLZ):
    pass


class ManagementTemplateIdSLZ(TemplateIdSLZ):
    pass


class ManagementGroupExpiredAtSLZ(ExpiredAtSLZ):
    id = serializers.IntegerField(help_text="用户组 ID")


class ManagementGroupsSLZ(serializers.Serializer):
    groups = serializers.ListField(child=ManagementGroupExpiredAtSLZ(label="用户组信息"))


class ManagementGroupApplicationBatchSLZ(ManagementGroupApplicationSLZ, ReasonSLZ, ManagementGroupsSLZ):
    pass


class GroupMemberExpiredSLZ(GroupMemberSLZ):
    expired_at = serializers.IntegerField(label="过期时间", max_value=PERMANENT_SECONDS)


class GroupBatchUpdateMemberSLZ(serializers.Serializer):
    members = serializers.ListField(label="成员列表", child=GroupMemberExpiredSLZ(label="成员"), allow_empty=False)

    def validate_members(self, value):
        members = []

        for m in value:
            # 过期时间不能小于当前时间
            if m["expired_at"] <= int(time.time()):
                raise serializers.ValidationError("expired_at must more then now")
            # 屏蔽admin授权
            if not (m["type"] == GroupMemberType.USER.value and m["id"] == ADMIN_USER):
                members.append(m)

        return members
