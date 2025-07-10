# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云 - 权限中心 (BlueKing-IAM) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from typing import List

from aenum import LowerStrEnum, auto, skip

from backend.util.enum import ChoicesEnum

# 各种 API 白名单控制时，表示允许任意 API
ALLOW_ANY = "*"


class BKNonEntityUser(ChoicesEnum, LowerStrEnum):
    """
    蓝鲸非实体用户，主要用于 API 调用时的审计，区别于正常的实体用户
    """

    # 双下划线是为了避免与实体用户名冲突
    BK__UNVERIFIED_USER = auto()
    BK__ANONYMOUS_USER = auto()
    _choices_labels = skip(
        (
            # 主要用于 API 调用时，ESB/APIGW 传递过来的 Jwt.user.verified 为 False 时，
            # Jwt.user.username 是不可信的，有可能是很随意的字符串
            # 所以可以使用 BK__UNVERIFIED_USER 统一表示这类用户
            (BK__UNVERIFIED_USER, "未认证的用户"),
            # 主要用于 API 调用时，ESB/APIGW 传递过来的 Jwt.user 为空时，但审计等其他场景需要做标识
            (BK__ANONYMOUS_USER, "匿名用户，即空用户"),
        )
    )


class BaseAPIEnum(ChoicesEnum, LowerStrEnum):
    """获取管理类 API、超级管理类 API、授权类 API 的枚举信息"""

    @classmethod
    def info(cls) -> List:
        enum_dict = dict(cls.get_choices())
        return [{"api": api, "name": enum_dict[api]} for api in enum_dict]
