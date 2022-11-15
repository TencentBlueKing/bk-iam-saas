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
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from backend.api.authentication import ESBAuthentication
from backend.api.management.constants import ManagementAPIEnum, VerifyAPIParamLocationEnum
from backend.api.management.v2.permissions import ManagementAPIPermission
from backend.api.management.v2.serializers import (
    ManagementApplicationIDSLZ,
    ManagementGradeManagerApplicationResultSLZ,
    ManagementGradeManagerCreateApplicationSLZ,
    ManagementGroupApplicationCreateSLZ,
)
from backend.apps.role.models import Role
from backend.biz.application import (
    ApplicationBiz,
    ApplicationGroupInfoBean,
    GradeManagerApplicationDataBean,
    GroupApplicationDataBean,
)
from backend.biz.group import GroupBiz
from backend.biz.role import RoleCheckBiz
from backend.service.constants import ApplicationTypeEnum, RoleType
from backend.service.models import Subject
from backend.trans.open_management import GradeManagerTrans


class ManagementGroupApplicationViewSet(GenericViewSet):
    """用户组申请单"""

    authentication_classes = [ESBAuthentication]
    permission_classes = [ManagementAPIPermission]
    management_api_permission = {
        "create": (
            VerifyAPIParamLocationEnum.GROUP_IDS_IN_BODY.value,
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

        source_system_id = kwargs["system_id"]

        # 检查用户组数量是否超限
        self.group_biz.check_subject_groups_quota(Subject.from_username(user_id), data["group_ids"])

        # 创建申请
        applications = self.biz.create_for_group(
            ApplicationTypeEnum.JOIN_GROUP.value,
            GroupApplicationDataBean(
                applicant=user_id,
                reason=data["reason"],
                groups=[
                    ApplicationGroupInfoBean(id=group_id, expired_at=data["expired_at"])
                    for group_id in data["group_ids"]
                ],
            ),
            source_system_id=source_system_id,
        )

        return Response({"ids": [a.id for a in applications]})


class ManagementGradeManagerApplicationViewSet(GenericViewSet):
    """分级管理员创建申请单"""

    authentication_classes = [ESBAuthentication]
    permission_classes = [ManagementAPIPermission]
    management_api_permission = {
        "create": (
            VerifyAPIParamLocationEnum.SYSTEM_IN_PATH.value,
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

        source_system_id = kwargs["system_id"]

        # 名称唯一性检查
        self.role_check_biz.check_grade_manager_unique_name(data["name"])

        # 兼容member格式
        data["members"] = [{"username": username} for username in data["members"]]

        # 结构转换
        info = self.trans.to_role_info(data, source_system_id=source_system_id)
        applications = self.biz.create_for_grade_manager(
            ApplicationTypeEnum.CREATE_GRADE_MANAGER.value,
            GradeManagerApplicationDataBean(applicant=user_id, reason=data["reason"], role_info=info),
            source_system_id=source_system_id,
            callback_id=data["callback_id"],
            callback_url=data["callback_url"],
            approval_title=data["title"],
            approval_content=data["content"],
        )

        return Response({"id": applications[0].id, "sn": applications[0].sn})


class ManagementGradeManagerUpdatedApplicationViewSet(GenericViewSet):
    """分级管理员更新申请单"""

    authentication_classes = [ESBAuthentication]
    permission_classes = [ManagementAPIPermission]
    management_api_permission = {
        "create": (
            VerifyAPIParamLocationEnum.ROLE_IN_PATH.value,
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

        source_system_id = kwargs["system_id"]

        role = get_object_or_404(Role, type=RoleType.GRADE_MANAGER.value, id=kwargs["id"])
        # 名称唯一性检查
        self.role_check_biz.check_grade_manager_unique_name(data["name"], role.name)

        # 兼容member格式
        data["members"] = [{"username": username} for username in data["members"]]

        info = self.trans.to_role_info(data, source_system_id=source_system_id)
        applications = self.biz.create_for_grade_manager(
            ApplicationTypeEnum.UPDATE_GRADE_MANAGER,
            GradeManagerApplicationDataBean(role_id=role.id, applicant=user_id, reason=data["reason"], role_info=info),
            source_system_id=source_system_id,
            callback_id=data["callback_id"],
            callback_url=data["callback_url"],
            approval_title=data["title"],
            approval_content=data["content"],
        )

        return Response({"id": applications[0].id, "sn": applications[0].sn})
