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

from copy import copy
from typing import List, Optional

from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from backend.account.serializers import AccountRoleSLZ
from backend.apps.group.audit import GroupMemberDeleteAuditProvider
from backend.apps.group.filters import GroupFilter
from backend.apps.group.models import Group
from backend.apps.group.serializers import GroupSearchSLZ
from backend.apps.policy.serializers import PolicySLZ
from backend.apps.role.serializers import RoleCommonActionSLZ
from backend.apps.subject.serializers import SubjectGroupSLZ, UserRelationSLZ
from backend.apps.user.models import UserProfile
from backend.audit.audit import audit_context_setter, view_audit_decorator
from backend.biz.constants import PermissionTypeEnum
from backend.biz.permission_audit import QueryAuthorizedSubjects
from backend.biz.policy import ConditionBean, InstanceBean, PathNodeBeanList
from backend.biz.role import ActionScopeDiffer
from backend.common.pagination import CustomPageNumberPagination
from backend.common.serializers import SystemQuerySLZ
from backend.common.time import get_soon_expire_ts
from backend.component.iam import list_all_subject_groups
from backend.mixins import BizMixin, TenantMixin
from backend.service.constants import SubjectRelationType
from backend.service.group import SubjectGroup
from backend.service.models import Subject

from .serializers import (
    GroupSLZ,
    QueryGroupSLZ,
    QueryRoleSLZ,
    SubjectTemplateGroupQuerySLZ,
    SubjectTemplateGroupSLZ,
    UserNewbieSLZ,
    UserNewbieUpdateSLZ,
    UserPolicySearchSLZ,
)


class UserGroupViewSet(BizMixin, GenericViewSet):
    pagination_class = CustomPageNumberPagination

    @swagger_auto_schema(
        operation_description="我的权限 - 用户组列表",
        query_serializer=QueryGroupSLZ(label="query_group"),
        responses={status.HTTP_200_OK: SubjectGroupSLZ(label="用户组", many=True)},
        tags=["user"],
    )
    def list(self, request, *args, **kwargs):
        slz = QueryGroupSLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)
        system_id = slz.validated_data["system_id"]

        subject = Subject.from_username(request.user.username)
        limit, offset = CustomPageNumberPagination().get_limit_offset_pair(request)

        if system_id:
            count, relations = self.group_biz.list_paging_system_subject_group(
                system_id, subject, limit=limit, offset=offset
            )
        else:
            count, relations = self.group_biz.list_paging_subject_group(subject, limit=limit, offset=offset)

        slz = GroupSLZ(instance=relations, many=True, context={"tenant_id": self.tenant_id})
        return Response({"count": count, "results": slz.data})

    @swagger_auto_schema(
        operation_description="我的权限 - 退出用户组",
        query_serializer=UserRelationSLZ(),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["user"],
    )
    @view_audit_decorator(GroupMemberDeleteAuditProvider)
    def destroy(self, request, *args, **kwargs):
        subject = Subject.from_username(request.user.username)

        serializer = UserRelationSLZ(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # 目前只支持移除用户的直接加入的用户组，不支持其通过部门关系加入的用户组
        if data["type"] == SubjectRelationType.GROUP.value:
            self.group_biz.remove_members(data["id"], [subject])

            # 写入审计上下文
            group = Group.objects.filter(id=int(data["id"])).first()
            audit_context_setter(group=group, members=[subject.dict()])

        return Response({})


class UserDepartmentGroupViewSet(BizMixin, GenericViewSet):
    pagination_class = None

    @swagger_auto_schema(
        operation_description="我的权限 - 继承自部门的用户组列表",
        responses={status.HTTP_200_OK: SubjectGroupSLZ(label="用户组", many=True)},
        tags=["user"],
    )
    def list(self, request, *args, **kwargs):
        slz = QueryGroupSLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)
        system_id = slz.validated_data["system_id"]

        subject = Subject.from_username(request.user.username)
        if system_id:
            relations = self.group_biz.list_all_system_user_department_group(system_id, subject)
        else:
            # 目前只能查询所有的，暂时不支持分页，如果有性能问题，需要考虑优化
            relations = self.group_biz.list_all_user_department_group(subject)
        slz = GroupSLZ(instance=relations, many=True, context={"tenant_id": self.tenant_id})
        return Response(slz.data)


