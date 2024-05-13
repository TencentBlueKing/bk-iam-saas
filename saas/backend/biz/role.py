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
from collections import defaultdict
from textwrap import dedent
from typing import Any, Dict, List, Optional, Set

from blue_krill.web.std_error import APIError
from django.conf import settings
from django.db import connection
from django.db.models import Case, Q, Value, When
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext as _
from django_celery_beat.models import CrontabSchedule, PeriodicTask
from pydantic import BaseModel, parse_obj_as
from rest_framework import serializers

from backend.apps.application.models import Application
from backend.apps.group.models import Group
from backend.apps.organization.models import Department, DepartmentMember, User
from backend.apps.role.models import (
    Role,
    RolePolicyExpiredNotificationConfig,
    RoleRelatedObject,
    RoleRelation,
    RoleResourceRelation,
    RoleSource,
    RoleUser,
)
from backend.apps.subject_template.models import SubjectTemplate
from backend.apps.template.models import PermTemplate
from backend.common.cache import cached
from backend.common.error_codes import error_codes
from backend.service.constants import (
    ACTION_ALL,
    ANY_ID,
    SUBJECT_ALL,
    SUBJECT_TYPE_ALL,
    SYSTEM_ALL,
    ApplicationStatus,
    ApplicationType,
    RoleRelatedObjectType,
    RoleSourceType,
    RoleType,
    SubjectType,
)
from backend.service.models import Attribute, Subject, System
from backend.service.role import AuthScopeAction, AuthScopeSystem, CommonAction, RoleInfo, RoleService, UserRole
from backend.service.system import SystemService

from .policy import (
    ConditionBean,
    InstanceBean,
    PathNodeBean,
    PathNodeBeanList,
    PolicyBean,
    PolicyBeanList,
    RelatedResourceBean,
    ResourceGroupBean,
    ThinSystem,
)
from .resource import ResourceNodeBean

logger = logging.getLogger("app")


class RoleInfoBean(RoleInfo):
    pass


class UserRoleNode(UserRole):
    is_member: bool = True
    sub_roles: List["UserRoleNode"] = []


class AuthScopeSystemBean(BaseModel):
    system: ThinSystem
    actions: List[PolicyBean]

    def is_any_system(self) -> bool:
        """是否任意系统"""
        return self.system.id == SYSTEM_ALL

    def is_any_action(self) -> bool:
        """是否任意操作"""
        return self.is_any_system() or (len(self.actions) == 1 and self.actions[0].action_id == ACTION_ALL)


class RoleScopeSystemActions(BaseModel):
    """
    role的授权范围系统-操作列表
    """

    systems: Dict[str, Set[str]]  # key: system_id, value: action_id_set

    def is_all_action(self, system_id: str) -> bool:
        """
        是否是全操作列表
        """
        if not self.has_system(system_id):
            return False

        if SYSTEM_ALL in self.systems or ACTION_ALL in self.systems[system_id]:
            return True

        return False

    def has_system(self, system_id: str) -> bool:
        return SYSTEM_ALL in self.systems or system_id in self.systems

    def list_action_id(self, system_id: str) -> List[str]:
        """
        返回role范围内的所有action_id, 如果为all_action, 应该事先判断
        """
        if system_id in self.systems:
            return list(self.systems[system_id])

        return []


