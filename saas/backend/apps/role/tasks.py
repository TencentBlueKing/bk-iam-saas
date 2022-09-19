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
from typing import Set
from urllib.parse import urlencode

from blue_krill.web.std_error import APIError
from celery import Task, task
from django.conf import settings
from django.template.loader import render_to_string

from backend.apps.group.models import Group
from backend.apps.role.models import Role, RoleRelatedObject, RoleUser
from backend.biz.action import ActionBiz
from backend.biz.group import GroupBiz, GroupTemplateGrantBean
from backend.biz.policy import PolicyBean, PolicyBeanList
from backend.biz.role import RoleBiz, RoleCheckBiz, RoleInfoBean
from backend.biz.system import SystemBiz
from backend.common.time import get_soon_expire_ts
from backend.component import esb
from backend.component.cmdb import list_biz
from backend.component.sops import list_project
from backend.service.constants import ADMIN_USER, RoleRelatedObjectType, RoleType
from backend.service.models.policy import ResourceGroupList
from backend.service.models.subject import Subject
from backend.service.role import AuthScopeAction, AuthScopeSystem
from backend.util.url import url_join
from backend.util.uuid import gen_uuid

from .constants import ManagementCommonActionNameEnum, ManagementGroupNameSuffixEnum

logger = logging.getLogger("celery")


@task(ignore_result=True)
def sync_system_manager():
    """
    创建系统管理员
    """
    # 查询后端所有的系统信息
    systems = {system.id: system for system in SystemBiz().list()}

    # 查询已创建的系统管理员的系统id
    exists_system_ids = Role.objects.filter(type=RoleType.SYSTEM_MANAGER.value).values_list("code", flat=True)

    # 遍历创建还未创建的系统管理员
    for system_id in set(systems.keys()) - set(exists_system_ids):
        system = systems[system_id]
        logger.info("create system_manager for system_id: %s", system_id)

        data = {
            "type": RoleType.SYSTEM_MANAGER.value,
            "code": system_id,
            "name": f"{system.name}",
            "name_en": f"{system.name_en}",
            "description": "",
            "members": [],
            "authorization_scopes": [{"system_id": system_id, "actions": [{"id": "*", "related_resource_types": []}]}],
            "subject_scopes": [{"type": "*", "id": "*"}],
        }
        RoleBiz().create(RoleInfoBean.parse_obj(data), "admin")


@task(ignore_result=True)
def role_group_expire_remind():
    """
    角色管理的用户组过期提醒
    """
    group_biz = GroupBiz()

    base_url = url_join(settings.APP_URL, "/group-perm-renewal")

    expired_at = get_soon_expire_ts()
    qs = Role.objects.all()
    for role in qs:
        group_ids = list(
            RoleRelatedObject.objects.filter(
                role_id=role.id, object_type=RoleRelatedObjectType.GROUP.value
            ).values_list("object_id", flat=True)
        )
        if not group_ids:
            continue

        exist_group_ids = group_biz.list_exist_groups_before_expired_at(group_ids, expired_at)
        if not exist_group_ids:
            continue

        groups = Group.objects.filter(id__in=exist_group_ids)

        params = {"source": "email", "current_role_id": role.id, "role_type": role.type}
        url = base_url + "?" + urlencode(params)

        mail_content = render_to_string(
            "group_expired_mail.html", {"groups": groups, "role": role, "url": url, "index_url": settings.APP_URL}
        )

        usernames = RoleUser.objects.filter(role_id=role.id).values_list("username", flat=True)
        try:
            esb.send_mail(",".join(usernames), "蓝鲸权限中心用户组续期提醒", mail_content)
        except Exception:  # pylint: disable=broad-except
            logger.exception("send role_group_expire_remind email fail, usernames=%s", usernames)


