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
from typing import List

from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from pydantic import parse_obj_as
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, views

from backend.api.authentication import ESBAuthentication
from backend.api.management.constants import ManagementAPIEnum, VerifyApiParamLocationEnum
from backend.api.management.mixins import ManagementAPIPermissionCheckMixin
from backend.api.management.v2.permissions import ManagementAPIPermission
from backend.api.management.v2.serializers import (
    ManagementApplicationIDSLZ,
    ManagementGradeManagerApplicationResultSLZ,
    ManagementGradeManagerCreateApplicationSLZ,
    ManagementGroupApplicationCreateSLZ,
)
from backend.apps.application.models import Application
from backend.apps.organization.models import User as UserModel
from backend.apps.role.models import Role
from backend.biz.application import (
    ApplicationBiz,
    ApplicationGroupInfoBean,
    GradeManagerApplicationDataBean,
    GroupApplicationDataBean,
)
from backend.biz.group import GroupBiz
from backend.biz.role import RoleCheckBiz
from backend.common.lock import gen_role_upsert_lock
from backend.service.constants import ApplicationType, RoleType, SubjectType
from backend.service.models import Applicant, Subject
from backend.trans.open_management import GradeManagerTrans


class ManagementGroupApplicationViewSet(GenericViewSet):
    """用户组申请单"""

    authentication_classes = [ESBAuthentication]
    permission_classes = [ManagementAPIPermission]
    management_api_permission = {
        "create": (
            VerifyApiParamLocationEnum.GROUP_IDS_IN_BODY.value,
            ManagementAPIEnum.V2_GROUP_APPLICATION_CREATE.value,
        ),
    }

    biz = ApplicationBiz()
    group_biz = GroupBiz()

    @swagger_auto_schema(
        operation_description="创建用户组申请单",
        request_body=ManagementGroupApplicationCreateSLZ(label="创建用户组申请单"),
        responses={status.HTTP_200_OK: ManagementApplicationIDSLZ(label="单据ID列表")},
        tags=["management.group.application"],
    )
    def create(self, request, *args, **kwargs):
        """
        创建用户组申请单
        """
        serializer = ManagementGroupApplicationCreateSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # 判断用户加入的用户组数与申请的数是否超过最大限制
        user_id = data["applicant"]

        # 转换为ApplicationBiz创建申请单所需数据结构
        user = UserModel.objects.get(username=user_id)

        source_system_id = kwargs["system_id"]

        # 检查用户组数量是否超限
        self.group_biz.check_subject_groups_quota(Subject.from_username(user_id), data["group_ids"])

        # 创建申请
        applications = self.biz.create_for_group(
            ApplicationType.JOIN_GROUP.value,
            GroupApplicationDataBean(
                applicant=user_id,
                reason=data["reason"],
                groups=[
                    ApplicationGroupInfoBean(id=group_id, expired_at=data["expired_at"])
                    for group_id in data["group_ids"]
                ],
                applicants=[Applicant(type=SubjectType.USER.value, id=user.username, display_name=user.display_name)],
            ),
            source_system_id=source_system_id,
            content_template=data["content_template"],
            group_content=data["group_content"],
            title_prefix=data["title_prefix"],
        )

        return Response({"ids": [a.id for a in applications]})


class ManagementGradeManagerApplicationViewSet(ManagementAPIPermissionCheckMixin, GenericViewSet):
    """分级管理员创建申请单"""

    authentication_classes = [ESBAuthentication]
    permission_classes = [ManagementAPIPermission]
    management_api_permission = {
        "create": (
            VerifyApiParamLocationEnum.SYSTEM_IN_PATH.value,
            ManagementAPIEnum.V2_GRADE_MANAGER_APPLICATION_CREATE.value,
        ),
    }

    biz = ApplicationBiz()
    role_check_biz = RoleCheckBiz()
    trans = GradeManagerTrans()

    @swagger_auto_schema(
        operation_description="分级管理员创建申请单",
        request_body=ManagementGradeManagerCreateApplicationSLZ(label="分级管理员创建申请单"),
        responses={status.HTTP_200_OK: ManagementGradeManagerApplicationResultSLZ(label="单据信息")},
        tags=["management.grade_manager.application"],
    )
    def create(self, request, *args, **kwargs):
        """
        分级管理员创建申请单
        """
        serializer = ManagementGradeManagerCreateApplicationSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user_id = data["applicant"]

        # API里数据鉴权: 不可超过接入系统可管控的授权系统范围
        source_system_id = kwargs["system_id"]
        auth_system_ids = list({i["system"] for i in data["authorization_scopes"]})
        self.verify_system_scope(source_system_id, auth_system_ids)

        # 兼容member格式
        data["members"] = [{"username": username} for username in data["members"]]

        # 结构转换
        info = self.trans.to_role_info(data, source_system_id=source_system_id)

        with gen_role_upsert_lock(data["name"]):
            # 名称唯一性检查
            self.role_check_biz.check_grade_manager_unique_name(data["name"])

            applications = self.biz.create_for_grade_manager(
                ApplicationType.CREATE_GRADE_MANAGER.value,
                GradeManagerApplicationDataBean(
                    applicant=user_id, reason=data["reason"], role_info=info, group_name=data["group_name"]
                ),
                source_system_id=source_system_id,
                callback_id=data["callback_id"],
                callback_url=data["callback_url"],
                approval_title=data["title"],
                approval_content=data["content"],
            )

        return Response({"id": applications[0].id, "sn": applications[0].sn})


