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

from backend.apps.role.models import AnonymousRole, Role
from backend.biz.role import can_user_manage_role

ROLE_SESSION_KEY = "_auth_role_id"


def authenticate(request=None, role_id=0):
    """authenticate user's current role"""
    user = getattr(request, "user", None)
    if not getattr(user, "is_authenticated", False):
        user = None
    # 1. 无用户或匿名用户，则直接返回
    if not user:
        return AnonymousRole()

    # 2. 用户的角色不存在, 返回staff
    if role_id == 0 or not can_user_manage_role(request.user.username, role_id):
        return AnonymousRole()

    # 3. 对于用户与角色关系认证通过的，返回对应的分级管理员(超级管理员和系统管理员是两类特殊的分级管理员)
    return Role.objects.get(id=role_id)
