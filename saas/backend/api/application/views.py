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
import time
from typing import List
from urllib.parse import urlencode

from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from pydantic import parse_obj_as
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, views

from backend.api.authentication import ESBAuthentication
from backend.api.permissions import ApprovalBotPermission
from backend.apps.application.models import Application
from backend.apps.application.serializers import ApplicationDetailSchemaSLZ, ApplicationDetailSLZ
from backend.apps.application.tasks import create_policies_renew_applications
from backend.apps.group.models import Group
from backend.apps.organization.models import User
from backend.apps.role.models import Role
from backend.biz.application import ApplicationBiz, ApplicationGroupInfoBean, GroupApplicationDataBean
from backend.biz.group import GroupBiz, GroupMemberExpiredAtBean
from backend.biz.helper import get_role_expired_group_members, get_user_expired_groups_policies
from backend.biz.open import ApplicationPolicyListCache
from backend.common.time import DAY_SECONDS
from backend.service.constants import ApplicationType, GroupMemberType, SubjectType
from backend.service.models.subject import Applicant
from backend.trans.open_application import AccessSystemApplicationTrans
from backend.util.url import url_join

from .serializers import (
    AccessSystemApplicationCustomPolicyResultSLZ,
    AccessSystemApplicationCustomPolicySLZ,
    AccessSystemApplicationSLZ,
    AccessSystemApplicationUrlSLZ,
    ApprovalBotRoleCallbackSLZ,
    ApprovalBotUserCallbackSLZ,
    ASApplicationCustomPolicyWithCustomTicketSLZ,
)


class ApplicationView(views.APIView):
    """
    接入系统申请
    """

    authentication_classes = [ESBAuthentication]
    permission_classes = [IsAuthenticated]

    access_system_application_trans = AccessSystemApplicationTrans()
    application_policy_list_cache = ApplicationPolicyListCache()

    @swagger_auto_schema(
        operation_description="接入系统权限申请",
        request_body=AccessSystemApplicationSLZ(label="接入系统申请数据"),
        responses={status.HTTP_200_OK: AccessSystemApplicationUrlSLZ(label="重定向URL")},
        tags=["open"],
    )
    def post(self, request):
        # 校验数据
        serializer = AccessSystemApplicationSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        system_id = data["system"]

        # 将申请的数据转换为PolicyBeanList数据结构，同时需要进行数据检查
        policy_list = self.access_system_application_trans.to_policy_list(data)

        # 保存到cache中
        cache_id = self.application_policy_list_cache.set(policy_list)

        # 返回重定向地址
        url = url_join(settings.APP_URL, "/apply-custom-perm")
        params = {"system_id": system_id, "cache_id": cache_id}
        url = url + "?" + urlencode(params)

        return Response({"url": url})


