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


class NewbieSceneEnum(ChoicesEnum, LowerStrEnum):
    """新手指引场景枚举"""

    RATING_MANAGER_AUTHORIZATION_SCOPE = auto()
    RATING_MANAGER_SUBJECT_SCOPE = auto()
    RATING_MANAGER_MERGE_ACTION = auto()
    SWITCH_ROLE = auto()
    CREATE_PERM_TEMPLATE = auto()
    CREATE_GROUP = auto()
    ADD_GROUP_MEMBER = auto()
    ADD_GROUP_PERM_TEMPLATE = auto()
    SET_GROUP_APPROVAL_PROCESS = auto()

    _choices_labels = skip(
        (
            (RATING_MANAGER_AUTHORIZATION_SCOPE, "分级管理员权限授权范围"),
            (RATING_MANAGER_SUBJECT_SCOPE, "分级管理员人员授权范围"),
            (RATING_MANAGER_MERGE_ACTION, "分级管理员合并操作"),
            (SWITCH_ROLE, "切换角色"),
            (CREATE_PERM_TEMPLATE, "创建权限模板"),
            (CREATE_GROUP, "创建用户组"),
            (ADD_GROUP_MEMBER, "添加用户组成员"),
            (ADD_GROUP_PERM_TEMPLATE, "添加用户组权限"),
            (SET_GROUP_APPROVAL_PROCESS, "配置用户组审批流程"),
        )
    )
