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
import logging
from typing import List

from rest_framework import exceptions

from backend.biz.org_sync.syncer import Syncer
from backend.common.error_codes import error_codes

from .constants import AuthorizationAPIEnum
from .models import AuthAPIAllowListConfig

logger = logging.getLogger("app")


class SubjectCheckMixin:
    def check_or_sync_user(self, username):
        """
        检测用户是否存在，不存在则同步用户
        """
        try:
            Syncer().sync_single_user(username)
        except Exception:  # pylint: disable=broad-except
            logger.exception(f"[OpenAPI] authorize user[{username}] check error")
            raise error_codes.VALIDATE_ERROR.format(f"user[{username}] not exists")


class AuthorizationAPIAllowListCheckMixin:
    """授权API相关白名单控制"""

    def check_allow_system_action(self, system_id: str, action_id: str):
        """
        检查实例授权API对于某个系统的某个Action是否允许调用
        目前暂时仅用于授权实例API，所以不需要参数auth_api_name
        """
        allowed = AuthAPIAllowListConfig.is_allowed(
            AuthorizationAPIEnum.AUTHORIZATION_INSTANCE.value, system_id, action_id
        )
        if not allowed:
            raise exceptions.PermissionDenied(
                detail="authorization instance api don't support the action[{}] of system[{}]".format(
                    action_id, system_id
                )
            )

    def check_allow_system_actions(self, system_id: str, action_ids: List[str]):
        """批量检查实例授权API对于某个系统的Actions是否允许调用"""
        for action_id in action_ids:
            self.check_allow_system_action(system_id, action_id)

    def check_allow_resource_type(self, system_id: str, resource_type_id: str):
        """
        检查新建关联实例授权API对于某个系统的某个资源类型是否允许调用
        目前暂时仅用于新建关联实例授权API，所以不需要参数auth_api_name
        """
        allowed = AuthAPIAllowListConfig.is_allowed(
            AuthorizationAPIEnum.CREATOR_AUTHORIZATION_INSTANCE.value, system_id, resource_type_id
        )

        if not allowed:
            raise exceptions.PermissionDenied(
                detail="authorization instance api don't support the resource type[{}] of system[{}]".format(
                    resource_type_id, system_id
                )
            )
