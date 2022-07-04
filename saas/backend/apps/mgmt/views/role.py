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
from rest_framework.viewsets import views

from backend.apps.mgmt.serializers import QueryRoleAuthorizationScopeSLZ, QueryRoleSubjectScopeSLZ
from backend.apps.role.serializers import GradeManagerActionSLZ, RoleScopeSubjectSLZ
from backend.biz.role import RoleBiz
from backend.biz.subject import SubjectInfoList
from backend.common.swagger import ResponseSwaggerAutoSchema


class RoleAuthorizationScopeView(views.APIView):
    """
    角色的授权范围查询
    """

    biz = RoleBiz()

    @swagger_auto_schema(
        operation_description="角色的授权范围",
        query_serializer=QueryRoleAuthorizationScopeSLZ,
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: GradeManagerActionSLZ(label="操作策略", many=True)},
        tags=["role"],
    )
    def get(self, request, *args, **kwargs):
        slz = QueryRoleAuthorizationScopeSLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)

        system_id = slz.validated_data["system_id"]
        group_id = slz.validated_data["group_id"]
        role = self.biz.get_role_by_group_id(group_id=group_id)

        # ResourceNameAutoUpdate
        scope_system = self.biz.get_auth_scope_bean_by_system(
            role.id, system_id, should_auto_update_resource_name=True
        )
        data = [one.dict() for one in scope_system.actions] if scope_system else []
        return Response(data)


class RoleSubjectScopeView(views.APIView):
    """
    角色的subject授权范围
    """

    biz = RoleBiz()

    @swagger_auto_schema(
        operation_description="角色的subject授权范围",
        query_serializer=QueryRoleSubjectScopeSLZ,
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: RoleScopeSubjectSLZ(label="操作策略", many=True)},
        tags=["mgmt.role"],
    )
    def get(self, request, *args, **kwargs):
        slz = QueryRoleSubjectScopeSLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)

        group_id = slz.validated_data["group_id"]
        role = self.biz.get_role_by_group_id(group_id=group_id)

        scopes = self.biz.list_subject_scope(role.id)

        subjects = SubjectInfoList(scopes).subjects if scopes else []
        return Response([one.dict() for one in subjects])
