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
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, mixins

from backend.account.permissions import role_perm_class
from backend.audit.models import get_event_model
from backend.common.filters import NoCheckModelFilterBackend
from backend.mixins import TenantMixin
from backend.service.constants import PermissionCodeEnum, RoleType

from .filters import EventFilter
from .serializers import EventDetailSchemaSLZ, EventDetailSLZ, EventListSchemaSLZ, EventListSLZ, EventQuerySLZ


class EventViewSet(TenantMixin, mixins.ListModelMixin, GenericViewSet):
    permission_classes = [role_perm_class(PermissionCodeEnum.AUDIT.value)]

    lookup_field = "id"
    serializer_class = EventListSLZ
    filterset_class = EventFilter
    filter_backends = [NoCheckModelFilterBackend]

    def get_queryset(self):
        month = self.request.query_params.get("month", "")
        Event = get_event_model(month)  # noqa: N806
        queryset = Event.objects.filter(tenant_id=self.tenant_id).order_by("-created_time")

        role = self.request.role
        if role.type == RoleType.SUPER_MANAGER.value:
            return queryset
        if role.type in [RoleType.SYSTEM_MANAGER.value, RoleType.GRADE_MANAGER.value]:
            return queryset.filter(role_id=role.id)

        return queryset.none()

    @swagger_auto_schema(
        operation_description="审计事件列表",
        responses={status.HTTP_200_OK: EventListSchemaSLZ(label="事件", many=True)},
        tags=["audit"],
    )
    def list(self, request, *args, **kwargs):
        slz = EventQuerySLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)

        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="审计事件详情",
        query_serializer=EventQuerySLZ(),
        responses={status.HTTP_200_OK: EventDetailSchemaSLZ(label="事件")},
        tags=["audit"],
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = EventDetailSLZ(instance)
        return Response(serializer.data)
