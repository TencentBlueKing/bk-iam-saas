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
from typing import Any, Dict, List

from pydantic import BaseModel

from backend.common.time import expired_at_display
from backend.service.constants import (
    ANY_ID,
    PolicyEnvConditionType,
    PolicyEnvType,
    SensitivityLevel,
    SubjectType,
    WeekDayEnum,
)
from backend.service.models import (
    ApplicationAuthorizationScope,
    ApplicationEnvironment,
    ApplicationGroupInfo,
    ApplicationGroupPermTemplate,
    ApplicationPolicyInfo,
    ApplicationRelatedResource,
    ApplicationResourceAttribute,
    ApplicationResourceCondition,
    ApplicationResourceGroup,
    ApplicationResourceGroupList,
    ApplicationResourceInstance,
    GradeManagerApplicationContent,
    GrantActionApplicationContent,
    GroupApplicationContent,
    HandoverApplicationContent,
)

from .ticket_content_tpl import FormSchemeEnum


# ---------------------------- 公共权限展示 ----------------------------
class BaseDictStrValue(BaseModel):
    label: str = ""
    value: str = ""


class BaseDictListValue(BaseModel):
    value: List[BaseDictStrValue]


class BaseText(BaseModel):
    label: str = ""
    scheme: str = FormSchemeEnum.BASE_TEXT.value
    value: str = ""


class BaseMultiLineText(BaseModel):
    label: str = ""
    scheme: str = FormSchemeEnum.BASE_TEXT.value
    value: List[BaseDictStrValue]


class ResourceUnlimited(BaseModel):
    """资源无限制展示方式"""

    label: str = "关联资源类型"  # 关联资源类型：xx
    scheme: str = FormSchemeEnum.BASE_TEXT.value
    value: str = "无限制"

    @classmethod
    def from_resource(cls, resource_type_name: str):
        return cls(label=f"关联资源类型: {resource_type_name}")


class ResourceInstanceColumnValue(BaseModel):
    """资源实例表格每一列的值"""

    type: BaseDictStrValue
    path: BaseDictListValue

    @classmethod
    def from_instance(cls, instance: ApplicationResourceInstance):
        if not instance:
            return cls(type=BaseDictStrValue(value="-"), path=BaseDictListValue(value=[BaseDictStrValue(value="-")]))
        path_name = ["/".join([p.name for p in path]) for path in instance.path]
        return cls(
            type=BaseDictStrValue(value=f"{instance.name}({len(instance.path)})"),
            path=BaseDictListValue(value=[BaseDictStrValue(value=n) for n in path_name]),
        )


class ResourceInstanceTable(BaseModel):
    """资源实例表格"""

    label: str = "关联资源类型"  # 关联资源类型：xx
    scheme: str = FormSchemeEnum.RESOURCE_INSTANCE_TABLE.value
    value: List[ResourceInstanceColumnValue]

    @classmethod
    def from_conditions(cls, resource_type_name: str, conditions: List[ApplicationResourceCondition]):
        values = []
        for c in conditions:
            for i in c.instances:
                values.append(ResourceInstanceColumnValue.from_instance(i))
        return cls(label=f"关联资源类型: {resource_type_name}", value=values)


class ResourceAttributeColumnValue(BaseModel):
    """资源属性表格每一列的值"""

    attributes: BaseDictListValue

    @classmethod
    def from_attributes(cls, attributes: List[ApplicationResourceAttribute]):
        if not attributes:
            return cls(attributes=BaseDictListValue(value=[BaseDictStrValue(value="-")]))
        return cls(
            attributes=BaseDictListValue(
                value=[
                    BaseDictStrValue(value=f"{attr.name}: {','.join([av.name for av in attr.values])}")
                    for attr in attributes
                ]
            )
        )


class ResourceAttributeTable(BaseModel):
    """资源属性表格"""

    label: str = "关联资源类型"  # 关联资源类型：xx
    scheme: str = FormSchemeEnum.RESOURCE_ATTRIBUTE_TABLE.value
    value: List[ResourceAttributeColumnValue]

    @classmethod
    def from_conditions(cls, resource_type_name: str, conditions: List[ApplicationResourceCondition]):
        return cls(
            label=f"关联资源类型: {resource_type_name}",
            value=[ResourceAttributeColumnValue.from_attributes(c.attributes) for c in conditions],
        )


