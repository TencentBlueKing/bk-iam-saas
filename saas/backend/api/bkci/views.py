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

import secrets

from django.shortcuts import get_object_or_404
from rest_framework import exceptions, mixins, serializers
from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from backend.api.bkci.filters import MigrateDataFilter
from backend.api.bkci.models import MigrateData, MigrateLegacyTask, MigrateTask
from backend.api.bkci.serializers import MigrateDataSLZ
from backend.api.bkci.tasks import BKCILegacyMigrateTask, BKCIMigrateTask
from backend.util.json import json_dumps


class BKCIMigrateAutherization(BaseAuthentication):
    def authenticate(self, request):
        token = request.GET.get("token", "")
        if not secrets.compare_digest(token, "9sBQj!M0"):
            raise exceptions.AuthenticationFailed("token error")


class MigrateTaskView(GenericViewSet):
    """迁移任务"""

    authentication_classes = [BKCIMigrateAutherization]
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializers.ListField(child=serializers.IntegerField()).run_validation(request.data)

        task = MigrateTask.objects.first()
        if not task or task.status in ("SUCCESS", "FAILURE"):
            MigrateTask.objects.all().delete()
            task = MigrateTask(role_ids=json_dumps(request.data), status="PENDING")
            task.save(force_insert=True)

            BKCIMigrateTask().delay()

        return Response({})

    def list(self, request, *args, **kwargs):
        task = MigrateTask.objects.first()
        if not task:
            return Response({"status": "NOT_EXISTS"})

        return Response({"status": task.status})


class MigrateDataView(GenericViewSet, mixins.ListModelMixin):
    """迁移数据"""

    authentication_classes = [BKCIMigrateAutherization]
    permission_classes = [AllowAny]

    queryset = MigrateData.objects.all().order_by("id")
    serializer_class = MigrateDataSLZ
    filterset_class = MigrateDataFilter


class MigrateLegacyTaskView(GenericViewSet):
    """迁移v0任务"""

    authentication_classes = [BKCIMigrateAutherization]
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializers.ListField(child=serializers.CharField()).run_validation(request.data)

        task = MigrateLegacyTask(project_ids=json_dumps(request.data), status="PENDING")
        task.save(force_insert=True)

        BKCILegacyMigrateTask().delay(task.id)

        return Response({"id": task.id})

    def retrieve(self, request, *args, **kwargs):
        task = get_object_or_404(MigrateLegacyTask.objects.all(), pk=kwargs["id"])

        return Response({"status": task.status})
