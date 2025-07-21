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

from backend.api.admin.constants import AdminAPIEnum
from backend.api.admin.permissions import AdminAPIPermission
from backend.api.authentication import ESBAuthentication
from backend.audit.models import get_event_model
from backend.audit.views import EventViewSet
from backend.common.pagination import CustomPageNumberPagination


class AdminAuditEventViewSet(EventViewSet):
    authentication_classes = [ESBAuthentication]
    permission_classes = [AdminAPIPermission]
    admin_api_permission = {"list": AdminAPIEnum.AUDIT_EVENT_LIST.value}

    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        month = self.request.query_params.get("month", "")
        Event = get_event_model(month)  # noqa: N806
        return Event.objects.filter(tenant_id=self.tenant_id).order_by("-created_time")