class ResourceBothColumnValue(BaseModel):
    """资源实例属性表格每一列的值"""

    type: BaseDictStrValue
    path: BaseDictListValue
    attributes: BaseDictListValue


class ResourceBothTable(BaseModel):
    """资源实例和属性表格"""

    label: str = "关联资源类型"  # 关联资源类型：xx
    scheme: str = FormSchemeEnum.RESOURCE_BOTH_TABLE.value
    value: List[ResourceBothColumnValue]

    @classmethod
    def from_conditions(cls, resource_type_name: str, conditions: List[ApplicationResourceCondition]):
        values = []
        for c in conditions:
            attr = ResourceAttributeColumnValue.from_attributes(c.attributes)
            for i in c.instances:
                inst = ResourceInstanceColumnValue.from_instance(i)
                values.append(ResourceBothColumnValue(type=inst.type, path=inst.path, attributes=attr.attributes))
        return cls(label=f"关联资源类型: {resource_type_name}", value=values)


class ActionRelatedResourceTypeInfo(BaseModel):
    """权限关联的资源类型"""

    value: List[BaseDictStrValue]
    # Note: dont use `List[Union[ResourceBothTable, ResourceInstanceTable, ResourceAttributeTable, ResourceUnlimited]]`
    # reason: https://pydantic-docs.helpmanual.io/usage/types/#unions
    children: List = []

    @classmethod
    def from_resource_types(cls, related_resource_types: List[ApplicationRelatedResource]):
        # 1. 与资源实例无关
        if not related_resource_types:
            return cls(value=[BaseDictStrValue(value="无需关联实例")])
        # 遍历关联的资源类型
        values = []
        children = []
        for i in related_resource_types:
            # 2. 无限制
            if not i.condition:
                values.append(BaseDictStrValue(value=f"{i.name}: 无限制"))
                children.append(ResourceUnlimited.from_resource(i.name))
                continue

            # 判断需要用哪种表格来渲染
            has_instance = False
            has_attribute = False
            for c in i.condition:
                if c.instances:
                    has_instance = True
                if c.attributes:
                    has_attribute = True

            # 3. 仅仅资源实例
            if has_instance and not has_attribute:
                v = []
                for c in i.condition:
                    for ist in c.instances:
                        v.append(f"{len(ist.path)}个{ist.name}")
                values.append(BaseDictStrValue(value=f"{i.name}: 已选择 {', '.join(v)}"))
                children.append(ResourceInstanceTable.from_conditions(i.name, i.condition))
                continue
            # 4. 仅仅属性
            if not has_instance and has_attribute:
                len_attr = sum([len(c.attributes) for c in i.condition])
                values.append(BaseDictStrValue(value=f"{i.name}: 已设置 {len_attr} 个属性条件"))
                children.append(ResourceAttributeTable.from_conditions(i.name, i.condition))
                continue
            # 5. 存在同时有属性和实例的条件组
            len_attr = sum([len(c.attributes) for c in i.condition])
            v = []
            for c in i.condition:
                for ist in c.instances:
                    v.append(f"{len(ist.path)}个{ist.name}")
            values.append(BaseDictStrValue(value=f"{i.name}: 已设置 {len_attr} 个属性条件; 已选择 {', '.join(v)}"))
            children.append(ResourceBothTable.from_conditions(i.name, i.condition))

        return cls(value=values, children=children)


class EnvironmentColumnValue(BaseModel):
    """环境属性表格每一列的值"""

    type: BaseDictStrValue
    condition: BaseDictListValue

    @classmethod
    def from_environment(cls, environment: ApplicationEnvironment) -> "EnvironmentColumnValue":
        type = BaseDictStrValue(value=dict(PolicyEnvType.get_choices())[environment.type])
        condition = BaseDictListValue(value=[])

        cond_type_dict = dict(PolicyEnvConditionType.get_choices())
        for cond in environment.condition:
            text = f"{cond_type_dict[cond.type]}: "
            if cond.type == PolicyEnvConditionType.TZ.value:
                text += cond.values[0].value
            elif cond.type == PolicyEnvConditionType.HMS.value:
                text += f"{cond.values[0].value} -- {cond.values[1].value}"
            elif cond.type == PolicyEnvConditionType.WEEKDAY.value:
                week_day_dict = dict(WeekDayEnum.get_choices())
                text += ", ".join([week_day_dict[int(v.value)] for v in cond.values])

            condition.value.append(BaseDictStrValue(value=text))

        return EnvironmentColumnValue(type=type, condition=condition)


