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

from rest_framework import serializers

from backend.api.constants import BKNonEntityUser
from backend.apps.role.models import Role
from backend.audit.detail import EventDetailExtra
from backend.audit.models import EventForMeta
from backend.biz.system import SystemBiz


class EventListSchemaSLZ(serializers.ModelSerializer):
    system = serializers.SerializerMethodField(label="系统信息")

    class Meta:
        model = EventForMeta
        fields = (
            "id",
            "source_type",
            "time",
            "type",
            "username",
            "system",
            "object_type",
            "object_id",
            "object_name",
            "status",
        )

    def get_system(self, obj):
        pass

    def get_username(self, obj):
        if obj.username == BKNonEntityUser.BK__UNVERIFIED_USER.value:
            return "UnverifiedUser"
        if obj.username == BKNonEntityUser.BK__ANONYMOUS_USER.value:
            return "AnonymousUser"
        return None


class EventListSLZ(EventListSchemaSLZ):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._systems = {s.id: s for s in SystemBiz().list()}

    def get_system(self, obj):
        system_id = obj.system_id
        system = self._systems.get(system_id, None)

        return {
            "id": system_id,
            "name": system.name if system else "",
            "name_en": system.name_en if system else "",
        }


class EventDetailSchemaSLZ(serializers.ModelSerializer):
    description = serializers.SerializerMethodField(label="描述")
    sub_objects = serializers.SerializerMethodField(label="子对象")
    extra_info = serializers.SerializerMethodField(label="额外信息")
    system = serializers.SerializerMethodField(label="系统信息")
    role_name = serializers.SerializerMethodField(label="角色名称")

    class Meta:
        model = EventForMeta
        fields = (
            "id",
            "source_type",
            "time",
            "type",
            "username",
            "role_type",
            "role_id",
            "role_name",
            "system",
            "object_type",
            "object_id",
            "object_name",
            "status",
            "description",
            "sub_objects",
            "extra_info",
        )

    def get_description(self, obj):
        pass

    def get_sub_objects(self, obj):
        pass

    def get_extra_info(self, obj):
        pass

    def get_system(self, obj):
        pass

    def get_role_name(self, obj):
        if not obj.role_id:
            return ""
        role = Role.objects.filter(id=obj.role_id).only("name").first()
        return role.name if role else ""

    def get_username(self, obj):
        if obj.username == BKNonEntityUser.BK__UNVERIFIED_USER.value:
            return "UnverifiedUser"
        if obj.username == BKNonEntityUser.BK__ANONYMOUS_USER.value:
            return "AnonymousUser"
        return None


class EventDetailSLZ(EventDetailSchemaSLZ):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._systems = {s.id: s for s in SystemBiz().list()}
        if self.instance:
            self._extra = EventDetailExtra(self.instance)

    def get_system(self, obj):
        system_id = obj.system_id
        system = self._systems.get(system_id, None)

        return {
            "id": system_id,
            "name": system.name if system else "",
            "name_en": system.name_en if system else "",
        }

    def get_description(self, obj):
        return self._extra.description

    def get_sub_objects(self, obj):
        return self._extra.sub_objects

    def get_extra_info(self, obj):
        return self._extra.extra_info


class EventQuerySLZ(serializers.Serializer):
    month = serializers.CharField(required=False)

    def validate_month(self, value):
        if value:
            try:
                time.strptime(value, "%Y%m")
            except Exception:  # pylint: disable=broad-except
                raise serializers.ValidationError("format error")

        return value
