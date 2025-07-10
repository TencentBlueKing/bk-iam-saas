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

from rest_framework import exceptions, permissions

from backend.api.management.constants import (
    IGNORE_VERIFY_API_CONFIG,
    ManagementAPIEnum,
    VerifyAPIObjectTypeEnum,
    VerifyApiParamLocationEnum,
    VerifyAPIParamSourceToObjectTypeMap,
)
from backend.api.management.mixins import ManagementAPIPermissionCheckMixin
from backend.api.management.v2.serializers import ManagementGroupIDsSLZ, ManagementGroupsSLZ
from backend.apps.role.models import Role, RoleRelatedObject, RoleSource
from backend.service.constants import RoleRelatedObjectType, RoleSourceType, RoleType


class ManagementAPIPermission(permissions.IsAuthenticated, ManagementAPIPermissionCheckMixin):
    """
    管理类API权限校验，校验的参数主要来自request.data、request.query_params、url_kwargs参数和request认证过的数据
    需要配合 management_api_permission
    management_api_permission = {
        "请求函数名称": (鉴权所需参数来源，鉴权API名称)
    }
    鉴权所需参数来源对应是：VerifyAPIParamLocationEnum枚举值
    鉴权API名称对应是：ManagementAPIEnum枚举值
    对于需要忽略鉴权的请求函数，可配置IGNORE_VERIFY_API_CONFIG，即{"请求函数名称": IGNORE_VERIFY_API_CONFIG}
    """

    def has_permission(self, request, view):
        # ESB认证必须通过
        if not super().has_permission(request, view):
            return False

        # 若配置了当前鉴权Class，但是没有配套的management_api_permission，则直接不通过
        if not hasattr(view, "management_api_permission"):
            return False

        # 默认值即为请求method，因为继承于APIView（即使是ViewSet，ViewSet也是继承了APIView的）
        handler_name = request.method.lower()
        # ViewSet.as_view({...}) 设置了method的映射，则进行更新为映射的值
        if hasattr(view, "action"):
            handler_name = view.action

        # 判断要处理的函数, 即handler是否配置了权限,
        # 若没有配置权限控制，则直接不通过，若实际需要忽略鉴权的，可显示配置IGNORE_VERIFY_API_CONFIG
        if handler_name not in view.management_api_permission:
            return False

        # API认证与鉴权
        param_source, api = view.management_api_permission[handler_name]
        # 对于配置了忽略鉴权的，直接返回鉴权通过
        if (param_source, api) == IGNORE_VERIFY_API_CONFIG:
            return True

        # 若校验不通过，则会直接抛出exceptions.PermissionDenied异常
        self._verify_api(view, request, param_source, api)

        return True

    def _verify_api(self, view, request, param_source, api):
        """
        根据param_source获取request.data、request.query_params、url_kwargs中的数据，对API进行校验
        """
        # 所有API认证鉴权所需
        app_code = request.bk_app_code

        # 对于所有V2 API都需要校验（1）app_code 与 system client (2) 校验systems是否有API白名单权限
        system_id = request.parser_context["kwargs"]["system_id"]
        self.verify_api(app_code, system_id, api)

        # 对于仅需校验路径里的System，则上面verify_api已经校验
        if param_source == VerifyApiParamLocationEnum.SYSTEM_IN_PATH.value:
            return

        # 参数来自URL
        if param_source in [
            VerifyApiParamLocationEnum.ROLE_IN_PATH.value,
            VerifyApiParamLocationEnum.GROUP_IN_PATH.value,
        ]:
            # 取URL中的参数值
            object_id_key = view.lookup_url_kwarg or view.lookup_field
            # 由于URL参数是必然会获取得到的，否则是已经404的，不会执行到这里，所以可以直接[]获取而不需要判断是否存在
            object_id = request.parser_context["kwargs"][object_id_key]
            self._verify_api_by_object(
                app_code, VerifyAPIParamSourceToObjectTypeMap[param_source], int(object_id), api, system_id
            )
            return

        # 参数来自body data - group_ids
        if param_source == VerifyApiParamLocationEnum.GROUP_IDS_IN_BODY:
            slz = ManagementGroupIDsSLZ(data=request.data)
            slz.is_valid(raise_exception=True)
            group_ids = slz.validated_data["group_ids"]

            self._verify_api_by_groups(app_code, group_ids, api, system_id)
            return

        # 参数来自query - group_ids
        if param_source == VerifyApiParamLocationEnum.GROUP_IDS_IN_QUERY:
            group_ids_str = request.query_params.get("group_ids")
            group_ids = list(map(int, group_ids_str.split(",")))

            self._verify_api_by_groups(app_code, group_ids, api, system_id)
            return

        # 参数来自body data - groups
        if param_source == VerifyApiParamLocationEnum.GROUPS_IN_BODY:
            slz = ManagementGroupsSLZ(data=request.data)
            slz.is_valid(raise_exception=True)
            group_ids = [group["id"] for group in slz.validated_data["groups"]]

            self._verify_api_by_groups(app_code, group_ids, api, system_id)
            return

    def _verify_api_by_role(self, app_code: str, role_id: int, api: ManagementAPIEnum, system_id: str):
        """
        由于管理员API有很大一部分都是在需要在分级管理员角色下操作的
        所以该方法主要是封装了对角色下的API校验
        """
        # 查询分级管理员的来源系统
        role_source = RoleSource.objects.filter(source_type=RoleSourceType.API.value, role_id=role_id).first()
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
                    detail=f"role[{role_id}] can not be operated by app_code[{app_code}], "
                    f"since role is not created by system[{system_id})]."
                )
        else:
            source_system_id = role_source.source_system_id

        # API认证和API鉴权
        self.verify_api(app_code, source_system_id, api)

    def _verify_api_by_group(self, app_code: str, group_id: int, api: ManagementAPIEnum, system_id: str):
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
                detail=f"group[{group_id}] can not operated by app_code[{app_code}], "
                f"since related role of group is not created by system[{system_id})]."
            )
        # 使用角色校验API
        self._verify_api_by_role(app_code, role_related_object.role_id, api, system_id)

    def _verify_api_by_object(
        self,
        app_code: str,
        object_type: VerifyAPIObjectTypeEnum,
        object_id: int,
        api: ManagementAPIEnum,
        system_id: str,
    ):
        """
        对Group/Role等对象下操作的管理类API认证和鉴权
        其实上是对verify_api_by_role和verify_api_by_group的统一封装
        """
        if object_type not in [VerifyAPIObjectTypeEnum.ROLE.value, VerifyAPIObjectTypeEnum.GROUP.value]:
            raise exceptions.PermissionDenied(detail=f"not support verify api by [{object_type}]")

        if object_type == VerifyAPIObjectTypeEnum.ROLE.value:
            self._verify_api_by_role(app_code, object_id, api, system_id)
        elif object_type == VerifyAPIObjectTypeEnum.GROUP.value:
            self._verify_api_by_group(app_code, object_id, api, system_id)

    def _verify_api_by_groups(self, app_code: str, group_ids: List[int], api: ManagementAPIEnum, system_id: str):
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
                f"since related role of group is not created by system[{system_id})]."
            )

        # 使用角色校验API
        role_ids_set = {r.role_id for r in role_related_objects}
        for role_id in role_ids_set:
            self._verify_api_by_role(app_code, role_id, api, system_id)