class EnvironmentTable(BaseModel):
    """环境属性表格"""

    label: str = "环境属性"
    scheme: str = FormSchemeEnum.ENVIRONMENT_TABLE.value
    value: List[EnvironmentColumnValue]

    @classmethod
    def from_environments(cls, environments: List[ApplicationEnvironment]) -> "EnvironmentTable":
        return EnvironmentTable(value=[EnvironmentColumnValue.from_environment(env) for env in environments])


class EnvironmentInfo(BaseModel):
    value: List[BaseDictStrValue]
    children: List[EnvironmentTable] = []

    @classmethod
    def from_environments(cls, environments: List[ApplicationEnvironment]) -> "EnvironmentInfo":
        if not environments:
            return EnvironmentInfo(value=[])

        return EnvironmentInfo(
            value=[BaseDictStrValue(value=f"已设置 {len(environments)} 个环境属性")],
            children=[EnvironmentTable.from_environments(environments)],
        )


class ResourceGroupColumnValue(BaseModel):
    related_resource_types: ActionRelatedResourceTypeInfo
    environments: EnvironmentInfo

    @classmethod
    def from_resource_group(cls, resource_group: ApplicationResourceGroup) -> "ResourceGroupColumnValue":
        return ResourceGroupColumnValue(
            related_resource_types=ActionRelatedResourceTypeInfo.from_resource_types(
                resource_group.related_resource_types
            ),
            environments=EnvironmentInfo.from_environments(resource_group.environments),
        )


class ResourceGroupTable(BaseModel):
    label: str = "资源组合"
    scheme: str = FormSchemeEnum.RESOURCE_GROUP_TABLE.value
    value: List[ResourceGroupColumnValue]

    @classmethod
    def from_resource_groups(cls, resource_groups: ApplicationResourceGroupList) -> "ResourceGroupTable":
        return ResourceGroupTable(value=[ResourceGroupColumnValue.from_resource_group(rg) for rg in resource_groups])


class ResourceGroupInfo(BaseModel):
    """资源组"""

    value: List[BaseDictStrValue]
    children: List[ResourceGroupTable] = []

    @classmethod
    def from_resource_groups(cls, resource_groups: ApplicationResourceGroupList) -> "ResourceGroupInfo":
        value = [BaseDictStrValue(value=cls.gen_resource_summary(resource_groups))]
        children = [ResourceGroupTable.from_resource_groups(resource_groups)]
        return ResourceGroupInfo(value=value, children=children)

    @staticmethod
    def gen_resource_summary(resource_groups: ApplicationResourceGroupList) -> str:
        """
        生成资源组合概要信息
        """
        if len(resource_groups) != 1:
            return f"已设置 {len(resource_groups)} 个资源组"

        summary = []
        for rg in resource_groups:
            for rt in rg.related_resource_types:
                resource_type_name = rt.name
                if len(rt.condition) == 0:
                    value = f"{resource_type_name}: 无限制"
                else:
                    # 解析资源条件
                    resource_name = ""
                    resource_count = 0
                    attribute_count = 0
                    for c in rt.condition:
                        for instance in c.instances:
                            resource_count += len(instance.path)
                            if resource_name == "":
                                if instance.path[0][-1].id == ANY_ID and len(instance.path[0]) > 1:
                                    resource_name = instance.path[0][-2].name
                                else:
                                    resource_name = instance.path[0][-1].name
                        attribute_count += len(c.attributes)

                    if attribute_count == 0 and resource_count == 1:
                        value = f"{resource_type_name}: {resource_name}"
                    elif attribute_count == 0 and resource_count > 1:
                        value = f"{resource_type_name}: {resource_name}等{resource_count}个实例"
                    elif attribute_count > 0 and resource_count == 0:
                        value = f"{resource_type_name}: {attribute_count}个属性"
                    else:
                        value = f"{resource_type_name}: {resource_count}个实例({attribute_count}个属性)"

                summary.append(value)

        return ", ".join(summary)


