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
from itertools import groupby
from typing import Any, Dict, List

from blue_krill.web.std_error import APIError

from backend.apps.role.models import Role
from backend.biz.resource import ResourceInfoBean, ResourceInfoDictBean
from backend.service.constants import ADMIN_USER
from backend.service.resource import ResourceProvider

from .group import GroupBiz
from .role import RoleBiz


def new_resource_provider(system_id: str, resource_type_id: str):
    return ResourceProvider(system_id, resource_type_id)


def fetch_auth_attributes(
    system_id: str, resource_type_id: str, ids: List[str], raise_api_exception=False
) -> ResourceInfoDictBean:
    """
    查询所有资源实例的用于鉴权的属性，同时如果查询有问题，则直接忽略错误
    """
    rp = new_resource_provider(system_id, resource_type_id)

    # 鉴权属性，需要包括拓扑路径，这种由权限中心产生的
    # TODO: _bk_iam_path_ 需要提取为常量，目前多处都直接裸写
    attrs = ["_bk_iam_path_"]
    # 查询支持该资源类型配置的属性
    try:
        resource_attrs = rp.list_attr()
        attrs.extend([i.id for i in resource_attrs])
    except APIError as error:
        logging.info(f"fetch_resource_all_auth_attributes({system_id}, {resource_type_id}) list_attr error: {error}")
        # 判断是否忽略接口异常
        if raise_api_exception:
            raise error

    # 查询资源实例的属性
    try:
        resource_infos = rp.fetch_instance_info(ids, attrs)
    except APIError as error:
        logging.info(
            f"fetch_resource_all_auth_attributes({system_id}, {resource_type_id}) "
            f"fetch_instance_info error: {error}"
        )
        # 不需要抛异常则直接返回
        if not raise_api_exception:
            return ResourceInfoDictBean(data={})
        raise error

    return ResourceInfoDictBean(data={i.id: ResourceInfoBean(**i.dict()) for i in resource_infos})


def exec_fill_resources_attribute(system_id, resource_type_id, resources):
    # 查询属性
    resource_ids = list({resource["id"] for resource in resources})
    resource_info_dict = fetch_auth_attributes(
        system_id=system_id, resource_type_id=resource_type_id, ids=resource_ids, raise_api_exception=False
    )
    # 填充属性
    for resource in resources:
        _id = resource["id"]
        if not resource_info_dict.has(_id):
            continue
        attrs = resource_info_dict.get_attributes(_id, ignore_none_value=True)
        # 填充
        resource["attribute"] = attrs


def fill_resources_attribute(resources: List[Dict[str, Any]]):
    """
    为资源实例填充属性
    """
    need_fetch_resources = []
    for resource in resources:
        if resource["id"] != "*" and not resource["attribute"]:
            need_fetch_resources.append(resource)

    if not need_fetch_resources:
        return

    for key, parts in groupby(need_fetch_resources, key=lambda resource: (resource["system"], resource["type"])):
        exec_fill_resources_attribute(key[0], key[1], list(parts))


class RoleSyncGroupBiz:
    """
    角色同步权限用户组操作
    """

    role_biz = RoleBiz()
    group_biz = GroupBiz()

    def delete_role_member(self, role: Role, username: str, operator: str = ADMIN_USER):
        """
        删除成员, 同时删除相关的权限
        """
        self.role_biz.delete_member(role.id, username)

        if role.sync_perm:
            self.group_biz.update_sync_perm_group_by_role(role, operator, sync_members=True)

    def batch_add_grade_manager_member(self, role: Role, usernames: List[str], operator: str = ADMIN_USER):
        """
        批量增加分级管理员成员
        """
        # 批量添加成员(添加时去重)
        self.role_biz.add_grade_manager_members(role.id, usernames)

        # 同步权限用户组成员
        if role.sync_perm:
            self.group_biz.update_sync_perm_group_by_role(role, operator, sync_members=True)

    def batch_delete_grade_manager_member(self, role: Role, usernames: List[str], operator: str = ADMIN_USER):
        """
        批量删除分级管理员成员
        """
        self.role_biz.delete_grade_manager_member(role.id, usernames)

        # 同步权限用户组成员
        if role.sync_perm:
            self.group_biz.update_sync_perm_group_by_role(role, operator, sync_members=True)