class RoleBiz:
    svc = RoleService()
    system_svc = SystemService()

    get_role_by_group_id = RoleService.__dict__["get_role_by_group_id"]
    list_system_common_actions = RoleService.__dict__["list_system_common_actions"]
    list_user_role = RoleService.__dict__["list_user_role"]
    list_paging_user_role = RoleService.__dict__["list_paging_user_role"]
    list_user_role_for_system = RoleService.__dict__["list_user_role_for_system"]
    list_subject_scope = RoleService.__dict__["list_subject_scope"]
    list_auth_scope = RoleService.__dict__["list_auth_scope"]
    list_by_ids = RoleService.__dict__["list_by_ids"]
    list_members_by_role_id = RoleService.__dict__["list_members_by_role_id"]

    transfer_groups_role = RoleService.__dict__["transfer_groups_role"]

    def get_role_scope_include_user(self, role_id: int, username: str) -> Optional[Role]:
        """
        查询授权范围包含用户的角色
        """
        role = Role.objects.filter(id=role_id).first()
        if not role:
            return None

        checker = RoleSubjectScopeChecker(role)
        try:
            checker.check([Subject.from_username(username)])
            return role
        except APIError:
            return None

    def create_grade_manager(self, info: RoleInfoBean, creator: str) -> Role:
        """
        创建分级管理员
        """
        role = self.svc.create(info, creator)
        RoleResourceRelationHelper(role).handle()
        return role

    def update(self, role: Role, info: RoleInfoBean, updater: str):
        """
        更新分级管理员
        """
        self.svc.update(role, info, updater)

        RoleResourceRelationHelper(role).handle()

    def sync_subset_manager_subject_scope(self, role_id: int):
        subject_scopes = self.svc.list_subject_scope(role_id)

        subset_manager_ids = list(RoleRelation.objects.filter(parent_id=role_id).values_list("role_id", flat=True))
        for subset_manager in Role.objects.filter(id__in=subset_manager_ids, inherit_subject_scope=True):
            self.svc.update_role_subject_scope(subset_manager.id, subject_scopes)

    def create_subset_manager(self, grade_manager: Role, info: RoleInfoBean, creator: str) -> Role:
        """
        创建子集管理员
        """
        role = self.svc.create_subset_manager(grade_manager, info, creator)
        RoleResourceRelationHelper(role).handle()
        return role

    def modify_system_manager_members(self, role_id: int, members: List[str]):
        """修改系统管理员的成员"""
        self.svc.modify_system_manager_members(role_id, members)

    def modify_system_manager_member_system_permission(self, role_id: int, need_sync_backend_role: bool):
        """系统管理员的成员系统权限是否开启"""
        self.svc.modify_system_manager_member_system_permission(role_id, need_sync_backend_role)

    def add_super_manager_member(self, username: str, need_sync_backend_role: bool):
        """
        添加超级管理员成员
        """
        self.svc.add_super_manager_member(username, need_sync_backend_role)

    def delete_super_manager_member(self, username: str):
        """删除超级管理员成员"""
        self.svc.delete_super_manager_member(username)

    def add_grade_manager_members(self, role_id: int, usernames: List[str]):
        """
        添加分级管理员成员
        """
        self.svc.add_grade_manager_members(role_id, usernames)

    def delete_grade_manager_member(self, role_id: int, usernames: List[str]):
        """
        批量删除分级管理员成员
        """
        RoleUser.objects.delete_grade_manager_member(role_id, usernames)

    def delete_member(self, role_id: int, username: str):
        """
        角色删除成员
        """
        self.svc.delete_member(role_id, username)

    def update_super_manager_member_system_permission(self, username: str, need_sync_backend_role: bool):
        """
        更新超级管理员成员的系统权限
        """
        self.svc.update_super_manager_member_system_permission(username, need_sync_backend_role)

    def _update_auth_scope_due_to_renamed_resource(
        self, role_id: int, auth_systems: List[AuthScopeSystem], auth_system_beans: List[AuthScopeSystemBean]
    ) -> List[AuthScopeSystemBean]:
        """
        更新分级管理员授权范围里的资源类型名称
        auth_systems: 是DB里原始的授权范围数据
        auth_system_beans: 即将给到页面的展示授权范围数据，与auth_systems相比，多了填充Name的展示数据
        auth_system_beans长度有时候会小于auth_systems的长度，因为可能有时候只需要展示部分系统的数据，而不是整个授权范围所有系统的数据
        返回更新后展示用途的授权范围数据
        """
        need_updated_policies_dict: Dict[str, List[PolicyBean]] = {}

        # 遍历授权范围里的每个系统策略
        for auth_system_bean in auth_system_beans:
            system_id = auth_system_bean.system.id
            # 任意Action，则跳过
            if auth_system_bean.is_any_action():
                continue
            # 尝试更新
            policy_list = PolicyBeanList(system_id=system_id, policies=auth_system_bean.actions)
            updated_policies = policy_list.auto_update_resource_name()
            # 需要更新
            if len(updated_policies) > 0:
                # 修改要返回的展示数据: 这里是完整覆盖，包括未被更新的策略，不能使用updated_policies
                auth_system_bean.actions = policy_list.policies
                # 记录要进行DB修改的数据
                need_updated_policies_dict[system_id] = policy_list.policies

        if len(need_updated_policies_dict) > 0:
            # 直接修改原始数据auth_systems，而不是auth_system_beans
            for auth_system in auth_systems:
                policies = need_updated_policies_dict.get(auth_system.system_id)
                # 不在修改范围内的，直接跳过
                if policies is None:
                    continue
                # 直接修改原始数据
                auth_system.actions = parse_obj_as(List[AuthScopeAction], policies)

            # 变更可授权的权限范围
            # Note: 这里的修改并没有处理并发的情况
            self.svc.update_role_auth_scope(role_id, auth_systems)

        return auth_system_beans

    def list_auth_scope_bean(
        self, role_id: int, should_auto_update_resource_name: bool = False
    ) -> List[AuthScopeSystemBean]:
        """
        查询角色的auth授权范围Bean
        """
        auth_systems = self.svc.list_auth_scope(role_id)
        system_list = self.system_svc.new_system_list()

        auth_system_beans = []
        for auth_system in auth_systems:
            auth_system_bean = self._gen_auth_scope_bean(auth_system, system_list)
            if not auth_system_bean:
                continue
            auth_system_beans.append(auth_system_bean)

        # ResourceNameAutoUpdate
        # 判断是否主动检查更新授权范围
        if should_auto_update_resource_name:
            auth_system_beans = self._update_auth_scope_due_to_renamed_resource(
                role_id, auth_systems, auth_system_beans
            )

        return auth_system_beans

    def _gen_auth_scope_bean(self, auth_system: AuthScopeSystem, system_list) -> Optional[AuthScopeSystemBean]:
        system = (
            system_list.get(auth_system.system_id)
            if auth_system.system_id != SYSTEM_ALL
            else System(id=SYSTEM_ALL, name="", name_en="", description="", description_en="")
        )
        if not system:
            return None

        if len(auth_system.actions) == 1 and auth_system.actions[0].id == ACTION_ALL:
            policies = [PolicyBean.parse_obj(auth_system.actions[0])]
        else:
            policies = PolicyBeanList(
                auth_system.system_id,
                parse_obj_as(List[PolicyBean], auth_system.actions),
                need_fill_empty_fields=True,
            ).policies

        return AuthScopeSystemBean(system=ThinSystem.parse_obj(system), actions=policies)

    def get_auth_scope_bean_by_system(
        self, role_id: int, system_id: str, should_auto_update_resource_name: bool = False
    ) -> Optional[AuthScopeSystemBean]:
        """
        获取指定系统的auth授权范围Bean
        """
        auth_systems = self.svc.list_auth_scope(role_id)
        system_list = self.system_svc.new_system_list()

        auth_system_bean = None
        for auth_system in auth_systems:
            if auth_system.system_id == system_id:
                auth_system_bean = self._gen_auth_scope_bean(auth_system, system_list)
                break

        # ResourceNameAutoUpdate
        # 判断是否主动检查更新授权范围
        if should_auto_update_resource_name and auth_system_bean is not None:
            auth_system_beans = self._update_auth_scope_due_to_renamed_resource(
                role_id, auth_systems, [auth_system_bean]
            )
            auth_system_bean = auth_system_beans[0]

        return auth_system_bean

    def incr_update_subject_scope(self, role: Role, subjects: List[Subject]):
        """
        增量更新管理员的人员授权范围
        """

        # 1. 对比超出管理员范围的部分subjects
        checker = RoleSubjectScopeChecker(role)
        exists_subjects = set(checker.check(subjects, raise_exception=False))

        incr_subjects = [subject for subject in subjects if subject not in exists_subjects]
        if not incr_subjects:
            return

        # 2. 把这部分subjects添加到管理员的管理范围
        subjects = self.list_subject_scope(role.id)
        subjects.extend(incr_subjects)
        self.svc.update_role_subject_scope(role.id, subjects)

    def incr_update_auth_scope(self, role: Role, incr_scopes: List[AuthScopeSystem]):
        """
        增量更新管理员的授权范围
        """
        # 查询已有的可授权范围
        auth_scopes = self.svc.list_auth_scope(role.id)
        need_update = False  # 是否需要更新

        checker = RoleAuthorizationScopeChecker(role)
        for scope in incr_scopes:
            # 比对出需要扩大的授权范围
            need_added_policies = checker.list_not_match_policy(
                scope.system_id, parse_obj_as(List[PolicyBean], scope.actions)
            )
            if not need_added_policies:
                continue

            need_update = True
            # 合并需要扩大的授权范围
            self._merge_auth_scope(auth_scopes, scope.system_id, need_added_policies)

        # 不需要变更
        if not need_update:
            return

        # 变更可授权的权限范围
        self.svc.update_role_auth_scope(role.id, auth_scopes)

    def _merge_auth_scope(self, auth_scopes: List[AuthScopeSystem], system_id: str, policies: List[PolicyBean]):
        """
        合并授权范围
        """
        # 转为PolicyList，便于进行数据合并操作
        policy_list = PolicyBeanList(system_id=system_id, policies=policies, need_fill_empty_fields=True)

        # 遍历，查找需要修改的数据和对应位置
        need_modified_policy_list = PolicyBeanList(system_id=system_id, policies=[])
        index = -1
        for idx, auth_scope in enumerate(auth_scopes):
            if auth_scope.system_id == system_id:
                index = idx
                need_modified_policy_list = PolicyBeanList(
                    system_id=system_id, policies=parse_obj_as(List[PolicyBean], auth_scope.actions)
                )
                break

        # 合并增量数据
        need_modified_policy_list.add(policy_list)

        # 修改已有的可授权范围
        new_auth_scope = AuthScopeSystem(
            system_id=system_id, actions=parse_obj_as(List[AuthScopeAction], need_modified_policy_list.policies)
        )
        if index == -1:
            auth_scopes.append(new_auth_scope)
        else:
            auth_scopes[index] = new_auth_scope

    def get_common_action_by_name(self, system_id: str, name: str) -> Optional[CommonAction]:
        common_actions = self.list_system_common_actions(system_id)
        for common_action in common_actions:
            if common_action.name == name:
                return common_action

        return None