# ---------------------------- 自定义权限申请 ----------------------------
class ActionColumnValue(BaseModel):
    """权限表格每一列的值"""

    action: BaseDictStrValue
    sensitivity_level: BaseDictStrValue
    resource_groups: ResourceGroupInfo
    expired_display: BaseDictStrValue

    @classmethod
    def from_policy(cls, policy: ApplicationPolicyInfo):
        if len(policy.resource_groups) == 0:
            resource_groups = ResourceGroupInfo(value=[BaseDictStrValue(value="无需关联实例")])
        else:
            resource_groups = ResourceGroupInfo.from_resource_groups(policy.resource_groups)
        return cls(
            action=BaseDictStrValue(value=policy.name),
            sensitivity_level=BaseDictStrValue(value=SensitivityLevel.get_choice_label(policy.sensitivity_level)),
            resource_groups=resource_groups,
            expired_display=BaseDictStrValue(value=policy.expired_display),
        )


class ActionTable(BaseModel):
    """权限表格"""

    label: str = "系统"  # 系统: xxx
    scheme: str = FormSchemeEnum.ACTION_TABLE.value
    value: List[ActionColumnValue]

    @classmethod
    def from_application(cls, content: GrantActionApplicationContent):
        values = [ActionColumnValue.from_policy(p) for p in content.policies]
        return cls(label=f"系统: {content.system.name}", value=values)


# ---------------------------- 加入用户组 ----------------------------
class GroupActionColumnValue(BaseModel):
    """用户组权限表格每一列的值"""

    action: BaseDictStrValue
    resource_groups: ResourceGroupInfo

    @classmethod
    def from_policy(cls, policy: ApplicationPolicyInfo):
        if len(policy.resource_groups) == 0:
            resource_groups = ResourceGroupInfo(value=[BaseDictStrValue(value="无需关联实例")])
        else:
            resource_groups = ResourceGroupInfo.from_resource_groups(policy.resource_groups)
        return cls(action=BaseDictStrValue(value=policy.name), resource_groups=resource_groups)


class GroupActionTable(BaseModel):
    """用户组权限表格"""

    label: str = "权限模板(系统)"  # 系统: xxx
    scheme: str = FormSchemeEnum.ACTION_TABLE_WITHOUT_EXP.value
    value: List[GroupActionColumnValue]

    @classmethod
    def from_template(cls, template: ApplicationGroupPermTemplate):
        values = [GroupActionColumnValue.from_policy(p) for p in template.policies]
        return cls(label=f"{template.name}({template.system.name})", value=values)


class GroupInfo(BaseModel):
    """用户组信息：包括名称和权限信息"""

    value: str
    children: List[GroupActionTable] = []

    @classmethod
    def from_group(cls, group: ApplicationGroupInfo):
        return cls(value=group.name, children=[GroupActionTable.from_template(t) for t in group.templates])


class GroupColumnValue(BaseModel):
    """用户组表格每一列的值"""

    id: BaseDictStrValue
    desc: BaseDictStrValue
    expired_display: BaseDictStrValue
    group_info: GroupInfo
    role_name: BaseDictStrValue
    highest_sensitivity_level: BaseDictStrValue  # 最高敏感等级

    @classmethod
    def from_group(cls, group: ApplicationGroupInfo):
        return cls(
            id=BaseDictStrValue(value=f"#{group.id}"),
            desc=BaseDictStrValue(value=group.description),
            expired_display=BaseDictStrValue(value=group.expired_display),
            group_info=GroupInfo.from_group(group),
            role_name=BaseDictStrValue(value=group.role_name),
            highest_sensitivity_level=BaseDictStrValue(
                value=SensitivityLevel.get_choice_label(group.highest_sensitivity_level)
            ),
        )


class GroupTable(BaseModel):
    """用户组表格"""

    label: str = "用户组"
    scheme: str = FormSchemeEnum.GROUP_TABLE.value
    value: List[GroupColumnValue]

    @classmethod
    def from_application(cls, application_data: GroupApplicationContent):
        # 遍历每个用户组
        group_column_value = [GroupColumnValue.from_group(g) for g in application_data.groups]
        return cls(label="用户组", value=group_column_value)


# ---------------------------- 申请创建分级管理员 ----------------------------
class AuthScopeActionColumnValue(BaseModel):
    """权限表格每一列的值"""

    action: BaseDictStrValue
    resource_groups: ResourceGroupInfo

    @classmethod
    def from_policy(cls, policy: ApplicationPolicyInfo):
        if len(policy.resource_groups) == 0:
            resource_groups = ResourceGroupInfo(value=[BaseDictStrValue(value="无需关联实例")])
        else:
            resource_groups = ResourceGroupInfo.from_resource_groups(policy.resource_groups)
        return cls(action=BaseDictStrValue(value=policy.name), resource_groups=resource_groups)


