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

from rest_framework import serializers

from .constants import SyncTaskStatus


class UserInfoSLZ(serializers.Serializer):
    username = serializers.CharField(label="用户名")
    name = serializers.CharField(label="中文名称")


class DepartmentBaseInfoSLZ(serializers.Serializer):
    id = serializers.IntegerField(label="部门ID")
    name = serializers.CharField(label="部门名称")
    full_name = serializers.CharField(label="部门全名称")
    child_count = serializers.IntegerField(label="子部门数量")
    member_count = serializers.IntegerField(label="成员数量")
    recursive_member_count = serializers.IntegerField(label="递归成员数量")


class OrganizationCategorySLZ(serializers.Serializer):
    id = serializers.IntegerField(label="目录ID")
    name = serializers.CharField(label="目录名称")
    departments = serializers.ListField(label="部门列表", child=DepartmentBaseInfoSLZ(label="部门信息"))


class DepartmentSLZ(DepartmentBaseInfoSLZ):
    children = serializers.ListField(label="子部门列表", child=DepartmentBaseInfoSLZ(label="子部门信息"))
    members = serializers.ListField(label="用户列表", child=UserInfoSLZ(label="用户信息"))


class UserQuerySLZ(serializers.Serializer):
    usernames = serializers.ListField(label="用户名列表", child=serializers.CharField(label="用户名"))


class OrganizationSearchSLZ(serializers.Serializer):
    keyword = serializers.CharField(label="搜索关键词")
    is_exact = serializers.BooleanField(label="是否精确匹配", required=False, default=False)


class OrganizationSearchResultSLZ(serializers.Serializer):
    departments = serializers.ListField(label="部门列表", child=DepartmentBaseInfoSLZ(label="部门信息"))
    users = serializers.ListField(label="用户列表", child=UserInfoSLZ(label="用户信息"))


class OrganizationSyncTaskSLZ(serializers.Serializer):
    status = serializers.CharField(label="同步任务状态", help_text=f"{SyncTaskStatus.get_choices()}")
    executor = serializers.CharField(label="执行者")
    created_time = serializers.CharField(label="执行开始时间")
    updated_time = serializers.CharField(label="执行结束时间")


class OrganizationSyncRecordSLZ(serializers.Serializer):
    id = serializers.IntegerField(label="同步记录id")
    created_time = serializers.CharField(label="执行开始时间")
    cost_time = serializers.IntegerField(label="耗时", read_only=True)
    executor = serializers.CharField(label="执行者")
    trigger_type = serializers.CharField(label="触发类型")
    status = serializers.CharField(label="同步任务状态", help_text=f"{SyncTaskStatus.get_choices()}")


class OrganizationSyncErrorLogSLZ(serializers.Serializer):
    exception_msg = serializers.CharField(label="异常信息", default="")
    traceback_msg = serializers.CharField(label="日志详情", default="")


class UserDepartmentQuerySLZ(serializers.Serializer):
    username = serializers.CharField(label="用户名")


class UserDepartmentInfoSLZ(serializers.Serializer):
    id = serializers.CharField(label="ID")
    name = serializers.CharField(label="名称")
    full_name = serializers.CharField(label="全名")
