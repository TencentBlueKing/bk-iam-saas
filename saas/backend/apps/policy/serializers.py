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
import sys

import pytz
from django.conf import settings
from rest_framework import serializers

from backend.apps.action.serializers import ActionSLZ
from backend.common.serializers import BaseAction
from backend.common.time import PERMANENT_SECONDS
from backend.service.constants import PolicyEnvConditionType, PolicyEnvType
from backend.util.uuid import gen_uuid


class ValueFiled(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        if not isinstance(data, (bool, int, str)):
            raise serializers.ValidationError("value only support (bool, int, float, str)")

        if isinstance(data, int) and (data > sys.maxsize or data < -sys.maxsize - 1):
            raise serializers.ValidationError(f"int value must be in range [{-sys.maxsize - 1}:{sys.maxsize}]")
        return data


class ResourceSLZ(serializers.Serializer):
    system_id = serializers.CharField(label="系统ID")
    type = serializers.CharField(label="资源类型")
    type_name = serializers.CharField(label="资源类型名称", allow_blank=True)
    id = serializers.CharField(label="资源实例ID", max_length=settings.MAX_LENGTH_OF_RESOURCE_ID)
    name = serializers.CharField(label="资源实例ID名称", allow_blank=True, trim_whitespace=False)


class InstanceSLZ(serializers.Serializer):
    type = serializers.CharField(label="资源类型")
    name = serializers.CharField(label="资源类型名称", allow_blank=True)
    path = serializers.ListField(
        label="层级链路",
        child=serializers.ListField(label="链路", child=ResourceSLZ(label="节点"), allow_empty=False),
        required=True,
        allow_empty=False,
    )


class ValueSLZ(serializers.Serializer):
    id = ValueFiled(label="属性VALUE")
    name = serializers.CharField(label="属性VALUE名称", allow_blank=True)


class AttributeSLZ(serializers.Serializer):
    id = serializers.CharField(label="属性KEY")
    name = serializers.CharField(label="属性KEY名称", allow_blank=True)
    values = serializers.ListField(label="属性VALUE", child=ValueSLZ(label="值"), allow_empty=False)


class ConditionSLZ(serializers.Serializer):
    id = serializers.CharField(label="条件id", allow_blank=True)
    instances = serializers.ListField(label="拓扑选择", child=InstanceSLZ(label="拓扑实例"))
    attributes = serializers.ListField(label="属性选择", child=AttributeSLZ(label="属性"))

    def validate(self, data):
        if not data["instances"] and not data["attributes"]:
            raise serializers.ValidationError({"instances": ["instance and attribute must not be both empty"]})

        if not data["id"]:
            data["id"] = gen_uuid()

        return data


class ResourceTypeSLZ(serializers.Serializer):
    system_id = serializers.CharField(label="资源类型系统ID")
    type = serializers.CharField(label="资源类型")
    condition = serializers.ListField(label="生效条件", child=ConditionSLZ(label="条件"))

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


class EnvConditionValueSLZ(serializers.Serializer):
    name = serializers.CharField(label="显示名称", required=False, allow_blank=True, default="")
    value = ValueFiled(label="环境属性值")


# for validate
class WeekdayEnvValueSLZ(EnvConditionValueSLZ):
    value = serializers.IntegerField(label="环境属性值", max_value=6, min_value=0)


# for validate
class HMSEnvValueSLZ(EnvConditionValueSLZ):
    value = serializers.RegexField(label="环境属性值", regex=r"^([0-1][0-9]|(2[0-3])):([0-5][0-9]):([0-5][0-9])$")


# for validate
class TZEnvValueSLZ(EnvConditionValueSLZ):
    value = serializers.CharField(label="环境属性值")

    def validate(self, attrs):
        value = attrs["value"]
        if value not in pytz.all_timezones:
            serializers.ValidationError({"value": ["{} is not a legal time zone representation".format(value)]})

        return attrs


class EnvConditionSLZ(serializers.Serializer):
    type = serializers.ChoiceField(label="环境属性条件类型", choices=PolicyEnvConditionType.get_choices())
    values = serializers.ListField(label="条件的值", child=EnvConditionValueSLZ(label="VALUE"))


# for validate
class WeekdayEnvConditionSLZ(EnvConditionSLZ):
    values = serializers.ListField(
        label="条件的值", child=WeekdayEnvValueSLZ(label="VALUE"), allow_empty=False, min_length=1, max_length=7
    )

    def validate(self, attrs):
        if len(attrs["values"]) != len({v["value"] for v in attrs["values"]}):
            raise serializers.ValidationError({"values": ["must not repeat"]})
        return attrs


# for validate
class HMSEnvConditionSLZ(EnvConditionSLZ):
    values = serializers.ListField(
        label="条件的值", child=HMSEnvValueSLZ(label="VALUE"), allow_empty=False, min_length=2, max_length=2
    )

    def validate(self, attrs):
        # 比较第一个时间要小于第二个时间, 格式正确的情况下, 直接使用字符串比较是可以
        if attrs["values"][0]["value"] >= attrs["values"][1]["value"]:
            raise serializers.ValidationError({"values": ["first hms must be smaller than the second"]})
        return attrs


# for validate
class TZEnvConditionSLZ(EnvConditionSLZ):
    values = serializers.ListField(
        label="条件的值", child=TZEnvValueSLZ(label="VALUE"), allow_empty=False, min_length=1, max_length=1
    )


class EnvironmentSLZ(serializers.Serializer):
    type = serializers.ChoiceField(label="环境属性类型", choices=PolicyEnvType.get_choices())
    condition = serializers.ListField(label="生效条件", child=EnvConditionSLZ(label="条件"))


ENV_COND_TYPE_SLZ_MAP = {
    PolicyEnvConditionType.TZ.value: TZEnvConditionSLZ,
    PolicyEnvConditionType.HMS.value: HMSEnvConditionSLZ,
    PolicyEnvConditionType.WEEKDAY.value: WeekdayEnvConditionSLZ,
}


# for validate
class PeriodDailyEnvironmentSLZ(EnvironmentSLZ):
    condition = serializers.ListField(label="生效条件", child=EnvConditionSLZ(label="条件"), min_length=2, max_length=3)

    def validate(self, data):
        condition_type_set = {c["type"] for c in data["condition"]}
        # type不能重复
        if len(data["condition"]) != len(condition_type_set):
            raise serializers.ValidationError({"condition": ["type must not repeat"]})

        # TZ与HMS必填, WeekDay选填
        if not (
            PolicyEnvConditionType.TZ.value in condition_type_set
            and PolicyEnvConditionType.HMS.value in condition_type_set
        ):
            raise serializers.ValidationError({"condition": ["tz and hms must be exists"]})

        for c in data["condition"]:
            if c["type"] not in ENV_COND_TYPE_SLZ_MAP:
                raise serializers.ValidationError({"condition": ["type: {} not exists".format(c["type"])]})

            slz = ENV_COND_TYPE_SLZ_MAP[c["type"]](data=c)
            slz.is_valid(raise_exception=True)
        return data


ENV_TYPE_SLZ_MAP = {PolicyEnvType.PERIOD_DAILY.value: PeriodDailyEnvironmentSLZ}


class ResourceGroupSLZ(serializers.Serializer):
    id = serializers.CharField(label="ID", allow_blank=True)
    related_resource_types = serializers.ListField(label="资源类型条件", child=ResourceTypeSLZ(label="资源类型"))
    environments = serializers.ListField(
        label="环境属性条件", child=EnvironmentSLZ(label="环境属性条件"), allow_empty=True, required=False, default=list
    )

    def validate(self, data):
        """
        自动填充resource_group_id
        """
        if not isinstance(data["id"], str) or not data["id"]:
            data["id"] = gen_uuid()

        # validate environment
        for e in data["environments"]:
            if e["type"] not in ENV_TYPE_SLZ_MAP:
                raise serializers.ValidationError({"environments": ["type: {} not exists".format(e["type"])]})

            slz = ENV_TYPE_SLZ_MAP[e["type"]](data=e)
            slz.is_valid(raise_exception=True)
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
    resource_groups = serializers.ListField(label="资源条件组", child=ResourceGroupSLZ(label="资源条件组"))

    def validate(self, data):
        # 校验一个policy中不能存在多个不同的时区环境属性
        tz_set = set()
        for rg in data["resource_groups"]:
            for env in rg["environments"]:
                if env["type"] != PolicyEnvType.PERIOD_DAILY.value:
                    continue

                for c in env["condition"]:
                    if c["type"] != PolicyEnvConditionType.TZ.value:
                        continue

                    tz_set.add(c["values"][0]["value"])

        if len(tz_set) > 1:
            raise serializers.ValidationError(
                {"resource_groups": {"environments": ["all time zones must be consistent"]}}
            )

        return data


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
    instances = serializers.ListField(label="拓扑选择", child=InstanceSLZ(label="拓扑实例"))


class PolicyPartDeleteSLZ(serializers.Serializer):
    system_id = serializers.CharField(label="资源类型系统ID")
    resource_group_id = serializers.CharField(label="资源条件组ID")
    type = serializers.CharField(label="资源类型")
    ids = serializers.ListField(label="整体删除的条件ID", child=serializers.CharField(label="ConditionID"), allow_empty=True)
    condition = serializers.ListField(label="部分删除条件", child=ConditionDeleteSLZ(label="条件"), allow_empty=True)

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
    id = serializers.CharField(label="操作ID")
    type = serializers.CharField(label="操作类型", allow_blank=True)
    resource_groups = serializers.ListField(label="资源条件组", child=ResourceGroupSLZ(label="资源条件组"))


class PolicyActionSLZ(BasePolicyActionSLZ):
    policy_id = serializers.IntegerField(label="策略id", required=False)
    expired_at = serializers.IntegerField(label="过期时间", max_value=PERMANENT_SECONDS)


class PolicyActionExpiredAtSLZ(BasePolicyActionSLZ):
    expired_at = serializers.IntegerField(label="过期时间", required=False, default=0, max_value=PERMANENT_SECONDS)


class RelatedPolicySLZ(serializers.Serializer):
    system_id = serializers.CharField(label="系统ID")
    source_policy = PolicyActionExpiredAtSLZ(label="来源策略")
    target_policies = serializers.ListField(
        label="操作策略", child=PolicyActionExpiredAtSLZ(label="策略"), required=False, default=list
    )
    is_custom_policy_apply = serializers.BooleanField(label="是否自定义权限申请", required=False, default=False)


class PolicyResourceCopySLZ(serializers.Serializer):
    resource_type = ResourceTypeSLZ(label="资源")
    actions = serializers.ListField(label="目标操作", child=BaseAction(label="操作"), allow_empty=True)


class RecommendActionPolicy(serializers.Serializer):
    actions = serializers.ListField(label="推荐操作", child=ActionSLZ(label="操作"))
    policies = serializers.ListField(label="推荐策略", child=PolicySLZ(label="策略"))