class AuthScopeActionTable(BaseModel):
    label: str = "系统"
    scheme: str = FormSchemeEnum.ACTION_TABLE_WITHOUT_EXP.value
    value: List[AuthScopeActionColumnValue]

    @classmethod
    def from_auth_scope(cls, scope: ApplicationAuthorizationScope):
        values = [AuthScopeActionColumnValue.from_policy(p) for p in scope.policies]
        return cls(label=f"{scope.system.name}", value=values)


class GradeManagerForm(BaseModel):
    # 基本信息描述、权限表格、授权人员范围
    # Note: dont use `List[Union[AuthScopeActionTable, BaseMultiLineText, BaseText]]`
    # reason: https://pydantic-docs.helpmanual.io/usage/types/#unions
    form_data: List

    @classmethod
    def from_application(cls, application_data: GradeManagerApplicationContent):
        form_data = [
            # 基本信息
            BaseText(label="【管理空间名称】", value=application_data.name),
            BaseText(label="【描述】", value=application_data.description if application_data.description else "--"),
            BaseText(label="【成员列表】", value=";".join([f"{m.id}({m.name})" for m in application_data.members])),
            BaseText(label="【操作和实例范围】"),
        ]

        # 渲染权限表格
        for scope in application_data.authorization_scopes:
            form_data.append(AuthScopeActionTable.from_auth_scope(scope))

        # 可授权人员范围
        users = [s for s in application_data.subject_scopes if s.type == SubjectType.USER.value]
        departments = [s for s in application_data.subject_scopes if s.type == SubjectType.DEPARTMENT.value]
        has_all_subject = SubjectType.ALL.value in {s.type for s in application_data.subject_scopes}
        if has_all_subject:
            form_data.append(BaseText(label="【可授权人员范围】", value="全员"))
        if users:
            user_values = [
                BaseDictStrValue(label="【可授权用户范围】: "),
                BaseDictStrValue(value=";".join([f"{u.id}({u.name})" for u in users])),
            ]
            form_data.append(BaseMultiLineText(value=user_values))
        if departments:
            department_values = [BaseDictStrValue(value=d.full_name) for d in departments]
            department_values.insert(0, BaseDictStrValue(label="【可授权的组织范围】: "))
            form_data.append(BaseMultiLineText(value=department_values))

        return cls(form_data=[d.dict() for d in form_data])


# ---------------------------- 权限交接申请 ----------------------------
class HandoverItemColumnValue(BaseModel):
    """权限交接详情表格每一列的值"""

    object_type: BaseDictStrValue
    name: BaseDictStrValue
    description: BaseDictStrValue
    expired_display: BaseDictStrValue

    @classmethod
    def from_group_info(cls, group_info: Dict[str, Any]):
        """从用户组信息创建"""
        expired_display = expired_at_display(group_info["expired_at"]) if group_info.get("expired_at") else "--"
        return cls(
            object_type=BaseDictStrValue(value="用户组"),
            name=BaseDictStrValue(value=group_info.get("name", "")),
            description=BaseDictStrValue(value=group_info.get("description", "--")),
            expired_display=BaseDictStrValue(value=expired_display),
        )

    @classmethod
    def from_custom_policy_info(cls, policy_info: Dict[str, Any]):
        """从自定义权限信息创建"""
        # 自定义权限是按系统分组的，需要展开每个权限
        values = []
        for policy_detail in policy_info.get("policy_details", []):
            expired_display = policy_detail.get("expired_display", "--")
            values.append(
                cls(
                    object_type=BaseDictStrValue(value="自定义权限"),
                    name=BaseDictStrValue(
                        value=f"{policy_info.get('name', '')} - {policy_detail.get('action_name', '')}"
                    ),
                    description=BaseDictStrValue(value="--"),
                    expired_display=BaseDictStrValue(value=expired_display),
                )
            )
        return values

    @classmethod
    def from_role_info(cls, role_info: Dict[str, Any]):
        """从角色信息创建"""
        return cls(
            object_type=BaseDictStrValue(value="角色"),
            name=BaseDictStrValue(value=role_info.get("name", "")),
            description=BaseDictStrValue(value=role_info.get("description", "--")),
            expired_display=BaseDictStrValue(value="--"),
        )

    @classmethod
    def from_template_info(cls, template_info: Dict[str, Any]):
        """从人员模板信息创建"""
        return cls(
            object_type=BaseDictStrValue(value="人员模板"),
            name=BaseDictStrValue(value=template_info.get("name", "")),
            description=BaseDictStrValue(value=template_info.get("description", "--")),
            expired_display=BaseDictStrValue(value="--"),
        )


