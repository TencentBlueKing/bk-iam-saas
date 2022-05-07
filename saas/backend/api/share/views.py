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

from backend.api.authentication import ESBAuthentication
from backend.biz.system import SystemBiz
from backend.common.swagger import ResponseSwaggerAutoSchema

from .permissions import ShareAPIPermission
from .serializers import ShareSystemSLZ


class SystemViewSet(GenericViewSet):
    """系统相关信息"""

    authentication_classes = [ESBAuthentication]
    permission_classes = [ShareAPIPermission]

    biz = SystemBiz()

    @swagger_auto_schema(
        operation_description="系统详情",
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: ShareSystemSLZ(label="系统详情")},
        tags=["group"],
    )
    def retrieve(self, request, *args, **kwargs):
        share_info = self.biz.get_share_info(kwargs["system_id"])

        data = ShareSystemSLZ(share_info).data
        return Response(data)
