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
from collections import Counter
from typing import Any, Dict, List, Union

from pydantic import ConfigDict, BaseModel, Field

from backend.service.models.subject import Applicant
from backend.util.model import ListModel

from ..constants import ApplicationStatus, ApplicationType, SensitivityLevel, SubjectType


class ApplicationTicket(BaseModel):
    """单据信息"""

    sn: str
    status: ApplicationStatus
    url: str = ""


class ApplicantDepartment(BaseModel):
    """申请者部门信息"""

    id: int
    name: str
    full_name: str


class ApplicantInfo(BaseModel):
    """申请者信息"""

    username: str
    organization: List[ApplicantDepartment]


class ApplicationDataBaseInfo(BaseModel):
    type: ApplicationType
    # 申请者信息
    applicant_info: ApplicantInfo
    # 申请原因
    reason: str


# 自定义权限申请数据内容数据结构 Start #
class ApplicationSystem(BaseModel):
    """申请内容里的系统"""

    id: str
    name: str
    name_en: str = ""


class ApplicationResourceInstancePathNode(BaseModel):
    # 实例ID
    id: str
    # 资源类型系统
    system_id: str = ""  # NOTE 兼容一下, 早期的policy数据中可能没有system_id
    # 资源类型
    type: str
    # 资源实例名称
    name: str = ""
    # 资源类型名称
    type_name: str = ""
    type_name_en: str = ""


class ApplicationResourceInstancePathList(ListModel[ApplicationResourceInstancePathNode]):
    pass


class ApplicationResourceInstance(BaseModel):
    # 资源类型
    type: str
    # 对应配置的拓扑或实例
    path: List[ApplicationResourceInstancePathList]
    # 资源类型名称
    name: str
    name_en: str = ""


class ApplicationResourceAttributeValue(BaseModel):
    id: Any = None
    name: str


class ApplicationResourceAttribute(BaseModel):
    id: str
    name: str
    values: List[ApplicationResourceAttributeValue]


class ApplicationResourceCondition(BaseModel):
    instances: List[ApplicationResourceInstance]
    attributes: List[ApplicationResourceAttribute]


class ApplicationRelatedResource(BaseModel):
    """申请内容里的策略的关联的资源类型"""

    # 资源类型的系统
    system_id: str
    # 资源类型
    type: str
    # 对应资源的范围
    condition: List[ApplicationResourceCondition]
    # 资源类型名称
    name: str
    name_en: str = ""


class ApplicationEnvironValue(BaseModel):
    """环境属性值"""

    name: str = ""
    value: str


class ApplicationEnvironCondition(BaseModel):
    """环境属性条件"""

    type: str
    values: List[ApplicationEnvironValue]


class ApplicationEnvironment(BaseModel):
    """环境属性"""

    type: str
    condition: List[ApplicationEnvironCondition]


class ApplicationResourceGroup(BaseModel):
    id: str
    related_resource_types: List[ApplicationRelatedResource]
    environments: List[ApplicationEnvironment]


class ApplicationResourceGroupList(ListModel[ApplicationResourceGroup]):
    pass


class ApplicationPolicyInfo(BaseModel):
    """申请内容里的策略"""

    action_id: str = Field(alias="id")
    resource_groups: ApplicationResourceGroupList
    expired_at: int = 0
    expired_display: str = ""
    # Action名称
    name: str
    name_en: str = ""
    sensitivity_level: str = ""
    model_config = ConfigDict(populate_by_name=True)


class GrantActionApplicationContent(BaseModel):
    """自定义权限申请内容"""

    system: ApplicationSystem
    policies: List[ApplicationPolicyInfo] = Field(alias="actions")
    applicants: List[Applicant]
    model_config = ConfigDict(populate_by_name=True)


class GrantActionApplicationData(ApplicationDataBaseInfo):
    """自定义申请单据所有数据"""

    content: GrantActionApplicationContent

    def raw_content(self) -> Dict:
        """返回原生申请内容，保存到DB里的"""
        data = self.content.dict(by_alias=True)
        data["action_sensitivity_level"] = self.get_action_sensitivity_level_field()
        return data

    def get_action_sensitivity_level_field(self) -> str:
        comments = []

        level_count = Counter(obj.sensitivity_level for obj in self.content.policies)
        for level in sorted(level_count.keys(), reverse=True):
            comments.append("{}个{}敏感等级操作".format(level_count[level], SensitivityLevel.get_choice_label(level)))

        return "包含" + ", ".join(comments)

    def get_applicants_field(self) -> str:
        return ", ".join(
            [
                "{}: {}({})".format("用户" if u.type == SubjectType.USER.value else "部门", u.display_name, u.id)
                for u in self.content.applicants
            ]
        )


