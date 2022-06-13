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
from aenum import auto, skip

from backend.api.constants import BaseAPIEnum


class AdminAPIEnum(BaseAPIEnum):
    """枚举每个Admin API"""

    # 用户组
    GROUP_LIST = auto()
    # 用户组成员
    GROUP_MEMBER_LIST = auto()
    # Subject
    SUBJECT_JOINED_GROUP_LIST = auto()

    # System
    SYSTEM_LIST = auto()

    # 角色
    ROLE_SUPER_MANAGER_MEMBER_LIST = auto()
    ROLE_SYSTEM_MANAGER_MEMBER_LIST = auto()

    _choices_labels = skip(
        (
            (SYSTEM_LIST, "获取系统列表"),
            (GROUP_LIST, "获取用户组列表"),
            (GROUP_MEMBER_LIST, "获取用户组成员列表"),
            (SUBJECT_JOINED_GROUP_LIST, "获取Subject加入的用户组列表"),
            (ROLE_SUPER_MANAGER_MEMBER_LIST, "获取超级管理员成员列表"),
            (ROLE_SYSTEM_MANAGER_MEMBER_LIST, "获取系统管理员及成员列表"),
        )
    )
