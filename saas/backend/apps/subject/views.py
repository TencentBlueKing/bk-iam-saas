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

from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from backend.account.permissions import role_perm_class
from backend.account.serializers import AccountRoleSLZ
from backend.apps.group.audit import GroupMemberDeleteAuditProvider
from backend.apps.group.models import Group
from backend.apps.group.serializers import GroupSearchSLZ
from backend.apps.policy.serializers import PolicyDeleteSLZ, PolicyPartDeleteSLZ, PolicySLZ, PolicySystemSLZ
from backend.apps.user.serializers import GroupSLZ, SubjectTemplateGroupSLZ, UserPolicySearchSLZ
from backend.apps.user.views import (
    SubjectGroupSearchMixin,
    UserDepartmentSubjectTemplateGroupViewSet,
    UserPolicySearchViewSet,
    UserSubjectTemplateGroupViewSet,
)
from backend.audit.audit import audit_context_setter, view_audit_decorator
from backend.biz.group import GroupBiz
from backend.biz.policy import ConditionBean, PolicyOperationBiz, PolicyQueryBiz
from backend.biz.role import RoleBiz
from backend.common.pagination import CustomPageNumberPagination
from backend.common.serializers import SystemQuerySLZ
from backend.service.constants import PermissionCodeEnum, SubjectRelationType
from backend.service.models import Subject

from .audit import SubjectPolicyDeleteAuditProvider, SubjectTemporaryPolicyDeleteAuditProvider
from .serializers import QueryRoleSLZ, SubjectGroupSLZ, UserRelationSLZ


class SubjectGroupViewSet(GenericViewSet):
    permission_classes = [role_perm_class(PermissionCodeEnum.MANAGE_ORGANIZATION.value)]

    pagination_class = CustomPageNumberPagination

    biz = GroupBiz()

    @swagger_auto_schema(
        operation_description="我的权限-用户组列表",
        responses={status.HTTP_200_OK: SubjectGroupSLZ(label="用户组", many=True)},
        tags=["subject"],
    )
    def list(self, request, *args, **kwargs):
        subject = Subject(type=kwargs["subject_type"], id=kwargs["subject_id"])
        # 分页参数
        limit, offset = CustomPageNumberPagination().get_limit_offset_pair(request)
        count, relations = self.biz.list_paging_subject_group(subject, limit=limit, offset=offset)
        slz = GroupSLZ(instance=relations, many=True)
        return Response({"count": count, "results": slz.data})

    @swagger_auto_schema(
        operation_description="我的权限-退出用户组",
        query_serializer=UserRelationSLZ(),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["subject"],
    )
    @view_audit_decorator(GroupMemberDeleteAuditProvider)
    def destroy(self, request, *args, **kwargs):
        subject = Subject(type=kwargs["subject_type"], id=kwargs["subject_id"])

        serializer = UserRelationSLZ(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # 目前只支持移除用户的直接加入的用户组，不支持其通过部门关系加入的用户组
        if data["type"] == SubjectRelationType.GROUP.value:
            self.biz.remove_members(data["id"], [subject])

            # 写入审计上下文
            group = Group.objects.filter(id=int(data["id"])).first()
            audit_context_setter(group=group, members=[subject.dict()])

        return Response({})


class SubjectDepartmentGroupViewSet(GenericViewSet):
    permission_classes = [role_perm_class(PermissionCodeEnum.MANAGE_ORGANIZATION.value)]

    pagination_class = None

    biz = GroupBiz()

    @swagger_auto_schema(
        operation_description="我的权限-继承自部门的用户组列表",
        responses={status.HTTP_200_OK: SubjectGroupSLZ(label="用户组", many=True)},
        tags=["subject"],
    )
    def list(self, request, *args, **kwargs):
        subject = Subject(type=kwargs["subject_type"], id=kwargs["subject_id"])
        # 目前只能查询所有的, 暂时不支持分页, 如果有性能问题, 需要考虑优化
        relations = self.biz.list_all_user_department_group(subject)
        slz = GroupSLZ(instance=relations, many=True)
        return Response(slz.data)


class SubjectSystemViewSet(GenericViewSet):
    permission_classes = [role_perm_class(PermissionCodeEnum.MANAGE_ORGANIZATION.value)]

    pagination_class = None  # 去掉swagger中的limit offset参数

    biz = PolicyQueryBiz()

    @swagger_auto_schema(
        operation_description="Subject有权限的所有系统列表",
        responses={status.HTTP_200_OK: PolicySystemSLZ(label="系统", many=True)},
        tags=["subject"],
    )
    def list(self, request, *args, **kwargs):
        subject = Subject(type=kwargs["subject_type"], id=kwargs["subject_id"])

        data = self.biz.list_system_counter_by_subject(subject)

        return Response([one.dict() for one in data])


class SubjectPolicyViewSet(GenericViewSet):
    permission_classes = [role_perm_class(PermissionCodeEnum.MANAGE_ORGANIZATION.value)]

    pagination_class = None  # 去掉swagger中的limit offset参数

    policy_query_biz = PolicyQueryBiz()
    policy_operation_biz = PolicyOperationBiz()

    @swagger_auto_schema(
        operation_description="Subject权限列表",
        query_serializer=SystemQuerySLZ(),
        responses={status.HTTP_200_OK: PolicySLZ(label="策略", many=True)},
        tags=["subject"],
    )
    def list(self, request, *args, **kwargs):
        subject = Subject(type=kwargs["subject_type"], id=kwargs["subject_id"])

        slz = SystemQuerySLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)

        system_id = slz.validated_data["system_id"]

        policies = self.policy_query_biz.list_by_subject(system_id, subject)

        # ResourceNameAutoUpdate
        updated_policies = self.policy_operation_biz.update_due_to_renamed_resource(system_id, subject, policies)

        return Response([p.dict() for p in updated_policies])

    @swagger_auto_schema(
        operation_description="删除权限",
        query_serializer=PolicyDeleteSLZ(),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["subject"],
    )
    @view_audit_decorator(SubjectPolicyDeleteAuditProvider)
    def destroy(self, request, *args, **kwargs):
        subject = Subject(type=kwargs["subject_type"], id=kwargs["subject_id"])

        slz = PolicyDeleteSLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)

        system_id = slz.validated_data["system_id"]
        ids = slz.validated_data["ids"]

        # 为了记录审计日志，需要在删除前查询
        policy_list = self.policy_query_biz.query_policy_list_by_policy_ids(system_id, subject, ids)

        # 删除权限
        self.policy_operation_biz.delete_by_ids(system_id, subject, ids)

        # 写入审计上下文
        audit_context_setter(subject=subject, system_id=system_id, policies=policy_list.policies)

        return Response()

    @swagger_auto_schema(
        operation_description="权限更新",
        request_body=PolicyPartDeleteSLZ(label="条件删除"),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["subject"],
    )
    @view_audit_decorator(SubjectPolicyDeleteAuditProvider)
    def update(self, request, *args, **kwargs):
        subject = Subject(type=kwargs["subject_type"], id=kwargs["subject_id"])

        slz = PolicyPartDeleteSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        policy_id = kwargs["pk"]
        resource_group_id = data["resource_group_id"]
        resource_system_id = data["system_id"]
        resource_type = data["type"]
        condition_ids = data["ids"]
        condition = data["condition"]

        # 为避免需要忽略的变量与国际化翻译变量"_"冲突，所以使用"__"
        system_id = self.policy_query_biz.get_policy_system_by_id(subject, policy_id)
        update_policy = self.policy_operation_biz.delete_partial(
            system_id,
            subject,
            policy_id,
            resource_group_id,
            resource_system_id,
            resource_type,
            condition_ids,
            [ConditionBean(attributes=[], **c) for c in condition],
        )

        # 写入审计上下文
        audit_context_setter(subject=subject, system_id=system_id, policies=[update_policy])

        return Response({})


