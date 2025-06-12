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

from backend.apps.model_builder.constants import (
    ActionTypeEnum,
    GenerateJsonTypeEnum,
    ModelSectionEnum,
    ModelSectionTypeList,
    SystemProviderAuthEnum,
)
from backend.apps.model_builder.models import MockSystemModel
from backend.service.constants import SelectionMode


class ModelSLZ(serializers.ModelSerializer):
    class Meta:
        model = MockSystemModel
        fields = ("id", "system_id", "owner", "updated_time", "created_time", "system")


class ModelIdSLZ(serializers.Serializer):
    id = serializers.IntegerField(label="模型ID")


class ModelUpdateSLZ(serializers.Serializer):
    type = serializers.ChoiceField(label="类型(type)", choices=ModelSectionEnum.get_choices())
    data = serializers.JSONField(label="数据(data)")


class RetrievePartSLZ(serializers.Serializer):
    type = serializers.ChoiceField(label="类型(type)", choices=ModelSectionEnum.get_choices(), required=False)


class DeletePartSLZ(serializers.Serializer):
    type = serializers.ChoiceField(label="类型(type)", choices=ModelSectionEnum.get_choices())
    id = serializers.CharField(label="ID(id)", required=False)

    def validate(self, data):
        if data["type"] in ModelSectionTypeList and not data.get("id"):
            raise serializers.ValidationError("id required")

        # id required=False if data["type"] in ("common_actions", "action_groups"):
        return data


class ResourceTypeListSLZ(serializers.Serializer):
    system_id = serializers.CharField(label="系统ID(system_id)", max_length=128, allow_blank=False)


class InstanceSelectionListSLZ(serializers.Serializer):
    system_id = serializers.CharField(label="系统ID(system_id)", max_length=128, allow_blank=False)


class GenerateJsonSLZ(serializers.Serializer):
    type = serializers.ChoiceField(label="类型(type)", choices=GenerateJsonTypeEnum.get_choices())


class ModelSystemIDExistsSLZ(serializers.Serializer):
    id = serializers.CharField(label="系统ID(id)", max_length=128)


class ModelDataIDExistsSLZ(serializers.Serializer):
    type = serializers.ChoiceField(label="类型(type)", choices=ModelSectionEnum.get_choices())
    id = serializers.CharField(label="ID(id)", max_length=128)


class ModelIDExistsResponseSLZ(serializers.Serializer):
    exists = serializers.BooleanField(label="Exists")


# ========= 系统 system
class SystemProviderConfigSLZ(serializers.Serializer):
    host = serializers.URLField(label="回调HOST(host)")
    auth = serializers.ChoiceField(label="鉴权方式(auth)", choices=SystemProviderAuthEnum.get_choices())

    healthz = serializers.CharField(label="健康检查地址(healthz)", required=False, default="/healthz")


class ModelSystemSLZ(serializers.Serializer):
    id = serializers.CharField(label="ID(id)", max_length=32)

    name = serializers.CharField(label="名称(name)", allow_blank=False)
    name_en = serializers.CharField(label="英文名称(name_en)", allow_blank=False)

    description = serializers.CharField(label="描述(description)", required=False)
    description_en = serializers.CharField(label="英文描述(description_en)", required=False)

    # required=False, 什么都不配置, 注册时会将发起注册的app_code加入
    clients = serializers.CharField(label="合法CLIENTS(clients)", required=False, default="")

    provider_config = SystemProviderConfigSLZ(label="回调配置(provider_config)")


# ========= 资源类型  resource type
class ResourceTypeProviderConfigSLZ(serializers.Serializer):
    path = serializers.CharField(label="PATH(path)")


class ResourceTypeSLZ(serializers.Serializer):
    id = serializers.CharField(label="ID(id)", max_length=32)
    name = serializers.CharField(label="名称(name)", allow_blank=False)
    name_en = serializers.CharField(label="英文名称(name_en)", allow_blank=False)

    description = serializers.CharField(label="描述(description)", required=False)
    description_en = serializers.CharField(label="英文描述(description_en)", required=False)

    # required=False, 前端是在不同页面配置做更新的
    provider_config = ResourceTypeProviderConfigSLZ(label="回调配置(provider_config)", required=False)

    version = serializers.IntegerField(label="版本(version)", default=1)


# ========= 实例视图 instance selection
class ReferenceResourceTypeSLZ(serializers.Serializer):
    system_id = serializers.CharField(label="系统ID(system_id)", max_length=32)
    id = serializers.CharField(label="ID(id)", max_length=32)


