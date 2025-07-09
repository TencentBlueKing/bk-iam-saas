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

import json
import uuid
from typing import Any, Dict, Type

from django.db import connections, models
from django.utils import timezone

from backend.common.constants import DEFAULT_TENANT_ID
from backend.common.models import BaseModel
from backend.service.constants import RoleType
from backend.util.json import json_dumps

from .constants import AuditObjectType, AuditSourceType, AuditStatus, AuditType

# 用于缓存每个月审计表模型
_audit_models: Dict[str, Type[Any]] = {}


class Event(BaseModel):
    tenant_id = models.CharField("租户 ID", max_length=64, default=DEFAULT_TENANT_ID)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source_type = models.CharField("事件来源类型", max_length=32, choices=AuditSourceType.get_choices())
    source_data_request_id = models.CharField("事件来源请求 ID", max_length=32, default="")
    source_data_app_code = models.CharField("事件来源请求 app code", max_length=128, default="")
    source_data_task_id = models.CharField("事件来源任务 ID", max_length=36, default="")
    time = models.DateTimeField(auto_now_add=True)
    type = models.CharField("事件类型", max_length=64, choices=AuditType.get_choices())
    username = models.CharField("用户名", max_length=64)
    role_type = models.CharField(
        "角色类型", max_length=32, default=RoleType.STAFF.value, choices=RoleType.get_choices()
    )
    role_id = models.IntegerField("角色 ID", default=0)
    system_id = models.CharField("系统 id", max_length=32, default="")  # 策略操作时记录
    object_type = models.CharField("对象类型", max_length=32, choices=AuditObjectType.get_choices())
    object_id = models.CharField("对象 ID", max_length=64)
    object_name = models.CharField("对象名称", max_length=128)
    _extra = models.TextField("附加数据", default="{}", db_column="extra")  # json
    status = models.IntegerField(
        "事件状态",
        default=AuditStatus.SUCCEED.value,  # type: ignore[attr-defined]
        choices=AuditStatus.get_choices(),
    )

    @property
    def extra(self):
        return json.loads(self._extra)

    @extra.setter
    def extra(self, data):
        self._extra = json_dumps(data)

    class Meta:
        abstract = True


class EventForMeta(Event):
    """
    用于 filter 与 serializer 的 Event Model
    请勿用于其它场景
    """

    class Meta:
        managed = False


def _get_sub_model(base_cls, suffix: str):
    table_name = f"audit_{base_cls.__name__.lower()}_{suffix}"

    class Metaclass(models.base.ModelBase):
        def __new__(cls, name, bases, attrs):
            name = f"{base_cls.__name__}_{suffix}"
            return models.base.ModelBase.__new__(cls, name, bases, attrs)

    class AuditModel(base_cls, metaclass=Metaclass):  # type: ignore
        @staticmethod
        def exists():
            return table_name in _get_connection().introspection.table_names()

        class Meta:
            db_table = table_name

    return AuditModel


def get_audit_db():
    if "audit" in connections:
        return "audit"

    return "default"


def _get_connection():
    return connections[get_audit_db()]


def _get_model(name: str, suffix: str = ""):
    if not suffix:
        suffix = timezone.now().strftime("%Y%m")

    key = f"{name}_{suffix}"
    cls = _audit_models.get(key)
    if cls is not None:
        return cls

    base_cls = globals()[name]
    cls = _get_sub_model(base_cls, suffix)
    if not cls.exists():
        # NOTE 并发时，可能会 raise
        with _get_connection().schema_editor() as schema_editor:
            schema_editor.create_model(cls)

    _audit_models[key] = cls
    return cls


def get_event_model(suffix: str = ""):
    return _get_model("Event", suffix)
