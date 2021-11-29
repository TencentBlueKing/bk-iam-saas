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
from django.conf import settings
from rest_framework import serializers

from backend.common.serializers import BaseAction
from backend.common.time import PERMANENT_SECONDS
from backend.util.uuid import gen_uuid


class ValueFiled(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        if not isinstance(data, (bool, int, float, str)):
            raise serializers.ValidationError("value only support (bool, int, float, str)")
        return data


class ResourceSLZ(serializers.Serializer):
    system_id = serializers.CharField(label="系统ID", required=True)
    type = serializers.CharField(label="资源类型", required=True)
    type_name = serializers.CharField(label="资源类型名称", required=True, allow_blank=True)
    id = serializers.CharField(label="资源实例ID", required=True)
    name = serializers.CharField(label="资源实例ID名称", required=True, allow_blank=True, trim_whitespace=False)


class InstanceSLZ(serializers.Serializer):
    type = serializers.CharField(label="资源类型", required=True)
    name = serializers.CharField(label="资源类型名称", required=True, allow_blank=True)
    path = serializers.ListField(
        label="层级链路",
        child=serializers.ListField(label="链路", child=ResourceSLZ(label="节点"), allow_empty=False),
        required=True,
        allow_empty=False,
    )


class ValueSLZ(serializers.Serializer):
    id = ValueFiled(label="属性VALUE", required=True)
    name = serializers.CharField(label="属性VALUE名称", required=True, allow_blank=True)


class AttributeSLZ(serializers.Serializer):
    id = serializers.CharField(label="属性KEY", required=True)
    name = serializers.CharField(label="属性KEY名称", required=True, allow_blank=True)
    values = serializers.ListField(label="属性VALUE", child=ValueSLZ(label="值"), required=True, allow_empty=False)


class ConditionSLZ(serializers.Serializer):
    id = serializers.CharField(label="条件id", allow_blank=True)
    instances = serializers.ListField(label="拓扑选择", required=True, child=InstanceSLZ(label="拓扑实例"))
    attributes = serializers.ListField(label="属性选择", required=True, child=AttributeSLZ(label="属性"))

    def validate(self, data):
        if not data["instances"] and not data["attributes"]:
            raise serializers.ValidationError({"instances": ["instance and attribute must not be both empty"]})

        if not data["id"]:
            data["id"] = gen_uuid()

        return data


class ResourceTypeSLZ(serializers.Serializer):
    system_id = serializers.CharField(label="资源类型系统ID", required=True)
    type = serializers.CharField(label="资源类型", required=True)
    condition = serializers.ListField(label="生效条件", child=ConditionSLZ(label="条件"), required=True)

    def validate(self, data):
        """
        检查条件的实例数量不超过1万
        """
        count = 0
        for c in data["condition"]:
            for i in c["instances"]:
                if i["type"] == data["type"]:
                    count += len(i["path"])

        if count > settings.SINGLE_POLICY_MAX_INSTANCES_LIMIT:
            raise serializers.ValidationError(
                {"condition": ["实例数量超过限制 {} 个".format(settings.SINGLE_POLICY_MAX_INSTANCES_LIMIT)]}
            )

        return data


class ResourceGroupSLZ(serializers.Serializer):
    id = serializers.CharField(label="ID", allow_blank=True)
    related_resource_types = serializers.ListField(label="资源类型条件", child=ResourceTypeSLZ(label="资源类型"), required=True)

    def validate(self, data):
        """
        自动填充resource_group_id
        """
        if not isinstance(data["id"], str) or not data["id"]:
            data["id"] = gen_uuid()

        return data


class PolicySLZ(serializers.Serializer):
    type = serializers.CharField(label="操作类型")
    id = serializers.CharField(label="操作ID")
    tag = serializers.CharField(label="标签")
    policy_id = serializers.IntegerField(label="策略ID")
    name = serializers.CharField(label="操作名称", allow_blank=True)
    description = serializers.CharField(label="操作描述")
    expired_at = serializers.IntegerField(label="过期时间", max_value=PERMANENT_SECONDS)
    expired_display = serializers.CharField()
    resource_groups = serializers.ListField(label="资源条件组", child=ResourceGroupSLZ(label="资源条件组"), required=True)


class PolicySystemSLZ(serializers.Serializer):
    id = serializers.CharField(label="系统ID")
    name = serializers.CharField(label="系统名称")
    count = serializers.IntegerField(label="权限数量")


class PolicyDeleteSLZ(serializers.Serializer):
    system_id = serializers.CharField(label="系统ID")
    ids = serializers.CharField(label="策略ID，多个以英文逗号分隔")

    def validate(self, data):
        # 验证 ID的合法性，并转化为后续view需要数据格式
        ids = data.get("ids") or ""
        if ids:
            try:
                data["ids"] = list(map(int, ids.split(",")))
            except Exception:  # pylint: disable=broad-except
                raise serializers.ValidationError({"ids": [f"策略IDS({ids})非法，策略ID只能是数字"]})
        return data


class ConditionDeleteSLZ(serializers.Serializer):
    id = serializers.CharField(label="条件id")
    instances = serializers.ListField(label="拓扑选择", required=True, child=InstanceSLZ(label="拓扑实例"))


class PolicyPartDeleteSLZ(serializers.Serializer):
    system_id = serializers.CharField(label="资源类型系统ID", required=True)
    resource_group_id = serializers.CharField(label="资源条件组ID", required=True)
    type = serializers.CharField(label="资源类型", required=True)
    ids = serializers.ListField(
        label="整体删除的条件ID", child=serializers.CharField(label="ConditionID"), required=True, allow_empty=True
    )
    condition = serializers.ListField(
        label="部分删除条件", child=ConditionDeleteSLZ(label="条件"), required=True, allow_empty=True
    )

    def validate(self, data):
        if not data["ids"] and not data["condition"]:
            raise serializers.ValidationError({"condition": ["删除条件不能全为空"]})
        return data


class IDNameSLZ(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()


class PolicyExpireSoonSLZ(serializers.Serializer):
    id = serializers.IntegerField(label="ID")
    system = IDNameSLZ(label="系统信息")
    action = IDNameSLZ(label="操作信息")
    expired_at = serializers.IntegerField(label="过期时间", max_value=PERMANENT_SECONDS)
    expired_display = serializers.CharField()


class BasePolicyActionSLZ(serializers.Serializer):
    id = serializers.CharField(label="操作ID", required=True)
    type = serializers.CharField(label="操作类型", required=True, allow_blank=True)
    resource_groups = serializers.ListField(label="资源条件组", child=ResourceGroupSLZ(label="资源条件组"), required=True)


class PolicyActionSLZ(BasePolicyActionSLZ):
    policy_id = serializers.IntegerField(label="策略id", required=False)
    expired_at = serializers.IntegerField(label="过期时间", required=True, max_value=PERMANENT_SECONDS)


class PolicyActionExpiredAtSLZ(BasePolicyActionSLZ):
    expired_at = serializers.IntegerField(label="过期时间", required=False, default=0, max_value=PERMANENT_SECONDS)


class RelatedPolicySLZ(serializers.Serializer):
    system_id = serializers.CharField(label="系统ID", required=True)
    source_policy = PolicyActionExpiredAtSLZ(label="来源策略")
    target_policies = serializers.ListField(
        label="操作策略", child=PolicyActionExpiredAtSLZ(label="策略"), required=False, default=list
    )


class PolicyResourceCopySLZ(serializers.Serializer):
    resource_type = ResourceTypeSLZ(label="资源")
    actions = serializers.ListField(label="目标操作", child=BaseAction(label="操作"), required=True, allow_empty=True)