class RoleCheckBiz:
    def check_grade_manager_unique_name(self, new_name: str, old_name: str = ""):
        """
        检查分级管理员名称唯一性
        仅仅检查分级管理员，若分级管理员类型是系统管理员和超级管理员则不检查
        包括申请中需要检查
        """
        # 如果新名称与旧名称一致，说明名称没改变
        if new_name.lower() == old_name.lower():
            return

        # 新名称已经有对应的分级管理员，则不可以
        if Role.objects.filter(
            name=new_name,
            type__in=[RoleType.SUPER_MANAGER.value, RoleType.SYSTEM_MANAGER.value, RoleType.GRADE_MANAGER.value],
        ).exists():
            raise error_codes.CONFLICT_ERROR.format(_("名称[{}]已存在，请修改为其他名称").format(new_name), True)

        # 检测是否已经有正在申请中的
        applications = Application.objects.filter(
            type__in=[
                ApplicationType.CREATE_GRADE_MANAGER.value,
                ApplicationType.UPDATE_GRADE_MANAGER.value,
            ],
            status=ApplicationStatus.PENDING.value,
        )
        names = {i.data.get("name") for i in applications}
        if new_name in names:
            raise error_codes.CONFLICT_ERROR.format(_("存在同名分级管理员[{}]或者在处理中的单据，请修改后再提交").format(new_name), True)

    def check_subset_manager_unique_name(self, grade_manager: Role, new_name: str, old_name: str = ""):
        """
        检查子集管理员的唯一性
        每个分级管理员里面的子集管理员名字必须唯一
        """
        # 如果新名称与旧名称一致，说明名称没改变
        if new_name.lower() == old_name.lower():
            return

        # 查询分级管理员已有的子集管理员id
        sub_ids = RoleRelation.objects.list_sub_id(grade_manager.id)

        # 检查对应的子集管理员名字是否冲突
        if Role.objects.filter(name=new_name, id__in=sub_ids).exists():
            raise error_codes.CONFLICT_ERROR.format(_("名称[{}]已存在，请修改为其他名称").format(new_name), True)

    def check_subset_manager_auth_scope(self, grade_manager: Role, auth_scopes: List[AuthScopeSystem]):
        """
        检查子集管理员的授权范围
        子集管理员的授权范围必须是分级管理员的子集
        """
        scope_checker = RoleAuthorizationScopeChecker(grade_manager)

        for system_scope in auth_scopes:
            try:
                scope_checker.check_policies(
                    system_scope.system_id, [PolicyBean.parse_obj(action) for action in system_scope.actions]
                )
            except APIError as e:
                raise error_codes.VALIDATE_ERROR.format(
                    _("系统: {} 授权范围校验错误: {}").format(system_scope.system_id, e.message),
                    replace=True,
                )

    def check_subset_manager_subject_scope(self, grade_manager: Role, subject_scopes: List[Subject]):
        """
        检查子集管理员的人员范围
        子集管理员的人员范围必须是否分级管理员的子集
        """
        scope_checker = RoleSubjectScopeChecker(grade_manager)
        scope_checker.check(subject_scopes)

    def check_member_count(self, role_id: int, new_member_count: int):
        """
        检查分级管理员成员数据
        """
        exists_count = RoleUser.objects.filter(role_id=role_id).count()
        member_limit = settings.SUBJECT_AUTHORIZATION_LIMIT["grade_manager_member_limit"]
        if exists_count + new_member_count > member_limit:
            raise error_codes.VALIDATE_ERROR.format(
                _("超过分级管理员最大可添加成员数{}").format(member_limit),
                True,
            )

    def check_subject_grade_manager_limit(self, subject: Subject):
        """
        检查subject加入的分级管理员数量是否超限
        Note: 目前subject仅仅支持User
        """
        limit = settings.SUBJECT_AUTHORIZATION_LIMIT["subject_grade_manager_limit"]
        role_ids = Role.objects.filter(type=RoleType.GRADE_MANAGER.value).values_list("id", flat=True)
        exists_count = RoleUser.objects.filter(username=subject.id, role_id__in=role_ids).count()
        if exists_count >= limit:
            raise serializers.ValidationError(_("成员({}): 可加入的分级管理员数量已超限 {}").format(subject.id, exists_count))

    def check_grade_manager_of_system_limit(self, system_id: str):
        """
        检查某个系统可创建的分级管理数量是否超限
        """
        default_limit = settings.SUBJECT_AUTHORIZATION_LIMIT["default_grade_manager_of_system_limit"]
        # 判断是否该系统有特殊配置限制数量
        value = settings.SUBJECT_AUTHORIZATION_LIMIT["grade_manager_of_specified_systems_limit"]
        try:
            system_limits = {}
            # 对value进行解析，value 格式为：system_id1:number1,system_id2:number2,...
            split_system_limits = value.split(",") if value else []
            for one_system_limit in split_system_limits:
                system_limit = one_system_limit.split(":")
                system_limits[system_limit[0].strip()] = int(system_limit[1].strip())
        except Exception as error:  # pylint: disable=broad-except noqa
            logger.error(
                f"parse grade_manager_of_specified_systems_limit from setting failed, value:{value}, error: {error}"
            )
            system_limits = {}

        limit = system_limits[system_id] if system_id in system_limits else default_limit

        exists_count = RoleSource.get_role_count(
            RoleType.GRADE_MANAGER.value, system_id, source_type=RoleSourceType.API.value
        )
        if exists_count >= limit:
            raise serializers.ValidationError(_("系统({}): 可创建的分级管理员数量已超过最大值 {}").format(system_id, limit))


