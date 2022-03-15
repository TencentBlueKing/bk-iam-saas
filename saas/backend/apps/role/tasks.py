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
from urllib.parse import urlencode

from celery import task
from django.conf import settings
from django.template.loader import render_to_string

from backend.apps.group.models import Group
from backend.apps.role.models import Role, RoleRelatedObject, RoleUser
from backend.biz.group import GroupBiz
from backend.biz.role import RoleBiz, RoleInfoBean
from backend.biz.system import SystemBiz
from backend.common.time import get_soon_expire_ts
from backend.component import esb
from backend.service.constants import RoleRelatedObjectType, RoleType
from backend.util.url import url_join

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

        mail_content = render_to_string("group_expired_mail.html", {"groups": groups, "role": role, "url": url})

        usernames = RoleUser.objects.filter(role_id=role.id).values_list("username", flat=True)
        try:
            esb.send_mail(",".join(usernames), "蓝鲸权限中心用户组续期提醒", mail_content)
        except Exception:  # pylint: disable=broad-except
            logger.exception("send role_group_expire_remind email fail, usernames=%s", usernames)