class UserGroupRenewViewSet(BizMixin, GenericViewSet):
    pagination_class = CustomPageNumberPagination

    @swagger_auto_schema(
        operation_description="用户即将过期用户组列表",
        query_serializer=QueryGroupSLZ(label="query_group"),
        responses={status.HTTP_200_OK: SubjectGroupSLZ(label="用户组", many=True)},
        tags=["user"],
    )
    def list(self, request, *args, **kwargs):
        slz = QueryGroupSLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)
        system_id = slz.validated_data["system_id"]

        subject = Subject.from_username(request.user.username)
        limit, offset = CustomPageNumberPagination().get_limit_offset_pair(request)
        expired_at = get_soon_expire_ts()

        if system_id:
            count, relations = self.group_biz.list_paging_system_subject_group_before_expired_at(
                system_id, subject, expired_at=expired_at, limit=limit, offset=offset
            )
        else:
            count, relations = self.group_biz.list_paging_subject_group_before_expired_at(
                subject, expired_at=expired_at, limit=limit, offset=offset
            )

        slz = GroupSLZ(instance=relations, many=True, context={"tenant_id": self.tenant_id})
        return Response({"count": count, "results": slz.data})


class UserProfileNewbieViewSet(TenantMixin, GenericViewSet):
    """
    用户配置 - 新手指引
    """

    pagination_class = None  # 去掉 swagger 中的 limit offset 参数

    @swagger_auto_schema(
        operation_description="用户配置 - 新手指引",
        responses={status.HTTP_200_OK: UserNewbieSLZ(label="新手指引", many=True)},
        tags=["user"],
    )
    def list(self, request, *args, **kwargs):
        data = UserProfile.objects.list_newbie(request.user.username)
        return Response(data)

    @swagger_auto_schema(
        operation_description="用户配置 - 新手指引设置",
        request_body=UserNewbieUpdateSLZ(label="场景"),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["user"],
    )
    def create(self, request, *args, **kwargs):
        serializer = UserNewbieUpdateSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        UserProfile.objects.update_newbie(self.tenant_id, request.user.username, data["scene"], True)

        return Response({})


class UserCommonActionViewSet(BizMixin, GenericViewSet):
    """
    常用操作
    """

    pagination_class = None  # 去掉 swagger 中的 limit offset 参数

    @swagger_auto_schema(
        operation_description="常用操作列表",
        query_serializer=SystemQuerySLZ(),
        responses={status.HTTP_200_OK: RoleCommonActionSLZ(label="常用操作", many=True)},
        tags=["user"],
    )
    def list(self, request, *args, **kwargs):
        data = []

        system_id = request.query_params.get("system_id")
        if system_id:
            data = self.role_biz.list_system_common_actions(system_id)

        return Response([one.dict() for one in data])


class RoleViewSet(BizMixin, GenericViewSet):
    pagination_class = None  # 去掉 swagger 中的 limit offset 参数

    @swagger_auto_schema(
        operation_description="用户角色权限",
        query_serializer=QueryRoleSLZ(label="query_role"),
        responses={status.HTTP_200_OK: AccountRoleSLZ(label="角色信息", many=True)},
        tags=["user"],
    )
    def list(self, request, *args, **kwargs):
        slz = QueryRoleSLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)
        with_perm = slz.validated_data["with_perm"]

        user_roles = self.role_biz.list_user_role(request.user.username, with_perm, with_hidden=False)
        return Response([one.dict() for one in user_roles])