class RoleListQuery:
    system_svc = SystemService()
    role_svc = RoleService()

    def __init__(self, role: Role, user: Optional[User] = None) -> None:
        self.role = role
        self.user = User.objects.filter(username=user.username).first() if user else None

    def list_system(self) -> List[System]:
        """
        查询系统列表
        """
        systems = self.system_svc.list()

        if self.role.type == RoleType.STAFF.value:
            return systems

        scopes = self.role_svc.list_auth_scope(self.role.id)
        system_set = {s.system_id for s in scopes}
        if SYSTEM_ALL in system_set:
            return systems
        return [s for s in systems if s.id in system_set]

    def list_scope_action_id(self, system_id: str) -> List[str]:
        """
        查询操作列表
        """
        if self.role.type == RoleType.STAFF.value:
            return [ACTION_ALL]

        system_actions = self.get_scope_system_actions()
        if not system_actions.has_system(system_id):
            return []

        if system_actions.is_all_action(system_id):
            return [ACTION_ALL]

        return system_actions.list_action_id(system_id)

    def get_scope_system_actions(self) -> RoleScopeSystemActions:
        """
        获取授权范围的系统-操作字典
        """
        scopes = self.role_svc.list_auth_scope(self.role.id)
        systems = {s.system_id: {a.id for a in s.actions} for s in scopes}
        return RoleScopeSystemActions(systems=systems)

    def query_template(self):
        """
        查询模板列表
        """
        assert self.user

        if self.role.type == RoleType.SUBSET_MANAGER.value:
            template_ids = self._query_subset_manager_template_id()
        else:
            template_ids = self._get_role_related_object_ids(RoleRelatedObjectType.TEMPLATE.value)
        return PermTemplate.objects.filter(id__in=template_ids)

    def _query_subset_manager_template_id(self) -> List[int]:
        """
        查询子集管理员可授权的模板列表

        1. 子集管理员可授权的模板列表来源于父级分级管理员的模板列表
        2. 子集管理员可授权的模板必须满足子集管理员的授权范围
        """

        assert self.role.type == RoleType.SUBSET_MANAGER.value

        # 1. 查询子集管理员的父级分级管理员
        parent_role_id = RoleRelation.objects.get_parent_role_id(self.role.id)
        if not parent_role_id:
            return []

        # 2. 查询子集管理员的授权范围
        system_actions = self.get_scope_system_actions()

        # 3. 查询分级管理员的模板列表
        parent_template_ids = list(
            RoleRelatedObject.objects.filter(
                role_id=parent_role_id, object_type=RoleRelatedObjectType.TEMPLATE.value
            ).values_list("object_id", flat=True)
        )

        template_ids = []
        # 4. 遍历筛选出满足子集管理员授权范围的模板id
        for template in PermTemplate.objects.filter(id__in=parent_template_ids):
            if not system_actions.has_system(template.system_id):
                continue

            # 满足授权范围
            if system_actions.is_all_action(template.system_id):
                template_ids.append(template.id)
                continue

            # 满足授权范围
            if set(template.action_ids).issubset(set(system_actions.list_action_id(template.system_id))):
                template_ids.append(template.id)

        return template_ids

    def query_group(self, inherit: bool = True, only_inherit: bool = False):
        """
        查询用户组列表
        """
        if self.role.type == RoleType.STAFF.value:
            return Group.objects.filter(hidden=False)

        group_ids = self._get_role_related_object_ids(
            RoleRelatedObjectType.GROUP.value, inherit=inherit, only_inherit=only_inherit
        )
        return Group.objects.filter(id__in=group_ids)

    def _get_role_related_object_ids(
        self, object_type: str, inherit: bool = True, only_inherit: bool = False
    ) -> List[int]:
        # 分级管理员可以管理子集管理员的所有用户组
        if (
            self.role.type == RoleType.GRADE_MANAGER.value
            and object_type == RoleRelatedObjectType.GROUP.value
            and inherit
        ):
            role_ids = RoleRelation.objects.list_sub_id(self.role.id)
            if not only_inherit:
                role_ids.append(self.role.id)
            return list(
                RoleRelatedObject.objects.filter(role_id__in=role_ids, object_type=object_type).values_list(
                    "object_id", flat=True
                )
            )

        if self.role.type != RoleType.STAFF.value:
            return list(
                RoleRelatedObject.objects.filter(role_id=self.role.id, object_type=object_type).values_list(
                    "object_id", flat=True
                )
            )

        assert self.user
        mgr_ids = self._list_authorization_scope_include_user_role_ids()
        # 查询 所有这些管理员创建的 对象 ids
        return list(
            RoleRelatedObject.objects.filter(role_id__in=mgr_ids, object_type=object_type).values_list(
                "object_id", flat=True
            )
        )

    def _list_authorization_scope_include_user_role_ids(self):
        """
        授权范围包含用户的角色id列表
        """
        # 1. 查询普通用户所在的部门id
        department_ids = self.user.ancestor_department_ids or [0]

        # 2. 查询 subjects 相关的分级管理员
        # grade_mgr_ids = ScopeSubject.objects.filter(
        #     Q(subject_type=RoleScopeSubjectType.DEPARTMENT.value, subject_id__in=department_ids)
        #     | Q(subject_type=RoleScopeSubjectType.USER.value, subject_id=self.user.username)  # noqa
        #     | Q(subject_type=SUBJECT_TYPE_ALL, subject_id=SUBJECT_ALL)  # noqa
        # ).values_list("role_id", flat=True)

        sql = dedent(
            """SELECT
            a.id
            FROM
            role_role a
            LEFT JOIN role_scopesubject b ON a.id = b.role_id
            WHERE
            a.hidden = 0
            AND (
                (
                b.subject_id IN %s
                AND b.`subject_type` = 'department'
                )
                OR (
                b.subject_id = %s
                AND b.`subject_type` = 'user'
                )
                OR (
                b.`subject_id` = '*'
                AND b.`subject_type` = '*'
                )
            )"""
        )

        with connection.cursor() as cursor:
            cursor.execute(sql, (tuple(department_ids), self.user.username))
            grade_mgr_ids = [row[0] for row in cursor.fetchall()]

        # 3. 查询 超级管理员 + 系统管理员的 ids
        super_ids = Role.objects.filter(
            Q(type=RoleType.SUPER_MANAGER.value) | Q(type=RoleType.SYSTEM_MANAGER.value)
        ).values_list("id", flat=True)

        return list(grade_mgr_ids) + list(super_ids)

    def list_role_scope_include_user(self):
        """
        授权范围包含用户的角色
        """
        assert self.user

        mgr_ids = self._list_authorization_scope_include_user_role_ids()
        return self.role_svc.list_by_ids(mgr_ids, with_hidden=False)

    def query_grade_manager(self, with_super: bool = False):
        """
        查询分级管理员列表
        """
        queryset = Role.objects.filter(type=RoleType.GRADE_MANAGER.value).order_by("-updated_time")
        if with_super:
            type_order = Case(
                When(type=RoleType.SUPER_MANAGER.value, then=Value(1)),
                When(type=RoleType.SYSTEM_MANAGER.value, then=Value(2)),
                When(type=RoleType.GRADE_MANAGER.value, then=Value(3)),
            )
            queryset = (
                Role.objects.filter(
                    type__in=[RoleType.SUPER_MANAGER, RoleType.SYSTEM_MANAGER, RoleType.GRADE_MANAGER.value]
                )
                .alias(type_order=type_order)
                .order_by("type_order", "-updated_time")
            )

        # 作为个人时，只能管理加入的的分级管理员
        assert self.user

        # 只要用户是超级管理员, 就可以管理所有分级管理员
        if self.is_user_super_manager(self.user):
            return queryset

        # 查询用户加入的角色id
        role_ids = list(RoleUser.objects.filter(username=self.user.username).values_list("role_id", flat=True))

        # 查询子集管理员的父级分级管理员id
        grade_manager_ids = list(RoleRelation.objects.filter(role_id__in=role_ids).values_list("parent_id", flat=True))
        role_ids.extend(grade_manager_ids)

        return queryset.filter(id__in=role_ids)

    @cached(timeout=5 * 60, key_function=lambda _, user: str(user.id))
    def is_user_super_manager(self, user: User):
        super_manager = get_super_manager()
        return RoleUser.objects.filter(username=user.username, role_id=super_manager.id).exists()

    def query_subset_manager(self):
        """
        查询子集管理员
        """
        if self.role.type == RoleType.GRADE_MANAGER.value:
            sub_ids = RoleRelation.objects.list_sub_id(self.role.id)
            return Role.objects.filter(type=RoleType.SUBSET_MANAGER.value, id__in=sub_ids).order_by("-updated_time")
        elif self.role.type == RoleType.SUBSET_MANAGER.value:
            return Role.objects.filter(type=RoleType.SUBSET_MANAGER.value, id=self.role.id)
        elif self.role.type == RoleType.STAFF.value:
            assert self.user
            role_ids = list(RoleUser.objects.filter(username=self.user.username).values_list("role_id", flat=True))
            return Role.objects.filter(type=RoleType.SUBSET_MANAGER.value, id__in=role_ids)
        elif self.role.type == RoleType.SUPER_MANAGER.value:
            return Role.objects.filter(type=RoleType.SUBSET_MANAGER.value)

        return Role.objects.none()

    def query_subject_template(self):
        """
        查询人员模板列表
        """
        if self.role.type == RoleType.STAFF.value:
            return SubjectTemplate.objects.all()

        subject_template_ids = self.query_subject_template_id()
        return SubjectTemplate.objects.filter(id__in=subject_template_ids)

    def query_subject_template_id(self):
        if self.role.type == RoleType.SUBSET_MANAGER.value:
            subject_template_ids = self._query_subset_manager_subject_template_id()
        else:
            subject_template_ids = self._get_role_related_object_ids(
                RoleRelatedObjectType.SUBJECT_TEMPLATE.value, inherit=False
            )

        return subject_template_ids

    def _query_subset_manager_subject_template_id(self) -> List[int]:
        """
        查询子集管理员可授权的人员模版列表
        """
        assert self.role.type == RoleType.SUBSET_MANAGER.value

        # 1. 查询子集管理员的父级分级管理员
        parent_role_id = RoleRelation.objects.get_parent_role_id(self.role.id)
        if not parent_role_id:
            return []

        return list(
            RoleRelatedObject.objects.filter(
                role_id=parent_role_id, object_type=RoleRelatedObjectType.SUBJECT_TEMPLATE.value
            ).values_list("object_id", flat=True)
        )


