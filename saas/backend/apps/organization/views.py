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
from django.db.models import Q
from drf_yasg.openapi import Response as yasg_response
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, views
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from backend.account.permissions import role_perm_class
from backend.apps.organization.constants import SyncType
from backend.apps.organization.models import Department, SyncRecord, User
from backend.apps.organization.serializers import (
    DepartmentSLZ,
    OrganizationCategorySLZ,
    OrganizationSearchResultSLZ,
    OrganizationSearchSLZ,
    OrganizationSyncTaskSLZ,
    UserInfoSLZ,
    UserQuerySLZ,
)
from backend.apps.organization.tasks import sync_organization
from backend.common.swagger import ResponseSwaggerAutoSchema
from backend.component import usermgr
from backend.service.constants import PermissionCodeEnum
from backend.util.cache import region


class CategoryViewSet(GenericViewSet):

    paginator = None  # 去掉swagger中的limit offset参数

    @swagger_auto_schema(
        operation_description="组织架构 - 多域目录列表",
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: OrganizationCategorySLZ(label="目录", many=True)},
        tags=["organization"],
    )
    def list(self, request, *args, **kwargs):
        categories = usermgr.list_category()
        data = []
        for i in categories:
            category = {"id": i["id"], "name": i["display_name"], "departments": []}
            departments = []
            roots = Department.objects.filter(category_id=i["id"], parent=None)
            for r in roots:
                departments.append(
                    {
                        "id": r.id,
                        "name": r.name,
                        "child_count": r.child_count,
                        "member_count": r.member_count,
                        "recursive_member_count": r.recursive_member_count,
                    }
                )
            if departments:
                category["departments"] = departments
                data.append(category)
        return Response(data)


class DepartmentViewSet(GenericViewSet):

    paginator = None  # 去掉swagger中的limit offset参数

    @swagger_auto_schema(
        operation_description="组织架构 - 部门信息(包含子部门列表)",
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: DepartmentSLZ},
        tags=["organization"],
    )
    def list(self, request, *args, **kwargs):
        dept_id = kwargs["department_id"]
        root = Department.objects.get(id=dept_id)
        children = root.get_children()
        members = root.members
        data = {
            "id": root.id,
            "name": root.name,
            "child_count": root.child_count,
            "member_count": root.member_count,
            "recursive_member_count": root.recursive_member_count,
            "children": [
                {
                    "id": r.id,
                    "name": r.name,
                    "child_count": r.child_count,
                    "member_count": r.member_count,
                    "recursive_member_count": r.recursive_member_count,
                }
                for r in children
            ],
            "members": [{"username": i.username, "name": i.display_name} for i in members],
        }
        return Response(data)


class UserView(views.APIView):

    paginator = None  # 去掉swagger中的limit offset参数

    @swagger_auto_schema(
        operation_description="组织架构 - 根据批量Username查询用户信息",
        auto_schema=ResponseSwaggerAutoSchema,
        request_body=UserQuerySLZ(label="查询条件"),
        responses={status.HTTP_200_OK: UserInfoSLZ(label="用户信息列表", many=True)},
        tags=["organization"],
    )
    def post(self, request, *args, **kwargs):
        serializer = UserQuerySLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        usernames = serializer.validated_data["usernames"]

        users = User.objects.filter(username__in=usernames)

        data = [{"username": u.username, "name": u.display_name} for u in users]

        return Response(data)


class OrganizationViewSet(GenericViewSet):

    paginator = None  # 去掉swagger中的limit offset参数

    @region.cache_on_arguments(expiration_time=60 * 5)
    def get_search_data(self, keyword, is_exact, limit):
        """
        获取search数据
        """
        # 默认模糊匹配
        department_query_condition = Q(name__icontains=keyword)
        user_query_condition = Q(display_name__icontains=keyword) | Q(username__icontains=keyword)
        if is_exact:
            department_query_condition = Q(name=keyword)
            user_query_condition = Q(display_name=keyword) | Q(username=keyword)

        departments = Department.objects.filter(department_query_condition)[0:limit]
        users = User.objects.filter(user_query_condition)[0:limit]
        return departments, users

    @swagger_auto_schema(
        operation_description="组织架构 - 搜索",
        auto_schema=ResponseSwaggerAutoSchema,
        query_serializer=OrganizationSearchSLZ,
        responses={status.HTTP_200_OK: OrganizationSearchResultSLZ},
        tags=["organization"],
    )
    def list(self, request, *args, **kwargs):
        # TODO: 添加Cache,组织架构变动则clear cache
        slz = OrganizationSearchSLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)
        keyword = slz.validated_data["keyword"]
        is_exact = slz.validated_data.get("is_exact")
        limit = 500

        departments, users = self.get_search_data(keyword, is_exact, limit)
        # 最多搜索各500个，超过则提示太多
        if len(departments) == limit or len(users) == limit:
            return Response({"is_too_much": True, "departments": [], "users": []})

        data = {
            "is_too_much": False,
            "departments": [
                {
                    "id": r.id,
                    "name": r.name,
                    "full_name": r.full_name,
                    "child_count": r.child_count,
                    "member_count": r.member_count,
                    "recursive_member_count": r.recursive_member_count,
                }
                for r in departments
            ],
            "users": [{"username": i.username, "name": i.display_name} for i in users],
        }
        return Response(data)


class OrganizationSyncTaskView(views.APIView):

    permission_classes = [role_perm_class(PermissionCodeEnum.MANAGE_ORGANIZATION.value)]

    paginator = None  # 去掉swagger中的limit offset参数

    @swagger_auto_schema(
        operation_description="组织架构 - 同步任务状态查询",
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: OrganizationSyncTaskSLZ(label="最新同步任务记录")},
        tags=["organization"],
    )
    def get(self, request, *args, **kwargs):
        """获取最新一条同步任务的记录"""
        # 仅获取全量同步的任务
        record = SyncRecord.objects.filter(type=SyncType.Full.value).order_by("id").last()
        status, executor, created_time, updated_time = "", "", "", ""
        if record:
            status = record.status
            executor = record.executor
            created_time = record.created_time_display
            updated_time = record.updated_time_display
        return Response(
            {"status": status, "executor": executor, "created_time": created_time, "updated_time": updated_time}
        )

    @swagger_auto_schema(
        operation_description="组织架构 - 执行同步任务",
        auto_schema=ResponseSwaggerAutoSchema,
        responses={status.HTTP_200_OK: yasg_response({})},
        tags=["organization"],
    )
    def post(self, request, *args, **kwargs):
        username = request.user.username
        # 异步调用任务
        sync_organization.delay(username)
        return Response({})
