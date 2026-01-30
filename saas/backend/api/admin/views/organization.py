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
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from backend.api.admin.constants import AdminAPIEnum
from backend.api.admin.permissions import AdminAPIPermission
from backend.api.admin.serializers import AdminOrganizationSyncConfigSLZ, AdminOrganizationSyncResultSLZ
from backend.api.authentication import ESBAuthentication
from backend.apps.organization.tasks import sync_organization


class AdminOrganizationSyncViewSet(GenericViewSet):
    authentication_classes = [ESBAuthentication]
    permission_classes = [AdminAPIPermission]
    admin_api_permission = {
        "sync": AdminAPIEnum.ORGANIZATION_SYNC.value,
    }

    @swagger_auto_schema(
        operation_description="触发组织架构同步（可选设置同步周期）",
        request_body=AdminOrganizationSyncConfigSLZ(label="同步配置"),
        responses={status.HTTP_200_OK: AdminOrganizationSyncResultSLZ(label="同步结果")},
        tags=["admin.organization"],
    )
    def sync(self, request, *args, **kwargs):
        """触发组织架构同步任务，可选设置同步周期"""
        slz = AdminOrganizationSyncConfigSLZ(data=request.data)
        slz.is_valid(raise_exception=True)

        sync_period = slz.validated_data.get("sync_period")
        data = {"sync_message": "组织架构同步任务已触发"}
        if sync_period:
            schedule_params = {
                "day_of_week": "*",
                "day_of_month": "*",
                "month_of_year": "*",
                "timezone": settings.CELERY_TIMEZONE,
            }
            # 根据时间间隔设置不同的调度策略
            if sync_period < 3600:
                schedule_params.update({"minute": f"*/{sync_period // 60}", "hour": "*"})
            elif sync_period < 86400:
                schedule_params.update({"minute": "0", "hour": f"*/{sync_period // 3600}"})
            else:
                days = sync_period // 86400
                schedule_params.update({
                    "minute": "0", 
                    "hour": "0",
                    "day_of_month": "*" if days == 1 else f"*/{days}"
                })
            # 获取或创建定时任务
            task_name = "periodic_sync_organization"
            periodic_task, created = PeriodicTask.objects.get_or_create(
                name=task_name,
                defaults={
                    "task": "backend.apps.organization.tasks.sync_organization",
                    "enabled": True,
                }
            )
            # 更新或创建 CrontabSchedule
            if periodic_task.crontab:
                schedule = periodic_task.crontab
                for key, value in schedule_params.items():
                    setattr(schedule, key, value)
                schedule.save()
            else:
                schedule = CrontabSchedule.objects.create(**schedule_params)
                periodic_task.crontab = schedule
                periodic_task.save()

            data["sync_message"] = f"组织架构同步任务已触发，同步周期已{'创建' if created else '更新'}为每{sync_period}秒执行一次"

        sync_organization.delay("admin_api")
        return Response(data)
