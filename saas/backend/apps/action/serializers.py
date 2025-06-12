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

from backend.common.serializers import ActionQuerySLZ
from backend.service.constants import SelectionMode


class GroupActionQuerySLZ(ActionQuerySLZ):
    group_id = serializers.IntegerField(label="用户组id", required=False, default=-1)
    user_id = serializers.CharField(label="用户ID", required=False, default="")
    all = serializers.BooleanField(label="查询所有的操作", default=False)
    hidden = serializers.BooleanField(label="是否隐藏", default=False)


class InstanceSelectionQuerySLZ(serializers.Serializer):
    system_id = serializers.CharField(required=True)
    action_id = serializers.CharField(required=True)
    resource_type_system = serializers.CharField(required=True)
    resource_type_id = serializers.CharField(required=True)


class ResourceTypeNodeSLZ(serializers.Serializer):
    id = serializers.CharField()
    system_id = serializers.CharField()
    name = serializers.CharField()
    name_en = serializers.CharField()


class InstanceSelectionSLZ(serializers.Serializer):
    name = serializers.CharField()
    name_en = serializers.CharField()
    ignore_iam_path = serializers.BooleanField(label="是否忽略路径")
    resource_type_chain = serializers.ListField(label="资源类型链路", child=ResourceTypeNodeSLZ(label="节点"))


class RelatedResourceTypeSLZ(serializers.Serializer):
    system_id = serializers.CharField()
    id = serializers.CharField()
    name = serializers.CharField()
    name_en = serializers.CharField()
    selection_mode = serializers.ChoiceField(SelectionMode.get_choices(), label="资源选择模式")


class RelatedEnvironmentSLZ(serializers.Serializer):
    type = serializers.CharField()


class ActionSLZ(serializers.Serializer):
    id = serializers.CharField(label="操作ID")
    tag = serializers.CharField(label="标签")
    name = serializers.CharField()
    name_en = serializers.CharField()
    description = serializers.CharField()
    description_en = serializers.CharField()
    type = serializers.CharField(label="操作类型")
    version = serializers.IntegerField()
    related_resource_types = serializers.ListField(
        label="关联资源类型", child=RelatedResourceTypeSLZ(label="资源类型")
    )
    related_actions = serializers.ListField(child=serializers.CharField())
    related_environments = serializers.ListField(child=RelatedEnvironmentSLZ())


class SystemsSLZ(serializers.Serializer):
    system_ids = serializers.CharField(label="系统ID", help_text="多个id使用,分割")


class AggregateResourceTypeSLZ(serializers.Serializer):
    system_id = serializers.CharField(label="系统ID")
    id = serializers.CharField(label="资源类型ID")
    name = serializers.CharField(label="资源类型名称")


class ThinAggActionSLZ(serializers.Serializer):
    system_id = serializers.CharField(label="系统ID")
    id = serializers.CharField(label="操作ID")
    name = serializers.CharField(label="操作名称")


class AggregateActionSLZ(serializers.Serializer):
    actions = serializers.ListField(label="操作列表", child=ThinAggActionSLZ(label="操作"))
    aggregate_resource_types = serializers.ListField(child=AggregateResourceTypeSLZ(label="聚合资源类型"))


class AggregateActionsSLZ(serializers.Serializer):
    aggregation = serializers.ListField(label="聚合操作", child=AggregateActionSLZ(label="聚合操作"))


class ActionGroupQuerySLZ(serializers.Serializer):
    system_id = serializers.CharField(label="系统ID")


class SubActionGroupSLZ(serializers.Serializer):
    id = serializers.IntegerField(label="操作分组ID")
    name = serializers.CharField(label="操作分组名称")
    sub_groups = serializers.ListField(label="子操作分组", child=serializers.DictField())
