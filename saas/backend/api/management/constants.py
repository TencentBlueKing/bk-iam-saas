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

from backend.util.enum import ChoicesEnum


class ManagementAPIEnum(ChoicesEnum, LowerStrEnum):
    """这里的枚举的是每个具体管理类API"""

    # 分级管理员
    GRADE_MANAGER_CREATE = auto()
    GRADE_MANAGER_UPDATE = auto()
    GRADE_MANAGER_MEMBER_LIST = auto()
    GRADE_MANAGER_MEMBER_ADD = auto()
    GRADE_MANAGER_MEMBER_DELETE = auto()
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
    # 用户相关
    USER_ROLE_LIST = auto()
    USER_ROLE_GROUP_LIST = auto()
    # 用户组申请单
    GROUP_APPLICATION_CREATE = auto()

    _choices_labels = skip(
        (
            # 分级管理员
            (GRADE_MANAGER_CREATE, "新建分级管理员"),
            (GRADE_MANAGER_UPDATE, "更新分级管理员"),
            (GRADE_MANAGER_MEMBER_LIST, "获取分级管理员成员列表"),
            (GRADE_MANAGER_MEMBER_ADD, "添加分级管理员成员"),
            (GRADE_MANAGER_MEMBER_DELETE, "删除分级管理员成员"),
            # 用户组
            (GROUP_LIST, "获取用户组列表"),
            (GROUP_BATCH_CREATE, "批量创建用户组"),
            (GROUP_UPDATE, "更新用户组"),
            (GROUP_DELETE, "删除用户组"),
            # 用户组成员
            (GROUP_MEMBER_LIST, "获取用户组成员列表"),
            (GROUP_MEMBER_ADD, "添加用户组成员"),
            (GROUP_MEMBER_DELETE, "删除用户组成员"),
            # 用户组权限
            (GROUP_POLICY_GRANT, "授权用户组"),
            # 用户相关
            (USER_ROLE_LIST, "获取用户加入的分级管理员列表"),
            (USER_ROLE_GROUP_LIST, "获取某个分级管理员下用户加入的用户组列表"),
            # 用户组申请单
            (GROUP_APPLICATION_CREATE, "创建用户组申请单"),
        )
    )


class VerifyAPIObjectTypeEnum(ChoicesEnum, LowerStrEnum):
    """API认证和鉴权时的角色对象类型"""

    ROLE = auto()
    GROUP = auto()


class VerifyAPIParamLocationEnum(ChoicesEnum, LowerStrEnum):
    ROLE_IN_PATH = auto()
    GROUP_IN_PATH = auto()
    SYSTEM_IN_BODY = auto()
    SYSTEM_IN_QUERY = auto()
    GROUP_IDS_IN_BODY = auto()

    _choices_labels = skip(
        (
            (ROLE_IN_PATH, "在URL里的role id参数"),
            (GROUP_IN_PATH, "在URL里的group id参数"),
            (SYSTEM_IN_BODY, "在body data里的system参数"),
            (SYSTEM_IN_QUERY, "在get请求query里的system参数"),
            (GROUP_IDS_IN_BODY, "在body data里的groups_ids参数"),
        )
    )


VerifyAPIParamSourceToObjectTypeMap = {
    VerifyAPIParamLocationEnum.ROLE_IN_PATH.value: VerifyAPIObjectTypeEnum.ROLE.value,
    VerifyAPIParamLocationEnum.GROUP_IN_PATH.value: VerifyAPIObjectTypeEnum.GROUP.value,
}

# 主要用于ViewSet里配置了ManagementAPIPermission，但是对于一些请求不需要对API鉴权的，可在management_api_permission里配置忽略鉴权
IGNORE_VERIFY_API_CONFIG = ("ignore", "ignore")
