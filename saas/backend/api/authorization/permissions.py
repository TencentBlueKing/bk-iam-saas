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

from rest_framework import permissions

from backend.api.mixins import SystemClientCheckMixin

from .constants import VerifyApiParamLocationEnum
from .mixins import AuthorizationAPIAllowListCheckMixin
from .serializers import AuthActionSLZ, AuthActionsSLZ, AuthResourceTypeSLZ, AuthSystemSLZ


class AuthorizationAPIPermission(
    permissions.IsAuthenticated, SystemClientCheckMixin, AuthorizationAPIAllowListCheckMixin
):
    """
    授权类API权限校验，校验的参数主要来自request.data、request.query_params、url_kwargs参数和request认证过的数据
    需要配合 authorization_api_permission
    authorization_api_permission = {
        "请求函数名称": (鉴权所需参数来源，鉴权API类型)
    }
    鉴权所需参数来源对应是：VerifyAPIParamLocationEnum枚举值
    鉴权API类型对应是：AuthorizationAPIEnum枚举值
    """

    def has_permission(self, request, view):
        # ESB认证必须通过
        if not super().has_permission(request, view):
            return False

        # 若配置了当前鉴权Class，但是没有配套的management_api_permission，则直接不通过
        if not hasattr(view, "authorization_api_permission"):
            return False

        # 默认值即为请求method，因为继承于APIView（即使是ViewSet，ViewSet也是继承了APIView的）
        handler_name = request.method.lower()
        # ViewSet.as_view({...}) 设置了method的映射，则进行更新为映射的值
        if hasattr(view, "action"):
            handler_name = view.action

        # 判断要处理的函数, 即handler是否配置了权限,
        # 若没有配置权限控制，则直接不通过
        if handler_name not in view.authorization_api_permission:
            return False

        # API认证与鉴权
        param_source, api = view.authorization_api_permission[handler_name]
        # 若校验不通过，则会直接抛出exceptions.PermissionDenied异常
        self._verify_api(request, param_source, api)

        return True

    def _verify_api(self, request, param_source, api):
        """
        根据param_source获取request.data、request.query_params、url_kwargs中的数据，对API进行校验
        """
        # 所有API认证鉴权所需
        app_code = request.bk_app_code

        # 对于所有授权接口，都必须校验调用方是否能访问该系统
        system_slz = AuthSystemSLZ(data=request.data)
        system_slz.is_valid(raise_exception=True)
        system_id = system_slz.validated_data["system"]
        self.verify_system_client(system_id, app_code)

        # 如果仅仅是校验System，则上面已校验，可以直接忽略了
        if param_source == VerifyApiParamLocationEnum.SYSTEM_IN_BODY.value:
            return

        # 资源类型
        if param_source == VerifyApiParamLocationEnum.RESOURCE_TYPE_IN_BODY.value:
            slz = AuthResourceTypeSLZ(data=request.data)
            slz.is_valid(raise_exception=True)
            resource_type_id = slz.validated_data["type"]
            self.verify_api(system_id, resource_type_id, api)
            return

        # 操作
        if param_source == VerifyApiParamLocationEnum.ACTION_IN_BODY.value:
            slz = AuthActionSLZ(data=request.data)
            slz.is_valid(raise_exception=True)
            action_id = slz.validated_data["action"]["id"]
            self.verify_api(system_id, action_id, api)
            return

        if param_source == VerifyApiParamLocationEnum.ACTIONS_IN_BODY.value:
            slz = AuthActionsSLZ(data=request.data)
            slz.is_valid(raise_exception=True)
            action_ids = [a["id"] for a in slz.validated_data["actions"]]
            self.verify_api_by_object_ids(system_id, action_ids, api)
            return
