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
from copy import copy

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
from backend.apps.role.constants import PermissionTypeEnum
from backend.apps.role.serializers import RoleCommonActionSLZ
from backend.apps.subject.serializers import SubjectGroupSLZ, UserRelationSLZ
from backend.apps.user.models import UserProfile
from backend.audit.audit import audit_context_setter, view_audit_decorator
from backend.biz.group import GroupBiz
from backend.biz.permission_audit import QueryAuthorizedSubjects
from backend.biz.policy import ConditionBean, InstanceBean, PathNodeBeanList, PolicyOperationBiz, PolicyQueryBiz
from backend.biz.role import ActionScopeDiffer, RoleBiz
from backend.common.pagination import CustomPageNumberPagination
from backend.common.serializers import SystemQuerySLZ
from backend.common.time import get_soon_expire_ts
from backend.component.iam import list_all_subject_groups
from backend.service.constants import SubjectRelationType
from backend.service.group import SubjectGroup
from backend.service.models import Subject

from .serializers import GroupSLZ, QueryGroupSLZ, QueryRoleSLZ, UserNewbieSLZ, UserNewbieUpdateSLZ, UserPolicySearchSLZ


class UserGroupViewSet(GenericViewSet):

    pagination_class = CustomPageNumberPagination

    biz = GroupBiz()

    @swagger_auto_schema(
        operation_description="我的权限-用户组列表",
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
            count, relations = self.biz.list_paging_system_subject_group(
                system_id, subject, limit=limit, offset=offset
            )
        else:
            count, relations = self.biz.list_paging_subject_group(subject, limit=limit, offset=offset)

        slz = GroupSLZ(instance=relations, many=True)
        return Response({"count": count, "results": slz.data})

    @swagger_auto_schema(
        operation_description="我的权限-退出用户组",
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
            self.biz.remove_members(data["id"], [subject])

            # 写入审计上下文
            group = Group.objects.filter(id=int(data["id"])).first()
            audit_context_setter(group=group, members=[subject.dict()])

        return Response({})


class UserDepartmentGroupViewSet(GenericViewSet):

    pagination_class = None

    biz = GroupBiz()

    @swagger_auto_schema(
        operation_description="我的权限-继承自部门的用户组列表",
        responses={status.HTTP_200_OK: SubjectGroupSLZ(label="用户组", many=True)},
        tags=["user"],
    )
    def list(self, request, *args, **kwargs):
        subject = Subject.from_username(request.user.username)
        # 目前只能查询所有的, 暂时不支持分页, 如果有性能问题, 需要考虑优化
        relations = self.biz.list_all_user_department_group(subject)
        slz = GroupSLZ(instance=relations, many=True)
        return Response(slz.data)


class UserGroupRenewViewSet(GenericViewSet):

    pagination_class = CustomPageNumberPagination

    # service
    group_biz = GroupBiz()

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

        slz = GroupSLZ(instance=relations, many=True)
        return Response({"count": count, "results": slz.data})


class UserProfileNewbieViewSet(GenericViewSet):
    """
    用户配置-新手指引
    """

    pagination_class = None  # 去掉swagger中的limit offset参数

    @swagger_auto_schema(
        operation_description="用户配置-新手指引",
        responses={status.HTTP_200_OK: UserNewbieSLZ(label="新手指引", many=True)},
        tags=["user"],
    )
    def list(self, request, *args, **kwargs):
        data = UserProfile.objects.list_newbie(request.user.username)
        return Response(data)

    @swagger_auto_schema(
        operation_description="用户配置-新手指引设置",
        request_body=UserNewbieUpdateSLZ(label="场景"),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["user"],
    )
    def create(self, request, *args, **kwargs):
        serializer = UserNewbieUpdateSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        UserProfile.objects.update_newbie(request.user.username, data["scene"], True)

        return Response({})


class UserCommonActionViewSet(GenericViewSet):
    """
    常用操作
    """

    pagination_class = None  # 去掉swagger中的limit offset参数

    role_biz = RoleBiz()

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


class RoleViewSet(GenericViewSet):

    pagination_class = None  # 去掉swagger中的limit offset参数

    biz = RoleBiz()

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

        user_roles = self.biz.list_user_role(request.user.username, with_perm, with_hidden=False)
        return Response([one.dict() for one in user_roles])


class UserGroupSearchViewSet(mixins.ListModelMixin, GenericViewSet):

    queryset = Group.objects.all()
    serializer_class = GroupSLZ

    biz = GroupBiz()

    @swagger_auto_schema(
        operation_description="搜索用户用户组列表",
        request_body=GroupSearchSLZ(label="用户组搜索"),
        responses={status.HTTP_200_OK: SubjectGroupSLZ(label="用户组", many=True)},
        tags=["user"],
    )
    def search(self, request, *args, **kwargs):
        slz = GroupSearchSLZ(data=request.data)
        slz.is_valid(raise_exception=True)

        data = slz.validated_data

        # 筛选
        f = GroupFilter(
            data={k: v for k, v in data.items() if k in ["id", "name", "description"] and v},
            queryset=self.get_queryset(),
        )
        queryset = f.qs

        subject = Subject.from_username(request.user.username)
        # 查询用户加入的所有用户组
        groups = list_all_subject_groups(subject.type, subject.id)
        ids = sorted([int(g["id"]) for g in groups])

        if data["system_id"] and data["action_id"]:
            # 通过实例或操作查询用户组
            data["permission_type"] = PermissionTypeEnum.RESOURCE_INSTANCE.value
            data["limit"] = 1000
            subjects = QueryAuthorizedSubjects(data).query_by_resource_instance(subject_type="group")
            subject_id_set = {int(s["id"]) for s in subjects}

            # 筛选同时有权限并且用户加入的用户组
            ids = [_id for _id in ids if _id in subject_id_set]

        if not ids:
            return Response({"count": 0, "results": []})

        queryset = queryset.filter(id__in=ids)

        page = self.paginate_queryset(queryset)
        if page is not None:
            group_dict = {int(one["id"]): one for one in groups}
            relations = [SubjectGroup(**group_dict[one.id]) for one in page]
            results = self.biz._convert_to_subject_group_beans(relations)

            slz = GroupSLZ(instance=results, many=True)
            return Response({"count": queryset.count(), "results": slz.data})

        return Response({"count": 0, "results": []})


class UserDepartmentGroupSearchViewSet(mixins.ListModelMixin, GenericViewSet):

    queryset = Group.objects.all()
    serializer_class = GroupSLZ

    biz = GroupBiz()

    @swagger_auto_schema(
        operation_description="搜索用户部门用户组列表",
        request_body=GroupSearchSLZ(label="用户组搜索"),
        responses={status.HTTP_200_OK: SubjectGroupSLZ(label="用户组", many=True)},
        tags=["user"],
    )
    def search(self, request, *args, **kwargs):
        slz = GroupSearchSLZ(data=request.data)
        slz.is_valid(raise_exception=True)

        data = slz.validated_data

        # 筛选
        f = GroupFilter(
            data={k: v for k, v in data.items() if k in ["id", "name", "description"] and v},
            queryset=self.get_queryset(),
        )
        queryset = f.qs

        subject = Subject.from_username(request.user.username)
        groups = self.biz.list_all_user_department_group(subject)

        # 查询用户加入的所有用户组
        ids = sorted([g.id for g in groups])

        if data["system_id"] and data["action_id"]:
            # 通过实例或操作查询用户组
            data["permission_type"] = PermissionTypeEnum.RESOURCE_INSTANCE.value
            data["limit"] = 1000
            subjects = QueryAuthorizedSubjects(data).query_by_resource_instance(subject_type="group")
            subject_id_set = {int(s["id"]) for s in subjects}

            # 筛选同时有权限并且用户加入的用户组
            ids = [_id for _id in ids if _id in subject_id_set]

        if not ids:
            return Response({"count": 0, "results": []})

        queryset = queryset.filter(id__in=ids)

        page = self.paginate_queryset(queryset)
        if page is not None:
            group_dict = {one.id: one for one in groups}
            relations = [group_dict[one.id] for one in page]

            slz = GroupSLZ(instance=relations, many=True)
            return Response({"count": queryset.count(), "results": slz.data})

        return Response({"count": 0, "results": []})


class UserPolicySearchViewSet(mixins.ListModelMixin, GenericViewSet):

    pagination_class = None  # 去掉swagger中的limit offset参数

    policy_query_biz = PolicyQueryBiz()
    policy_operation_biz = PolicyOperationBiz()

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

        subject = Subject.from_username(request.user.username)
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
