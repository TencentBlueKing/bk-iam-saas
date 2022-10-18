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
from aenum import LowerStrEnum, StrEnum, auto, skip
from django.utils.translation import gettext as _

from backend.util.enum import ChoicesEnum

ANY_ID = "*"
ADMIN_USER = "admin"
SYSTEM_ALL = "*"
ACTION_ALL = "*"
SUBJECT_ALL = "*"
SUBJECT_TYPE_ALL = "*"


class SubjectType(ChoicesEnum, LowerStrEnum):
    ALL = "*"
    USER = auto()
    DEPARTMENT = auto()
    GROUP = auto()

    _choices_labels = skip(((USER, _("用户")), (GROUP, _("用户组")), (DEPARTMENT, _("部门"))))


class SubjectRelationType(ChoicesEnum, LowerStrEnum):
    """用户的权限来源关系"""

    DEPARTMENT = auto()
    GROUP = auto()

    _choices_labels = skip(((GROUP, "用户组"), (DEPARTMENT, "部门")))


# ---------------------------------------------------------------------------------------------- #
# Resource Provider
# ---------------------------------------------------------------------------------------------- #
# fetch_instance_info 接口的批量限制
FETCH_MAX_LIMIT = 1000


# ---------------------------------------------------------------------------------------------- #
# Group Constants
# ---------------------------------------------------------------------------------------------- #
class GroupMemberType(ChoicesEnum, LowerStrEnum):
    USER = auto()
    DEPARTMENT = auto()

    _choices_labels = skip(((USER, "用户"), (DEPARTMENT, "部门")))


class GroupSaaSAttributeEnum(ChoicesEnum, LowerStrEnum):
    """用户组SaaS属性枚举"""

    READONLY = auto()

    _choices_labels = skip(((READONLY, "只读"),))


class GroupAttributeValueTypeEnum(ChoicesEnum, LowerStrEnum):
    """用户组SaaS属性值的数据类型"""

    String = auto()
    Boolean = auto()
    Integer = auto()


# 每个属性的值类型
GROUP_SAAS_ATTRIBUTE_VALUE_TYPE_MAP = {
    GroupSaaSAttributeEnum.READONLY.value: GroupAttributeValueTypeEnum.Boolean.value
}
# 每个属性的默认值
GROUP_SAAS_ATTRIBUTE_DEFAULT_VALUE_MAP = {GroupSaaSAttributeEnum.READONLY.value: False}


# ---------------------------------------------------------------------------------------------- #
# Policy Constants
# ---------------------------------------------------------------------------------------------- #
class SelectionMode(ChoicesEnum, LowerStrEnum):
    ALL = auto()
    INSTANCE = auto()
    ATTRIBUTE = auto()

    _choices_labels = skip(((ALL, _("实例与属性")), (INSTANCE, _("实例")), (ATTRIBUTE, _("属性"))))


# ---------------------------------------------------------------------------------------------- #
# Role Constants
# ---------------------------------------------------------------------------------------------- #
class RoleType(ChoicesEnum, LowerStrEnum):
    STAFF = auto()
    SUPER_MANAGER = auto()
    SYSTEM_MANAGER = auto()
    RATING_MANAGER = auto()
    SUBSET_MANAGER = auto()

    _choices_labels = skip(
        (
            (STAFF, "个人用户"),
            (SUPER_MANAGER, "超级管理员"),
            (SYSTEM_MANAGER, "系统管理员"),
            (RATING_MANAGER, "分级管理员"),
            (SUBSET_MANAGER, "子集管理员"),
        )
    )


class RoleScopeType(ChoicesEnum, LowerStrEnum):
    AUTHORIZATION = auto()
    SUBJECT = auto()

    _choices_labels = skip(((AUTHORIZATION, "系统操作"), (SUBJECT, "授权对象")))


class RoleRelatedObjectType(ChoicesEnum, LowerStrEnum):
    TEMPLATE = auto()
    GROUP = auto()

    _choices_labels = skip(((TEMPLATE, "权限模板"), (GROUP, "用户组")))


class RoleScopeSubjectType(ChoicesEnum, LowerStrEnum):
    USER = auto()
    DEPARTMENT = auto()
    ANY = "*"

    _choices_labels = skip(((USER, "用户"), (DEPARTMENT, "部门"), (ANY, "任意")))


