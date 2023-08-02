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
from functools import wraps
from typing import Any, Dict, List

from django.utils.translation import gettext as _
from drf_yasg.utils import swagger_auto_schema
from pydantic.tools import parse_obj_as
from rest_framework import exceptions, serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, views

from backend.apps.application.models import Application
from backend.apps.organization.models import User as UserModel
from backend.apps.role.models import Role
from backend.biz.application import (
    ApplicationBiz,
    ApplicationGroupInfoBean,
    ApplicationRenewPolicyInfoBean,
    GradeManagerApplicationDataBean,
    GroupApplicationDataBean,
)
from backend.biz.group import GroupBiz
from backend.biz.policy import PolicyBean, PolicyBeanList, PolicyQueryBiz
from backend.biz.policy_tag import ConditionTagBean, ConditionTagBiz
from backend.biz.role import RoleBiz, RoleCheckBiz, can_user_manage_role
from backend.biz.subject import SubjectInfoList
from backend.common.error_codes import error_codes
from backend.common.lock import gen_role_upsert_lock
from backend.service.constants import ADMIN_USER, ApplicationType, RoleType, SubjectType
from backend.service.models import Applicant, Subject
from backend.trans.application import ApplicationDataTrans
from backend.trans.role import RoleTrans

from .filters import ApplicationFilter
from .serializers import (
    ApplicationDetailSchemaSLZ,
    ApplicationDetailSLZ,
    ApplicationListSLZ,
    ApplicationSLZ,
    ConditionCompareSLZ,
    ConditionTagSLZ,
    GradeManagerCreatedApplicationSLZ,
    GradeManagerUpdateApplicationSLZ,
    GroupApplicationSLZ,
    RenewGroupApplicationSLZ,
    RenewPolicyApplicationSLZ,
)


def admin_not_need_apply_check(func):
    """
    admin用户不需要申请权限检查
    """

    @wraps(func)
    def wrapper(view, request, *args, **kwargs):
        if request.user.username == ADMIN_USER:
            raise error_codes.INVALID_ARGS.format(_("用户admin默认拥有任意权限, 无需申请"))

        return func(view, request, *args, **kwargs)

    return wrapper