class RoleObjectRelationChecker:
    """
    角色对象关系检查
    """

    def __init__(self, role: Role):
        self.role = role

    def list_relation_role_id(self):
        """
        查询出role关联的所有role id

        分级管理员可以管理所有的子集管理员相关的信息
        """
        role_ids = [self.role.id]

        if self.role.type == RoleType.GRADE_MANAGER.value:
            sub_ids = RoleRelation.objects.list_sub_id(self.role.id)
            return role_ids + sub_ids

        return role_ids

    def _check_object(self, obj_type: str, obj_id: int) -> bool:
        # 如果是超级管理员, 直接返回True
        if self.role.type == RoleType.SUPER_MANAGER.value:
            return True

        return RoleRelatedObject.objects.filter(
            role_id__in=self.list_relation_role_id(), object_type=obj_type, object_id=obj_id
        ).exists()

    def _check_object_ids(self, obj_type: str, obj_ids: List[int]) -> bool:
        # 如果是超级管理员, 直接返回True
        if self.role.type == RoleType.SUPER_MANAGER.value:
            return True

        count = RoleRelatedObject.objects.filter(
            role_id__in=self.list_relation_role_id(), object_type=obj_type, object_id__in=obj_ids
        ).count()
        return count == len(set(obj_ids))

    def check_group(self, obj) -> bool:
        return self._check_object(RoleRelatedObjectType.GROUP.value, obj.id)

    def check_template(self, obj) -> bool:
        return self._check_object(RoleRelatedObjectType.TEMPLATE.value, obj.id)

    def check_group_ids(self, ids: List[int]) -> bool:
        return self._check_object_ids(RoleRelatedObjectType.GROUP.value, ids)