class SubjectPolicyResourceGroupDeleteViewSet(GenericViewSet):
    policy_query_biz = PolicyQueryBiz()
    policy_operation_biz = PolicyOperationBiz()

    @swagger_auto_schema(
        operation_description="Policy删除资源组",
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["subject"],
    )
    @view_audit_decorator(SubjectPolicyDeleteAuditProvider)
    def destroy(self, request, *args, **kwargs):
        policy_id = kwargs["pk"]
        resource_group_id = kwargs["resource_group_id"]
        subject = Subject(type=kwargs["subject_type"], id=kwargs["subject_id"])

        system_id = self.policy_query_biz.get_policy_system_by_id(subject, policy_id)
        # 删除权限
        update_policy = self.policy_operation_biz.delete_by_resource_group_id(
            system_id, subject, policy_id, resource_group_id
        )

        # 写入审计上下文
        audit_context_setter(subject=subject, system_id=system_id, policies=[update_policy])

        return Response()


class SubjectRoleViewSet(GenericViewSet):
    pagination_class = None  # 去掉swagger中的limit offset参数

    biz = RoleBiz()

    @swagger_auto_schema(
        operation_description="用户角色权限",
        query_serializer=QueryRoleSLZ(label="query_role"),
        responses={status.HTTP_200_OK: AccountRoleSLZ(label="角色信息", many=True)},
        tags=["subject"],
    )
    def list(self, request, *args, **kwargs):
        slz = QueryRoleSLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)
        with_perm = slz.validated_data["with_perm"]

        user_roles = self.biz.list_user_role(request.user.username, with_perm, with_hidden=False)
        return Response([one.dict() for one in user_roles])


