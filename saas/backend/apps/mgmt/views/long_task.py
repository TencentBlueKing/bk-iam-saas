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
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, mixins

from backend.account.permissions import RolePermission
from backend.apps.mgmt.filters import LongTaskFilter
from backend.apps.mgmt.serializers import LongTaskSLZ, SubTaskSLZ
from backend.long_task.constants import TaskStatus
from backend.long_task.models import SubTaskState, TaskDetail
from backend.long_task.tasks import TaskFactory
from backend.service.constants import PermissionCodeEnum


class LongTaskViewSet(mixins.ListModelMixin, GenericViewSet):
    permission_classes = [RolePermission]
    action_permission = {
        "list": PermissionCodeEnum.MANAGE_LONG_TASK.value,
        "retrieve": PermissionCodeEnum.MANAGE_LONG_TASK.value,
        "retry": PermissionCodeEnum.MANAGE_LONG_TASK.value,
    }
    queryset = TaskDetail.objects.all()
    serializer_class = LongTaskSLZ
    filterset_class = LongTaskFilter

    @swagger_auto_schema(
        operation_description="长时任务列表",
        responses={status.HTTP_200_OK: LongTaskSLZ(label="长时任务列表", many=True)},
        tags=["mgmt.api"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(self, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="长时任务详情",
        responses={status.HTTP_200_OK: SubTaskSLZ(label="长时任务详情", many=True)},
        tags=["mgmt.api"],
    )
    def retrieve(self, request, *args, **kwargs):
        task_id = kwargs["id"]
        sub_task = SubTaskState.objects.filter(task_id=task_id)

        return Response(SubTaskSLZ(sub_task, many=True).data)

    @swagger_auto_schema(
        operation_description="长时任务失败重试",
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["mgmt.api"],
    )
    def retry(self, request, *args, **kwargs):
        task_id = kwargs["id"]
        task = TaskDetail.objects.filter(id=task_id).first()
        if task.status == TaskStatus.FAILURE.value:
            TaskFactory().run(task.id)

        return Response({})
