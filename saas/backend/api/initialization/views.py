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

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import views

from backend.biz.org_sync.syncer import Syncer
from backend.common.authentication import BasicAppCodeAuthentication
from backend.mixins import TenantMixin

from .serializers import SyncUserSLZ


class SyncUserView(TenantMixin, views.APIView):
    """
    同步用户
    """

    authentication_classes = [BasicAppCodeAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        slz = SyncUserSLZ(data=request.data)
        slz.is_valid(raise_exception=True)

        Syncer(self.tenant_id).sync_single_user(slz.validated_data["username"])

        return Response({})