class SubjectGroupSearchMixin(BizMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSLZ

    def search(self, request, *args, **kwargs):
        slz = GroupSearchSLZ(data=request.data)
        slz.is_valid(raise_exception=True)

        data = slz.validated_data

        # 筛选
        f = GroupFilter(
            data={
                k: v
                for k, v in data.items()
                if k in ["id", "name", "description", "hidden"]
                if isinstance(v, bool) or v
            },
            queryset=self.get_queryset().filter(tenant_id=self.tenant_id),
        )
        queryset = f.qs

        subject = self.get_subject(request, kwargs)
        # 查询用户加入的所有用户组
        group_dict = self.get_group_dict(subject)
        ids = sorted(group_dict.keys())

        search_group_ids = self.search_group_ids(request, kwargs, data)
        if search_group_ids is not None:
            ids = [_id for _id in ids if _id in set(search_group_ids)]

        if not ids:
            return Response({"count": 0, "results": []})

        queryset = queryset.filter(id__in=ids)

        page = self.paginate_queryset(queryset)
        if page is not None:
            results = self.get_page_result(group_dict, page)

            slz = GroupSLZ(instance=results, many=True, context={"tenant_id": self.tenant_id})
            return Response({"count": queryset.count(), "results": slz.data})

        return Response({"count": 0, "results": []})

    def search_group_ids(self, request, kwargs, data) -> Optional[List[int]]:
        return search_group_ids(request.tenant_id, data)

    def get_subject(self, request, kwargs):
        return Subject.from_username(request.user.username)

    def get_group_dict(self, subject: Subject):
        groups = list_all_subject_groups(subject.type, subject.id)
        return {int(one["id"]): one for one in groups}

    def get_page_result(self, group_dict, page):
        relations = [SubjectGroup(**group_dict[one.id]) for one in page]
        return self.group_biz._convert_to_subject_group_beans(relations)


class UserGroupSearchViewSet(SubjectGroupSearchMixin):
    @swagger_auto_schema(
        operation_description="搜索用户用户组列表",
        request_body=GroupSearchSLZ(label="用户组搜索"),
        responses={status.HTTP_200_OK: SubjectGroupSLZ(label="用户组", many=True)},
        tags=["user"],
    )
    def search(self, request, *args, **kwargs):
        return super().search(request, *args, **kwargs)


class UserDepartmentGroupSearchViewSet(SubjectGroupSearchMixin):
    @swagger_auto_schema(
        operation_description="搜索用户部门用户组列表",
        request_body=GroupSearchSLZ(label="用户组搜索"),
        responses={status.HTTP_200_OK: SubjectGroupSLZ(label="用户组", many=True)},
        tags=["user"],
    )
    def search(self, request, *args, **kwargs):
        return super().search(request, *args, **kwargs)

    def get_group_dict(self, subject: Subject):
        groups = self.group_biz.list_all_user_department_group(subject)
        return {one.id: one for one in groups}

    def get_page_result(self, group_dict, page):
        return [group_dict[one.id] for one in page]


class UserPolicySearchViewSet(BizMixin, mixins.ListModelMixin, GenericViewSet):
    pagination_class = None  # 去掉 swagger 中的 limit offset 参数

    @swagger_auto_schema(
        operation_description="搜索用户权限策略列表",
        request_body=UserPolicySearchSLZ(label="用户组搜索"),
        responses={status.HTTP_200_OK: PolicySLZ(label="策略", many=True)},
        tags=["user"],
    )
    def search(self, request, *args, **kwargs):
        slz = UserPolicySearchSLZ(data=request.data)
        slz.is_valid(raise_exception=True)

        data = slz.validated_data
        system_id = data["system_id"]

        subject = self.get_subject(request, kwargs)
        policies = self.policy_query_biz.list_by_subject(system_id, subject)

        # ResourceNameAutoUpdate
        policies = self.policy_operation_biz.update_due_to_renamed_resource(system_id, subject, policies)

        if not data["action_id"]:
            return Response([p.dict() for p in policies])

        for p in policies:
            if p.action_id == data["action_id"]:
                for ri in data["resource_instances"]:
                    # 判断操作是否有实例的权限
                    for rg in p.resource_groups:
                        rrt = rg.get_related_resource_type(ri["system_id"], ri["type"])
                        if not rrt:
                            return Response([])

                        path = copy(ri["path"])
                        path.append({"type": ri["type"], "id": ri["id"], "name": ri["name"]})

                        conditions = [
                            ConditionBean(
                                instances=[InstanceBean(type=ri["type"], path=[PathNodeBeanList.parse_obj(path)])],
                                attributes=[],
                            )
                        ]

                        if ActionScopeDiffer(None, None)._diff_conditions(conditions, rrt.condition):
                            break
                    else:
                        # 没有匹配的策略
                        return Response([])

                return Response([p.dict()])

        # no action_id policy
        return Response([])

    def get_subject(self, request, kwargs):
        return Subject.from_username(request.user.username)


class UserSubjectTemplateGroupViewSet(BizMixin, GenericViewSet):
    pagination_class = CustomPageNumberPagination

    @swagger_auto_schema(
        operation_description="我的权限 - 人员模版用户组列表",
        request_body=GroupSearchSLZ(label="用户组搜索"),
        responses={
            status.HTTP_200_OK: SubjectTemplateGroupSLZ(label="用户组", many=True, context={"tenant_id": "tenant_id"})
        },
        tags=["user"],
    )
    def list(self, request, *args, **kwargs):
        slz = GroupSearchSLZ(data=request.data)
        slz.is_valid(raise_exception=True)

        data = slz.validated_data

        group_ids = self.search_group_ids(request, kwargs, data)

        subject = self.get_subject(request, kwargs)
        query_slz = SubjectTemplateGroupQuerySLZ(data=request.query_params)
        query_slz.is_valid(raise_exception=True)

        count = self.subject_template_biz.get_subject_template_group_count(
            subject,
            id=data["id"],
            name=data["name"],
            description=data["description"],
            hidden=data["hidden"],
            group_ids=group_ids,
            system_id=query_slz.validated_data["system_id"],
        )
        relations = self.subject_template_biz.list_paging_subject_template_group(
            subject,
            id=data["id"],
            name=data["name"],
            description=data["description"],
            hidden=data["hidden"],
            group_ids=group_ids,
            system_id=query_slz.validated_data["system_id"],
            limit=query_slz.validated_data["limit"],
            offset=query_slz.validated_data["offset"],
        )

        slz = SubjectTemplateGroupSLZ(instance=relations, many=True, context={"tenant_id": self.tenant_id})
        return Response({"count": count, "results": slz.data})

    def search_group_ids(self, request, kwargs, data) -> Optional[List[int]]:
        return search_group_ids(request.tenant_id, data)

    def get_subject(self, request, kwargs):
        return Subject.from_username(request.user.username)


def search_group_ids(tenant_id, data) -> Optional[List[int]]:
    group_ids = None
    if data["system_id"] and data["action_id"]:
        # 通过实例或操作查询用户组
        data["permission_type"] = PermissionTypeEnum.RESOURCE_INSTANCE.value
        data["limit"] = 10000
        subjects = QueryAuthorizedSubjects(tenant_id, data).query_by_resource_instance(subject_type="group")
        group_ids = list({int(s["id"]) for s in subjects})
    return group_ids


class UserDepartmentSubjectTemplateGroupViewSet(BizMixin, GenericViewSet):
    pagination_class = CustomPageNumberPagination

    @swagger_auto_schema(
        operation_description="我的权限 - 部门人员模版用户组列表",
        request_body=GroupSearchSLZ(label="用户组搜索"),
        responses={
            status.HTTP_200_OK: SubjectTemplateGroupSLZ(label="用户组", many=True, context={"tenant_id": "tenant_id"})
        },
        tags=["user"],
    )
    def list(self, request, *args, **kwargs):
        slz = GroupSearchSLZ(data=request.data)
        slz.is_valid(raise_exception=True)

        data = slz.validated_data

        group_ids = self.search_group_ids(request, kwargs, data)

        subject = self.get_subject(request, kwargs)
        query_slz = SubjectTemplateGroupQuerySLZ(data=request.query_params)
        query_slz.is_valid(raise_exception=True)

        count = self.subject_template_biz.get_subject_department_template_group_count(
            subject,
            id=data["id"],
            name=data["name"],
            description=data["description"],
            hidden=data["hidden"],
            group_ids=group_ids,
            system_id=query_slz.validated_data["system_id"],
        )
        relations = self.subject_template_biz.list_paging_subject_department_template_group(
            subject,
            id=data["id"],
            name=data["name"],
            description=data["description"],
            hidden=data["hidden"],
            group_ids=group_ids,
            system_id=query_slz.validated_data["system_id"],
            limit=query_slz.validated_data["limit"],
            offset=query_slz.validated_data["offset"],
        )

        slz = SubjectTemplateGroupSLZ(instance=relations, many=True, context={"tenant_id": self.tenant_id})
        return Response({"count": count, "results": slz.data})

    def search_group_ids(self, request, kwargs, data):
        return search_group_ids(request.tenant_id, data)

    def get_subject(self, request, kwargs):
        return Subject.from_username(request.user.username)


class UserFavoriteSystemViewSet(TenantMixin, GenericViewSet):
    """
    用户添加或删除收藏的系统
    """

    @swagger_auto_schema(
        operation_description="添加收藏系统",
        request_body=serializers.ListSerializer(child=serializers.CharField(label="系统 ID")),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["user"],
    )
    def create(self, request, *args, **kwargs):
        slz = serializers.ListSerializer(data=request.data, child=serializers.CharField(label="系统 ID"))
        slz.is_valid(raise_exception=True)

        UserProfile.objects.add_favorite_systems(self.tenant_id, request.user.username, slz.validated_data)

        return Response({})

    @swagger_auto_schema(
        operation_description="移除收藏系统",
        request_body=serializers.ListSerializer(child=serializers.CharField(label="系统 ID")),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["user"],
    )
    def destroy(self, request, *args, **kwargs):
        slz = serializers.ListSerializer(data=request.data, child=serializers.CharField(label="系统 ID"))
        slz.is_valid(raise_exception=True)

        UserProfile.objects.remove_favorite_systems(request.user.username, slz.validated_data)

        return Response({})
