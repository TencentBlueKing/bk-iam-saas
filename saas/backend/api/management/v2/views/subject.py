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
from typing import Dict, List

from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from backend.api.authentication import ESBAuthentication
from backend.api.management.constants import ManagementAPIEnum, VerifyApiParamLocationEnum
from backend.api.management.v2.permissions import ManagementAPIPermission
from backend.api.management.v2.serializers import (
    ManagementMemberGroupDetailInputInPathSLZ,
    ManagementMemberGroupDetailInputSLZ,
    ManagementMemberGroupDetailOutputSLZ,
    ManagementSubjectGroupBelongSLZ,
)
from backend.apps.group.models import Group
from backend.apps.subject_template.models import SubjectTemplateGroup
from backend.biz.group import GroupBiz
from backend.common.error_codes import error_codes
from backend.component.iam import list_all_subject_groups
from backend.service.constants import GroupMemberType
from backend.service.models import Subject
from backend.util.time import utc_string_to_timestamp


class ManagementUserGroupBelongViewSet(GenericViewSet):
    """用户与用户组归属"""

    authentication_classes = [ESBAuthentication]
    permission_classes = [ManagementAPIPermission]
    management_api_permission = {
        "check": (
            VerifyApiParamLocationEnum.GROUP_IDS_IN_QUERY.value,
            ManagementAPIEnum.V2_USER_GROUPS_BELONG_CHECK.value,
        ),
    }

    pagination_class = None

    group_biz = GroupBiz()

    @swagger_auto_schema(
        operation_description="用户与用户组归属判断",
        query_serializer=ManagementSubjectGroupBelongSLZ("用户组所属判断"),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["management.user.group.belong"],
    )
    def check(self, request, *args, **kwargs):
        serializer = ManagementSubjectGroupBelongSLZ(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            group_ids_str = data["group_ids"]
            group_ids = list(map(int, group_ids_str.split(",")))
        except ValueError:
            raise error_codes.INVALID_ARGS.format(f"group_ids: {group_ids_str} valid error")

        username = kwargs["user_id"]

        group_belongs = self.group_biz.check_subject_groups_belong(
            Subject.from_username(username),
            group_ids,
        )

        return Response(group_belongs)


class ManagementDepartmentGroupBelongViewSet(GenericViewSet):
    """部门与用户组归属"""

    authentication_classes = [ESBAuthentication]
    permission_classes = [ManagementAPIPermission]
    management_api_permission = {
        "check": (
            VerifyApiParamLocationEnum.GROUP_IDS_IN_QUERY.value,
            ManagementAPIEnum.V2_DEPARTMENT_GROUPS_BELONG_CHECK.value,
        ),
    }

    pagination_class = None

    group_biz = GroupBiz()

    @swagger_auto_schema(
        operation_description="部门与用户组归属判断",
        query_serializer=ManagementSubjectGroupBelongSLZ("用户组所属判断"),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["management.department.group.belong"],
    )
    def check(self, request, *args, **kwargs):
        serializer = ManagementSubjectGroupBelongSLZ(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        group_ids = list(map(int, data["group_ids"].split(",")))
        department_id = kwargs["id"]

        group_belongs = self.group_biz.check_subject_groups_belong(
            Subject.from_department_id(department_id),
            group_ids,
        )

        return Response(group_belongs)


class ManagementMemberGroupDetailViewSet(GenericViewSet):
    """用户组成员在用户组内的详情"""

    authentication_classes = [ESBAuthentication]
    permission_classes = [ManagementAPIPermission]
    management_api_permission = {
        "list": (
            VerifyApiParamLocationEnum.GROUP_IDS_IN_QUERY.value,
            ManagementAPIEnum.V2_MEMBER_GROUPS_DETAIL_LIST.value,
        ),
    }

    pagination_class = None

    @staticmethod
    def _get_subject_group_dict(subject: Subject, group_ids: List[int]) -> Dict[int, Dict[str, int]]:
        """
        从后台查询加入的用户组详情
        """
        # Note: 可能有性能问题，部分用户加入的用户组可能过多，后续可考虑后台支持 group_ids 过滤查询
        #  这里参考了 [web api] /api/v1/roles/group_members/<subject_type>/<subject_id>/groups/
        groups = list_all_subject_groups(subject.type, subject.id)
        return {
            int(one["id"]): {
                "expired_at": one["expired_at"],
                "created_at": utc_string_to_timestamp(one["created_at"]),
            }
            for one in groups
            if int(one["id"]) in group_ids
        }

    @swagger_auto_schema(
        operation_description="用户组成员在用户组内的详情",
        responses={status.HTTP_200_OK: ManagementMemberGroupDetailOutputSLZ(label="加入用户组的详细信息", many=True)},
        tags=["management.role.group_member_detail"],
    )
    def list(self, request, *args, **kwargs):
        # URL 路径参数 获取用户组成员类型和成员 ID
        path_slz = ManagementMemberGroupDetailInputInPathSLZ(data=kwargs)
        path_slz.is_valid(raise_exception=True)
        path_data = path_slz.validated_data
        group_member_type, member_id = path_data["group_member_type"], path_data["member_id"]

        # 请求参数
        slz = ManagementMemberGroupDetailInputSLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data
        group_ids = list(map(int, data["group_ids"]))

        # 查询成员在组里的详情：过期时间、加入的时间
        subject_group_map = {}
        if group_member_type in (GroupMemberType.DEPARTMENT.value, GroupMemberType.USER.value):
            # 用户或组织
            subject = Subject(type=group_member_type, id=member_id)
            subject_group_map = self._get_subject_group_dict(subject, group_ids)
        elif group_member_type == GroupMemberType.TEMPLATE.value:
            # 人员模板
            template_groups = SubjectTemplateGroup.objects.filter(template_id=int(member_id), group_id__in=group_ids)
            subject_group_map = {
                i.group_id: {
                    "expired_at": i.expired_at,
                    "created_at": int(i.created_time.timestamp()),
                }
                for i in template_groups
            }

        # 只返回存在关系的用户组
        groups = Group.objects.filter(id__in=list(subject_group_map.keys()))

        return Response(
            ManagementMemberGroupDetailOutputSLZ(
                groups, many=True, context={"subject_group_map": subject_group_map}
            ).data
        )