class RoleAuthorizationScopeChecker:
    """
    角色模板授权范围检查
    TODO 结构变更重点修改
    """

    svc = RoleService()

    def __init__(self, role: Role):
        self.role = role
        if self.role.type == RoleType.STAFF.value:
            raise error_codes.FORBIDDEN  # 普通用户不能授权

    @cached_property
    def system_action_scope(self):
        scopes = self.svc.list_auth_scope(self.role.id)
        return {s.system_id: {a.id: a for a in s.actions} for s in scopes}

    def _check_system_in_scope(self, system_id):
        system_action_scope = self.system_action_scope
        if system_id not in system_action_scope and SYSTEM_ALL not in system_action_scope:
            raise error_codes.FORBIDDEN.format(
                message=_("{} 系统不在分级管理员的授权范围内，请先编辑分级管理员授权范围").format(system_id), replace=True
            )

    def _check_action_in_scope(self, system_id, action_id):
        system_action_scope = self.system_action_scope
        if SYSTEM_ALL in system_action_scope or ACTION_ALL in system_action_scope[system_id]:
            return ACTION_ALL

        action_scope = system_action_scope[system_id]
        if action_id not in action_scope:
            raise error_codes.FORBIDDEN.format(
                message=_("{} 操作不在分级管理员的授权范围内，请先编辑分级管理员授权范围").format(action_id), replace=True
            )  # 操作不在授权范围内

        return ""

    def remove_path_outside_scope(
        self, system_id: str, action_id: str, paths: List[List[PathNodeBean]]
    ) -> List[List[PathNodeBean]]:
        """
        移除不在授权范围内的路径
        """
        if self._check_action_in_scope(system_id, action_id) == ACTION_ALL:
            return paths

        policy_scope = PolicyBean.parse_obj(self.system_action_scope[system_id][action_id])
        match_paths: List[List[PathNodeBean]] = []
        path_string_set: Set[str] = set()
        for rg in policy_scope.resource_groups:
            match_paths.extend(self._filter_path_match_resource_group(paths, rg, path_string_set))
            # 如果所有的路径都能匹配授权范围, 直接返回
            if len(match_paths) == len(paths):
                break

        return match_paths

    def _filter_path_match_resource_group(
        self, paths: List[List[PathNodeBean]], resource_group: ResourceGroupBean, path_string_set: Set[str]
    ) -> List[List[PathNodeBean]]:
        for rrt in resource_group.related_resource_types:
            scope_str_paths = []
            inside_paths = []
            for path_list in rrt.iter_path_list(ignore_attribute=True):
                sp = path_list.to_path_string()
                # 处理路径中存在*的情况
                if sp.endswith(",*/"):
                    sp = sp[:-2]

                scope_str_paths.append(sp)

            for path in paths:
                ps = PathNodeBeanList.parse_obj(path).to_path_string()
                if ps not in path_string_set and self._is_path_match_scope_paths(path, scope_str_paths):
                    inside_paths.append(path)
                    path_string_set.add(ps)

            paths = inside_paths

        return paths

    def _is_path_match_scope_paths(self, path: List[PathNodeBean], scope_str_paths: List[str]):
        tp = PathNodeBeanList.parse_obj(path).to_path_string()
        for sp in scope_str_paths:
            if tp.startswith(sp):
                return True
        return False

    def check_policies(self, system_id: str, policies: List[PolicyBean]):
        """
        检查重构后的Policy结构
        """
        self._check_system_in_scope(system_id)
        for p in policies:
            self._check_policy_in_scope(system_id, p)

    def list_not_match_policy(self, system_id: str, policies: List[PolicyBean]) -> List[PolicyBean]:
        """与check_policies的检测逻辑一样，只是不直接抛异常，而是返回不满足的策略"""
        try:
            self._check_system_in_scope(system_id)
        except APIError:
            # 整个系统都不满足，则返回原有所有策略
            return policies

        # 遍历每条权限进行判断
        not_match_policies = []
        for p in policies:
            try:
                self._check_policy_in_scope(system_id, p)
            except APIError:
                not_match_policies.append(p)

        return not_match_policies

    def _check_policy_in_scope(self, system_id, policy: PolicyBean):
        if self._check_action_in_scope(system_id, policy.action_id) == ACTION_ALL:
            return

        policy_scope = self.system_action_scope[system_id][policy.action_id]
        differ = ActionScopeDiffer(policy, PolicyBean.parse_obj(policy_scope))
        if not differ.diff():
            raise error_codes.FORBIDDEN.format(
                message=_("{} 操作选择的资源实例不在分级管理员的授权范围内，请编辑分级管理员授权范围").format(policy.action_id), replace=True
            )  # 操作的资源选择范围不满足分级管理员的资源选择范围

    def check_systems(self, system_ids: List[str]):
        """检查系统是否符合角色的管理范围"""
        for system_id in system_ids:
            self._check_system_in_scope(system_id)

    def check_actions(self, system_id: str, action_ids: List[str]):
        self._check_system_in_scope(system_id)

        role_actions = RoleListQuery(self.role).list_scope_action_id(system_id)
        if ACTION_ALL in role_actions:
            return

        action_id_set = set(role_actions)
        for action_id in action_ids:
            if action_id not in action_id_set:
                raise error_codes.FORBIDDEN.format(
                    message=_("{} 操作不在角色的授权范围内").format(action_id), replace=True
                )  # 操作不在授权范围内


