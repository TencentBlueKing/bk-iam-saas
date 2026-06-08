# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云 - 权限中心 (BlueKing-IAM) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, views
from rest_framework.response import Response

from backend.apps.action.serializers import ActionGroupQuerySLZ, SubActionGroupSLZ
from backend.mixins import BizMixin


class ActionGroupView(BizMixin, views.APIView):
    """
    操作分组
    """

    @swagger_auto_schema(
        operation_description="获取操作分组",
        query_serializer=ActionGroupQuerySLZ(),
        responses={status.HTTP_200_OK: SubActionGroupSLZ(label="操作分组", many=True)},
        tags=["action"],
    )
    def get(self, request):
        slz = ActionGroupQuerySLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)

        system_id = slz.validated_data["system_id"]

        action_list = self.action_biz.list(system_id)
        action_groups = self.action_group_biz.list_with_frontend_id_by_actions(system_id, action_list.actions)

        return Response([one.dict() for one in action_groups])