class ApplicationViewSet(GenericViewSet):

    queryset = Application.objects.all()
    filterset_class = ApplicationFilter

    trans = ApplicationDataTrans()
    biz = ApplicationBiz()

    @swagger_auto_schema(
        operation_description="提交权限申请",
        request_body=ApplicationSLZ(label="申请"),
        responses={status.HTTP_201_CREATED: serializers.Serializer()},
        tags=["application"],
    )
    @admin_not_need_apply_check
    def create(self, request, *args, **kwargs):
        serializer = ApplicationSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        user_id = request.user.username

        # 将Dict数据转换为创建单据所需的数据结构
        application_data = self.trans.from_grant_policy_application(user_id, data)
        # 创建单据
        self.biz.create_for_policy(ApplicationType.GRANT_ACTION.value, application_data)

        return Response({}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description="权限申请列表",
        responses={status.HTTP_200_OK: ApplicationListSLZ(label="申请列表", many=True)},
        tags=["application"],
    )
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset()).filter(applicant=request.user.username)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ApplicationListSLZ(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ApplicationListSLZ(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="权限申请详情",
        responses={status.HTTP_200_OK: ApplicationDetailSchemaSLZ(label="申请详情")},
        tags=["application"],
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.applicant != request.user.username:
            raise exceptions.PermissionDenied
        serializer = ApplicationDetailSLZ(instance)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="撤销申请单",
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["application"],
    )
    def cancel(self, request, *args, **kwargs):
        user_id = request.user.username
        application = self.get_object()

        self.biz.cancel_application(application, user_id)

        return Response({})


class ApplicationApprovalView(views.APIView):
    """
    第三方系统审批后回调权限中心
    """

    # Note：目前回调接口暂时不进行API认证鉴权
    authentication_classes = ()
    permission_classes = ()

    biz = ApplicationBiz()

    # Note: 这里会回调第三方处理，所以不定义参数
    def post(self, request, *args, **kwargs):
        callback_id = kwargs["callback_id"]
        self.biz.handle_approval_callback_request(callback_id, request)
        return Response({})


class ConditionView(views.APIView):
    """
    条件对比, 对比申请的数据与已有数据的差异
    """

    policy_biz = PolicyQueryBiz()
    condition_biz = ConditionTagBiz()

    @swagger_auto_schema(
        operation_description="条件差异对比",
        request_body=ConditionCompareSLZ(label="资源条件"),
        responses={status.HTTP_200_OK: ConditionTagSLZ(label="条件差异", many=True)},
        tags=["application"],
    )
    def post(self, request, *args, **kwargs):
        serializer = ConditionCompareSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        # 1. 查询用户已有的policy的condition
        related_resource_type: Dict[str, Any] = data["related_resource_type"]
        old_condition = self.policy_biz.get_policy_resource_type_conditions(
            Subject.from_username(request.user.username),
            data["policy_id"],
            data["resource_group_id"],
            related_resource_type["system_id"],
            related_resource_type["type"],
        )

        # 2. 对比合并差异
        conditions = self.condition_biz.compare_and_tag(
            parse_obj_as(List[ConditionTagBean], related_resource_type["condition"]),
            parse_obj_as(List[ConditionTagBean], old_condition),
        )

        return Response([c.dict() for c in conditions])


class ApplicationByGroupView(views.APIView):
    """
    申请加入用户组
    """

    biz = ApplicationBiz()
    group_biz = GroupBiz()

    @swagger_auto_schema(
        operation_description="加入用户组申请",
        request_body=GroupApplicationSLZ(label="加入用户组"),
        responses={status.HTTP_201_CREATED: serializers.Serializer()},
        tags=["application"],
    )
    @admin_not_need_apply_check
    def post(self, request, *args, **kwargs):
        serializer = GroupApplicationSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        user_id = request.user.username

        # 检查用户组数量是否超限
        self.group_biz.check_subject_groups_quota(Subject.from_username(user_id), [g["id"] for g in data["groups"]])

        applicants = data["applicants"]
        if not applicants:
            applicants = [{"type": SubjectType.USER.value, "id": user_id}]

        applicant_infos = SubjectInfoList([Subject.parse_obj(one) for one in applicants]).subjects

        # 创建申请
        self.biz.create_for_group(
            ApplicationType.JOIN_GROUP.value,
            GroupApplicationDataBean(
                applicant=user_id,
                reason=data["reason"],
                groups=[ApplicationGroupInfoBean(id=g["id"], expired_at=data["expired_at"]) for g in data["groups"]],
                applicants=[Applicant(type=one.type, id=one.id, display_name=one.name) for one in applicant_infos],
            ),
            source_system_id=data["source_system_id"],
        )

        return Response({}, status=status.HTTP_201_CREATED)


class ApplicationByGradeManagerView(views.APIView):
    """
    申请创建分级管理员
    """

    biz = ApplicationBiz()
    role_check_biz = RoleCheckBiz()
    role_trans = RoleTrans()

    @swagger_auto_schema(
        operation_description="申请创建分级管理员",
        request_body=GradeManagerCreatedApplicationSLZ(label="申请创建分级管理员"),
        responses={status.HTTP_201_CREATED: serializers.Serializer()},
        tags=["application"],
    )
    def post(self, request, *args, **kwargs):
        serializer = GradeManagerCreatedApplicationSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        user_id = request.user.username

        # 结构转换
        info = self.role_trans.from_role_data(data)

        with gen_role_upsert_lock(data["name"]):
            # 名称唯一性检查
            self.role_check_biz.check_grade_manager_unique_name(data["name"])

            self.biz.create_for_grade_manager(
                ApplicationType.CREATE_GRADE_MANAGER.value,
                GradeManagerApplicationDataBean(applicant=user_id, reason=data["reason"], role_info=info),
            )

        return Response({}, status=status.HTTP_201_CREATED)


class ApplicationByGradeManagerUpdatedView(views.APIView):
    """
    申请修改分级管理员
    """

    biz = ApplicationBiz()
    role_biz = RoleBiz()
    role_check_biz = RoleCheckBiz()
    role_trans = RoleTrans()

    @swagger_auto_schema(
        operation_description="申请修改分级管理员",
        request_body=GradeManagerUpdateApplicationSLZ(label="申请修改分级管理员"),
        responses={status.HTTP_201_CREATED: serializers.Serializer()},
        tags=["application"],
    )
    def post(self, request, *args, **kwargs):
        serializer = GradeManagerUpdateApplicationSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        user_id = request.user.username

        role = Role.objects.get(type=RoleType.GRADE_MANAGER.value, id=data["id"])

        # 必须是分级管理员的成员才可以申请修改
        if not can_user_manage_role(user_id, role.id):
            raise error_codes.FORBIDDEN.format(message=_("非分级管理员({})的成员，无权限申请修改").format(role.name), replace=True)

        # 查询已有的策略范围
        old_scopes = self.role_biz.list_auth_scope(role.id)
        # 查询旧的数据
        old_system_policy_list = {
            one.system_id: PolicyBeanList(one.system_id, parse_obj_as(List[PolicyBean], one.actions))
            for one in old_scopes
        }

        info = self.role_trans.from_role_data(data, old_system_policy_list=old_system_policy_list)

        with gen_role_upsert_lock(data["name"]):
            # 名称唯一性检查
            self.role_check_biz.check_grade_manager_unique_name(data["name"], role.name)

            self.biz.create_for_grade_manager(
                ApplicationType.UPDATE_GRADE_MANAGER,
                GradeManagerApplicationDataBean(
                    role_id=role.id, applicant=user_id, reason=data["reason"], role_info=info
                ),
            )

        return Response({}, status=status.HTTP_201_CREATED)


class ApplicationByRenewGroupView(views.APIView):
    """
    申请续期用户组
    """

    biz = ApplicationBiz()

    @swagger_auto_schema(
        operation_description="续期用户组申请",
        request_body=RenewGroupApplicationSLZ(label="续期用户组"),
        responses={status.HTTP_201_CREATED: serializers.Serializer()},
        tags=["application"],
    )
    def post(self, request):
        serializer = RenewGroupApplicationSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        # 转换为ApplicationBiz创建申请单所需数据结构
        user = UserModel.objects.get(username=request.user.username)

        # 创建申请
        self.biz.create_for_group(
            ApplicationType.RENEW_GROUP.value,
            GroupApplicationDataBean(
                applicant=user.username,
                reason=data["reason"],
                groups=parse_obj_as(List[ApplicationGroupInfoBean], data["groups"]),
                applicants=[Applicant(type=SubjectType.USER.value, id=user.username, display_name=user.display_name)],
            ),
            source_system_id=data["source_system_id"],
        )

        return Response({}, status=status.HTTP_201_CREATED)


class ApplicationByRenewPolicyView(views.APIView):
    """
    申请续期权限
    """

    biz = ApplicationBiz()

    @swagger_auto_schema(
        operation_description="申请续期权限",
        request_body=RenewPolicyApplicationSLZ(label="续期用户组"),
        responses={status.HTTP_201_CREATED: serializers.Serializer()},
        tags=["application"],
    )
    def post(self, request):
        serializer = RenewPolicyApplicationSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        self.biz.create_for_renew_policy(
            parse_obj_as(List[ApplicationRenewPolicyInfoBean], data["policies"]), request.user.username, data["reason"]
        )

        return Response({}, status=status.HTTP_201_CREATED)


class ApplicationByTemporaryPolicyView(views.APIView):
    """
    申请临时权限
    """

    trans = ApplicationDataTrans()
    biz = ApplicationBiz()

    @swagger_auto_schema(
        operation_description="提交临时权限申请",
        request_body=ApplicationSLZ(label="申请"),
        responses={status.HTTP_201_CREATED: serializers.Serializer()},
        tags=["application"],
    )
    @admin_not_need_apply_check
    def post(self, request, *args, **kwargs):
        serializer = ApplicationSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        user_id = request.user.username

        # 将Dict数据转换为创建单据所需的数据结构
        application_data = self.trans.from_grant_temporary_policy_application(user_id, data)
        # 创建单据
        self.biz.create_for_policy(ApplicationType.GRANT_TEMPORARY_ACTION.value, application_data)

        return Response({}, status=status.HTTP_201_CREATED)