class RoleSubjectScopeChecker:
    """
    角色用户组授权范围检查
    """

    svc = RoleService()

    def __init__(self, role: Role):
        self.role = role

    # TODO 代码优化, 圈复杂度28, 规范要求20以下
    def check(self, subjects: List[Subject], raise_exception: bool = True) -> List[Subject]:
        if self.role.type == RoleType.STAFF.value:
            raise error_codes.FORBIDDEN  # 普通用户不能授权

        scopes = self.svc.list_subject_scope(self.role.id)
        scope_set = {(i.type, i.id) for i in scopes}

        # 任意则直接返回
        if (SUBJECT_TYPE_ALL, SUBJECT_ALL) in scope_set:
            return subjects

        # 若scope里已存在，则无需再校验
        need_check_subject = [s for s in subjects if (s.type, s.id) not in scope_set]
        # 若没有需要再校验的，则直接返回
        if not need_check_subject:
            return subjects

        # 剩下需要的校验的subject，若是用户则需要其所有所在部门(包括祖先部门)在scope部门里，若是部门则需要其祖先部门在scope部门里
        department_scopes = {int(s.id) for s in scopes if s.type == SubjectType.DEPARTMENT.value}

        # 【对于部门】则需要查询其祖先是否在department_scopes里，
        # 【对于用户】则需要查询用户在的所有部门的祖先是否在department_scopes里
        # 所有需要查询祖先的部门，为了减少DB查询，会先获取用户和部门需要查询祖先的所有部门，然后再一次性查询DB
        need_query_ancestor_departments = set()
        # 需要查询的用户
        need_query_users = set()
        for s in need_check_subject:
            if s.type == SubjectType.DEPARTMENT.value:
                need_query_ancestor_departments.add(int(s.id))
            elif s.type == SubjectType.USER.value:
                need_query_users.add(s.id)

        # DB查询用户，需要知道用户的所有在的部门，不包含部门的祖先 username 对应的 set(DepartmentIDs)
        user_direct_department = defaultdict(set)
        if need_query_users:
            users = User.objects.filter(username__in=need_query_users)
            # 查询用户直接加入的部门
            department_members = DepartmentMember.objects.filter(user_id__in=[i.id for i in users])
            # 这里是记录user_id与其直接部门ID的集合, user_id 对应的 set(DepartmentIDs)
            user_id_direct_departments = defaultdict(set)
            for dm in department_members:
                user_id_direct_departments[dm.user_id].add(dm.department_id)
            # 遍历每个用户，获得其所有所在的部门
            for u in users:
                # 将user_id_direct_departments转换为user_direct_department
                user_direct_department[u.username] = user_id_direct_departments[u.id]
                # 每个部门也是需要查询其祖先部门的
                need_query_ancestor_departments.update(user_id_direct_departments[u.id])

        # DB查询所有部门的祖先部门，包括部门本身
        department_ancestors = defaultdict(set)
        if need_query_ancestor_departments:
            departments = Department.objects.filter(id__in=need_query_ancestor_departments)
            for d in departments:
                department_ancestors[d.id] = set(d.ancestor_ids)
                department_ancestors[d.id].add(d.id)

        need_delete_set = set()

        # 开始校验
        for s in need_check_subject:
            # 【对于部门】则需要查询其祖先是否在department_scopes里，
            if s.type == SubjectType.DEPARTMENT.value:
                if len(department_ancestors[int(s.id)] & department_scopes) == 0:
                    if raise_exception:
                        raise error_codes.FORBIDDEN.format(
                            message=_("部门({})在分级管理员的授权范围内，请编辑分级管理员授权范围").format(s.id), replace=True
                        )

                    need_delete_set.add((s.type, s.id))

            elif s.type == SubjectType.USER.value:
                # 校验用户，需要查询遍历用户的每个直接部门，然后再去每个直接部门的祖先，所有祖先和直接部门的集合即为用户所有所在的部门
                department_set = set()
                for d in user_direct_department[s.id]:
                    department_set.update(department_ancestors[d])
                if len(department_set & department_scopes) == 0:
                    if raise_exception:
                        raise error_codes.FORBIDDEN.format(
                            message=_("用户({})在分级管理员的授权范围内，请编辑分级管理员授权范围").format(s.id), replace=True
                        )

                    need_delete_set.add((s.type, s.id))

        return [one for one in subjects if (one.type, one.id) not in need_delete_set]