class HandoverItemTable(BaseModel):
    """权限交接详情表格"""

    label: str = "交接详情"
    scheme: str = FormSchemeEnum.HANDOVER_TABLE.value  # 使用ticket_content_tpl.py中定义的scheme
    value: List[HandoverItemColumnValue]

    @classmethod
    def from_handover_info(cls, handover_info: Dict[str, Any]):
        """从交接信息创建表格"""
        values = []

        # 处理用户组
        groups = handover_info.get("group_ids")
        if groups:
            for group in groups:
                if isinstance(group, dict):
                    values.append(HandoverItemColumnValue.from_group_info(group))

        # 处理自定义权限
        custom_policies = handover_info.get("custom_policies")
        if custom_policies:
            for policy_info in custom_policies:
                if isinstance(policy_info, dict):
                    values.extend(HandoverItemColumnValue.from_custom_policy_info(policy_info))

        # 处理角色
        roles = handover_info.get("role_ids")
        if roles:
            for role in roles:
                if isinstance(role, dict):
                    values.append(HandoverItemColumnValue.from_role_info(role))

        # 处理人员模板
        templates = handover_info.get("subject_template_ids")
        if templates:
            for template in templates:
                if isinstance(template, dict):
                    values.append(HandoverItemColumnValue.from_template_info(template))

        # 如果没有找到任何值，则添加一个空行表示暂无数据
        if not values:
            values.append(
                HandoverItemColumnValue(
                    object_type=BaseDictStrValue(value="暂无数据"),
                    name=BaseDictStrValue(value="--"),
                    description=BaseDictStrValue(value="--"),
                    expired_display=BaseDictStrValue(value="--"),
                )
            )

        return cls(value=values)


class HandoverForm(BaseModel):
    """权限交接表单"""

    # Note: dont use `List[Union[BaseText, HandoverItemTable, BaseMultiLineText]]`
    # reason: https://pydantic-docs.helpmanual.io/usage/types/#unions
    form_data: List

    @classmethod
    def from_application(cls, application_data: HandoverApplicationContent):
        """从权限交接申请内容创建表单"""
        # 处理handover_info，将ID列表转换为详细信息
        handover_info = application_data.handover_info
        processed_handover_info = {}

        if handover_info:
            from backend.apps.handover.constants import HandoverObjectType
            from backend.apps.handover.validation import (
                GroupInfoProcessor,
                GustomPolicyProcessor,
                RoleInfoProcessor,
                SubjectTemplateProcessor,
            )

            HANDOVER_VALIDATOR_MAP = {
                HandoverObjectType.GROUP_IDS.value: GroupInfoProcessor,
                HandoverObjectType.CUSTOM_POLICIES.value: GustomPolicyProcessor,
                HandoverObjectType.ROLE_IDS.value: RoleInfoProcessor,
                HandoverObjectType.SUBJECT_TEMPLATE_IDS.value: SubjectTemplateProcessor,
            }

            # 转换原始ID列表为详细信息
            for key, value in handover_info.items():
                if not value:
                    continue
                try:
                    processor_class = HANDOVER_VALIDATOR_MAP.get(key)
                    if processor_class:
                        processor = processor_class(application_data.handover_from, value)
                        info = processor.get_info()
                        processed_handover_info[key] = info
                    else:
                        # 未知类型，保持原数据
                        processed_handover_info[key] = value
                except Exception:
                    # 如果处理失败，保持原数据
                    processed_handover_info[key] = value

        form_data = [
            # 基本信息
            BaseText(label="【交接人】", value=application_data.handover_from),
            BaseText(label="【被交接人】", value=application_data.handover_to),
            BaseText(label="【交接详情】"),
        ]

        # 添加交接详情表格
        if processed_handover_info:
            form_data.append(HandoverItemTable.from_handover_info(processed_handover_info))
        else:
            # 如果handover_info不存在，添加一个空表格
            form_data.append(HandoverItemTable(value=[]))

        return cls(form_data=[d.dict() for d in form_data])
