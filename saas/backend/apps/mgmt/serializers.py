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

from backend.api.admin.constants import AdminAPIEnum
from backend.api.authorization.constants import AuthorizationAPIEnum
from backend.api.management.constants import ManagementAPIEnum
from backend.apps.group.models import Group
from backend.apps.template.models import PermTemplate
from backend.biz.system import SystemBiz
from backend.long_task.constants import TaskStatus, TaskType

from .constants import ApiType, ObjectType


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


class QueryLongTaskSLZ(serializers.Serializer):
    type = serializers.ChoiceField(label="长时任务类型", choices=TaskType.get_choices())


class LongTaskSLZ(serializers.Serializer):
    id = serializers.CharField(label="任务ID")
    type = serializers.CharField(label="任务类型")
    status = serializers.SerializerMethodField(label="任务状态")
    object = serializers.SerializerMethodField(label="任务相关参数")

    def get_status(self, obj):
        return TaskStatus.get_choice_label(obj.status)

    def get_object(self, obj):
        args = obj.args
        if obj.type == TaskType.GROUP_AUTHORIZATION.value:
            id = args[0]["id"]
            group = Group.objects.filter(id=id).first()
            object = [
                {
                    "type": ObjectType.GROUP.value,
                    "id": id,
                    "name": group.name if group else ""
                }
            ]

        elif obj.type == TaskType.TEMPLATE_UPDATE.value:
            id = args[0]
            template = PermTemplate.objects.filter(id=id).first()
            object = [
                {
                    "type": ObjectType.TEMPLATE.value,
                    "id": id,
                    "name": template.name if template else ""
                }
            ]

        return object


class SubTaskSLZ(serializers.Serializer):
    id = serializers.CharField(label="子任务ID")
    status = serializers.SerializerMethodField(label="状态")
    exception = serializers.CharField(label="异常信息")

    def get_status(self, obj):
        return TaskStatus.get_choice_label(obj.status)
