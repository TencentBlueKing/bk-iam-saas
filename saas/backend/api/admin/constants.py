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

from backend.api.constants import APIEnumMsgHandler


class AdminAPIEnum(APIEnumMsgHandler):
    """枚举每个Admin API"""

    # 用户组
    GROUP_LIST = auto()
    # 用户组成员
    GROUP_MEMBER_LIST = auto()
    # Subject
    SUBJECT_JOINED_GROUP_LIST = auto()

    _choices_labels = skip(
        (
            (GROUP_LIST, "获取用户组列表"),
            (GROUP_MEMBER_LIST, "获取用户组成员列表"),
            (SUBJECT_JOINED_GROUP_LIST, "获取Subject加入的用户组列表"),
        )
    )