class ApplicationDetailView(GenericViewSet):
    """
    接入系统申请详情
    """

    authentication_classes = [ESBAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Application.objects.all()
    lookup_field = "sn"

    @swagger_auto_schema(
        operation_description="权限申请详情",
        responses={status.HTTP_200_OK: ApplicationDetailSchemaSLZ(label="申请详情")},
        tags=["open"],
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ApplicationDetailSLZ(instance)
        return Response(serializer.data)


class ApplicationCustomPolicyView(views.APIView):
    """
    创建自定义权限申请单
    """

    authentication_classes = [ESBAuthentication]
    permission_classes = [IsAuthenticated]

    access_system_application_trans = AccessSystemApplicationTrans()
    application_biz = ApplicationBiz()

    @swagger_auto_schema(
        operation_description="创建自定义权限申请单",
        request_body=AccessSystemApplicationCustomPolicySLZ(label="创建自定义权限申请单"),
        responses={status.HTTP_200_OK: AccessSystemApplicationCustomPolicyResultSLZ(label="申请单信息")},
        tags=["open"],
    )
    def post(self, request):
        # 校验数据
        serializer = AccessSystemApplicationCustomPolicySLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        username = data["applicant"]

        # 将Dict数据转换为创建单据所需的数据结构
        application_data = self.access_system_application_trans.from_grant_policy_application(username, data)
        # 创建单据
        applications = self.application_biz.create_for_policy(ApplicationType.GRANT_ACTION.value, application_data)

        return Response({"id": applications[0].id, "sn": applications[0].sn})


class ApprovalBotUserCallbackView(views.APIView):
    """
    审批机器人用户续期回调
    """

    authentication_classes = [ESBAuthentication]
    permission_classes = [ApprovalBotPermission]

    biz = ApplicationBiz()

    @swagger_auto_schema(
        operation_description="审批机器人用户续期回调",
        request_body=ApprovalBotUserCallbackSLZ(label="回调数据"),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["open"],
    )
    def post(self, request):
        # 校验数据
        serializer = ApprovalBotUserCallbackSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        username = data["username"]

        user = User.objects.filter(username=username).first()
        if not user:
            return Response({})

        month = data["month"]

        now = int(time.time())
        expired_at = now + month * 30 * DAY_SECONDS

        def renew_expired_at(x):
            return expired_at if x < now else x + month * 30 * DAY_SECONDS

        groups, policies = get_user_expired_groups_policies(user, data["expired_at_before"], data["expired_at_after"])
        # 生成自定义权限申请单
        if policies:
            policies_data = {
                "reason": "续期",
                "policies": [
                    {
                        "expired_at": renew_expired_at(p.policy.expired_at),
                        "id": p.policy.policy_id,
                    }
                    for p in policies
                    if p.policy
                ],
            }
            create_policies_renew_applications.delay(policies_data, username)

        # 生成用户组申请单
        if groups:
            policies_data = [
                {
                    "id": g.id,
                    "expired_at": renew_expired_at(g.expired_at),
                }
                for g in groups
            ]
            self.biz.create_for_group(
                ApplicationType.RENEW_GROUP.value,
                GroupApplicationDataBean(
                    applicant=username,
                    reason="续期",
                    groups=parse_obj_as(List[ApplicationGroupInfoBean], policies_data),
                    applicants=[Applicant(type=SubjectType.USER.value, id=username, display_name=user.display_name)],
                ),
                source_system_id="",
            )

        return Response({})


class ApprovalBotRoleCallbackView(views.APIView):
    """
    审批机器人角色回调
    """

    authentication_classes = [ESBAuthentication]
    permission_classes = [ApprovalBotPermission]

    group_biz = GroupBiz()

    @swagger_auto_schema(
        operation_description="审批机器人角色回调",
        request_body=ApprovalBotRoleCallbackSLZ(label="回调数据"),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["open"],
    )
    def post(self, request):
        # 校验数据
        serializer = ApprovalBotRoleCallbackSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        role_id = data["role_id"]

        role = Role.objects.filter(id=role_id).first()
        if not role:
            return Response({})

        month = data["month"]

        now = int(time.time())
        expired_at = now + month * 30 * DAY_SECONDS

        group_members = get_role_expired_group_members(role, data["expired_at_before"], data["expired_at_after"])
        # 用户组成员续期
        for group_member in group_members:
            group = Group.objects.filter(id=group_member["id"]).first()
            if not group:
                continue

            renew_expired_at = (
                expired_at
                if group_member["expired_at"] < now
                else group_member["expired_at"] + month * 30 * DAY_SECONDS
            )
            if group_member["subject_type"] != GroupMemberType.TEMPLATE.value:
                self.group_biz.update_members_expired_at(
                    group.id,
                    [
                        GroupMemberExpiredAtBean(
                            type=group_member["subject_type"],
                            id=group_member["subject_id"],
                            expired_at=renew_expired_at,
                        )
                    ],
                )

            # 处理人员模版的续期
            if group_member["subject_type"] == GroupMemberType.TEMPLATE.value:
                self.group_biz.update_subject_template_expired_at(
                    group.id,
                    int(group_member["subject_id"]),
                    renew_expired_at,
                )

        return Response({})


class ApplicationCustomPolicyWithCustomTicketView(views.APIView):
    """
    创建自定义权限申请单 - 允许单据自定义审批内容
    """

    authentication_classes = [ESBAuthentication]
    permission_classes = [IsAuthenticated]

    access_system_application_trans = AccessSystemApplicationTrans()
    application_biz = ApplicationBiz()

    @swagger_auto_schema(
        operation_description="创建自定义权限申请单-允许单据自定义审批内容",
        request_body=ASApplicationCustomPolicyWithCustomTicketSLZ(),
        responses={status.HTTP_200_OK: AccessSystemApplicationCustomPolicyResultSLZ(label="申请单信息", many=True)},
        tags=["open"],
    )
    def post(self, request):
        serializer = ASApplicationCustomPolicyWithCustomTicketSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        username = data["applicant"]

        # 将Dict数据转换为创建单据所需的数据结构
        (
            application_data,
            policy_ticket_contents,
        ) = self.access_system_application_trans.from_grant_policy_with_custom_ticket_application(username, data)
        # 创建单据
        applications = self.application_biz.create_for_policy(
            ApplicationType.GRANT_ACTION.value,
            application_data,
            data["ticket_content_template"] or None,
            policy_ticket_contents,
            data["ticket_title_prefix"],
        )

        return Response([{"id": a.id, "sn": a.sn} for a in applications])