# 自定义权限申请数据内容数据结构 End #


# 申请加入用户组数据内容数据结构 Start #
class ApplicationGroupPermTemplate(BaseModel):
    id: int
    name: str
    system: ApplicationSystem
    policies: List[ApplicationPolicyInfo]


class ApplicationGroupInfo(BaseModel):
    """申请内容的用户组信息"""

    id: int
    name: str
    description: str
    # 申请加入用户组的有效期
    expired_at: int = 0
    expired_display: str = ""
    # 用户组自身的权限信息(包含权限模板和自定义权限)
    templates: List[ApplicationGroupPermTemplate]
    # 管理员名称
    role_name: str = ""
    # 最高敏感等级
    highest_sensitivity_level: str = ""

    def __init__(self, **data: Any):
        super().__init__(**data)

        policy_sensitivity_levels = [p.sensitivity_level for t in self.templates for p in t.policies]
        self.highest_sensitivity_level = (
            max(policy_sensitivity_levels) if policy_sensitivity_levels else SensitivityLevel.L1.value  # type: ignore
        )


class GroupApplicationContent(BaseModel):
    """加入用户组的申请内容"""

    groups: List[ApplicationGroupInfo]
    applicants: List[Applicant]


class GroupApplicationData(ApplicationDataBaseInfo):
    """加入用户组的申请内容"""

    content: GroupApplicationContent

    def raw_content(self) -> Dict:
        """返回原生申请内容，保存到DB里的"""
        # 由于申请加入用户组至少要一个组，而且多个组的加入有效期是一样的，所以取第一个即可
        first_group = self.content.groups[0]
        data = {
            "expired_at": first_group.expired_at,
            "expired_display": first_group.expired_display,
            "groups": [
                group.dict(include={"id", "name", "description", "expired_at", "highest_sensitivity_level"})
                for group in self.content.groups
            ],
            "applicants": [one.dict() for one in self.content.applicants],
            "action_sensitivity_level": self.get_action_sensitivity_level_field(),
        }
        return data

    def get_action_sensitivity_level_field(self) -> str:
        comments = []

        level_count = Counter(obj.highest_sensitivity_level for obj in self.content.groups)
        for level in sorted(level_count.keys(), reverse=True):
            comments.append(
                "最高敏感等级 {} 的用户组{}个".format(SensitivityLevel.get_choice_label(level), level_count[level]))

        return "包含" + ", ".join(comments)

    def get_applicants_field(self) -> str:
        return ", ".join(
            [
                "{}: {}({})".format("用户" if u.type == SubjectType.USER.value else "部门", u.display_name, u.id)
                for u in self.content.applicants
            ]
        )


# 申请加入用户组数据内容数据结构 End #


# 申请创建/更新分级管理员数据结构 Start #
class ApplicationSubject(BaseModel):
    type: SubjectType
    id: str
    name: str
    full_name: str = ""  # 仅仅部门有全名


class ApplicationAuthorizationScope(BaseModel):
    """分级管理员可授权范围"""

    system: ApplicationSystem
    policies: List[ApplicationPolicyInfo] = Field(alias="actions")
    model_config = ConfigDict(populate_by_name=True)


class GradeManagerApplicationContent(BaseModel):
    """申请创建或更新分级管理员内容"""

    id: int = 0
    name: str
    description: str
    members: List[ApplicationSubject]
    subject_scopes: List[ApplicationSubject]
    authorization_scopes: List[ApplicationAuthorizationScope]
    sync_perm: bool = False
    group_name: str = ""


class GradeManagerApplicationData(ApplicationDataBaseInfo):
    """申请创建或更新分级管理员内容"""

    content: GradeManagerApplicationContent

    def raw_content(self) -> Dict:
        """返回原生申请内容，保存到DB里的"""
        data = {
            "id": self.content.id,
            "name": self.content.name,
            "description": self.content.description,
            "members": [member.id for member in self.content.members],
            "subject_scopes": [subject.dict(include={"type", "id"}) for subject in self.content.subject_scopes],
            "authorization_scopes": [scope.dict(by_alias=True) for scope in self.content.authorization_scopes],
            "sync_perm": self.content.sync_perm,
            "group_name": self.content.group_name,
        }

        return data


# 申请创建/更新分级管理员数据结构 End #


# 定义新类型，几种单据的联合, 这里不使用NewType，不然mypy检查过不了
TypeUnionApplicationData = Union[GrantActionApplicationData, GroupApplicationData, GradeManagerApplicationData]
