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
import time
from typing import Any, MutableMapping, Union

from django.conf import settings
from rest_framework import serializers
from rest_framework.serializers import empty

from backend.apps.policy.serializers import AttributeSLZ
from backend.common.time import PERMANENT_SECONDS

logger = logging.getLogger("app")


class ASInstanceSLZ(serializers.Serializer):
    """
    接入系统申请的资源实例
    """

    system = serializers.CharField(label="系统ID", default="", allow_blank=True, required=False)
    type = serializers.CharField(label="资源类型")
    id = serializers.CharField(label="资源ID", max_length=settings.MAX_LENGTH_OF_RESOURCE_ID)


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
                    for rrt in action.get("related_resource_types", None) or []:
                        self._convert_system(rrt)
                        for rrt_instance in rrt.get("instances", []):
                            for node in rrt_instance:
                                self._convert_system(node)
            except Exception:  # pylint: disable=broad-except
                logger.exception(f"convert access system's application serialized data fail! data={data}")

        super().__init__(instance, data, **kwargs)

    def validate(self, data):
        action_ids = {action["id"] for action in data["actions"]}
        if len(data["actions"]) != len(action_ids):
            raise serializers.ValidationError("actions must not repeat")
        return data


class AccessSystemApplicationUrlSLZ(serializers.Serializer):
    url = serializers.URLField()


class AccessSystemApplicationCustomPolicySLZ(AccessSystemApplicationSLZ):
    """接入系统创建自定义申请单"""

    applicant = serializers.CharField(label="申请者的用户名", max_length=32)
    reason = serializers.CharField(label="申请理由", max_length=255)
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


class AccessSystemApplicationCustomPolicyResultSLZ(serializers.Serializer):
    id = serializers.CharField(label="申请单据ID")
    sn = serializers.CharField(label="ITSM审批单SN")


class ApprovalBotUserCallbackSLZ(serializers.Serializer):
    username = serializers.CharField(label="用户名")
    expired_at_before = serializers.IntegerField(label="过期时间")
    expired_at_after = serializers.IntegerField(label="过期时间")
    month = serializers.IntegerField(label="续期月数")


class ApprovalBotRoleCallbackSLZ(serializers.Serializer):
    role_id = serializers.IntegerField(label="角色ID")
    expired_at_before = serializers.IntegerField(label="过期时间")
    expired_at_after = serializers.IntegerField(label="过期时间")
    month = serializers.IntegerField(label="续期月数")


class ASResourceTypeWithCustomTicketSLZ(serializers.Serializer):
    """
    接入系统申请操作的资源类型
    """

    system = serializers.CharField(label="系统ID")
    type = serializers.CharField(label="资源类型")
    instance = serializers.ListField(
        label="资源拓扑", child=ASInstanceSLZ(label="资源实例"), required=False, allow_empty=True, default=list
    )
    attributes = serializers.ListField(
        label="属性", default=list, required=False, child=AttributeSLZ(label="属性"), allow_empty=True
    )


class ASActionWithCustomTicketSLZ(serializers.Serializer):
    id = serializers.CharField(label="操作ID")
    related_resource_types = serializers.ListField(
        label="关联资源类型", child=ASResourceTypeWithCustomTicketSLZ(label="资源类型"), allow_empty=True, default=list
    )

    ticket_content = serializers.DictField(label="单条权限的审批单内容", required=False, allow_empty=True, default=dict)


class ASApplicationCustomPolicyWithCustomTicketSLZ(serializers.Serializer):
    """接入系统自定义权限申请单据创建"""

    applicant = serializers.CharField(label="申请者的用户名", max_length=32)
    reason = serializers.CharField(label="申请理由", max_length=255)
    expired_at = serializers.IntegerField(
        label="过期时间", required=False, default=0, min_value=0, max_value=PERMANENT_SECONDS
    )

    ticket_title_prefix = serializers.CharField(label="审批单标题前缀", required=False, allow_blank=True, default="")
    ticket_content_template = serializers.DictField(label="审批单内容模板", required=False, allow_empty=True, default=dict)

    system = serializers.CharField(label="系统ID")
    actions = serializers.ListField(label="申请操作", child=ASActionWithCustomTicketSLZ(label="操作"), allow_empty=False)

    def validate_expired_at(self, value):
        """
        验证过期时间
        """
        if 0 < value <= (time.time()):
            raise serializers.ValidationError("greater than now timestamp")
        return value

    def validate(self, data):
        # 自定义 ITSM 单据展示内容
        content_template = data["ticket_content_template"]
        if content_template:
            # 必须满足 ITSM 的单据数据结构
            if "schemes" not in content_template or "form_data" not in content_template:
                raise serializers.ValidationError(
                    {"ticket_content_template": ["ticket_content_template 中必须包含 schemes 和 form_data "]}
                )

            if not isinstance(content_template["form_data"], list) or len(content_template["form_data"]) == 0:
                raise serializers.ValidationError(
                    {"ticket_content_template": ["ticket_content_template 中必须包含 form_data，且 form_data 必须为非空数组"]}
                )

            # IAM 所需的策略 Form （索引）
            policy_forms = [
                i
                for i in content_template["form_data"]
                if isinstance(i, dict)
                and i.get("scheme") == "policy_table_scheme"
                and isinstance(i.get("value"), list)
            ]
            if len(policy_forms) != 1:
                raise serializers.ValidationError(
                    {
                        "ticket_content_template": [
                            "ticket_content_template['form_data'] 必须"
                            "包含 IAM 指定 scheme 为 iam_policy_table_scheme 且 value 为列表的项,"
                        ]
                    },
                )
            # 必须每条权限都有配置单据所需渲染内容
            empty_ticket_content_actions = [
                str(ind + 1) for ind, a in enumerate(data["actions"]) if not a["ticket_content"]
            ]
            if len(empty_ticket_content_actions) > 0:
                raise serializers.ValidationError(
                    {
                        "actions": [
                            f"当 ticket_content_template 不为空时，所有权限的 ticket_content 都必须非空，当前请求中，"
                            f"第 {','.join(empty_ticket_content_actions)} 条权限的 ticket_content 为空"
                        ]
                    }
                )

        return data