class SubjectTemporaryPolicyViewSet(GenericViewSet):
    permission_classes = [role_perm_class(PermissionCodeEnum.MANAGE_ORGANIZATION.value)]

    pagination_class = None  # 去掉swagger中的limit offset参数

    policy_query_biz = PolicyQueryBiz()
    policy_operation_biz = PolicyOperationBiz()

    @swagger_auto_schema(
        operation_description="用户的所有临时权限列表",
        query_serializer=SystemQuerySLZ(),
        responses={status.HTTP_200_OK: PolicySLZ(label="策略", many=True)},
        tags=["subject"],
    )
    def list(self, request, *args, **kwargs):
        slz = SystemQuerySLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)

        system_id = slz.validated_data["system_id"]

        subject = Subject(type=kwargs["subject_type"], id=kwargs["subject_id"])
        policies = self.policy_query_biz.list_temporary_by_subject(system_id, subject)

        return Response([p.dict() for p in policies])

    @swagger_auto_schema(
        operation_description="删除权限",
        query_serializer=PolicyDeleteSLZ(),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["subject"],
    )
    @view_audit_decorator(SubjectTemporaryPolicyDeleteAuditProvider)
    def destroy(self, request, *args, **kwargs):
        slz = PolicyDeleteSLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)

        system_id = slz.validated_data["system_id"]
        ids = slz.validated_data["ids"]
        subject = Subject(type=kwargs["subject_type"], id=kwargs["subject_id"])

        policies = self.policy_query_biz.list_temporary_by_policy_ids(system_id, subject, ids)

        # 删除权限
        self.policy_operation_biz.delete_temporary_policies_by_ids(system_id, subject, ids)

        # 写入审计上下文
        audit_context_setter(subject=subject, system_id=system_id, policies=policies)

        return Response()


class SubjectTemporaryPolicySystemViewSet(GenericViewSet):
    permission_classes = [role_perm_class(PermissionCodeEnum.MANAGE_ORGANIZATION.value)]

    pagination_class = None  # 去掉swagger中的limit offset参数

    biz = PolicyQueryBiz()

    @swagger_auto_schema(
        operation_description="Subject有临时权限的所有系统列表",
        responses={status.HTTP_200_OK: PolicySystemSLZ(label="系统", many=True)},
        tags=["subject"],
    )
    def list(self, request, *args, **kwargs):
        subject = Subject(type=kwargs["subject_type"], id=kwargs["subject_id"])

        data = self.biz.list_temporary_system_counter_by_subject(subject)

        return Response([one.dict() for one in data])


class SubjectGroupSearchViewSet(SubjectGroupSearchMixin):
    @swagger_auto_schema(
        operation_description="搜索subject用户组列表",
        request_body=GroupSearchSLZ(label="用户组搜索"),
        responses={status.HTTP_200_OK: SubjectGroupSLZ(label="用户组", many=True)},
        tags=["subject"],
    )
    def search(self, request, *args, **kwargs):
        return super().search(request, *args, **kwargs)

    def get_subject(self, request, kwargs):
        return Subject(type=kwargs["subject_type"], id=kwargs["subject_id"])


class SubjectDepartmentGroupSearchViewSet(SubjectGroupSearchMixin):
    @swagger_auto_schema(
        operation_description="搜索Subject部门用户组列表",
        request_body=GroupSearchSLZ(label="用户组搜索"),
        responses={status.HTTP_200_OK: SubjectGroupSLZ(label="用户组", many=True)},
        tags=["subject"],
    )
    def search(self, request, *args, **kwargs):
        return super().search(request, *args, **kwargs)

    def get_subject(self, request, kwargs):
        return Subject(type=kwargs["subject_type"], id=kwargs["subject_id"])

    def get_group_dict(self, subject: Subject):
        groups = self.biz.list_all_user_department_group(subject)
        return {one.id: one for one in groups}

    def get_page_result(self, group_dict, page):
        return [group_dict[one.id] for one in page]


class SubjectPolicySearchViewSet(UserPolicySearchViewSet):
    @swagger_auto_schema(
        operation_description="搜索subject权限策略列表",
        request_body=UserPolicySearchSLZ(label="用户组搜索"),
        responses={status.HTTP_200_OK: PolicySLZ(label="策略", many=True)},
        tags=["subject"],
    )
    def search(self, request, *args, **kwargs):
        return super().search(request, *args, **kwargs)

    def get_subject(self, request, kwargs):
        return Subject(type=kwargs["subject_type"], id=kwargs["subject_id"])


class SubjectTemplateGroupViewSet(UserSubjectTemplateGroupViewSet):
    @swagger_auto_schema(
        operation_description="我的权限-人员模版用户组列表",
        request_body=GroupSearchSLZ(label="用户组搜索"),
        responses={status.HTTP_200_OK: SubjectTemplateGroupSLZ(label="用户组", many=True)},
        tags=["subject"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_subject(self, request, kwargs):
        return Subject(type=kwargs["subject_type"], id=kwargs["subject_id"])


class DepartmentSubjectTemplateGroupViewSet(UserDepartmentSubjectTemplateGroupViewSet):
    @swagger_auto_schema(
        operation_description="我的权限-部门人员模版用户组列表",
        request_body=GroupSearchSLZ(label="用户组搜索"),
        responses={status.HTTP_200_OK: SubjectTemplateGroupSLZ(label="用户组", many=True)},
        tags=["subject"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_subject(self, request, kwargs):
        return Subject(type=kwargs["subject_type"], id=kwargs["subject_id"])