class RoleSourceTypeEnum(ChoicesEnum, LowerStrEnum):
    """角色创建来源"""

    API = auto()
    WEB = auto()
    DEFAULT_INIT = auto()

    _choices_labels = skip(((API, "api"), (WEB, "web"), (DEFAULT_INIT, "default init")))


class PermissionCodeEnum(ChoicesEnum, LowerStrEnum):
    MANAGE_GROUP = auto()
    MANAGE_TEMPLATE = auto()
    MANAGE_SUPER_MANAGER_MEMBER = auto()
    MANAGE_SYSTEM_MANAGER_MEMBER = auto()
    CREATE_RATING_MANAGER = auto()
    MANAGE_RATING_MANAGER = auto()
    TRANSFER_GROUP = auto()
    AUDIT = auto()
    CONFIGURE_APPROVAL_PROCESS = auto()
    CONFIGURE_MANAGER = auto()
    MANAGE_SYSTEM_SETTING = auto()
    MANAGE_GLOBAL_SETTING = auto()
    MANAGE_ORGANIZATION = auto()
    MANAGE_COMMON_ACTION = auto()
    VIEW_AUTHORIZED_SUBJECTS = auto()
    MANAGE_API_WHITE_LIST = auto()
    MANAGE_LONG_TASK = auto()
    CREATE_SUBSET_MANAGER = auto()
    MANAGE_SUBSET_MANAGER = auto()
    TRANSFER_GROUP_BY_RATING_MANAGER = auto()


# ---------------------------------------------------------------------------------------------- #
# Template Constants
# ---------------------------------------------------------------------------------------------- #
class TemplatePreUpdateStatus(ChoicesEnum, LowerStrEnum):
    WAITING = auto()
    RUNNING = auto()
    FINISHED = auto()

    _choices_labels = skip(((RUNNING, "运行中"), (WAITING, "等待中")))


# ---------------------------------------------------------------------------------------------- #
# Application & Approval Constants
# ---------------------------------------------------------------------------------------------- #
class ApplicationTypeEnum(ChoicesEnum, LowerStrEnum):
    GRANT_ACTION = auto()
    RENEW_ACTION = auto()
    JOIN_GROUP = auto()
    RENEW_GROUP = auto()
    JOIN_RATING_MANAGER = auto()
    CREATE_RATING_MANAGER = auto()
    UPDATE_RATING_MANAGER = auto()
    GRANT_TEMPORARY_ACTION = auto()

    _choices_labels = skip(
        (
            (GRANT_ACTION, "自定义权限申请"),
            (RENEW_ACTION, "自定义权限续期"),
            (JOIN_GROUP, "加入用户组"),
            (RENEW_GROUP, "用户组续期"),
            (JOIN_RATING_MANAGER, "加入分级管理员"),
            (CREATE_RATING_MANAGER, "创建分级管理员"),
            (UPDATE_RATING_MANAGER, "修改分级管理员"),
            (GRANT_TEMPORARY_ACTION, "临时权限申请"),
        )
    )


# IAM支持的审批流程节点类型
class ProcessorNodeTypeEnum(LowerStrEnum):
    SUPER_MANAGER = auto()
    SYSTEM_MANAGER = auto()
    RATING_MANAGER = auto()
    INSTANCE_APPROVER = auto()


# 每一种申请单据，对应的审批流程节点可以支持的ROLE
APPLICATION_SUPPORT_PROCESSOR_ROLE_MAP = {
    ApplicationTypeEnum.GRANT_ACTION.value: (
        ProcessorNodeTypeEnum.SUPER_MANAGER.value,
        ProcessorNodeTypeEnum.SYSTEM_MANAGER.value,
        ProcessorNodeTypeEnum.INSTANCE_APPROVER.value,
    ),
    ApplicationTypeEnum.JOIN_GROUP.value: (
        ProcessorNodeTypeEnum.SUPER_MANAGER.value,
        ProcessorNodeTypeEnum.RATING_MANAGER.value,
    ),
    ApplicationTypeEnum.JOIN_RATING_MANAGER.value: (
        ProcessorNodeTypeEnum.SUPER_MANAGER.value,
        ProcessorNodeTypeEnum.RATING_MANAGER.value,
    ),
    ApplicationTypeEnum.CREATE_RATING_MANAGER.value: (ProcessorNodeTypeEnum.SUPER_MANAGER.value,),
    ApplicationTypeEnum.UPDATE_RATING_MANAGER.value: (ProcessorNodeTypeEnum.SUPER_MANAGER.value,),
}


