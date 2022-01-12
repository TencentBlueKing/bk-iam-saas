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
from typing import Any, Dict, List, Union

from pydantic import BaseModel, Field

from backend.util.model import ListModel

from ..constants import ApplicationStatus, ApplicationTypeEnum, SubjectType


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
    type: ApplicationTypeEnum
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


class ApplicationResourceInstance(BaseModel):
    # 资源类型
    type: str
    # 对应配置的拓扑或实例
    path: List[List[ApplicationResourceInstancePathNode]]
    # 资源类型名称
    name: str
    name_en: str = ""


class ApplicationResourceAttributeValue(BaseModel):
    id: Any
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


class ApplicationResourceGroupList(ListModel):
    __root__: List[ApplicationResourceGroup]


class ApplicationPolicyInfo(BaseModel):
    """申请内容里的策略"""

    action_id: str = Field(alias="id")
    resource_groups: ApplicationResourceGroupList
    expired_at: int = 0
    expired_display: str = ""
    # Action名称
    name: str
    name_en: str = ""

    class Config:
        # 当字段设置别名时，初始化支持原名或别名传入，False时，则只能是别名传入，同时配合dict(by_alias=True)可控制字典数据时的key是否别名
        allow_population_by_field_name = True


class GrantActionApplicationContent(BaseModel):
    """自定义权限申请内容"""

    system: ApplicationSystem
    policies: List[ApplicationPolicyInfo] = Field(alias="actions")

    class Config:
        # 当字段设置别名时，初始化支持原名或别名传入，False时，则只能是别名传入，同时配合dict(by_alias=True)可控制字典数据时的key是否别名
        allow_population_by_field_name = True


class GrantActionApplicationData(ApplicationDataBaseInfo):
    """自定义申请单据所有数据"""

    content: GrantActionApplicationContent

    def raw_content(self) -> Dict:
        """返回原生申请内容，保存到DB里的"""
        return self.content.dict(by_alias=True)


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


class GroupApplicationContent(BaseModel):
    """加入用户组的申请内容"""

    groups: List[ApplicationGroupInfo]


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
                group.dict(include={"id", "name", "description", "expired_at"}) for group in self.content.groups
            ],
        }
        return data


# 申请加入用户组数据内容数据结构 End #


# 申请创建/更新分级管理员数据结构 Start #
class ApplicationSubject(BaseModel):
    type: SubjectType
    id: str
    name: str
    full_name: str = ""  # 仅仅部门有全名


class ApplicationAuthorizationScope(GrantActionApplicationContent):
    """分级管理员可授权范围"""

    pass


class GradeManagerApplicationContent(BaseModel):
    """申请创建或更新分级管理员内容"""

    id: int = 0
    name: str
    description: str
    members: List[ApplicationSubject]
    subject_scopes: List[ApplicationSubject]
    authorization_scopes: List[ApplicationAuthorizationScope]


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
        }

        return data


# 申请创建/更新分级管理员数据结构 End #


# 定义新类型，几种单据的联合, 这里不使用NewType，不然mypy检查过不了
TypeUnionApplicationData = Union[GrantActionApplicationData, GroupApplicationData, GradeManagerApplicationData]
