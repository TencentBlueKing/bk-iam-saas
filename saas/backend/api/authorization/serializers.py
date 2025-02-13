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

from django.conf import settings
from django.utils.translation import gettext as _
from rest_framework import serializers

from backend.apps.policy.serializers import ValueFiled
from backend.common.time import PERMANENT_SECONDS
from backend.service.constants import ANY_ID, SubjectType

from .constants import OperateEnum

REVOKE_INSTANCE_LIMIT = 1000


class AuthSystemSLZ(serializers.Serializer):
    """授权的系统"""

    system = serializers.CharField(label="系统ID")


class SubjectSLZ(serializers.Serializer):
    type = serializers.ChoiceField(
        label="类型",
        # 允许授权的Subject类型
        choices=[(SubjectType.USER.value, "用户"), (SubjectType.GROUP.value, "用户组")],
    )
    id = serializers.CharField(label="id")


class ResourceInstanceSLZ(serializers.Serializer):
    system = serializers.CharField(label="系统ID")
    type = serializers.CharField(label="资源类型")
    id = serializers.CharField(label="资源ID", max_length=settings.MAX_LENGTH_OF_RESOURCE_ID)
    name = serializers.CharField(label="资源名称", trim_whitespace=False)


class PathNodeSLZ(serializers.Serializer):
    system = serializers.CharField(label="系统ID", default="", allow_blank=True, required=False)
    type = serializers.CharField(label="资源类型")
    id = serializers.CharField(label="资源实例ID", max_length=settings.MAX_LENGTH_OF_RESOURCE_ID)
    name = serializers.CharField(label="资源实例ID名称", allow_blank=True, trim_whitespace=False)

    def validate(self, attrs):
        """
        路径授权时，只有ID为任意，Name才可以为空字符串
        """
        _id = attrs["id"]
        if _id == ANY_ID:
            attrs["name"] = _("无限制")
            return attrs

        # 非任意ID则Name必填
        if attrs["name"] == "":
            raise serializers.ValidationError(f"name is required when id({_id}) is not `*`")

        return attrs


class ResourcePathSLZ(serializers.Serializer):
    system = serializers.CharField(label="系统ID")
    type = serializers.CharField(label="资源类型")
    path = serializers.ListField(label="拓扑层级", child=PathNodeSLZ(label="实例"), allow_empty=False)


class AuthActionIDSLZ(serializers.Serializer):
    id = serializers.CharField(label="操作ID")


class AuthActionSLZ(serializers.Serializer):
    action = AuthActionIDSLZ(label="操作")


class AuthActionsSLZ(serializers.Serializer):
    actions = serializers.ListField(label="操作列表", child=AuthActionIDSLZ(label="操作"), allow_empty=False)


class BaseAuthSLZ(AuthSystemSLZ):
    asynchronous = serializers.BooleanField(label="是否同步调用", default=False)  # noqa
    operate = serializers.ChoiceField(label="授权/回收", choices=OperateEnum.get_choices())
    subject = SubjectSLZ(label="授权对象")
    expired_at = serializers.IntegerField(
        label="过期时间", required=False, default=0, min_value=0, max_value=PERMANENT_SECONDS
    )

    def validate_expired_at(self, value):
        """
        验证过期时间
        """
        if 0 < value <= (time.time()):
            raise serializers.ValidationError("greater than now timestamp")
        return value


class AuthInstanceSLZ(BaseAuthSLZ, AuthActionSLZ):
    resources = serializers.ListField(label="资源实例", child=ResourceInstanceSLZ(label="实例"), allow_empty=True)


class AuthPathSLZ(BaseAuthSLZ, AuthActionSLZ):
    # 如果action是与资源实例无关的，那么resources允许为空列表，但是字段还是要有，保持格式一致
    resources = serializers.ListField(label="资源拓扑", child=ResourcePathSLZ(label="拓扑"), allow_empty=True)


class SimpleInstanceSLZ(serializers.Serializer):
    id = serializers.CharField(label="资源ID", max_length=settings.MAX_LENGTH_OF_RESOURCE_ID)
    name = serializers.CharField(label="资源名称", trim_whitespace=False)


class BatchResourceInstanceSLZ(serializers.Serializer):
    system = serializers.CharField(label="系统ID")
    type = serializers.CharField(label="资源类型")
    instances = serializers.ListField(label="资源实例", child=SimpleInstanceSLZ(label="实例"), allow_empty=True)


