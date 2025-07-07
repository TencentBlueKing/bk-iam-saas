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
from aenum import LowerStrEnum, auto, skip

from backend.api.constants import BaseAPIEnum
from backend.util.enum import ChoicesEnum


class AdminAPIEnum(BaseAPIEnum):
    """枚举每个Admin API"""

    # 用户组
    GROUP_LIST = auto()
    GROUP_BATCH_CREATE = auto()
    GROUP_UPDATE = auto()
    GROUP_DELETE = auto()

    # 用户组成员
    GROUP_MEMBER_LIST = auto()
    GROUP_MEMBER_ADD = auto()
    GROUP_MEMBER_DELETE = auto()

    # 用户组权限
    GROUP_POLICY_GRANT = auto()

    # 模板
    TEMPLATE_LIST = auto()
    TEMPLATE_CREATE = auto()

    # Subject
    SUBJECT_JOINED_GROUP_LIST = auto()
    SUBJECT_ROLE_LIST = auto()

    # System
    SYSTEM_LIST = auto()
    SYSTEM_PROVIDER_CONFIG_LIST = auto()

    # 角色
    ROLE_SUPER_MANAGER_MEMBER_LIST = auto()
    ROLE_SYSTEM_MANAGER_MEMBER_LIST = auto()

    # 审计
    AUDIT_EVENT_LIST = auto()

    # 冻结
    SUBJECT_FREEZE_UNFREEZE = auto()

    # 清理
    SUBJECT_PERMISSION_CLEANUP = auto()

    # 是否有权限数据
    SUBJECT_PERMISSION_EXISTS = auto()

    # 用户组权限列表
    SUBJECT_GROUP_PERMISSION = auto()

    # 自定义权限列表
    SUBJECT_CUSTOM_PERMISSION = auto()

    # 管理权限查询
    SUBJECT_MANAGEMENT_PERMISSION = auto()

    _choices_labels = skip(
        (
            (SYSTEM_LIST, "获取系统列表"),
            (SYSTEM_PROVIDER_CONFIG_LIST, "获取系统回调信息"),
            (GROUP_LIST, "获取用户组列表"),
            (GROUP_BATCH_CREATE, "批量创建用户组"),
            (GROUP_UPDATE, "更新用户组"),
            (GROUP_DELETE, "删除用户组"),
            (GROUP_MEMBER_LIST, "获取用户组成员列表"),
            (GROUP_MEMBER_ADD, "添加用户组成员"),
            (GROUP_MEMBER_DELETE, "移除用户组成员"),
            (GROUP_POLICY_GRANT, "授权用户组"),
            (TEMPLATE_CREATE, "新建模板"),
            (SUBJECT_JOINED_GROUP_LIST, "获取Subject加入的用户组列表"),
            (SUBJECT_ROLE_LIST, "获取Subject角色列表"),
            (ROLE_SUPER_MANAGER_MEMBER_LIST, "获取超级管理员成员列表"),
            (ROLE_SYSTEM_MANAGER_MEMBER_LIST, "获取系统管理员及成员列表"),
            (AUDIT_EVENT_LIST, "获取审计事件列表"),
            (SUBJECT_FREEZE_UNFREEZE, "冻结/解冻Subject"),
            (SUBJECT_PERMISSION_CLEANUP, "权限清理"),
            (SUBJECT_PERMISSION_EXISTS, "权限是否存在"),
            (SUBJECT_GROUP_PERMISSION, "用户组权限列表"),
            (SUBJECT_CUSTOM_PERMISSION, "自定义权限列表"),
            (SUBJECT_MANAGEMENT_PERMISSION, "管理权限查询"),
        )
    )


class VerifyApiParamLocationEnum(ChoicesEnum, LowerStrEnum):
    GROUP_IN_PATH = auto()

    _choices_labels = skip(((GROUP_IN_PATH, "在URL里的group id参数"),))
