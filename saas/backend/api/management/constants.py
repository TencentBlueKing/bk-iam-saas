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


class ManagementAPIEnum(BaseAPIEnum):
    """这里的枚举的是每个具体管理类API"""

    # 分级管理员
    GRADE_MANAGER_LIST = auto()
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
    GROUP_POLICY_LIST = auto()
    GROUP_POLICY_GRANT = auto()
    GROUP_POLICY_REVOKE = auto()
    GROUP_POLICY_DELETE = auto()
    # 用户相关
    USER_ROLE_LIST = auto()
    USER_ROLE_GROUP_LIST = auto()
    # 用户组申请单
    GROUP_APPLICATION_CREATE = auto()

    # V2 API
    # 用户组
    V2_GROUP_LIST = auto()
    V2_GROUP_BATCH_CREATE = auto()
    V2_GROUP_UPDATE = auto()
    V2_GROUP_DELETE = auto()
    # 用户组成员
    V2_GROUP_MEMBER_LIST = auto()
    V2_GROUP_MEMBER_ADD = auto()
    V2_GROUP_MEMBER_DELETE = auto()
    V2_GROUP_MEMBER_EXPIRED_AT_UPDATE = auto()
    # 用户组权限
    V2_GROUP_POLICY_GRANT = auto()
    V2_GROUP_POLICY_REVOKE = auto()
    V2_GROUP_POLICY_DELETE = auto()
    V2_GROUP_POLICY_ACTION_LIST = auto()
    # 用户组申请单
    V2_GROUP_APPLICATION_CREATE = auto()
    V2_GROUP_APPLICATION_RENEW = auto()
    # 用户组归属
    V2_USER_GROUPS_BELONG_CHECK = auto()
    V2_DEPARTMENT_GROUPS_BELONG_CHECK = auto()
    # 分级管理员
    V2_GRADE_MANAGER_CREATE = auto()
    V2_GRADE_MANAGER_UPDATE = auto()
    V2_GRADE_MANAGER_DELETE = auto()
    V2_GRADE_MANAGER_DETAIL = auto()
    V2_GRADE_MANAGER_APPLICATION_CREATE = auto()
    V2_GRADE_MANAGER_APPLICATION_UPDATE = auto()
    # 子集管理员
    V2_SUBSET_MANAGER_CREATE = auto()
    V2_SUBSET_MANAGER_LIST = auto()
    V2_SUBSET_MANAGER_DETAIL = auto()
    V2_SUBSET_MANAGER_UPDATE = auto()
    V2_SUBSET_MANAGER_DELETE = auto()
    # 审批
    V2_APPLICATION_APPROVAL = auto()
    V2_APPLICATION_CANCEL = auto()

    _choices_labels = skip(
        (
            # 分级管理员
            (GRADE_MANAGER_LIST, "获取分级管理员列表"),
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
            (GROUP_POLICY_REVOKE, "回收用户组权限"),
            (GROUP_POLICY_DELETE, "删除用户组策略"),
            # 用户相关
            (USER_ROLE_LIST, "获取用户加入的分级管理员列表"),
            (USER_ROLE_GROUP_LIST, "获取某个分级管理员下用户加入的用户组列表"),
            # 用户组申请单
            (GROUP_APPLICATION_CREATE, "创建用户组申请单"),
            # V2
            # 用户组
            (V2_GROUP_LIST, "[V2]用户组列表"),
            (V2_GROUP_BATCH_CREATE, "[V2]批量创建用户组"),
            (V2_GROUP_UPDATE, "[V2]更新用户组"),
            (V2_GROUP_DELETE, "[V2]删除用户组"),
            # 用户组成员
            (V2_GROUP_MEMBER_LIST, "[V2]获取用户组成员列表"),
            (V2_GROUP_MEMBER_ADD, "[V2]添加用户组成员"),
            (V2_GROUP_MEMBER_DELETE, "[V2]删除用户组成员"),
            (V2_GROUP_MEMBER_EXPIRED_AT_UPDATE, "[V2]用户组成员续期"),
            # 用户组权限
            (V2_GROUP_POLICY_GRANT, "[V2]授权用户组"),
            (V2_GROUP_POLICY_REVOKE, "[V2]回收用户组权限"),
            (V2_GROUP_POLICY_DELETE, "[V2]删除用户组策略"),
            (V2_GROUP_POLICY_ACTION_LIST, "[V2]用户组策略对应操作列表"),
            # 用户组申请单
            (V2_GROUP_APPLICATION_CREATE, "[V2]创建用户组申请单"),
            (V2_GROUP_APPLICATION_RENEW, "[V2]用户组续期申请单"),
            # 用户组归属
            (V2_USER_GROUPS_BELONG_CHECK, "[V2]判断用户与用户组归属"),
            (V2_DEPARTMENT_GROUPS_BELONG_CHECK, "[V2]判断部门与用户组归属"),
            # 分级管理员
            (V2_GRADE_MANAGER_DETAIL, "[V2]分级管理员详情"),
            (V2_GRADE_MANAGER_CREATE, "[V2]新建分级管理员"),
            (V2_GRADE_MANAGER_UPDATE, "[V2]更新分级管理员"),
            (V2_GRADE_MANAGER_APPLICATION_CREATE, "[V2]创建分级管理员创建申请单"),
            (V2_GRADE_MANAGER_APPLICATION_UPDATE, "[V2]创建分级管理员更新申请单"),
            # 子集管理员
            (V2_SUBSET_MANAGER_CREATE, "[V2]创建子集管理员"),
            (V2_SUBSET_MANAGER_LIST, "[V2]子集管理员列表"),
            # 审批
            (V2_APPLICATION_APPROVAL, "[V2]申请单审批通知"),
            # 申请单取消
            (V2_APPLICATION_CANCEL, "[V2]申请单取消"),
        )
    )


class VerifyAPIObjectTypeEnum(ChoicesEnum, LowerStrEnum):
    """API认证和鉴权时的角色对象类型"""

    ROLE = auto()
    GROUP = auto()


class VerifyApiParamLocationEnum(ChoicesEnum, LowerStrEnum):
    ROLE_IN_PATH = auto()
    GROUP_IN_PATH = auto()
    SYSTEM_IN_BODY = auto()
    SYSTEM_IN_QUERY = auto()
    GROUP_IDS_IN_BODY = auto()
    SYSTEM_IN_PATH = auto()
    GROUP_IDS_IN_QUERY = auto()

    _choices_labels = skip(
        (
            (ROLE_IN_PATH, "在URL里的role id参数"),
            (GROUP_IN_PATH, "在URL里的group id参数"),
            (SYSTEM_IN_BODY, "在body data里的system参数"),
            (SYSTEM_IN_QUERY, "在get请求query里的system参数"),
            (GROUP_IDS_IN_BODY, "在body data里的groups_ids参数"),
            (SYSTEM_IN_PATH, "在路径里的system参数"),
            (GROUP_IDS_IN_QUERY, "在get请求query里的groups_ids参数"),
        )
    )


VerifyAPIParamSourceToObjectTypeMap = {
    VerifyApiParamLocationEnum.ROLE_IN_PATH.value: VerifyAPIObjectTypeEnum.ROLE.value,
    VerifyApiParamLocationEnum.GROUP_IN_PATH.value: VerifyAPIObjectTypeEnum.GROUP.value,
}

# 主要用于ViewSet里配置了ManagementAPIPermission，但是对于一些请求不需要对API鉴权的，可在management_api_permission里配置忽略鉴权
IGNORE_VERIFY_API_CONFIG = ("ignore", "ignore")