class AuthBatchInstanceSLZ(BaseAuthSLZ, AuthActionsSLZ):
    resources = serializers.ListField(label="资源实例", child=BatchResourceInstanceSLZ(label="批量实例"), allow_empty=True)

    def validate(self, data):
        operate = data["operate"]
        if operate == OperateEnum.GRANT.value:
            for resource in data["resources"]:
                if len(resource["instances"]) > settings.AUTHORIZATION_INSTANCE_LIMIT:
                    raise serializers.ValidationError(
                        f"maximum number of instance grant {settings.AUTHORIZATION_INSTANCE_LIMIT}"
                    )
        if operate == OperateEnum.REVOKE.value:
            for resource in data["resources"]:
                if len(resource["instances"]) > REVOKE_INSTANCE_LIMIT:
                    raise serializers.ValidationError(f"maximum number of instance revoke {REVOKE_INSTANCE_LIMIT}")
        return data


class BatchResourcePathSLZ(serializers.Serializer):
    system = serializers.CharField(label="系统ID")
    type = serializers.CharField(label="资源类型")
    paths = serializers.ListField(
        label="批量层级",
        child=serializers.ListField(label="拓扑层级", child=PathNodeSLZ(label="实例"), allow_empty=False),
        allow_empty=True,
    )


class AuthBatchPathSLZ(BaseAuthSLZ, AuthActionsSLZ):
    # 如果action是与资源实例无关的，那么resources允许为空列表，但是字段还是要有，保持格式一致
    resources = serializers.ListField(label="资源拓扑", child=BatchResourcePathSLZ(label="匹配资源拓扑"), allow_empty=True)

    def validate(self, data):
        operate = data["operate"]
        if operate == OperateEnum.GRANT.value:
            for resource in data["resources"]:
                if len(resource["paths"]) > settings.AUTHORIZATION_INSTANCE_LIMIT:
                    raise serializers.ValidationError(
                        f"maximum number of path grant {settings.AUTHORIZATION_INSTANCE_LIMIT}"
                    )
        if operate == OperateEnum.REVOKE.value:
            for resource in data["resources"]:
                if len(resource["paths"]) > REVOKE_INSTANCE_LIMIT:
                    raise serializers.ValidationError(f"maximum number of path revoke {REVOKE_INSTANCE_LIMIT}")
        return data


class AuthResourceTypeSLZ(serializers.Serializer):
    type = serializers.CharField(label="资源类型")


class ResourceCreatorActionBaseInfoSLZ(AuthSystemSLZ, AuthResourceTypeSLZ):
    creator = serializers.CharField(label="创建者")


class AncestorSLZ(serializers.Serializer):
    system = serializers.CharField(label="祖先资源的系统ID")
    type = serializers.CharField(label="祖先资源类型")
    id = serializers.CharField(label="祖先资源ID", max_length=settings.MAX_LENGTH_OF_RESOURCE_ID)


class SingleInstanceSLZ(serializers.Serializer):
    id = serializers.CharField(label="资源ID", max_length=settings.MAX_LENGTH_OF_RESOURCE_ID)
    name = serializers.CharField(label="资源名称", trim_whitespace=False)
    ancestors = serializers.ListField(label="祖先", child=AncestorSLZ(label="祖先层级"), allow_empty=True, required=False)


class ResourceCreatorActionSLZ(ResourceCreatorActionBaseInfoSLZ, SingleInstanceSLZ):
    pass


class BatchResourceCreatorActionSLZ(ResourceCreatorActionBaseInfoSLZ):
    instances = serializers.ListField(
        label="批量资源实例",
        child=SingleInstanceSLZ(label="资源实例"),
        allow_empty=False,
        max_length=settings.AUTHORIZATION_INSTANCE_LIMIT,
    )


class SingleAttributeValueSLZ(serializers.Serializer):
    id = ValueFiled(label="属性VALUE")
    name = serializers.CharField(label="属性VALUE名称")


class SingleAttributeSLZ(serializers.Serializer):
    id = serializers.CharField(label="属性KEY")
    name = serializers.CharField(label="属性KEY名称")
    values = serializers.ListField(label="属性VALUE", child=SingleAttributeValueSLZ(label="值"))


class ResourceCreatorActionAttributeSLZ(ResourceCreatorActionBaseInfoSLZ):
    attributes = serializers.ListField(
        label="属性", default=list, child=SingleAttributeSLZ(label="属性"), allow_empty=True
    )


class ResourceCreatorOneActionAttributeSLZ(ResourceCreatorActionAttributeSLZ):
    action_id = serializers.CharField(label="操作id")
