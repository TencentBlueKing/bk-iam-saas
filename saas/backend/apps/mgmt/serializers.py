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

from django.db.models import QuerySet
from rest_framework import serializers

from backend.api.admin.constants import AdminAPIEnum
from backend.api.authorization.constants import AuthorizationAPIEnum
from backend.api.management.constants import ManagementAPIEnum
from backend.biz.group import GroupBiz
from backend.biz.system import SystemBiz
from backend.biz.template import TemplateBiz
from backend.long_task.constants import TaskStatus, TaskType

from .constants import ApiType, LongTaskObjectType


class QueryApiSLZ(serializers.Serializer):
    api_type = serializers.ChoiceField(label="API类型", choices=ApiType.get_choices())


class ApiSLZ(serializers.Serializer):
    api = serializers.CharField(label="API")
    name = serializers.CharField(label="API名称")


class AdminApiWhiteListSLZ(serializers.Serializer):
    id = serializers.IntegerField(label="白名单记录ID")
    api_info = serializers.SerializerMethodField(label="API信息")
    app_code = serializers.CharField(label="应用TOKEN")

    def get_api_info(self, obj):
        api = obj.api

        return {"api": api, "name": AdminAPIEnum.get_choice_label(api)}


class AdminApiAddWhiteListSLZ(serializers.Serializer):
    app_code = serializers.CharField(label="应用TOKEN")
    api = serializers.CharField(label="超级管理类API")

    def validate_api(self, value):
        if value == "*" or value in dict(AdminAPIEnum.get_choices()):
            return value
        raise serializers.ValidationError(f"api: {value} 非法")


class AuthorizationApiWhiteListSLZ(serializers.Serializer):
    id = serializers.IntegerField(label="白名单记录ID")
    api_info = serializers.SerializerMethodField(label="API信息")
    system_info = serializers.SerializerMethodField(label="系统信息")
    object_id = serializers.CharField(label="资源类型ID")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._system_list = SystemBiz().new_system_list()

    def get_api_info(self, obj):
        api = obj.type
        return {"api": api, "name": AuthorizationAPIEnum.get_choice_label(api)}

    def get_system_info(self, obj):
        system_id = obj.system_id
        system = self._system_list.get(system_id)

        return {
            "id": system_id,
            "name": system.name if system else "",
            "name_en": system.name_en if system else "",
        }


class AuthorizationApiWhiteListSchemaSLZ(AuthorizationApiWhiteListSLZ):
    def __init__(self, *args, **kwargs):
        serializers.ModelSerializer.__init__(self, *args, **kwargs)


class AuthorizationApiAddWhiteListSLZ(serializers.Serializer):
    system_id = serializers.CharField(label="系统ID")
    api = serializers.ChoiceField(label="授权类API", choices=AuthorizationAPIEnum.get_choices())
    object_id = serializers.CharField(label="资源类型ID")


class ManagementApiWhiteListSLZ(serializers.Serializer):
    id = serializers.IntegerField(label="白名单记录ID")
    api_info = serializers.SerializerMethodField(label="API信息")
    system_info = serializers.SerializerMethodField(label="系统信息")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._system_list = SystemBiz().new_system_list()

    def get_api_info(self, obj):
        api = obj.api

        return {"api": api, "name": ManagementAPIEnum.get_choice_label(api)}

    def get_system_info(self, obj):
        system_id = obj.system_id
        system = self._system_list.get(system_id)

        return {
            "id": system_id,
            "name": system.name if system else "",
            "name_en": system.name_en if system else "",
        }


class ManagementApiWhiteListSchemaSLZ(ManagementApiWhiteListSLZ):
    def __init__(self, *args, **kwargs):
        serializers.ModelSerializer.__init__(self, *args, **kwargs)


class ManagementApiAddWhiteListSLZ(serializers.Serializer):
    system_id = serializers.CharField(label="系统ID")
    api = serializers.CharField(label="管理类API")

    def validate_api(self, value):
        if value == "*" or value in dict(ManagementAPIEnum.get_choices()):
            return value
        raise serializers.ValidationError(f"api: {value} 非法")


class LongTaskSLZ(serializers.Serializer):
    id = serializers.CharField(label="任务ID")
    type = serializers.CharField(label="任务类型")
    status = serializers.SerializerMethodField(label="任务状态")
    object = serializers.SerializerMethodField(label="任务相关参数")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        group_ids = []
        template_ids = []
        if isinstance(self.instance, (QuerySet, list)) and self.instance:
            for task_detail in self.instance:
                if task_detail.type == TaskType.GROUP_AUTHORIZATION.value:
                    group_ids.append(task_detail.args[0]["id"])

                if task_detail.type == TaskType.TEMPLATE_UPDATE.value:
                    template_ids.append(task_detail.args[0])

            self._template_name_dict = TemplateBiz().get_template_name_dict_by_ids(template_ids)
            self._group_name_dict = GroupBiz().get_group_name_dict_by_ids(group_ids)

    def get_status(self, obj):
        return TaskStatus.get_choice_label(obj.status)

    def get_object(self, obj):
        args = obj.args
        if obj.type == TaskType.GROUP_AUTHORIZATION.value:
            id = args[0]["id"]
            object = [
                {"type": LongTaskObjectType.GROUP.value, "id": id, "name": self._group_name_dict.get(int(id), "")}
            ]

        elif obj.type == TaskType.TEMPLATE_UPDATE.value:
            id = args[0]
            object = [
                {"type": LongTaskObjectType.TEMPLATE.value, "id": id, "name": self._template_name_dict.get(id, "")}
            ]

        return object


class SubTaskSLZ(serializers.Serializer):
    id = serializers.CharField(label="子任务ID")
    status = serializers.SerializerMethodField(label="状态")
    exception = serializers.CharField(label="异常信息")

    def get_status(self, obj):
        return TaskStatus.get_choice_label(obj.status)
