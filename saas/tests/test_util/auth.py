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

from typing import Optional

from backend.account import get_user_model
from backend.apps.role.models import AnonymousRole, Role
from backend.service.constants import RoleType
from tests.test_util.helpers import generate_random_string


def create_user(username: Optional[str] = None):
    """
    该函数主要是生成用户对象，用于模拟API请求时的用户态，即request.user
    """
    username = username or generate_random_string(length=6)
    user_model = get_user_model()
    return user_model(username=username)


def create_auth_role(role_type: RoleType, role_id: int = 0):
    """
    该函数主要是生成用户角色，用于模拟API请求时以不同角色访问
    """
    # 超级管理员
    if role_type == RoleType.SUPER_MANAGER.value:
        return Role(type=RoleType.SUPER_MANAGER.value, id=1, name="超级管理员")
    if role_type == RoleType.SYSTEM_MANAGER.value:
        return Role(type=RoleType.SYSTEM_MANAGER.value, id=role_id, name="系统管理员")
    # 默认是普通用户
    return AnonymousRole()
