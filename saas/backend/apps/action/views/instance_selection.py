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
from rest_framework import status, views
from rest_framework.response import Response

from backend.biz.instance_selection import InstanceSelectionBiz

from ..serializers import InstanceSelectionQuerySLZ, InstanceSelectionSLZ


class InstanceSelectionView(views.APIView):
    pagination_class = None  # 去掉swagger中的limit offset参数

    biz = InstanceSelectionBiz()

    @swagger_auto_schema(
        operation_description="资源实例选择视图",
        query_serializer=InstanceSelectionQuerySLZ(),
        responses={status.HTTP_200_OK: InstanceSelectionSLZ(label="选择视图", many=True)},
        tags=["action"],
    )
    def get(self, request, *args, **kwargs):
        slz = InstanceSelectionQuerySLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)

        slz_data = slz.validated_data

        instance_selection = self.biz.list_by_action_resource_type(
            slz_data["system_id"],
            slz_data["action_id"],
            slz_data["resource_type_system"],
            slz_data["resource_type_id"],
        )

        return Response([one.dict() for one in instance_selection])
