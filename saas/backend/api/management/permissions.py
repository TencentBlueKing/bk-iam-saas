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

from .constants import IGNORE_VERIFY_API_CONFIG, VerifyAPIParamLocationEnum, VerifyAPIParamSourceToObjectTypeMap
from .mixins import ManagementAPIPermissionCheckMixin
from .serializers import ManagementGroupIDsSLZ, ManagementSourceSystemSLZ


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
        return self._verify_api(view, request, param_source, api)

    def _verify_api(self, view, request, param_source, api):
        """
        根据param_source获取request.data、request.query_params、url_kwargs中的数据，对API进行校验
        """
        # 所有API认证鉴权所需
        app_code = request.bk_app_code

        # 参数来着URL
        if param_source in [
            VerifyAPIParamLocationEnum.ROLE_IN_PATH.value,
            VerifyAPIParamLocationEnum.GROUP_IN_PATH.value,
        ]:
            # 取URL中的参数值
            object_id_key = view.lookup_url_kwarg or view.lookup_field
            # 由于URL参数是必然会获取得到的，否则是已经404的，不会执行到这里，所以可以直接[]获取而不需要判断是否存在
            object_id = request.parser_context["kwargs"][object_id_key]
            self.verify_api_by_object(app_code, VerifyAPIParamSourceToObjectTypeMap[param_source], int(object_id), api)
            return True

        # 参数system来着Body Data或Query
        if param_source in [
            VerifyAPIParamLocationEnum.SYSTEM_IN_BODY.value,
            VerifyAPIParamLocationEnum.SYSTEM_IN_QUERY.value,
        ]:
            # 确定参数是在body还是在query里
            request_params = (
                request.data
                if param_source == VerifyAPIParamLocationEnum.SYSTEM_IN_BODY.value
                else request.query_params
            )
            # 取request body/param参数值, TODO: 后续考虑是否约定传入所需参数的Key列表
            # 序列化保证system参数一定存在，这里序列化只解析了需要的，不会将其他的进行解析
            slz = ManagementSourceSystemSLZ(data=request_params)
            slz.is_valid(raise_exception=True)
            source_system_id = slz.validated_data["system"]

            self.verify_api(app_code, source_system_id, api)
            return True

        # 参数来着body data - group_ids
        if param_source == VerifyAPIParamLocationEnum.GROUP_IDS_IN_BODY:
            slz = ManagementGroupIDsSLZ(data=request.data)
            slz.is_valid(raise_exception=True)
            group_ids = slz.validated_data["group_ids"]

            self.verify_api_by_groups(app_code, group_ids, api)
            return True

        return False
