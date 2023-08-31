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
from pydantic.tools import parse_obj_as
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from backend.api.authentication import ESBAuthentication
from backend.api.management.constants import ManagementAPIEnum, VerifyApiParamLocationEnum
from backend.api.management.v2.filters import GroupFilter
from backend.api.management.v2.permissions import ManagementAPIPermission
from backend.api.management.v2.serializers import (
    ManagementGradeManagerGroupCreateSLZ,
    ManagementGroupBaseInfoUpdateSLZ,
    ManagementGroupGrantSLZ,
    ManagementGroupMemberDeleteSLZ,
    ManagementGroupMemberSLZ,
    ManagementGroupPolicyDeleteSLZ,
    ManagementGroupRevokeSLZ,
    ManagementGroupSLZ,
    ManagementQueryGroupSLZ,
)
from backend.apps.group.audit import (
    GroupCreateAuditProvider,
    GroupDeleteAuditProvider,
    GroupMemberCreateAuditProvider,
    GroupMemberDeleteAuditProvider,
    GroupMemberRenewAuditProvider,
    GroupPolicyCreateAuditProvider,
    GroupPolicyDeleteAuditProvider,
    GroupPolicyUpdateAuditProvider,
    GroupUpdateAuditProvider,
)
from backend.apps.group.models import Group
from backend.apps.group.serializers import GroupAddMemberSLZ
from backend.apps.policy.models import Policy
from backend.apps.policy.serializers import PolicySLZ
from backend.apps.role.models import Role
from backend.audit.audit import add_audit, audit_context_setter, view_audit_decorator
from backend.audit.constants import AuditSourceType
from backend.biz.group import (
    GroupBiz,
    GroupCheckBiz,
    GroupCreationBean,
    GroupMemberExpiredAtBean,
    GroupTemplateGrantBean,
)
from backend.biz.policy import PolicyOperationBiz, PolicyQueryBiz
from backend.biz.role import RoleBiz, RoleListQuery
from backend.common.filters import NoCheckModelFilterBackend
from backend.common.lock import gen_group_upsert_lock
from backend.common.pagination import CompatiblePagination
from backend.service.constants import GroupSaaSAttributeEnum, RoleType, SubjectType
from backend.service.models import Subject
from backend.trans.open_management import ManagementCommonTrans


