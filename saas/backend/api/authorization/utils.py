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
from typing import Dict, List

from pydantic.tools import parse_obj_as

from backend.apps.role.models import RoleScope
from backend.biz.policy import PolicyBean
from backend.biz.resource import ResourceBiz, ResourceNodeBean
from backend.biz.role import RoleAuthorizationScopeChecker, RoleBiz
from backend.common.error_codes import APIException
from backend.service.constants import RoleScopeType
from backend.service.models import Action, Policy, RelatedResource, ResourceInstance, Subject, group_paths
from backend.service.role import AuthScopeAction, AuthScopeSystem
from backend.util.json import json_dumps


# TODO: [重构]迁移到biz.trans下
def join_ancestors_to_resource_instances(system_id: str, _type: str, instances: List[Dict]) -> List[ResourceInstance]:
    """将资源实例和其祖先组装成ResourceInstance对象"""
    resource_biz = ResourceBiz()

    paths: List[List[Dict]] = []  # 多个以path方式表示的实例
    for instance in instances:
        _id = instance["id"]
        name = instance["name"]
        ancestors = instance.get("ancestors")
        # 资源实例实例，处理成路径方式表示
        path: List[Dict] = []
        # 处理祖先填充Name
        if ancestors:
            # 需要查询的资源实例,祖先每个实例都需要
            resource_nodes = [ResourceNodeBean(system_id=r["system"], type=r["type"], id=r["id"]) for r in ancestors]
            # 查询资源Name
            resource_node_name_dict = resource_biz.fetch_resource_name(resource_nodes, raise_not_found_exception=True)
            # 组装成路径
            for r in ancestors:
                ancestor_name = resource_node_name_dict.get_name(r["system"], r["type"], r["id"])
                path.append({"system_id": r["system"], "type": r["type"], "id": r["id"], "name": ancestor_name})

        # 层级最后一个是要创建的资源实例
        path.append({"system_id": system_id, "type": _type, "id": _id, "name": name})

        # 追加每个以path方式表示的实例
        paths.append(path)

    # 将多个以path方式表示的实例进行分组
    group_instances = group_paths(paths)

    resource_instance = ResourceInstance(
        system_id=system_id, type=_type, instances=group_instances, type_name=_type, type_name_en=_type
    )

    return [resource_instance]


# TODO: [重构]待重构open模块时一起迁移或重构掉
def check_scope(system_id: str, actions: List[Action], subject: Subject, resources: List[ResourceInstance]):
    policies = []
    for action in actions:
        # 创建新的policy
        related_resource_types = []
        if len(action.related_resource_types) > 0:
            related_resource_types = [RelatedResource.from_resource_instance(r) for r in resources]
        policy = Policy(id=action.id, related_resource_types=related_resource_types, type=action.type)
        policies.append(policy)

    policy_beans = [PolicyBean.parse_obj(p.dict()) for p in policies]
    role = RoleBiz().get_role_by_group_id(int(subject.id))
    # 校验权限是否满足角色的管理范围
    scope_checker = RoleAuthorizationScopeChecker(role)
    try:
        scope_checker.check_policies(system_id, policy_beans)
    except APIException:
        # Note: 这里是临时处理方案，最终方案是完全支持权限模型变更
        # 临时方案：校验不通过，则修改分级管理员的权限范围，使其通过
        _add_policies_to_role_authorization_scope(scope_checker, system_id, policy_beans)


def _add_policies_to_role_authorization_scope(
    scope_checker: RoleAuthorizationScopeChecker, system_id: str, policies: List[PolicyBean]
):
    """添加权限到分级管理员的范围里"""
    # 需要被添加的策略列表
    need_added_policies = []

    # Note: 以下代码里有调用 scope_checker 的 protected 方法是因为暂时不侵入修改scope_checker来提供一个public方法
    try:
        scope_checker._check_system_in_scope(system_id)
        # 如果不需要整个系统都添加，则遍历每条权限进行判断
        for p in policies:
            try:
                scope_checker._check_policy_in_scope(system_id, p)
            except APIException:
                # 校验不通过的，则需要添加到分级管理员范围内
                need_added_policies.append(p)
    except APIException:
        # 整个系统都不在分级管理员的授权范围内，则所有policies都需要添加到分级管理员范围内
        need_added_policies = policies

    if len(need_added_policies) == 0:
        return

    # 获取分级管理员可授权范围
    role_id = scope_checker.role.id
    auth_scopes: List[AuthScopeSystem] = RoleBiz().list_auth_scope(role_id)

    # 找到对应要变更的系统位置
    index = -1
    for idx, auth_scope in enumerate(auth_scopes):
        if auth_scope.system_id == system_id:
            index = idx
            break

    # 新老策略进行合并
    policies_dict = {p.id: PolicyBean.parse_obj(p) for p in auth_scopes[index].actions} if index != -1 else {}
    for policy in need_added_policies:
        # 不在，表示新增的
        if policy.action_id not in policies_dict:
            policies_dict[policy.action_id] = policy
            continue
        # 策略合并
        policy.add_related_resource_types(policies_dict[policy.action_id].related_resource_types)
        policies_dict[policy.action_id] = policy

    auth_scope = AuthScopeSystem(
        system_id=system_id, actions=parse_obj_as(List[AuthScopeAction], [p.dict() for p in policies_dict.values()])
    )

    # 若系统不在可授权范围内，则直接追加，否则替换掉
    if index == -1:
        auth_scopes.append(auth_scope)
    else:
        auth_scopes[index] = auth_scope

    # 保存
    RoleScope.objects.filter(role_id=role_id, type=RoleScopeType.AUTHORIZATION.value).update(
        content=json_dumps([one.dict() for one in auth_scopes]),
    )
