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
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, views

from backend.apps.user.models import UserProfile
from backend.biz.resource_type import ResourceTypeBiz
from backend.biz.role import RoleListQuery
from backend.biz.system import SystemBiz
from backend.component import iam

from .serializers import QueryResourceTypeSLZ, SystemQuerySLZ, SystemResourceTypeSLZ, SystemSLZ


class SystemViewSet(GenericViewSet):
    pagination_class = None  # 去掉swagger中的limit offset参数

    biz = SystemBiz()

    @swagger_auto_schema(
        operation_description="系统列表",
        query_serializer=SystemQuerySLZ(label="系统ID"),
        responses={status.HTTP_200_OK: SystemSLZ(label="系统", many=True)},
        tags=["system"],
    )
    def list(self, request, *args, **kwargs):
        slz = SystemQuerySLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)

        all = slz.validated_data["all"]
        if all:
            systems = self.biz.list()
        else:
            systems = RoleListQuery(request.role).list_system()

        hidden = slz.validated_data["hidden"]
        if hidden:
            data = [
                i.dict(include={"id", "name", "name_en"}) for i in systems if i.id not in settings.HIDDEN_SYSTEM_LIST
            ]  # NOTE: 屏蔽掉需要隐藏的系统
        else:
            data = [i.dict(include={"id", "name", "name_en"}) for i in systems]

        # 处理系统收藏
        user_favorite_systems = UserProfile.objects.list_favorite_systems(request.user.username)
        for i in data:
            if i["id"] in user_favorite_systems:
                i["is_favorite"] = True
            else:
                i["is_favorite"] = False

        # 把is_favorite系统排序到前面
        data.sort(key=lambda x: x["is_favorite"], reverse=True)

        return Response(data)


class ResourceTypeViewSet(GenericViewSet):
    pagination_class = None  # 去掉swagger中的limit offset参数

    biz = ResourceTypeBiz()

    @swagger_auto_schema(
        operation_description="资源类别列表",
        query_serializer=QueryResourceTypeSLZ(label="系统ID"),
        responses={status.HTTP_200_OK: SystemResourceTypeSLZ(label="资源类别", many=True)},
        tags=["system"],
    )
    def list_resource_types(self, request, *args, **kwargs):
        system_id = request.query_params["system_id"]
        data = self.biz.list_resource_types_by_system_id(system_id=system_id)
        return Response(data)


class SystemCustomFrontendSettingsView(views.APIView):
    """
    查询系统定制前端配置
    """

    @swagger_auto_schema(
        operation_description="查询系统定制前端配置",
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["system"],
    )
    def get(self, request, *args, **kwargs):
        system_id = kwargs["system_id"]
        settings = iam.get_custom_frontend_settings(system_id)

        return Response(settings)
