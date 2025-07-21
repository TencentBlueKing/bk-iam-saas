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

from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from backend.api.authentication import ESBAuthentication
from backend.api.management.constants import ManagementAPIEnum, VerifyApiParamLocationEnum
from backend.api.management.v1.permissions import ManagementAPIPermission
from backend.api.management.v1.serializers import ManagementApplicationIDSLZ, ManagementGroupApplicationCreateSLZ
from backend.apps.organization.models import User as UserModel
from backend.biz.application import ApplicationGroupInfoBean, GroupApplicationDataBean
from backend.mixins import BizMixin
from backend.service.constants import ApplicationType, SubjectType
from backend.service.models import Applicant, Subject


class ManagementGroupApplicationViewSet(BizMixin, GenericViewSet):
    """用户组申请单"""

    authentication_classes = [ESBAuthentication]
    permission_classes = [ManagementAPIPermission]
    management_api_permission = {
        "create": (
            VerifyApiParamLocationEnum.GROUP_IDS_IN_BODY.value,
            ManagementAPIEnum.GROUP_APPLICATION_CREATE.value,
        ),
    }

    @swagger_auto_schema(
        operation_description="创建用户组申请单",
        request_body=ManagementGroupApplicationCreateSLZ(label="创建用户组申请单"),
        responses={status.HTTP_200_OK: ManagementApplicationIDSLZ(label="单据 ID 列表")},
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

        # 检查用户组数量是否超限
        self.group_biz.check_subject_groups_quota(Subject.from_username(user_id), data["group_ids"])

        # 转换为 ApplicationBiz 创建申请单所需数据结构
        user = UserModel.objects.get(username=user_id)

        # 创建申请
        applications = self.application_biz.create_for_group(
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
        )

        return Response({"ids": [a.id for a in applications]})
