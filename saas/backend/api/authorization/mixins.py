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
from rest_framework.response import Response

from backend.api.constants import ALLOW_ANY
from backend.biz.org_sync.syncer import Syncer
from backend.biz.policy import PolicyBean, PolicyBeanList, PolicyOperationBiz, PolicyQueryBiz
from backend.biz.role import RoleBiz
from backend.common.cache import cachedmethod
from backend.common.error_codes import error_codes
from backend.service.constants import ADMIN_USER, SubjectType
from backend.service.models import Subject
from backend.trans.role import RoleAuthScopeTrans

from .constants import ALLOW_LIST_OBJECT_OPERATION_STEP, AllowListMatchOperationEnum, AuthorizationAPIEnum, OperateEnum
from .models import AuthAPIAllowListConfig

logger = logging.getLogger("app")


# TODO: 目前其他OpenAPI暂时没有其他多种匹配规则的需求，后续需要则抽取到api下共用
class AllowItem:
    def __init__(self, object_id: str):
        # Note: 这里兼容了旧数据无Operation的情况，无Operation默认是eq
        self.operation = AllowListMatchOperationEnum.EQ.value
        self.object_id = object_id

        # 解析object_id，拆分出operation 和 匹配的对象
        # 若分隔符在object_id里，说明需要拆分出真正的object_id和operation
        if ALLOW_LIST_OBJECT_OPERATION_STEP in object_id:
            object_split_list = object_id.split(ALLOW_LIST_OBJECT_OPERATION_STEP)
            # 长度非2，则说明非正常的规则，则默认使用等于匹配
            if len(object_split_list) == 2:
                self.operation = object_split_list[0]
                self.object_id = object_split_list[1]

    def match(self, object_id: str) -> bool:
        """判断是否匹配，需要根据每种不同的匹配规则进行判断"""
        # 特殊判断：任意情况
        if self.object_id == ALLOW_ANY:
            return True

        if self.operation == AllowListMatchOperationEnum.EQ.value:
            return object_id == self.object_id

        # Note: 对于前缀匹配，存储是的前缀，所以应该判断self.object_id是否是object_id的前缀
        if self.operation == AllowListMatchOperationEnum.STARTS_WITH.value:
            return object_id.startswith(self.object_id)

        return False


class AuthorizationAPIAllowListCheckMixin:
    """授权API相关白名单控制"""

    @cachedmethod(timeout=5 * 60)  # 缓存5分钟
    def _list_system_allow_list(self, api: str, system_id: str) -> List[AllowItem]:
        """查询系统某类API的白名单"""
        allow_list = AuthAPIAllowListConfig.objects.filter(type=api, system_id=system_id)
        return [AllowItem(object_id=i.object_id) for i in allow_list]

    def _is_allowed(self, api: str, system_id: str, object_id: str) -> bool:
        """判断是否系统允许某个API"""
        allow_list = self._list_system_allow_list(api, system_id)
        for i in allow_list:
            if i.match(object_id):
                return True

        return False

    def verify_api(self, system_id: str, object_id: str, api: AuthorizationAPIEnum):
        """
        对授权API进行权限校验，判断该系统是否允许调用
        """
        is_allowed = self._is_allowed(api, system_id, object_id)

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
    role_auth_scope_trans = RoleAuthScopeTrans()

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
            logger.exception(f"[OpenAPI] authorize user[{username}] check_or_sync fail")
            raise error_codes.VALIDATE_ERROR.format(f"user[{username}] not exists")

    def _check_scope(self, subject: Subject, policy_list: PolicyBeanList):
        """检查是否策略超过用户组对应分级管理员可授权的范围"""
        assert subject.type == SubjectType.GROUP.value

        # 用户组对应的分级管理员
        role = self.role_biz.get_role_by_group_id(int(subject.id))

        # NOTE: 临时处理: 自动扩张管理员的授权范围
        self.role_biz.incr_update_auth_scope(role, [self.role_auth_scope_trans.from_policy_list(policy_list)])

    def policy_response(self, policy: PolicyBean):
        """所有返回单一策略的接口都统一返回的结构"""
        return Response(
            # TODO: 这个PolicyID是否去除呢？这里已经调整为SaaS Policy ID了，对于调用方没什么意义
            {"policy_id": policy.policy_id, "statistics": {"instance_count": policy.count_all_type_instance()}}
        )

    def batch_policy_response(self, policies: List[PolicyBean]):
        """所有返回批量策略的接口都统一返回的结构"""
        return Response(
            [
                {
                    "action": {"id": p.action_id},
                    "policy_id": p.policy_id,
                    "statistics": {"instance_count": p.count_all_type_instance()},
                }
                for p in policies
            ]
        )