class ManagementGradeManagerUpdatedApplicationViewSet(ManagementAPIPermissionCheckMixin, GenericViewSet):
    """分级管理员更新申请单"""

    authentication_classes = [ESBAuthentication]
    permission_classes = [ManagementAPIPermission]
    management_api_permission = {
        "create": (
            VerifyApiParamLocationEnum.ROLE_IN_PATH.value,
            ManagementAPIEnum.V2_GRADE_MANAGER_APPLICATION_UPDATE.value,
        ),
    }

    lookup_field = "id"

    biz = ApplicationBiz()
    role_check_biz = RoleCheckBiz()
    trans = GradeManagerTrans()

    @swagger_auto_schema(
        operation_description="分级管理员更新申请单",
        request_body=ManagementGradeManagerCreateApplicationSLZ(label="分级管理员更新申请单"),
        responses={status.HTTP_200_OK: ManagementGradeManagerApplicationResultSLZ(label="单据信息")},
        tags=["management.grade_manager.application"],
    )
    def create(self, request, *args, **kwargs):
        """
        分级管理员更新申请单
        """
        serializer = ManagementGradeManagerCreateApplicationSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user_id = data["applicant"]

        # API里数据鉴权: 不可超过接入系统可管控的授权系统范围
        source_system_id = kwargs["system_id"]
        auth_system_ids = list({i["system"] for i in data["authorization_scopes"]})
        self.verify_system_scope(source_system_id, auth_system_ids)

        role = get_object_or_404(Role, type=RoleType.GRADE_MANAGER.value, id=kwargs["id"])

        # 兼容member格式
        data["members"] = [{"username": username} for username in data["members"]]

        info = self.trans.to_role_info(data, source_system_id=source_system_id)

        with gen_role_upsert_lock(data["name"]):
            # 名称唯一性检查
            self.role_check_biz.check_grade_manager_unique_name(data["name"], role.name)

            applications = self.biz.create_for_grade_manager(
                ApplicationType.UPDATE_GRADE_MANAGER,
                GradeManagerApplicationDataBean(
                    role_id=role.id,
                    applicant=user_id,
                    reason=data["reason"],
                    role_info=info,
                    group_name=data["group_name"],
                ),
                source_system_id=source_system_id,
                callback_id=data["callback_id"],
                callback_url=data["callback_url"],
                approval_title=data["title"],
                approval_content=data["content"],
            )

        return Response({"id": applications[0].id, "sn": applications[0].sn})


class ManagementApplicationCancelView(views.APIView):
    """
    申请单取消
    """

    authentication_classes = [ESBAuthentication]
    permission_classes = [ManagementAPIPermission]
    management_api_permission = {
        "put": (
            VerifyApiParamLocationEnum.SYSTEM_IN_PATH.value,
            ManagementAPIEnum.V2_APPLICATION_CANCEL.value,
        ),
    }

    biz = ApplicationBiz()

    # Note: 这里会回调第三方处理，所以不定义参数
    def put(self, request, *args, **kwargs):
        source_system_id = kwargs["system_id"]
        callback_id = kwargs["callback_id"]

        # 校验系统与callback_id对应的审批存在
        application = get_object_or_404(Application, source_system_id=source_system_id, callback_id=callback_id)

        # 接入系统自行cancel itsm 单据
        self.biz.cancel_application(application, application.applicant, need_cancel_ticket=False)

        return Response({})


class ManagementGroupRenewApplicationViewSet(GenericViewSet):
    """用户组续期申请单"""

    authentication_classes = [ESBAuthentication]
    permission_classes = [ManagementAPIPermission]
    management_api_permission = {
        "create": (
            VerifyApiParamLocationEnum.GROUP_IDS_IN_BODY.value,
            ManagementAPIEnum.V2_GROUP_APPLICATION_RENEW.value,
        ),
    }

    biz = ApplicationBiz()
    group_biz = GroupBiz()

    @swagger_auto_schema(
        operation_description="用户组续期申请单",
        request_body=ManagementGroupApplicationCreateSLZ(label="用户组续期申请单"),
        responses={status.HTTP_200_OK: ManagementApplicationIDSLZ(label="单据ID列表")},
        tags=["management.group.application"],
    )
    def create(self, request, *args, **kwargs):
        """
        用户组续期申请单
        """
        serializer = ManagementGroupApplicationCreateSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # 判断用户加入的用户组数与申请的数是否超过最大限制
        user_id = data["applicant"]

        # 转换为ApplicationBiz创建申请单所需数据结构
        user = UserModel.objects.get(username=user_id)

        source_system_id = kwargs["system_id"]

        # 检查用户组数量是否超限
        self.group_biz.check_subject_groups_quota(Subject.from_username(user_id), data["group_ids"])

        # 创建申请
        applications = self.biz.create_for_group(
            ApplicationType.RENEW_GROUP.value,
            GroupApplicationDataBean(
                applicant=user.username,
                reason=data["reason"],
                groups=parse_obj_as(
                    List[ApplicationGroupInfoBean],
                    [{"id": _id, "expired_at": data["expired_at"]} for _id in data["group_ids"]],
                ),
                applicants=[Applicant(type=SubjectType.USER.value, id=user.username, display_name=user.display_name)],
            ),
            source_system_id=source_system_id,
        )

        return Response({"ids": [a.id for a in applications]})
