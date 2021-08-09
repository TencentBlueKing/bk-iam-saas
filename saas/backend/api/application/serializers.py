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
import logging
from typing import Any, MutableMapping, Union

from rest_framework import serializers
from rest_framework.serializers import empty

from backend.apps.policy.serializers import AttributeSLZ

logger = logging.getLogger(__name__)


class ASInstanceSLZ(serializers.Serializer):
    """
    接入系统申请的资源实例
    """

    system = serializers.CharField(label="系统ID", default="", allow_blank=True, required=False)
    type = serializers.CharField(label="资源类型")
    id = serializers.CharField(label="资源ID")


class ASResourceTypeSLZ(serializers.Serializer):
    """
    接入系统申请操作的资源类型
    """

    system = serializers.CharField(label="系统ID")
    type = serializers.CharField(label="资源类型")
    instances = serializers.ListField(
        label="资源拓扑",
        child=serializers.ListField(child=ASInstanceSLZ(label="资源实例"), allow_empty=False),
        allow_empty=True,
        default=list,
    )
    attributes = serializers.ListField(
        label="属性", default=list, required=False, child=AttributeSLZ(label="属性"), allow_empty=True
    )


class ASActionSLZ(serializers.Serializer):
    """
    接入系统申请操作
    """

    id = serializers.CharField(label="操作ID")
    related_resource_types = serializers.ListField(
        label="关联资源类型", child=ASResourceTypeSLZ(label="资源类型"), allow_empty=True, default=list
    )


class AccessSystemApplicationSLZ(serializers.Serializer):
    """
    接入系统申请
    """

    system = serializers.CharField(label="系统ID")
    actions = serializers.ListField(label="申请操作", child=ASActionSLZ(label="操作"), allow_empty=False)

    @staticmethod
    def _convert_system(data: MutableMapping[str, Any]):
        """兼容数据里system和system_id"""
        if "system" not in data and "system_id" in data:
            data["system"] = data["system_id"]

    def __init__(self, instance=None, data: Union[empty, MutableMapping] = empty, **kwargs):
        # 兼容用户传入system与system_id，之前老的协议是system_id，后面新协议都统一是system
        if data is not empty:
            try:
                self._convert_system(data)
                for action in data.get("actions", []):
                    for rrt in action.get("related_resource_types", []):
                        self._convert_system(rrt)
                        for rrt_instance in rrt.get("instances", []):
                            for node in rrt_instance:
                                self._convert_system(node)
            except Exception as error:  # pylint: disable=broad-except
                logger.info(f"when access system application data serialized, convert system data error: {error}")

        super().__init__(instance, data, **kwargs)

    def validate(self, data):
        action_ids = {action["id"] for action in data["actions"]}
        if len(data["actions"]) != len(action_ids):
            raise serializers.ValidationError("actions must not repeat")
        return data


class AccessSystemApplicationUrlSLZ(serializers.Serializer):
    url = serializers.URLField()
