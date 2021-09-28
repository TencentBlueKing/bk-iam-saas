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
from backend.biz.policy import PolicyBean, PolicyBeanList, PolicyOperationBiz, PolicyQueryBiz
from backend.biz.role import RoleAuthorizationScopeChecker, RoleBiz
from backend.common.error_codes import APIException, error_codes
from backend.service.constants import ADMIN_USER, SubjectType
from backend.service.models import Subject

from .constants import AuthorizationAPIEnum, OperateEnum
from .models import AuthAPIAllowListConfig

logger = logging.getLogger("app")


class AuthorizationAPIAllowListCheckMixin:
    """授权API相关白名单控制"""

    def verify_api(self, system_id: str, object_id: str, api: AuthorizationAPIEnum):
        """
        对授权API进行权限校验，判断该系统是否允许调用
        """
        is_allowed = AuthAPIAllowListConfig.is_allowed(api, system_id, object_id)
        if not is_allowed:
            raise exceptions.PermissionDenied(
                detail=f"{api} api don't support the [{object_id}] of system[{system_id}]"
            )

    def verify_api_by_object_ids(self, system_id: str, object_ids: List[str], api: AuthorizationAPIEnum):
        """
        批量Object进行校验
        """
        for object_id in object_ids:
            self.verify_api(system_id, object_id, api)


class AuthViewMixin:
    """所有授权API的一些公共处理函数"""

    role_biz = RoleBiz()

    policy_query_biz = PolicyQueryBiz()
    policy_operation_biz = PolicyOperationBiz()

    def grant_or_revoke(self, operate: OperateEnum, subject: Subject, policy_list: PolicyBeanList) -> List[PolicyBean]:
        """授权或回收权限"""
        system_id = policy_list.system_id

        # 对于授权Admin，自动忽略
        if subject.type == SubjectType.USER.value and subject.id.lower() == ADMIN_USER:
            # 原样返回，PolicyID=0，默认没有执行实际授权
            return policy_list.policies

        # 检测被授权的用户是否存在，不存在则尝试同步
        if subject.type == SubjectType.USER.value:
            self._check_or_sync_user(subject.id)

        # 特殊逻辑：校验授权用户组是否超过其分级管理员范围
        if subject.type == SubjectType.GROUP.value and operate == OperateEnum.GRANT.value:
            self._check_scope(subject, policy_list)

        policies = []
        # 授权或回收
        if operate == OperateEnum.GRANT.value:
            action_ids = [p.action_id for p in policy_list.policies]
            self.policy_operation_biz.alter(system_id, subject, policy_list.policies)
            policies = self.policy_query_biz.list_by_subject(system_id, subject, action_ids)
        elif operate == OperateEnum.REVOKE.value:
            policies = self.policy_operation_biz.revoke(system_id, subject, policy_list.policies)

        return policies

    def _check_or_sync_user(self, username):
        """
        检测用户是否存在，不存在则同步用户
        """
        try:
            Syncer().sync_single_user(username)
        except Exception:  # pylint: disable=broad-except
            logger.exception(f"[OpenAPI] authorize user[{username}] check error")
            raise error_codes.VALIDATE_ERROR.format(f"user[{username}] not exists")

    def _check_scope(self, subject: Subject, policy_list: PolicyBeanList):
        """检查是否策略超过用户组对应分级管理员可授权的范围"""
        assert subject.type == SubjectType.GROUP.value

        # 用户组对应的分级管理员
        role = self.role_biz.get_role_by_group_id(int(subject.id))
        # 校验权限是否满足角色的管理范围
        scope_checker = RoleAuthorizationScopeChecker(role)
        system_id = policy_list.system_id
        try:
            scope_checker.check_policies(system_id, policy_list.policies)
        except APIException:
            # Note: 这里是临时处理方案，最终方案是完全支持权限模型变更
            # 临时方案：校验不通过，则修改分级管理员的权限范围，使其通过
            need_added_policies = scope_checker.list_not_match_policy(system_id, policy_list.policies)
            self.role_biz.inc_update_auth_scope(role.id, system_id, need_added_policies)
