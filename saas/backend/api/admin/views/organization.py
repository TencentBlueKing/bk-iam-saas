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
from django_celery_beat.models import CrontabSchedule, PeriodicTask
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from backend.api.admin.constants import AdminAPIEnum
from backend.api.admin.permissions import AdminAPIPermission
from backend.api.admin.serializers import AdminOrganizationSyncConfigSLZ
from backend.api.authentication import ESBAuthentication
from backend.apps.organization.tasks import sync_organization


class AdminOrganizationSyncViewSet(GenericViewSet):
    authentication_classes = [ESBAuthentication]
    permission_classes = [AdminAPIPermission]
    admin_api_permission = {
        "sync": AdminAPIEnum.ORGANIZATION_SYNC.value,
    }

    @swagger_auto_schema(
        operation_description="触发组织架构同步",
        request_body=AdminOrganizationSyncConfigSLZ(label="同步配置"),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["admin.organization"],
    )
    def sync(self, request, *args, **kwargs):
        """触发组织架构同步任务，可选设置同步周期"""
        slz = AdminOrganizationSyncConfigSLZ(data=request.data)
        slz.is_valid(raise_exception=True)

        sync_crontab = slz.validated_data.get("sync_crontab")
        if sync_crontab:
            task_name = "periodic_sync_organization"
            schedule, _ = CrontabSchedule.objects.get_or_create(
                minute=sync_crontab._orig_minute,
                hour=sync_crontab._orig_hour,
                day_of_month=sync_crontab._orig_day_of_month,
                month_of_year=sync_crontab._orig_month_of_year,
                day_of_week=sync_crontab._orig_day_of_week,
                timezone=settings.CELERY_TIMEZONE,
            )
            PeriodicTask.objects.update_or_create(
                name=task_name,
                defaults={
                    "task": "backend.apps.organization.tasks.sync_organization",
                    "crontab": schedule,
                    "enabled": True,
                },
            )

        sync_organization.delay("admin_api")
        return Response({})
