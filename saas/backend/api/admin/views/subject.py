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
from django.utils.translation import gettext as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from backend.api.admin.constants import AdminAPIEnum
from backend.api.admin.permissions import AdminAPIPermission
from backend.api.admin.serializers import AdminSubjectGroupSLZ, SubjectRoleSLZ
from backend.api.authentication import ESBAuthentication
from backend.biz.group import GroupBiz
from backend.biz.role import RoleBiz
from backend.common.error_codes import error_codes
from backend.common.pagination import CompatiblePagination
from backend.service.constants import SubjectType
from backend.service.models import Subject


class AdminSubjectGroupViewSet(GenericViewSet):
    """Subject的用户组"""

    pagination_class = None  # 去掉swagger中的limit offset参数

    authentication_classes = [ESBAuthentication]
    permission_classes = [AdminAPIPermission]

    admin_api_permission = {"list": AdminAPIEnum.SUBJECT_JOINED_GROUP_LIST.value}

    group_biz = GroupBiz()

    @swagger_auto_schema(
        operation_description="Subject加入的用户组列表",
        responses={status.HTTP_200_OK: AdminSubjectGroupSLZ(label="用户组", many=True)},
        tags=["admin.subject.group"],
    )
    def list(self, request, *args, **kwargs):
        subject = Subject(type=kwargs["subject_type"], id=kwargs["subject_id"])
        relations = self.group_biz.list_subject_group(subject, is_recursive=True)
        return Response([one.dict(include={"id", "name", "expired_at"}) for one in relations])


class SubjectRoleViewSet(GenericViewSet):
    """Subject的角色列表"""

    authentication_classes = [ESBAuthentication]
    permission_classes = [AdminAPIPermission]

    admin_api_permission = {"list": AdminAPIEnum.SUBJECT_ROLE_LIST.value}

    role_biz = RoleBiz()

    @swagger_auto_schema(
        operation_description="Subject的角色列表",
        responses={status.HTTP_200_OK: SubjectRoleSLZ(label="角色信息", many=True)},
        tags=["admin.subject.group"],
    )
    def list(self, request, *args, **kwargs):
        # 分页参数
        limit, offset = CompatiblePagination().get_limit_offset_pair(request)

        # subject_type should be 'user'
        if kwargs["subject_type"] != SubjectType.USER.value:
            raise error_codes.INVALID_ARGS.format(_("只有subject_type=user才有角色"))

        subject_id = kwargs["subject_id"]

        count, data = self.role_biz.list_paging_user_role(subject_id, limit, offset)
        results = [one.dict() for one in data]
        return Response({"count": count, "results": results})