class InstanceSelectionSLZ(serializers.Serializer):
    id = serializers.CharField(label="ID(id)", max_length=32)
    name = serializers.CharField(label="名称(name)", allow_blank=False)
    name_en = serializers.CharField(label="英文名称(name_en)", allow_blank=False)
    is_dynamic = serializers.BooleanField(label="是否动态(is_dynamic)", default=False)
    resource_type_chain = serializers.ListField(
        label="资源类型链路(resource_type_chain)",
        child=ReferenceResourceTypeSLZ(label="资源类型(resource_type)"),
        required=True,
        allow_empty=False,
    )


# ========= 操作 action
class ReferenceInstanceSelectionSLZ(serializers.Serializer):
    system_id = serializers.CharField(label="系统ID(system_id)", max_length=32)
    id = serializers.CharField(label="ID(id)", max_length=32)
    ignore_iam_path = serializers.BooleanField(label="忽略路径(ignore_iam_path)", required=False, default=False)


class RelatedResourceTypeSLZ(serializers.Serializer):
    system_id = serializers.CharField(label="系统ID(system_id)", max_length=32)
    id = serializers.CharField(label="ID(id)", max_length=32)

    name_alias = serializers.CharField(label="别名(name_alias)", required=False, allow_blank=True)
    name_alias_en = serializers.CharField(label="英文别名(name_alias_en)", required=False, allow_blank=True)

    # required=True, 前端是必须填的(IAM Backend Model并没有要求必填)
    selection_mode = serializers.ChoiceField(
        label="实例选择方式(selection_mode)",
        choices=SelectionMode.get_choices(),
        default=SelectionMode.INSTANCE.value,
    )

    related_instance_selections = serializers.ListField(
        label="依赖实例视图(related_instance_selections)",
        child=ReferenceInstanceSelectionSLZ(label="实例视图(instance_selection)"),
        required=False,
        allow_empty=False,
    )


class ActionSLZ(serializers.Serializer):
    id = serializers.CharField(label="ID(id)", max_length=32)
    name = serializers.CharField(label="名称(name)", allow_blank=False)
    name_en = serializers.CharField(label="英文名称(name_en)", allow_blank=False)

    description = serializers.CharField(label="描述(description)", required=False)
    description_en = serializers.CharField(label="英文描述(description_en)", required=False)

    type = serializers.ChoiceField(label="类型(type)", choices=ActionTypeEnum.get_choices())

    related_resource_types = serializers.ListField(
        label="操作对象(related_resource_types)",
        child=RelatedResourceTypeSLZ(label="资源类型(resource_type)"),
        required=False,
        allow_empty=True,
    )

    related_actions = serializers.ListField(
        label="依赖操作(related_actions)",
        child=serializers.CharField(label="操作ID(action_id)"),
        required=False,
        allow_empty=True,
    )
    version = serializers.IntegerField(label="版本(version)", default=1)


class ActionIDSLZ(serializers.Serializer):
    id = serializers.CharField(label="操作ID(id)")


# ========= 操作分组 action groups
class ActionSubGroupSLZ(serializers.Serializer):
    name = serializers.CharField(label="名称(name)", allow_blank=False)
    name_en = serializers.CharField(label="英文名称(name_en)", allow_blank=False)
    actions = serializers.ListField(
        label="操作列表(actions)", child=ActionIDSLZ(label="操作(action)"), allow_empty=False
    )


class ActionGroupSLZ(serializers.Serializer):
    name = serializers.CharField(label="名称(name)", allow_blank=False)
    name_en = serializers.CharField(label="英文名称(name_en)", allow_blank=False)
    actions = serializers.ListField(
        label="操作列表(actions)", child=ActionIDSLZ(label="操作()"), required=False, allow_empty=True
    )
    sub_groups = serializers.ListField(
        label="二级操作组(sub_groups)",
        child=ActionSubGroupSLZ(label="二级分组(sub_group)"),
        required=False,
        allow_empty=True,
    )


# ========= 常用操作 common actions
class CommonActionSLZ(serializers.Serializer):
    name = serializers.CharField(label="名称(name)", allow_blank=False)
    name_en = serializers.CharField(label="英文名称(name_en)", allow_blank=False)
    actions = serializers.ListField(
        label="操作列表(actions)", child=ActionIDSLZ(label="操作(action)"), allow_empty=False
    )

    def validate_actions(self, value):
        # id uniq in one common_action
        s = set()
        for action in value:
            action_id = action["id"]
            if action_id in s:
                raise serializers.ValidationError(f"duplicate action_id={action_id} in actions")
            s.add(action_id)
        return value
