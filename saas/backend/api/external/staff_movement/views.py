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
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from backend.api.external.staff_movement.authentication import ResignApiAuthentication
from backend.api.external.staff_movement.serializers import (
    AssetSLZ,
    HandoverResultSLZ,
    RecycleSLZ,
    ResignHandoverSLZ,
    RtxSLZ,
)
from backend.apps.handover.constants import HandoverStatus
from backend.apps.handover.models import HandoverRecord, HandoverTask
from backend.apps.handover.tasks import execute_handover_task
from backend.apps.handover.views import HandoverViewSet
from backend.biz.group import GroupBiz
from backend.biz.policy import PolicyOperationBiz, PolicyQueryBiz
from backend.common.error_codes import error_codes
from backend.common.exception_handler import exception_handler
from backend.common.lock import gen_permission_handover_lock
from backend.service.models.subject import Subject


class GetAssetsViewSet(GenericViewSet):
    """资产列表"""

    permission_classes = []  # type: ignore[var-annotated]
    authentication_classes = [ResignApiAuthentication]
    renderer_classes = [JSONRenderer]

    group_biz = GroupBiz()
    policy_query_biz = PolicyQueryBiz()

    def handle_exception(self, exc):
        context = self.get_exception_handler_context()
        response = exception_handler(exc, context)
        if response is None:
            return None
        data = response.data
        return Response(
            {"code": data.get("code"), "message": data.get("message"), "assets": []},
            status=response.status_code,
        )

    @swagger_auto_schema(
        operation_description="PCG权限交接-获取资产列表",
        request_body=RtxSLZ(label="用户"),
        responses={status.HTTP_200_OK: AssetSLZ(label="资产列表", many=True)},
        tags=["resign"],
    )
    def list(self, request, *args, **kwargs):
        serializer = RtxSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)
        rtx = serializer.validated_data["rtx"]

        subject = Subject.from_username(username=rtx)
        groups = self.group_biz.list_all_subject_group(subject=subject)

        systems = self.policy_query_biz.list_system_counter_by_subject(subject)
        assets = []

        group_role_dict = self.group_biz.get_group_role_dict_by_ids(group_ids=[group.id for group in groups])
        for group in groups:
            assets.append(
                {
                    "id": group.id,
                    "info": group_role_dict.get(group.id).name,
                    "role_type": group.name,
                    "remark": "",
                    "info_key": "",
                    "info_url": "",
                }
            )
        for system in systems:
            assets.append(
                {"id": 0, "info": system.id, "role_type": "细粒度操作权限", "remark": "", "info_key": "", "info_url": ""}
            )
        return Response({"assets": assets, "code": 0, "msg": "OK"})


class ResignHandoverViewSet(HandoverViewSet):
    """交接"""

    permission_classes = []  # type: ignore[var-annotated]
    authentication_classes = [ResignApiAuthentication]
    renderer_classes = [JSONRenderer]

    policy_query_biz = PolicyQueryBiz()

    def handle_exception(self, exc):
        context = self.get_exception_handler_context()
        response = exception_handler(exc, context)
        if response is None:
            return None
        data = response.data
        return Response(
            {"code": data.get("code"), "message": data.get("message"), "err_list": []},
            status=response.status_code,
        )

    @swagger_auto_schema(
        operation_description="PCG权限交接-交接",
        request_body=ResignHandoverSLZ(label="用户"),
        responses={status.HTTP_200_OK: HandoverResultSLZ(label="错误信息")},
        tags=["resign"],
    )
    def handover(self, request, *args, **kwargs):
        serializer = ResignHandoverSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)
        activity_rtx = serializer.validated_data["activity_rtx"]
        handover_rtx = serializer.validated_data["handover_rtx"]
        assets = serializer.validated_data["assets"]
        handover_info = {"group_ids": [], "custom_policies": []}
        err_list = []
        for asset in assets:
            if asset["id"] == 0:
                policies = self.policy_query_biz.list_by_subject(asset["info"], Subject.from_username(activity_rtx))
                policy_ids = [policy.policy_id for policy in policies]
                handover_info["custom_policies"].append({"system_id": asset["info"], "policy_ids": policy_ids})
            else:
                handover_info["group_ids"].append(asset["id"])

        lock = gen_permission_handover_lock(activity_rtx)
        if not lock.acquire():
            # 拿不到锁, 直接返回
            raise error_codes.TASK_EXIST
        try:
            handover_record = HandoverRecord.objects.filter(
                handover_from=activity_rtx, status=HandoverStatus.RUNNING.value
            ).first()
            if handover_record is not None:
                # 已存在正在运行的任务, 不能新建任务
                raise error_codes.TASK_EXIST

            with transaction.atomic():
                # 创建任务
                handover_record = HandoverRecord.objects.create(
                    handover_from=activity_rtx, handover_to=handover_rtx, reason="离职交接"
                )

                handover_task_details = self._gen_handover_tasks(activity_rtx, handover_info, handover_record)

                # 创建子任务信息
                if handover_task_details:
                    HandoverTask.objects.bulk_create(handover_task_details, batch_size=100)

            execute_handover_task.delay(
                handover_from=activity_rtx, handover_to=handover_rtx, handover_record_id=handover_record.id
            )
        except Exception as e:  # pylint: disable=broad-except
            err_list.append({"fail_reason": str(e), "info": []})
        finally:
            # 释放锁
            lock.release()

        return Response({"err_list": err_list, "code": 0, "msg": "OK"})


class RecycleViewSet(ResignHandoverViewSet):
    """回收"""

    permission_classes = []  # type: ignore[var-annotated]
    authentication_classes = [ResignApiAuthentication]
    renderer_classes = [JSONRenderer]

    group_biz = GroupBiz()
    policy_query_biz = PolicyQueryBiz()
    policy_operation_biz = PolicyOperationBiz()

    @swagger_auto_schema(
        operation_description="PCG权限交接-回收",
        request_body=RecycleSLZ(label="用户"),
        responses={status.HTTP_200_OK: HandoverResultSLZ(label="错误信息")},
        tags=["resign"],
    )
    def recycle(self, request, *args, **kwargs):
        serializer = RecycleSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)
        activity_rtx = serializer.validated_data["activity_rtx"]
        assets = serializer.validated_data["assets"]
        err_list = []
        for asset in assets:
            try:
                if asset["id"] == 0:
                    # 自定义权限回收
                    policies = self.policy_query_biz.list_by_subject(
                        asset["info"], Subject.from_username(activity_rtx)
                    )
                    policy_ids = [policy.policy_id for policy in policies]
                    self.policy_operation_biz.delete_by_ids(
                        asset["info"], Subject.from_username(activity_rtx), policy_ids
                    )
                else:
                    # 用户组权限回收
                    self.group_biz.remove_members(str(asset["id"]), [Subject.from_username(activity_rtx)])
            except Exception as e:  # pylint: disable=broad-except
                err_list.append({"fail_reason": str(e), "info": asset})
                continue

        return Response({"err_list": err_list, "code": 0, "msg": "OK"})