class ManagementGradeManagerGroupViewSet(GenericViewSet):
    """分级管理员下用户组"""

    authentication_classes = [ESBAuthentication]
    permission_classes = [ManagementAPIPermission]

    management_api_permission = {
        "create": (VerifyApiParamLocationEnum.ROLE_IN_PATH.value, ManagementAPIEnum.V2_GROUP_BATCH_CREATE.value),
        "list": (VerifyApiParamLocationEnum.ROLE_IN_PATH.value, ManagementAPIEnum.V2_GROUP_LIST.value),
    }

    lookup_field = "id"
    queryset = Role.objects.filter(type__in=[RoleType.GRADE_MANAGER.value, RoleType.SUBSET_MANAGER.value]).order_by(
        "-updated_time"
    )
    filterset_class = GroupFilter
    filter_backends = [NoCheckModelFilterBackend]

    group_biz = GroupBiz()
    group_check_biz = GroupCheckBiz()

    @swagger_auto_schema(
        operation_description="批量创建用户组",
        request_body=ManagementGradeManagerGroupCreateSLZ(label="用户组"),
        responses={status.HTTP_200_OK: serializers.ListSerializer(child=serializers.IntegerField(label="用户组ID"))},
        tags=["management.role.group"],
    )
    def create(self, request, *args, **kwargs):
        if "id" not in kwargs:
            role = get_object_or_404(Role, type=RoleType.SYSTEM_MANAGER.value, code=kwargs["system_id"])
        else:
            role = get_object_or_404(self.queryset, id=kwargs["id"])

        serializer = ManagementGradeManagerGroupCreateSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)
        groups_data = serializer.validated_data["groups"]

        # 用户组数量在角色内是否超限
        self.group_check_biz.check_role_group_limit(role, len(groups_data))

        infos = parse_obj_as(List[GroupCreationBean], groups_data)
        # 来源系统是否隐藏与角色保持一致
        for one in infos:
            one.source_system_id = role.source_system_id
            one.hidden = role.hidden

        attrs = None
        if serializer.validated_data["create_attributes"]:
            attrs = {
                GroupSaaSAttributeEnum.SOURCE_TYPE.value: AuditSourceType.OPENAPI.value,
            }

        with gen_group_upsert_lock(role.id):
            # 用户组名称在角色内唯一
            group_names = [g["name"] for g in groups_data]
            self.group_check_biz.batch_check_role_group_names_unique(role.id, group_names)

            groups = self.group_biz.batch_create(
                role.id,
                infos,
                request.user.username,
                attrs=attrs,
            )

        # 添加审计信息
        # TODO: 后续其他地方也需要批量添加审计时再抽象出一个batch_add_audit方法，将for循环逻辑放到方法里
        for g in groups:
            add_audit(GroupCreateAuditProvider, request, group=g)

        return Response([group.id for group in groups])

    @swagger_auto_schema(
        operation_description="用户组列表",
        query_serializer=ManagementQueryGroupSLZ(label="query_group"),
        responses={status.HTTP_200_OK: ManagementGroupSLZ(label="用户组", many=True)},
        tags=["management.role.group"],
    )
    def list(self, request, *args, **kwargs):
        slz = ManagementQueryGroupSLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)
        inherit = slz.validated_data["inherit"]

        role = get_object_or_404(self.queryset, id=kwargs["id"])

        queryset = RoleListQuery(role).query_group(inherit=inherit)
        queryset = self.filter_queryset(queryset)
        queryset = self._filter(request, queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ManagementGroupSLZ(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ManagementGroupSLZ(queryset, many=True)
        return Response(serializer.data)

    def _filter(self, request, queryset):
        """
        用户组筛选
        """
        system_id = self.kwargs["system_id"]

        # 使用操作, 资源实例筛选有权限的用户组
        action_id = request.query_params.get("action_id") or ""
        resource_type_system_id = request.query_params.get("resource_type_system_id")
        resource_type_id = request.query_params.get("resource_type_id")
        resource_id = request.query_params.get("resource_id")
        bk_iam_path = request.query_params.get("bk_iam_path") or ""

        if action_id and (not resource_type_system_id or not resource_type_id or not resource_id):
            # 只使用action_id筛选
            return self._filter_by_action(queryset, system_id, action_id)

        if resource_type_system_id and resource_type_id and resource_id:
            # 使用操作, 资源实例筛选
            return self._filter_by_action_resource(
                queryset, system_id, action_id, resource_type_system_id, resource_type_id, resource_id, bk_iam_path
            )

        return queryset

    def _filter_by_action(self, queryset, system_id: str, action_id: str):
        """
        筛选有自定义权限的用户组
        """
        group_ids = list(
            Policy.objects.filter(
                subject_type=SubjectType.GROUP.value, system_id=system_id, action_id=action_id
            ).values_list("subject_id", flat=True)
        )
        if not group_ids:
            return Group.objects.none()

        return queryset.filter(id__in=[int(id) for id in group_ids])

    def _filter_by_action_resource(
        self,
        queryset,
        system_id: str,
        action_id: str,
        resource_type_system_id: str,
        resource_type_id: str,
        resource_id: str,
        bk_iam_path: str = "",
    ):
        """
        筛选有实例操作权限的用户组
        """
        subjects = self.group_biz.list_rbac_group_by_resource(
            system_id, action_id, resource_type_system_id, resource_type_id, resource_id, bk_iam_path
        )
        if not subjects:
            return Group.objects.none()

        return queryset.filter(id__in=[int(subject.id) for subject in subjects])


class ManagementSystemManagerGroupViewSet(ManagementGradeManagerGroupViewSet):
    authentication_classes = [ESBAuthentication]
    permission_classes = [ManagementAPIPermission]

    management_api_permission = {
        # 对于在系统管理员下创建用户组，可以忽略参数里的权限校验来源
        "create": (VerifyApiParamLocationEnum.SYSTEM_IN_PATH.value, ManagementAPIEnum.V2_GROUP_BATCH_CREATE.value),
    }

    lookup_field = "code"
    lookup_url_kwarg = "system_id"
    queryset = Role.objects.filter(type=RoleType.SYSTEM_MANAGER.value).order_by("-updated_time")

    @swagger_auto_schema(
        operation_description="系统管理员下批量创建用户组",
        request_body=ManagementGradeManagerGroupCreateSLZ(label="用户组"),
        responses={status.HTTP_200_OK: serializers.ListSerializer(child=serializers.IntegerField(label="用户组ID"))},
        tags=["management.role.group"],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class ManagementGroupViewSet(GenericViewSet):
    """用户组"""

    authentication_classes = [ESBAuthentication]
    permission_classes = [ManagementAPIPermission]

    management_api_permission = {
        "update": (VerifyApiParamLocationEnum.GROUP_IN_PATH.value, ManagementAPIEnum.V2_GROUP_UPDATE.value),
        "destroy": (VerifyApiParamLocationEnum.GROUP_IN_PATH.value, ManagementAPIEnum.V2_GROUP_DELETE.value),
    }

    lookup_field = "id"
    queryset = Group.objects.all()

    biz = GroupBiz()
    group_check_biz = GroupCheckBiz()
    role_biz = RoleBiz()

    @swagger_auto_schema(
        operation_description="修改用户组",
        request_body=ManagementGroupBaseInfoUpdateSLZ(label="用户组"),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["management.role.group"],
    )
    @view_audit_decorator(GroupUpdateAuditProvider)
    def update(self, request, *args, **kwargs):
        group = self.get_object()

        serializer = ManagementGroupBaseInfoUpdateSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = request.user.username
        data = serializer.validated_data

        # 只更新非空值
        name = data.get("name") or group.name
        description = data.get("description") or group.description

        # 用户组名称在角色内唯一
        role = self.role_biz.get_role_by_group_id(group.id)

        with gen_group_upsert_lock(role.id):
            self.group_check_biz.check_role_group_name_unique(role.id, name, group.id)

            # 更新
            group = self.biz.update(group, name, description, group.apply_disable, user_id)

        # 写入审计上下文
        audit_context_setter(group=group)

        return Response({})

    @swagger_auto_schema(
        operation_description="删除用户组",
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["management.role.group"],
    )
    @view_audit_decorator(GroupDeleteAuditProvider)
    def destroy(self, request, *args, **kwargs):
        group = self.get_object()

        self.biz.delete(group.id)

        # 写入审计上下文
        audit_context_setter(group=group)

        return Response({})


class ManagementGroupMemberViewSet(GenericViewSet):
    """用户组成员"""

    authentication_classes = [ESBAuthentication]
    permission_classes = [ManagementAPIPermission]

    management_api_permission = {
        "list": (VerifyApiParamLocationEnum.GROUP_IN_PATH.value, ManagementAPIEnum.V2_GROUP_MEMBER_LIST.value),
        "create": (VerifyApiParamLocationEnum.GROUP_IN_PATH.value, ManagementAPIEnum.V2_GROUP_MEMBER_ADD.value),
        "destroy": (VerifyApiParamLocationEnum.GROUP_IN_PATH.value, ManagementAPIEnum.V2_GROUP_MEMBER_DELETE.value),
    }

    lookup_field = "id"
    queryset = Group.objects.all()
    pagination_class = CompatiblePagination

    biz = GroupBiz()
    group_check_biz = GroupCheckBiz()
    role_biz = RoleBiz()

    @swagger_auto_schema(
        operation_description="用户组成员列表",
        responses={status.HTTP_200_OK: ManagementGroupMemberSLZ(label="用户组成员信息", many=True)},
        tags=["management.role.group.member"],
    )
    def list(self, request, *args, **kwargs):
        group = self.get_object()

        # 分页参数
        limit, offset = CompatiblePagination().get_limit_offset_pair(request)

        count, group_members = self.biz.list_paging_group_member(group.id, limit, offset)
        results = [one.dict(include={"type", "id", "name", "expired_at"}) for one in group_members]
        return Response({"count": count, "results": results})

    @swagger_auto_schema(
        operation_description="用户组添加成员",
        request_body=GroupAddMemberSLZ(label="用户组成员"),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["management.role.group.member"],
    )
    @view_audit_decorator(GroupMemberCreateAuditProvider)
    def create(self, request, *args, **kwargs):
        group = self.get_object()

        serializer = GroupAddMemberSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        members_data = data["members"]
        expired_at = data["expired_at"]
        # 成员Dict结构转换为Subject结构，并去重
        members = list(set(parse_obj_as(List[Subject], members_data)))

        # 检测成员是否满足管理的授权范围
        role = self.role_biz.get_role_by_group_id(group.id)
        self.group_check_biz.check_role_subject_scope(role, members)
        self.group_check_biz.check_member_count(group.id, len(members))

        # 添加成员
        self.biz.add_members(group.id, members, expired_at)

        # 写入审计上下文
        audit_context_setter(group=group, members=[m.dict() for m in members])

        return Response({})

    @swagger_auto_schema(
        operation_description="用户组删除成员",
        query_serializer=ManagementGroupMemberDeleteSLZ(label="用户组成员"),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["management.role.group.member"],
    )
    @view_audit_decorator(GroupMemberDeleteAuditProvider)
    def destroy(self, request, *args, **kwargs):
        group = self.get_object()

        serializer = ManagementGroupMemberDeleteSLZ(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        members = [Subject(**{"type": data["type"], "id": _id}) for _id in data["ids"]]
        self.biz.remove_members(str(group.id), members)

        # 写入审计上下文
        audit_context_setter(group=group, members=[m.dict() for m in members])

        return Response({})


class ManagementGroupMemberExpiredAtViewSet(GenericViewSet):
    """用户组成员有效期"""

    authentication_classes = [ESBAuthentication]
    permission_classes = [ManagementAPIPermission]

    management_api_permission = {
        "update": (
            VerifyApiParamLocationEnum.GROUP_IN_PATH.value,
            ManagementAPIEnum.V2_GROUP_MEMBER_EXPIRED_AT_UPDATE.value,
        ),
    }

    lookup_field = "id"
    queryset = Group.objects.all()

    biz = GroupBiz()

    @swagger_auto_schema(
        operation_description="用户组成员有效期更新",
        request_body=GroupAddMemberSLZ(label="用户组成员"),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["management.role.group.member"],
    )
    @view_audit_decorator(GroupMemberRenewAuditProvider)
    def update(self, request, *args, **kwargs):
        group = self.get_object()

        serializer = GroupAddMemberSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        members = [
            GroupMemberExpiredAtBean(type=m["type"], id=m["id"], expired_at=data["expired_at"])
            for m in data["members"]
        ]

        # 更新有效期
        self.biz.update_members_expired_at(group.id, members)

        # 写入审计上下文
        audit_context_setter(group=group, members=data["members"])

        return Response({})


class ManagementGroupPolicyViewSet(GenericViewSet):
    """用户组权限 - 自定义权限"""

    authentication_classes = [ESBAuthentication]
    permission_classes = [ManagementAPIPermission]

    pagination_class = None  # 去掉swagger中的limit offset参数

    management_api_permission = {
        "list": (VerifyApiParamLocationEnum.GROUP_IN_PATH.value, ManagementAPIEnum.GROUP_POLICY_LIST.value),
        "create": (VerifyApiParamLocationEnum.GROUP_IN_PATH.value, ManagementAPIEnum.GROUP_POLICY_GRANT.value),
        "destroy": (VerifyApiParamLocationEnum.GROUP_IN_PATH.value, ManagementAPIEnum.GROUP_POLICY_REVOKE.value),
    }

    lookup_field = "id"
    queryset = Group.objects.all()

    group_biz = GroupBiz()
    role_biz = RoleBiz()
    policy_operation_biz = PolicyOperationBiz()
    policy_query_biz = PolicyQueryBiz()
    trans = ManagementCommonTrans()

    @swagger_auto_schema(
        operation_description="用户组授权",
        request_body=ManagementGroupGrantSLZ(label="权限"),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["management.role.group.policy"],
    )
    @view_audit_decorator(GroupPolicyCreateAuditProvider)
    def create(self, request, *args, **kwargs):
        group = self.get_object()
        # 序列化数据
        serializer = ManagementGroupGrantSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        system_id = data["system"] or kwargs["system_id"]
        action_ids = [a["id"] for a in data["actions"]]
        resources = data["resources"]

        # 将授权的权限数据转为PolicyBeanList
        policy_list = self.trans.to_policy_list_for_batch_action_and_resources(system_id, action_ids, resources)

        # 组装数据进行对用户组权限处理
        template = GroupTemplateGrantBean(
            system_id=system_id,
            template_id=0,  # 自定义权限template_id为0
            policies=policy_list.policies,
        )
        role = self.role_biz.get_role_by_group_id(group.id)

        # 检查数据正确性：授权范围是否超限角色访问，这里不需要检查资源实例名称，因为授权时，接入系统可能使用同步方式，这时候资源可能还没创建
        self.group_biz.check_before_grant(
            group, [template], role, need_check_action_not_exists=False, need_check_resource_name=False
        )

        # Note: 这里不能使用 group_biz封装的"异步"授权（其是针对模板权限的），否则会导致连续授权时，第二次调用会失败
        # 这里主要是针对自定义授权，直接使用policy_biz提供的方法即可
        self.policy_operation_biz.alter(system_id, Subject.from_group_id(group.id), policy_list.policies)

        # 写入审计上下文
        audit_context_setter(group=group, system_id=system_id, policies=policy_list.policies)

        return Response({})

    @swagger_auto_schema(
        operation_description="用户组权限回收",
        request_body=ManagementGroupRevokeSLZ(label="权限"),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["management.role.group.policy"],
    )
    @view_audit_decorator(GroupPolicyUpdateAuditProvider)
    def destroy(self, request, *args, **kwargs):
        group = self.get_object()
        # 序列化数据
        serializer = ManagementGroupRevokeSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        system_id = data["system"] or kwargs["system_id"]
        action_ids = [a["id"] for a in data["actions"]]
        resources = data["resources"]

        # 将授权的权限数据转为PolicyBeanList
        policy_list = self.trans.to_policy_list_for_batch_action_and_resources(system_id, action_ids, resources)

        # Note: 这里不能使用 group_biz封装的"异步"变更权限（其是针对模板权限的），否则会导致连续授权时，第二次调用会失败
        # 这里主要是针对自定义授权的回收，直接使用policy_biz提供的方法即可
        self.policy_operation_biz.revoke(system_id, Subject.from_group_id(group.id), policy_list.policies)

        # 写入审计上下文
        audit_context_setter(group=group, system_id=system_id, policies=policy_list.policies)

        return Response({})

    @swagger_auto_schema(
        operation_description="用户组自定义权限列表",
        responses={status.HTTP_200_OK: PolicySLZ(label="策略", many=True)},
        tags=["management.role.group.policy"],
    )
    def list(self, request, *args, **kwargs):
        system_id = kwargs["system_id"]
        group = self.get_object()

        subject = Subject.from_group_id(group.id)

        policies = self.policy_query_biz.list_by_subject(system_id, subject)

        # ResourceNameAutoUpdate
        updated_policies = self.policy_operation_biz.update_due_to_renamed_resource(system_id, subject, policies)

        return Response([p.dict() for p in updated_policies])


class ManagementGroupActionPolicyViewSet(GenericViewSet):
    """用户组权限 - 自定义权限 - 操作级别变更"""

    authentication_classes = [ESBAuthentication]
    permission_classes = [ManagementAPIPermission]

    management_api_permission = {
        "destroy": (VerifyApiParamLocationEnum.GROUP_IN_PATH.value, ManagementAPIEnum.V2_GROUP_POLICY_DELETE.value),
    }

    lookup_field = "id"
    queryset = Group.objects.all()

    group_biz = GroupBiz()
    policy_query_biz = PolicyQueryBiz()
    policy_operation_biz = PolicyOperationBiz()

    @swagger_auto_schema(
        operation_description="用户组权限删除",
        request_body=ManagementGroupPolicyDeleteSLZ(label="权限"),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["management.role.group.policy"],
    )
    @view_audit_decorator(GroupPolicyDeleteAuditProvider)
    def destroy(self, request, *args, **kwargs):
        group = self.get_object()
        # 序列化数据
        serializer = ManagementGroupPolicyDeleteSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        system_id = data["system"] or kwargs["system_id"]
        action_ids = [a["id"] for a in data["actions"]]

        # 查询将要被删除PolicyID列表
        policies = self.policy_query_biz.list_by_subject(system_id, Subject.from_group_id(group.id), action_ids)

        # 根据PolicyID删除策略
        policy_ids = [p.policy_id for p in policies]
        self.policy_operation_biz.delete_by_ids(system_id, Subject.from_group_id(group.id), policy_ids)

        # 写入审计上下文
        audit_context_setter(group=group, system_id=system_id, policies=policies)

        return Response({})


class ManagementGroupPolicyActionViewSet(GenericViewSet):
    """用户组自定义权限 - 操作"""

    authentication_classes = [ESBAuthentication]
    permission_classes = [ManagementAPIPermission]

    management_api_permission = {
        "list": (VerifyApiParamLocationEnum.GROUP_IN_PATH.value, ManagementAPIEnum.V2_GROUP_POLICY_ACTION_LIST.value),
    }

    lookup_field = "id"
    queryset = Group.objects.all()

    group_biz = GroupBiz()
    policy_query_biz = PolicyQueryBiz()

    @swagger_auto_schema(
        operation_description="查询用户组有权限的Action列表",
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["management.role.group.policy"],
    )
    def list(self, request, *args, **kwargs):
        group = self.get_object()

        system_id = kwargs["system_id"]
        subject = Subject.from_group_id(group.id)

        # 查询用户组Policy列表
        policies = self.policy_query_biz.list_by_subject(system_id, subject)

        return Response([{"id": p.action_id} for p in policies])