class InitBizGradeManagerTask(Task):
    biz = RoleBiz()
    role_check_biz = RoleCheckBiz()
    group_biz = GroupBiz()
    action_biz = ActionBiz()

    _exist_names: Set[str] = set()

    def run(self):
        biz_info = list_biz()
        biz_id_set = [one["bk_biz_id"] for one in biz_info["info"]]

        projects = list_project()
        for project in projects:
            if project["bk_biz_id"] in biz_id_set:
                self._create_grade_manager(project)

    def _create_grade_manager(self, project):
        biz_name = project["name"]
        if biz_name in self._exist_names:
            return

        try:
            self.role_check_biz.check_unique_name(biz_name)
        except APIError:
            # 缓存结果
            self._exist_names.add(biz_name)
            return

        role_info = self._init_role_info(project)

        role = self.biz.create(role_info, ADMIN_USER)

        # 创建用户组并授权
        authorization_scopes = role_info.dict()["authorization_scopes"]
        for name_suffix in [ManagementGroupNameSuffixEnum.OPS.value, ManagementGroupNameSuffixEnum.READ.value]:
            description = "{}业务运维人员的权限".format(biz_name)
            if name_suffix == ManagementGroupNameSuffixEnum.READ.value:
                description = "仅包含{}各系统的查看权限".format(biz_name)

            group = self.group_biz.create_and_add_members(
                role.id,
                biz_name + name_suffix,
                description=description,
                creator=ADMIN_USER,
                subjects=[],
                expired_at=0,
            )

            templates = self._init_group_auth_info(authorization_scopes, name_suffix)
            self.group_biz.grant(role, group, templates)

        self._exist_names.add(biz_name)

    def _init_role_info(self, data):
        """
        创建初始化分级管理员数据

        1. 遍历各个需要初始化的系统
        2. 查询系统的常用操作与系统的操作信息, 拼装出授权范围
        3. 返回role info
        """
        role_info = RoleInfoBean(
            name=data["name"],
            description="管理员可授予他人{}业务的权限".format(data["name"]),
            members=[ADMIN_USER],
            subject_scopes=[Subject(type="*", id="*")],
            authorization_scopes=[],
        )

        # 默认需要初始化的系统列表
        systems = settings.INIT_GRADE_MANAGER_SYSTEM_LIST
        bk_sops_system = "bk_sops"
        for system_id in systems:
            resource_type = "biz" if system_id != bk_sops_system else "project"
            resource_system = "bk_cmdb" if system_id != bk_sops_system else bk_sops_system
            resource_id = data["bk_biz_id"] if system_id != bk_sops_system else data["project_id"]
            resource_name = data["name"]

            auth_scope = AuthScopeSystem(system_id=system_id, actions=[])

            # 1. 查询常用操作
            common_action = self.biz.get_common_action_by_name(system_id, ManagementCommonActionNameEnum.OPS.value)
            if not common_action:
                continue

            # 2. 查询操作信息
            action_list = self.action_biz.list(system_id)

            # 3. 生成授权范围
            for action_id in common_action.action_ids:
                action = action_list.get(action_id)
                if not action:
                    continue

                # 不关联资源类型的操作
                if len(action.related_resource_types) == 0:
                    auth_scope_action = AuthScopeAction(id=action.id, resource_groups=ResourceGroupList(__root__=[]))
                else:
                    policy_data = {
                        "id": action.id,
                        "resource_groups": [
                            {
                                "related_resource_types": [
                                    {
                                        "system_id": rrt.system_id,
                                        "type": rrt.id,
                                        "condition": [
                                            {
                                                "id": gen_uuid(),
                                                "instances": [
                                                    {
                                                        "type": resource_type,
                                                        "path": [
                                                            [
                                                                {
                                                                    "id": resource_id,
                                                                    "name": resource_name,
                                                                    "system_id": resource_system,
                                                                    "type": resource_type,
                                                                }
                                                            ]
                                                        ],
                                                    }
                                                ],
                                                "attributes": [],
                                            }
                                        ],
                                    }
                                    for rrt in action.related_resource_types
                                ]
                            }
                        ],
                    }
                    auth_scope_action = AuthScopeAction.parse_obj(policy_data)

                auth_scope.actions.append(auth_scope_action)

            # 4. 组合授权范围
            if auth_scope.actions:
                role_info.authorization_scopes.append(auth_scope)

        return role_info

    def _init_group_auth_info(self, authorization_scopes, name_suffix: str):
        templates = []
        for auth_scope in authorization_scopes:
            system_id = auth_scope["system_id"]
            actions = auth_scope["actions"]
            if name_suffix == ManagementGroupNameSuffixEnum.READ.value:
                common_action = self.biz.get_common_action_by_name(
                    system_id, ManagementCommonActionNameEnum.READ.value
                )
                if not common_action:
                    continue

                actions = [a for a in actions if a["id"] in common_action.action_ids]

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
