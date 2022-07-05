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

from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response

from backend.apps.template import tasks  # noqa
from backend.apps.template.serializers import TemplateListSchemaSLZ, TemplateListSLZ
from backend.apps.template.views import TemplateViewSet
from backend.biz.role import RoleBiz, RoleListQuery

permission_logger = logging.getLogger("permission")


class TemplateQueryMixin:
    def get_queryset(self):
        pass


class TemplateViewSet(TemplateQueryMixin, TemplateViewSet):

    role_biz = RoleBiz()

    @swagger_auto_schema(
        operation_description="模板列表",
        responses={status.HTTP_200_OK: TemplateListSchemaSLZ(label="模板", many=True)},
        tags=["template"],
    )
    def list(self, request, *args, **kwargs):
        group_id = request.query_params.get("group_id", "")
        role = self.role_biz.get_role_by_group_id(group_id=group_id)
        queryset = self.filter_queryset(RoleListQuery(role, request.user).query_template())

        # 查询role的system-actions set
        role_system_actions = RoleListQuery(role).get_scope_system_actions()
        page = self.paginate_queryset(queryset)
        if page is not None:
            # 查询模板中对group_id中有授权的
            exists_template_set = self._query_group_exists_template_set(group_id, page)

            serializer = TemplateListSLZ(
                page, many=True, authorized_template=exists_template_set, role_system_actions=role_system_actions
            )
            print(serializer.data)

            return self.get_paginated_response(serializer.data)

        # 查询模板中对group_id中有授权的
        exists_template_set = self._query_group_exists_template_set(group_id, queryset)
        serializer = TemplateListSLZ(
            queryset, many=True, authorized_template=exists_template_set, role_system_actions=role_system_actions
        )
        return Response(serializer.data)
