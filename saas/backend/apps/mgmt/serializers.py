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
from backend.biz.system import SystemBiz

from .constants import ApiType


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
    api = serializers.ChoiceField(label="超级管理类API", choices=AdminAPIEnum.get_choices())


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


class AuthorizationApiWhiteListSchemaSLZ(serializers.Serializer):
    id = serializers.IntegerField(label="白名单记录ID")
    api_info = serializers.DictField(label="API信息")
    system_info = serializers.DictField(label="系统信息")
    object_id = serializers.CharField(label="资源类型ID")


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


class ManagementApiWhiteListSchemaSLZ(serializers.Serializer):
    id = serializers.IntegerField(label="白名单记录ID")
    api_info = serializers.DictField(label="API信息")
    system_info = serializers.DictField(label="系统信息")


class ManagementApiAddWhiteListSLZ(serializers.Serializer):
    system_id = serializers.CharField(label="系统ID")
    api = serializers.ChoiceField(label="管理类API", choices=ManagementAPIEnum.get_choices())
