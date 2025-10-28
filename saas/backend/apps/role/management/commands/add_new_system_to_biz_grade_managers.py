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
from typing import List

from django.core.management.base import BaseCommand

from backend.apps.group.models import Group
from backend.apps.role.constants import ManagementCommonActionNameEnum, ManagementGroupNameSuffixEnum
from backend.apps.role.models import Role, RoleRelatedObject
from backend.apps.role.tasks import AuthScopeActionGenerator, ResourceInstance
from backend.biz.group import GroupBiz, GroupTemplateGrantBean
from backend.biz.policy import PolicyBean, PolicyBeanList
from backend.biz.role import RoleBiz
from backend.component.cmdb import list_biz
from backend.service.action import ActionService
from backend.service.constants import RoleRelatedObjectType, RoleType
from backend.service.role import AuthScopeSystem


class Command(BaseCommand):
    """为包含运维组和查看组的分级管理员添加系统权限"""

    role_biz = RoleBiz()
    action_svc = ActionService()
    group_biz = GroupBiz()

    def add_arguments(self, parser):
        parser.add_argument("--system_id", type=str, help="系统ID", required=True)

    def handle(self, *args, **options):
        system_id = options["system_id"]
        biz_info = self.get_biz_info()
        biz_name_list = list(biz_info.keys())
        roles = Role.objects.filter(type=RoleType.GRADE_MANAGER.value, name__in=biz_name_list)
        for role in roles:
            group_ids = list(
                RoleRelatedObject.objects.filter(
                    role_id=role.id, object_type=RoleRelatedObjectType.GROUP.value
                ).values_list("object_id", flat=True)
            )
            ops_group = Group.objects.filter(
                id__in=group_ids, name=role.name + ManagementGroupNameSuffixEnum.OPS.value
            ).first()
            read_group = Group.objects.filter(
                id__in=group_ids, name=role.name + ManagementGroupNameSuffixEnum.READ.value
            ).first()

            instance = ResourceInstance(
                system_id=system_id, type="biz", id=biz_info[role.name]["bk_biz_id"], name=role.name
            )
            auth_scope_list = [self._init_system_auth_scope(system_id, instance)]

            # 更新管理空间授权范围
            self.role_biz.incr_update_auth_scope(role, auth_scope_list)

            # 更新运维组和查看组的授权模板
            ops_group_templates = self._generate_group_auth_templates(
                auth_scope_list, ManagementCommonActionNameEnum.OPS.value
            )
            read_group_templates = self._generate_group_auth_templates(
                auth_scope_list, ManagementCommonActionNameEnum.READ.value
            )

            if ops_group:
                try:
                    self.group_biz.grant(role, ops_group, ops_group_templates, need_check=True)
                except Exception as e:
                    self.stdout.write(f"grant ops group for {role.name} failed,error message: {e}")

            if read_group:
                try:
                    self.group_biz.grant(role, read_group, read_group_templates, need_check=True)
                except Exception as e:
                    self.stdout.write(f"grant read group for {role.name} failed,error message: {e}")

    def _init_system_auth_scope(self, system_id: str, instance: ResourceInstance):
        auth_scope = AuthScopeSystem(system_id=system_id, actions=[])
        common_action = self.role_biz.get_common_action_by_name(system_id, ManagementCommonActionNameEnum.OPS.value)
        if not common_action:
            self.stdout.write(
                f"system {system_id} is not configured common action {ManagementCommonActionNameEnum.OPS.value}",
            )
            return auth_scope
        # 2. 查询操作信息
        action_list = self.action_svc.new_action_list(system_id)

        # 3. 生成授权范围
        for action_id in common_action.action_ids:
            action = action_list.get(action_id)
            if not action:
                self.stdout.write(
                    f"system {system_id} action {action_id} not exists in common action"
                    f" {ManagementCommonActionNameEnum.OPS.value}"
                )
                continue

            # 分发者模式
            auth_scope_action = AuthScopeActionGenerator(system_id, action, instance).generate()

            if auth_scope_action:
                auth_scope.actions.append(auth_scope_action)

        return auth_scope

    def get_biz_info(self):
        biz_info = list_biz()
        return {one["bk_biz_name"]: one for one in biz_info["info"]}

    def _generate_group_auth_templates(self, authorization_scopes: List[AuthScopeSystem], name_suffix_type: str):
        templates = []
        for auth_scope in authorization_scopes:
            system_id = auth_scope.system_id
            actions = auth_scope.actions

            common_action = self.role_biz.get_common_action_by_name(system_id, name_suffix_type)
            if not common_action:
                self.stdout.write(f"system {system_id} is not configured common action {name_suffix_type}")
                continue

            actions = [a for a in actions if a.id in common_action.action_ids]

            policies = [PolicyBean.parse_obj(action) for action in actions]
            policy_list = PolicyBeanList(
                system_id=system_id,
                policies=policies,
                need_fill_empty_fields=True,  # 填充相关字段
            )

            template = GroupTemplateGrantBean(
                system_id=system_id,
                template_id=0,  # 自定义权限template_id为0
                policies=policy_list.policies,
            )

            templates.append(template)

        return templates

    def _get_ops_action_ids(self, system_id: str):
        common_action = self.role_biz.get_common_action_by_name(system_id, ManagementCommonActionNameEnum.OPS.value)
        if not common_action:
            self.stdout.write(
                f"system {system_id} is not configured common action {ManagementCommonActionNameEnum.OPS.value}"
            )
            return []
        return common_action.action_ids

    def _get_read_action_ids(self, system_id: str):
        common_action = self.role_biz.get_common_action_by_name(system_id, ManagementCommonActionNameEnum.READ.value)
        if not common_action:
            self.stdout.write(
                f"system {system_id} is not configured common action {ManagementCommonActionNameEnum.READ.value}"
            )
            return []
        return common_action.action_ids
