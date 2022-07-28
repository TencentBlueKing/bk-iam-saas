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

from rest_framework import exceptions

from backend.api.constants import ALLOW_ANY
from backend.api.mixins import SystemClientCheckMixin
from backend.apps.role.models import Role, RoleRelatedObject, RoleSource
from backend.common.cache import cachedmethod
from backend.service.constants import RoleRelatedObjectType, RoleSourceTypeEnum, RoleType

from .constants import ManagementAPIEnum, VerifyAPIObjectTypeEnum
from .models import ManagementAPIAllowListConfig, SystemAllowAuthSystem


class ManagementAPIPermissionCheckMixin(SystemClientCheckMixin):
    """管理类API认证与鉴权
    1. API认证：校验app_code与system
    2. API鉴权: 查询管理类API白名单表
    3. API数据鉴权：查询系统可管控的授权系统表
    """

    @cachedmethod(timeout=5 * 60)  # 缓存5分钟
    def verify_api_allow_list(self, system_id: str, api: ManagementAPIEnum):
        """
        API鉴权: 查询管理类API白名单表，判断是否允许访问API
        """
        allowed = ManagementAPIAllowListConfig.is_allowed(system_id, api)
        if not allowed:
            raise exceptions.PermissionDenied(detail=f"system[{system_id}] does not allow call management api[{api}]")

    def verify_system_scope(self, system_id: str, auth_system_ids: List[str]):
        """
        API数据鉴权：查询系统可管控的授权系统表，校验接入系统是否越权提交了其他系统的数据
        主要是针对分级管理员创建和更新时的可授权范围
        """
        # 加速判断：大部分系统都只是管理自身系统的权限，即可授权范围里的每个系统都只能等于自身
        if all([sys_id == system_id for sys_id in auth_system_ids]):
            return

        #  接入系统可管控的系统表[system_id/auth_system_id]来实现管控更多接入系统权限
        allowed_auth_system = list(
            SystemAllowAuthSystem.objects.filter(system_id=system_id).values_list("auth_system_id", flat=True)
        )
        allowed_system_ids = set(allowed_auth_system)
        # 任何系统都允许访问自身
        allowed_system_ids.add(system_id)

        # 如果允许管理的系统存在任意，则说明该系统可管理所有系统，鉴权直接通过
        if ALLOW_ANY in allowed_system_ids:
            return

        # 遍历校验
        for sys_id in auth_system_ids:
            if sys_id not in allowed_system_ids:
                raise exceptions.PermissionDenied(
                    detail=f"system[{system_id}] does not operate system[{sys_id}]'s permission data"
                )

    def verify_api(self, app_code: str, system_id: str, api: ManagementAPIEnum):
        """
        该方法为最常用的API认证和鉴权方法，包括：校验app_code与system和校验管理类API权限
        """
        # API认证
        self.verify_system_client(system_id, app_code)
        # API鉴权
        self.verify_api_allow_list(system_id, api)

    def verify_api_by_role(self, app_code: str, role_id: int, api: ManagementAPIEnum, system_id: str = ""):
        """
        由于管理员API有很大一部分都是在需要在分级管理员角色下操作的
        所以该方法主要是封装了对角色下的API校验
        """
        # 查询分级管理员的来源系统
        role_source = RoleSource.objects.filter(source_type=RoleSourceTypeEnum.API.value, role_id=role_id).first()
        # 角色来源不存在，说明页面创建或默认初始化的，非API创建，所以任何系统都无法操作
        if role_source is None:
            # 如果role是对应system_id的系统管理员，则其来源则默认为传入的系统
            if (
                system_id
                and Role.objects.filter(id=role_id, type=RoleType.SYSTEM_MANAGER.value, code=system_id).exists()
            ):
                source_system_id = system_id

            else:
                raise exceptions.PermissionDenied(
                    detail=f"role[{role_id}] can not be operated by app_code[{app_code}], since role source not exists"
                )
        else:
            source_system_id = role_source.source_system_id

        # API认证和API鉴权
        self.verify_api(app_code, source_system_id, api)

    def verify_api_by_group(self, app_code: str, group_id: int, api: ManagementAPIEnum, system_id: str = ""):
        """
        对用户组下的对象进行操作时，比如增删成员、添加权限等，需要进行API认证鉴权
        所以该方法主要是封装了对用户组下的API校验
        """
        # 查询用户组的来源角色
        role_related_object = RoleRelatedObject.objects.filter(
            object_type=RoleRelatedObjectType.GROUP.value, object_id=group_id
        ).first()
        # 查询不到用户组对应的角色，说明无权限访问
        if role_related_object is None:
            raise exceptions.PermissionDenied(
                detail=f"group[{group_id}] can not operated by app_code[{app_code}], since related role not exists"
            )
        # 使用角色校验API
        self.verify_api_by_role(app_code, role_related_object.role_id, api, system_id)

    def verify_api_by_object(
        self,
        app_code: str,
        object_type: VerifyAPIObjectTypeEnum,
        object_id: int,
        api: ManagementAPIEnum,
        system_id: str = "",
    ):
        """
        对Group/Role等对象下操作的管理类API认证和鉴权
        其实上是对verify_api_by_role和verify_api_by_group的统一封装
        """
        if object_type not in [VerifyAPIObjectTypeEnum.ROLE.value, VerifyAPIObjectTypeEnum.GROUP.value]:
            raise exceptions.PermissionDenied(detail=f"not support verify api by [{object_type}]")

        if object_type == VerifyAPIObjectTypeEnum.ROLE.value:
            self.verify_api_by_role(app_code, object_id, api, system_id)
        elif object_type == VerifyAPIObjectTypeEnum.GROUP.value:
            self.verify_api_by_group(app_code, object_id, api, system_id)

    def verify_api_by_groups(self, app_code: str, group_ids: List[int], api: ManagementAPIEnum, system_id: str = ""):
        """
        批量操作用户组，需要进行API认证鉴权
        所以该方法主要是封装了对用户组下的API校验
        """
        # 查询用户组的来源角色
        role_related_objects = RoleRelatedObject.objects.filter(
            object_type=RoleRelatedObjectType.GROUP.value, object_id__in=group_ids
        )
        # 所有用户组都必须有一一对应的角色，否则说明是越权请求
        # 有角色关联的用户组
        related_group_ids = {r.object_id for r in role_related_objects}
        # 无角色关联的用户组，即未认证过的用户组ID
        unauthorized_group_ids = [group_id for group_id in group_ids if group_id not in related_group_ids]
        # 如果存在未认证的用户组ID，则说明越权了
        if len(unauthorized_group_ids) > 0:
            raise exceptions.PermissionDenied(
                detail=f"groups[{unauthorized_group_ids}] can not operated by app_code[{app_code}], "
                f"since related role not exists"
            )

        # 使用角色校验API
        role_ids_set = {r.role_id for r in role_related_objects}
        for role_id in role_ids_set:
            self.verify_api_by_role(app_code, role_id, api, system_id)
