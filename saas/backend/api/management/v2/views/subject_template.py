"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云 - 权限中心 (BlueKing-IAM) available.
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
from backend.api.management.constants import ManagementAPIEnum, VerifyApiParamLocationEnum
from backend.api.management.v2.permissions import ManagementAPIPermission
from backend.api.management.v2.serializers import ManagementSubjectTemplateSLZ
from backend.apps.role.models import Role
from backend.apps.subject_template.filters import SubjectTemplateFilter
from backend.biz.role import RoleListQuery
from backend.common.filters import NoCheckModelFilterBackend
from backend.mixins import TenantMixin
from backend.service.constants import RoleType


class ManagementGradeManagerSubjectTemplateViewSet(TenantMixin, GenericViewSet):
    """分级管理员下人员模版"""

    authentication_classes = [ESBAuthentication]
    permission_classes = [ManagementAPIPermission]

    management_api_permission = {
        "list": (VerifyApiParamLocationEnum.ROLE_IN_PATH.value, ManagementAPIEnum.V2_SUBJECT_TEMPLATE_LIST.value),
    }

    lookup_field = "id"
    filterset_class = SubjectTemplateFilter
    filter_backends = [NoCheckModelFilterBackend]

    def get_queryset(self):
        return Role.objects.filter(
            tenant_id=self.tenant_id, type__in=[RoleType.GRADE_MANAGER.value, RoleType.SUBSET_MANAGER.value]
        ).order_by("-updated_time")

    @swagger_auto_schema(
        operation_description="人员模版列表",
        responses={status.HTTP_200_OK: ManagementSubjectTemplateSLZ(label="人员模版", many=True)},
        tags=["management.role.subject_template"],
    )
    def list(self, request, *args, **kwargs):
        role = get_object_or_404(self.get_queryset(), id=kwargs["id"])

        queryset = RoleListQuery(role).query_subject_template()
        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ManagementSubjectTemplateSLZ(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ManagementSubjectTemplateSLZ(queryset, many=True)
        return Response(serializer.data)
