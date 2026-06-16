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
import time

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
from backend.apps.handover.tasks import execute_handover_task
from backend.apps.handover.views import HandoverViewSet
from backend.audit.audit import log_group_event, log_user_event
from backend.audit.constants import AuditSourceType, AuditType
from backend.biz.group import GroupBiz
from backend.biz.policy import PolicyOperationBiz, PolicyQueryBiz
from backend.common.exception_handler import exception_handler
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
        # 调用方只处理 HTTP 200 响应，统一返回 200，通过 code 区分成功与失败
        return Response(
            {"code": data.get("code"), "msg": data.get("message"), "assets": []},
            status=status.HTTP_200_OK,
        )

    @swagger_auto_schema(
        operation_description="PCG 权限交接 - 获取资产列表",
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

    group_biz = GroupBiz()
    policy_query_biz = PolicyQueryBiz()

    def handle_exception(self, exc):
        context = self.get_exception_handler_context()
        response = exception_handler(exc, context)
        if response is None:
            return None
        data = response.data
        # 调用方只处理 HTTP 200 响应，统一返回 200，通过 code 区分成功与失败
        return Response(
            {"code": data.get("code"), "msg": data.get("message"), "err_list": []},
            status=status.HTTP_200_OK,
        )

    @swagger_auto_schema(
        operation_description="PCG 权限交接 - 交接",
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

        handover_info, err_list = self._filter_expired_assets(activity_rtx, assets)

        # 还有未过期的资产需要交接
        if handover_info["group_ids"] or handover_info["custom_policies"]:
            # 非预期异常（锁冲突、DB 等）不再 try/except，交给 handle_exception 兜底
            handover_record = self._create_handover_record(activity_rtx, handover_rtx, "[PCG] 离职交接", handover_info)
            execute_handover_task.delay(
                handover_from=activity_rtx, handover_to=handover_rtx, handover_record_id=handover_record.id
            )

        if err_list:
            msg = "；".join(list({item["fail_reason"] for item in err_list}))
            return Response({"err_list": err_list, "code": 500, "msg": msg})
        # 异步处理中
        return Response({"err_list": [], "code": 202, "msg": "OK"})

    def _filter_expired_assets(self, activity_rtx, assets):
        """前置过期检查：逐资产过滤，过期资产加入 err_list，未过期的构建 handover_info"""
        handover_info = {"group_ids": [], "custom_policies": []}
        err_list = []

        now_ts = int(time.time())
        subject = Subject.from_username(activity_rtx)
        valid_group_ids = {g.id for g in self.group_biz.list_all_subject_group(subject) if g.expired_at > now_ts}

        for asset in assets:
            if asset["id"] == 0:
                policies = self.policy_query_biz.list_by_subject(asset["info"], subject)
                policy_ids = [p.policy_id for p in policies if not p.is_expired()]
                if not policy_ids:
                    err_list.append({"fail_reason": "自定义权限已过期，无法交接，只能回收", "info": asset})
                    continue
                handover_info["custom_policies"].append({"system_id": asset["info"], "policy_ids": policy_ids})
            else:
                if asset["id"] not in valid_group_ids:
                    err_list.append({"fail_reason": "用户组权限已过期，无法交接，只能回收", "info": asset})
                    continue
                handover_info["group_ids"].append(asset["id"])

        return handover_info, err_list


class RecycleViewSet(ResignHandoverViewSet):
    """回收"""

    permission_classes = []  # type: ignore[var-annotated]
    authentication_classes = [ResignApiAuthentication]
    renderer_classes = [JSONRenderer]

    group_biz = GroupBiz()
    policy_query_biz = PolicyQueryBiz()
    policy_operation_biz = PolicyOperationBiz()

    @swagger_auto_schema(
        operation_description="PCG 权限交接 - 回收",
        request_body=RecycleSLZ(label="用户"),
        responses={status.HTTP_200_OK: HandoverResultSLZ(label="错误信息")},
        tags=["resign"],
    )
    def recycle(self, request, *args, **kwargs):
        serializer = RecycleSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)
        activity_rtx = serializer.validated_data["activity_rtx"]
        assets = serializer.validated_data["assets"]
        subject = Subject.from_username(activity_rtx)
        err_list = []
        for asset in assets:
            try:
                if asset["id"] == 0:
                    # 自定义权限回收
                    policies = self.policy_query_biz.list_by_subject(asset["info"], subject)
                    policy_ids = [policy.policy_id for policy in policies]
                    self.policy_operation_biz.delete_by_ids(asset["info"], subject, policy_ids)
                    log_user_event(
                        AuditType.USER_POLICY_DELETE.value,
                        subject,
                        asset["info"],
                        [p.dict() for p in policies],
                        source_type=AuditSourceType.OPENAPI.value,
                    )
                else:
                    # 用户组权限回收
                    self.group_biz.remove_members(str(asset["id"]), [subject])
                    log_group_event(
                        AuditType.GROUP_MEMBER_DELETE.value,
                        subject,
                        [int(asset["id"])],
                        source_type=AuditSourceType.OPENAPI.value,
                    )
            except Exception as e:  # pylint: disable=broad-except
                err_list.append({"fail_reason": str(e), "info": asset})

        if err_list:
            msg = "；".join(list({item["fail_reason"] for item in err_list}))
            return Response({"err_list": err_list, "code": 500, "msg": msg})
        return Response({"err_list": [], "code": 0, "msg": "OK"})
