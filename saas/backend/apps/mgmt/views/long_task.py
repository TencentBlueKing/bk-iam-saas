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
from drf_yasg.openapi import Response as yasg_response
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, mixins

from backend.account.permissions import RolePermission
from backend.apps.mgmt.serializers import LongTaskSLZ, QueryLongTaskSLZ, SubTaskSLZ
from backend.common.swagger import ResponseSwaggerAutoSchema
from backend.long_task.constants import TaskStatus
from backend.long_task.models import SubTaskState, TaskDetail
from backend.long_task.tasks import TaskFactory
from backend.service.constants import PermissionCodeEnum


class LongTaskViewSet(mixins.ListModelMixin, GenericViewSet):

    permission_classes = [RolePermission]
    action_permission = {
        "list": PermissionCodeEnum.MANAGE_LONG_TASK.value,
        "retrieve": PermissionCodeEnum.MANAGE_LONG_TASK.value,
        "retry": PermissionCodeEnum.MANAGE_LONG_TASK.value
    }

    @swagger_auto_schema(
        operation_description="长时任务列表",
        query_serializer=QueryLongTaskSLZ(label="long_task"),
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: LongTaskSLZ(label="长时任务列表", many=True)},
        tags=["mgmt.api"],
    )
    def list(self, request, *args, **kwargs):
        slz = QueryLongTaskSLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)
        long_task_type = slz.validated_data["type"]
        task_detail = LongTaskSLZ(TaskDetail.objects.filter(type=long_task_type), many=True).data

        return Response({"count": len(task_detail), "results": task_detail})

    @swagger_auto_schema(
        operation_description="长时任务详情",
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: SubTaskSLZ(label="长时任务详情", many=True)},
        tags=["mgmt.api"],
    )
    def retrieve(self, request, *args, **kwargs):
        task_id = kwargs["id"]
        sub_task = SubTaskSLZ(SubTaskState.objects.filter(task_id=task_id), many=True).data

        return Response({"count": len(sub_task), "results": sub_task})

    @swagger_auto_schema(
        operation_description="长时任务失败重试",
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: yasg_response({})},
        tags=["mgmt.api"],
    )
    def retry(self, request, *args, **kwargs):
        task_id = kwargs["id"]
        task = TaskDetail.objects.filter(id=task_id).first()
        if task.status == TaskStatus.FAILURE.value:
            TaskFactory()(task.id)

        return Response({})
