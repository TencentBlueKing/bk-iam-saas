# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云 - 权限中心 (BlueKing-IAM) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from datetime import timedelta
from typing import List

from bk_audit.log.exporters import LoggerExporter
from bk_audit.log.models import AuditEvent
from celery import shared_task
from django.conf import settings
from django.utils import timezone

from backend.apps.policy.models import Policy
from backend.audit.models import Event, get_event_model

from .constants import AuditSourceType, AuditType


@shared_task(ignore_result=True)
def pre_create_audit_model():
    """
    预创建下一个月的审计模型
    """
    next_month = (timezone.now() + timedelta(days=15)).strftime("%Y%m")
    get_event_model(next_month)


@shared_task(ignore_result=True)
def log_audit_event(suffix: str, id: str):
    """
    记录审计事件到审计中心规范的日志文件
    """
    AuditModel = get_event_model(suffix)  # noqa: N806
    event = AuditModel.objects.get(id=id)

    # 处理审计事件转换成日志，并记录日志
    AuditEventHandler().log(event)


class AuditEventHandler:
    exporter = LoggerExporter()

    handle_method_map = {
        AuditType.USER_BLACKLIST_MEMBER_CREATE.value: "handle_without_resource",
        AuditType.USER_BLACKLIST_MEMBER_DELETE.value: "handle_without_resource",
        AuditType.USER_PERMISSION_CLEAN.value: "handle_without_resource",
        AuditType.APPROVAL_GLOBAL_UPDATE.value: "handle_without_resource",
        AuditType.ROLE_CREATE.value: "handle_without_resource",
        AuditType.GROUP_CREATE.value: "handle_without_resource",
        AuditType.TEMPLATE_CREATE.value: "handle_without_resource",
        AuditType.USER_POLICY_CREATE.value: "handle_policy_create",
        AuditType.GROUP_POLICY_CREATE.value: "handle_policy_create",
        AuditType.USER_TEMPORARY_POLICY_CREATE.value: "handle_policy_create",
        AuditType.USER_POLICY_UPDATE.value: "handle_policy_update",
        AuditType.GROUP_POLICY_UPDATE.value: "handle_policy_update",
        AuditType.USER_POLICY_DELETE.value: "handle_policy_delete",
        AuditType.GROUP_POLICY_DELETE.value: "handle_policy_delete",
        AuditType.USER_TEMPORARY_POLICY_DELETE.value: "handle_policy_delete",
        AuditType.ADMIN_API_ALLOW_LIST_CONFIG_CREATE.value: "handle_white_list",
        AuditType.ADMIN_API_ALLOW_LIST_CONFIG_DELETE.value: "handle_white_list",
        AuditType.AUTHORIZATION_API_ALLOW_LIST_CONFIG_CREATE.value: "handle_white_list",
        AuditType.AUTHORIZATION_API_ALLOW_LIST_CONFIG_DELETE.value: "handle_white_list",
        AuditType.MANAGEMENT_API_ALLOW_LIST_CONFIG_CREATE.value: "handle_white_list",
        AuditType.MANAGEMENT_API_ALLOW_LIST_CONFIG_DELETE.value: "handle_white_list",
    }

    def log(self, event: Event):
        """
        记录日志
        """
        handle_method_name = self.handle_method_map.get(event.type, "handle_default")
        audit_events = getattr(self, handle_method_name)(event)
        self.exporter.export(audit_events)

    def handle_default(self, event: Event) -> List[AuditEvent]:
        """
        默认转换
        """
        action_id = event.type.replace(".", "_")

        audit_event = AuditEvent(
            event_id=event.id.hex,
            request_id=event.source_data_request_id,
            username=event.username,
            start_time=event.created_timestamp * 1000,
            bk_app_code=settings.APP_CODE,
            access_type=AuditSourceType.to_int(event.source_type),
            action_id=action_id,
            resource_type_id=event.object_type,
            instance_id=event.object_id,
            instance_name=event.object_name,
            result_code=event.status,
            extend_data=event.extra,
        )

        return [audit_event]

    def handle_without_resource(self, event: Event) -> List[AuditEvent]:
        """
        处理不需要关联资源的操作
        """
        extend_data = event.extra
        if not extend_data and event.type in [
            AuditType.ROLE_CREATE.value,
            AuditType.GROUP_CREATE.value,
            AuditType.TEMPLATE_CREATE.value,
        ]:
            extend_data.update({"id": event.object_id, "name": event.object_name, "type": event.object_type})

        action_id = event.type.replace(".", "_")

        audit_event = AuditEvent(
            event_id=event.id.hex,
            request_id=event.source_data_request_id,
            username=event.username,
            start_time=event.created_timestamp * 1000,
            bk_app_code=settings.APP_CODE,
            access_type=AuditSourceType.to_int(event.source_type),
            action_id=action_id,
            result_code=event.status,
            extend_data=extend_data,
        )

        return [audit_event]

    def handle_policy_create(self, event: Event) -> List[AuditEvent]:
        action_id = (
            "policy_create"
            if event.type != AuditType.USER_TEMPORARY_POLICY_CREATE.value
            else "temporary_policy_create"
        )

        extra_data = event.extra
        extra_data["subject"] = {
            "type": event.object_type,
            "id": event.object_id,
        }

        audit_event = AuditEvent(
            event_id=event.id.hex,
            request_id=event.source_data_request_id,
            username=event.username,
            start_time=event.created_timestamp * 1000,
            bk_app_code=settings.APP_CODE,
            access_type=AuditSourceType.to_int(event.source_type),
            action_id=action_id,
            result_code=event.status,
            extend_data=extra_data,
        )

        return [audit_event]

    def handle_policy_update(self, event: Event) -> List[AuditEvent]:
        extra_data = event.extra
        # 如果是用户组模板策略更新
        if "template_id" in extra_data and extra_data["template_id"] != 0:
            extra_data["subject"] = {
                "type": event.object_type,
                "id": event.object_id,
            }

            return [
                AuditEvent(
                    event_id=event.id.hex,
                    request_id=event.source_data_request_id,
                    username=event.username,
                    start_time=event.created_timestamp * 1000,
                    bk_app_code=settings.APP_CODE,
                    access_type=AuditSourceType.to_int(event.source_type),
                    action_id="policy_update",
                    resource_type_id="policy",
                    instance_id="0",
                    result_code=event.status,
                    extend_data=extra_data,
                )
            ]

        system_id = extra_data["system_id"]
        action_ids = [p.get("action_id", p.get("id", "")) for p in extra_data["policies"]]

        policies = Policy.objects.filter(
            subject_type=event.object_type, subject_id=event.object_id, system_id=system_id, action_id__in=action_ids
        ).defer("_resources")

        audit_events = []
        for p in policies:
            audit_events.append(
                AuditEvent(
                    request_id=event.source_data_request_id,
                    username=event.username,
                    start_time=event.created_timestamp * 1000,
                    bk_app_code=settings.APP_CODE,
                    access_type=AuditSourceType.to_int(event.source_type),
                    action_id="policy_update",
                    resource_type_id="policy",
                    instance_id=str(p.id),
                    instance_name=p.display_name,
                    result_code=event.status,
                    extend_data={},
                )
            )

        return audit_events

    def handle_policy_delete(self, event: Event) -> List[AuditEvent]:
        action_id = (
            "policy_delete"
            if event.type != AuditType.USER_TEMPORARY_POLICY_DELETE.value
            else "temporary_policy_delete"
        )

        extra_data = event.extra
        extra_data["subject"] = {
            "type": event.object_type,
            "id": event.object_id,
        }

        audit_event = AuditEvent(
            event_id=event.id.hex,
            request_id=event.source_data_request_id,
            username=event.username,
            start_time=event.created_timestamp * 1000,
            bk_app_code=settings.APP_CODE,
            access_type=AuditSourceType.to_int(event.source_type),
            action_id=action_id,
            resource_type_id="policy",
            instance_id="0",
            result_code=event.status,
            extend_data=extra_data,
        )

        return [audit_event]

    def handle_white_list(self, event: Event) -> List[AuditEvent]:
        if event.type.startswith("admin.api.allow.list.config"):
            resource_type_id = "admin_api_white_list"
        elif event.type.startswith("authorization.api.allow.list.config"):
            resource_type_id = "auth_api_white_list"
        elif event.type.startswith("management.api.allow.list.config"):
            resource_type_id = "management_api_white_list"

        action_id = f"{resource_type_id}_" + event.type.split(".")[-1]

        audit_event = AuditEvent(
            event_id=event.id.hex,
            request_id=event.source_data_request_id,
            username=event.username,
            start_time=event.created_timestamp * 1000,
            bk_app_code=settings.APP_CODE,
            access_type=AuditSourceType.to_int(event.source_type),
            action_id=action_id,
            resource_type_id=resource_type_id,
            instance_id=event.object_id,
            instance_name=event.object_name,
            result_code=event.status,
            extend_data=event.extra,
        )

        return [audit_event]