class ProcessorSourceEnum(ChoicesEnum, StrEnum):
    """审批流程节点里的处理者来源"""

    IAM = auto()
    OTHER = auto()


# 对于IAM来源的处理者，IAM有固定支持的处理者类型
IAM_SUPPORT_PROCESSOR_TYPES = [
    ProcessorNodeTypeEnum.SUPER_MANAGER.value,
    ProcessorNodeTypeEnum.SYSTEM_MANAGER.value,
    ProcessorNodeTypeEnum.RATING_MANAGER.value,
    ProcessorNodeTypeEnum.INSTANCE_APPROVER.value,
]


# 支持配置默认流程的申请审批类型
DEFAULT_PROCESS_SUPPORT_APPLICATION_TYPES = [
    ApplicationTypeEnum.GRANT_ACTION.value,
    ApplicationTypeEnum.JOIN_GROUP.value,
    ApplicationTypeEnum.CREATE_RATING_MANAGER.value,
]


class ApplicationStatus(ChoicesEnum, LowerStrEnum):
    """申请单状态"""

    PENDING = auto()
    PASS = auto()
    REJECT = auto()
    CANCELLED = auto()

    _choices_labels = skip(((PENDING, _("审批中")), (PASS, _("通过")), (REJECT, _("拒绝")), (CANCELLED, _("已取消"))))


DEAULT_RESOURCE_GROUP_ID = "00000000000000000000000000000000"


# ---------------------------------------------------------------------------------------------- #
# Policy environment
# ---------------------------------------------------------------------------------------------- #
class PolicyEnvTypeEnum(ChoicesEnum, LowerStrEnum):
    PERIOD_DAILY = auto()

    _choices_labels = skip(((PERIOD_DAILY, _("时间")),))


class PolicyEnvConditionTypeEnum(ChoicesEnum, LowerStrEnum):
    TZ = auto()
    HMS = auto()
    WEEKDAY = auto()

    _choices_labels = skip(
        (
            (TZ, _("时区")),
            (HMS, _("时分秒")),
            (WEEKDAY, _("WEEKDAY")),
        )
    )


class WeekDayEnum(ChoicesEnum):
    SUN = 0
    MON = 1
    TUE = 2
    WED = 3
    THU = 4
    FRI = 5
    SAT = 6

    _choices_labels = skip(
        (
            (SUN, _("星期天")),
            (MON, _("星期一")),
            (TUE, _("星期二")),
            (WED, _("星期三")),
            (THU, _("星期四")),
            (FRI, _("星期五")),
            (SAT, _("星期六")),
        )
    )


# ---------------------------------------------------------------------------------------------- #
# Model Change Event
# ---------------------------------------------------------------------------------------------- #
class ModelChangeEventTypeEnum(ChoicesEnum, LowerStrEnum):
    ActionPolicyDeleted = "action_policy_deleted"
    ActionDeleted = "action_deleted"


class ModelChangeEventStatusEnum(ChoicesEnum, LowerStrEnum):
    Pending = auto()
    Finished = auto()


# ---------------------------------------------------------------------------------------------- #
# UniversalPolicy
# ---------------------------------------------------------------------------------------------- #
class AuthTypeEnum(ChoicesEnum, LowerStrEnum):
    RBAC = auto()
    ABAC = auto()
    ALL = auto()
    NONE = auto()

    _choices_labels = skip(
        (
            (RBAC, "RBAC"),
            (ABAC, "ABAC"),
            (ALL, "ALL"),
            (NONE, "NONE"),
        )
    )


class AbacPolicyChangeType(ChoicesEnum, LowerStrEnum):
    CREATED = auto()
    UPDATED = auto()
    DELETED = auto()
    NONE = auto()
