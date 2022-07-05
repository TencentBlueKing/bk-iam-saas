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
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from backend.apps.mgmt.serializers import QuerySystemSLZ
from backend.apps.system import serializers
from backend.biz.role import RoleBiz, RoleListQuery


class MgmtSystemViewSet(GenericViewSet):

    paginator = None  # 去掉swagger中的limit offset参数

    biz = RoleBiz()

    @swagger_auto_schema(
        operation_description="系统列表",
        query_serializer=QuerySystemSLZ,
        responses={status.HTTP_200_OK: serializers.SystemSLZ(label="系统", many=True)},
        tags=["system"],
    )
    def list(self, request, *args, **kwargs):

        slz = QuerySystemSLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)

        group_id = slz.validated_data["group_id"]
        role = self.biz.get_role_by_group_id(group_id=group_id)

        systems = RoleListQuery(role).list_system()
        data = [i.dict(include={"id", "name", "name_en"}) for i in systems]
        return Response(data)