class ActionScopeDiffer:
    """
    分级管理员创建的模板策略与分级管理员的scope限制范围比较
    """

    def __init__(self, template_policy: PolicyBean, scope_policy: PolicyBean):
        self.template_policy = template_policy
        self.scope_policy = scope_policy

    def diff(self) -> bool:
        """
        1. 遍历每个resource_group是否能包含
        2. 只要有一个不能包含就不能判断在范围内
        """
        for rg in self.template_policy.resource_groups:
            if not self._diff_related_resource_types(rg.related_resource_types, self.scope_policy):
                return False

        return True

    def _diff_related_resource_types(
        self, related_resource_types: List[RelatedResourceBean], scope_policy: PolicyBean
    ) -> bool:
        for rg in scope_policy.resource_groups:
            if self._diff_scope_resource_group(related_resource_types, rg):
                return True
        return False

    def _diff_scope_resource_group(
        self, related_resource_types: List[RelatedResourceBean], scope_resource_group: ResourceGroupBean
    ) -> bool:
        for rt in related_resource_types:
            scope_rt = scope_resource_group.get_related_resource_type(rt.system_id, rt.type)
            if not scope_rt:
                return False
            if not self._diff_conditions(rt.condition, scope_rt.condition):
                return False

        return True

    def _diff_instances(self, template_instances: List[InstanceBean], scope_instances: List[InstanceBean]) -> bool:
        scope_paths = []
        for i in scope_instances:
            for p in i.path:
                sp = p.to_path_string()

                # 处理路径中存在*的情况
                if sp.endswith(",*/"):
                    sp = sp[:-2]

                scope_paths.append(sp)

        for i in template_instances:
            for p in i.path:
                path = p.to_path_string()
                for sp in scope_paths:
                    if path.startswith(sp):
                        break
                else:
                    return False  # 模板中的某个路径, 不能满足任意一个范围中的路径

        return True

    def _diff_attributes(self, template_attributes: List[Attribute], scope_attributes: List[Attribute]) -> bool:
        template_attrs = {a.id: {v.id for v in a.values} for a in template_attributes}
        scope_attrs = {a.id: {v.id for v in a.values} for a in scope_attributes}

        # 模板的属性key必须包含所有范围的key, 属性key之间的关系为AND
        if not set(scope_attrs.keys()).issubset(set(template_attrs.keys())):
            return False

        for key in scope_attrs.keys():
            # 模板的属性值, 必须为范围属性值的一部分, 属性值之间的关系为OR
            if not template_attrs[key].issubset(scope_attrs[key]):
                return False

        return True

    def _diff_condition(self, template_condition: ConditionBean, scope_condition: ConditionBean) -> bool:
        # 范围只有实例, 模板也有实例, 只要实例满足范围即可
        if scope_condition.instances and not scope_condition.attributes and template_condition.instances:
            return self._diff_instances(template_condition.instances, scope_condition.instances)

        # 范围只有属性, 模板也有属性, 只要属性满足范围即可
        if scope_condition.attributes and not scope_condition.instances and template_condition.attributes:
            return self._diff_attributes(template_condition.attributes, scope_condition.attributes)

        # 范围既有属性又有实例, 模板也是既有属性, 既有实例, 分别比较实例与属性
        if (
            scope_condition.instances
            and scope_condition.attributes
            and template_condition.instances
            and template_condition.attributes
        ):
            return self._diff_instances(
                template_condition.instances, scope_condition.instances
            ) and self._diff_attributes(template_condition.attributes, scope_condition.attributes)

        return False

    def _diff_conditions(
        self, template_conditions: List[ConditionBean], scope_conditions: List[ConditionBean]
    ) -> bool:
        # 范围为任意
        if not scope_conditions:
            return True

        # 模板为任意, 但是范围有限制
        if not template_conditions and scope_conditions:
            return False

        # 笛卡尔积遍历计算, 模板的条件只要满足范围中一条就算是满足, 同时模板的中的条件必须所有都要满足范围中的一条
        for tc in template_conditions:
            for sc in scope_conditions:
                if self._diff_condition(tc, sc):
                    break
            else:
                return False  # 循环正常结束, tc不满足sc中的任意一条

        return True


@cached(timeout=60 * 60)  # 1 hour
def get_super_manager() -> Role:
    return Role.objects.filter(type=RoleType.SUPER_MANAGER.value).first()


def can_user_manage_role(username: str, role_id: int) -> bool:
    """是否用户能管理角色"""
    role_ids = [role_id]

    relation = RoleRelation.objects.filter(role_id=role_id).first()
    if relation:
        role_ids.append(relation.parent_id)

    super_manager = get_super_manager()
    if super_manager:
        role_ids.append(super_manager.id)

    return RoleUser.objects.filter(role_id__in=role_ids, username=username).exists()


class RoleResourceRelationHelper:
    """分析变更角色的资源关系"""

    svc = RoleService()

    def __init__(self, role: Role) -> None:
        self.role = role

    def handle(self):
        resource_nodes: Set[ResourceNodeBean] = set()

        # 遍历角色的所有资源范围, 分析出资源标签, 并创建数据
        auth_systems = self.svc.list_auth_scope(self.role.id)
        for system_actions in auth_systems:
            for action in system_actions.actions:
                policy = PolicyBean.parse_obj(action)
                if len(policy.list_thin_resource_type()) != 1:
                    continue

                for rg in policy.resource_groups:
                    rrt: RelatedResourceBean = rg.related_resource_types[0]  # type: ignore
                    for condition in rrt.condition:
                        # 忽略有属性的condition
                        if not condition.has_no_attributes():
                            continue

                        # 遍历所有的实例路径, 筛选出有查询有实例审批人的实例
                        for instance in condition.instances:
                            for path in instance.path:
                                first_node = path[0]
                                if (
                                    first_node.system_id,
                                    first_node.type,
                                ) not in settings.ROLE_RESOURCE_RELATION_TYPE_SET:
                                    continue

                                if len(path) == 1 or (len(path) == 2 and path[1].id == ANY_ID):
                                    resource_nodes.add(ResourceNodeBean.parse_obj(first_node))

        RoleResourceRelation.objects.filter(role_id=self.role.id).delete()

        if not resource_nodes:
            return

        labels = [
            RoleResourceRelation(
                role_id=self.role.id, system_id=node.system_id, resource_type_id=node.type, resource_id=node.id
            )
            for node in resource_nodes
        ]
        RoleResourceRelation.objects.bulk_create(labels, ignore_conflicts=True)


@cached(timeout=600)
def get_global_notification_config() -> Dict[str, Any]:
    """获取全局通知配置"""
    role = get_super_manager()
    notification_config = RolePolicyExpiredNotificationConfig.objects.filter(role_id=role.id).get()
    return notification_config.config


def update_periodic_permission_expire_remind_schedule(hour: int, minute: int) -> None:
    """更新周期性权限到期提醒调度"""
    name = "periodic_permission_expire_remind"

    task = PeriodicTask.objects.filter(name=name).prefetch_related("crontab").first()
    if not task:
        # 如果不存在, 则创建
        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute=minute,
            hour=hour,
            day_of_week="*",
            day_of_month="*",
            month_of_year="*",
            timezone=timezone.get_current_timezone(),
        )
        PeriodicTask.objects.create(
            crontab=schedule,
            name=name,
            task="config.celery_app.permission_expire_remind",
        )
        return

    schedule = task.crontab
    if int(schedule.minute) == minute and int(schedule.hour) == hour:
        # 如果没有变更, 则无需更新
        return

    if not PeriodicTask.objects.filter(crontab_id=task.crontab_id).exclude(name=name).exists():
        # 如果只有这一个任务, 则更新
        schedule.minute = minute
        schedule.hour = hour
        schedule.save()
        return

    schedule, _ = CrontabSchedule.objects.get_or_create(
        minute=minute,
        hour=hour,
        day_of_week="*",
        day_of_month="*",
        month_of_year="*",
        timezone=timezone.get_current_timezone(),
    )
    task = schedule
    task.save()
