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
import json
from typing import Dict, List

from django.db import models

from backend.common.models import BaseModel, CompressedJSONField
from backend.service.constants import SubjectType, TemplatePreUpdateStatus
from backend.util.json import json_dumps

from .managers import (
    PermTemplateManager,
    PermTemplatePolicyAuthorizedManager,
    PermTemplatePreGroupSyncManager,
    PermTemplatePreUpdateLockManager,
)


class PermTemplate(BaseModel):
    """
    权限模板
    """

    name = models.CharField("模板名称", max_length=128)
    system_id = models.CharField("系统ID", max_length=32)
    description = models.CharField("描述", max_length=255, default="")
    subject_count = models.IntegerField("授权对象数量", default=0)
    _action_ids = models.TextField("操作列表", db_column="action_ids")

    objects = PermTemplateManager()

    class Meta:
        verbose_name = "权限模板"
        verbose_name_plural = "权限模板"
        ordering = ["-created_time"]
        indexes = [models.Index(fields=["system_id"])]

    @property
    def action_ids(self):
        return json.loads(self._action_ids)

    @action_ids.setter
    def action_ids(self, data):
        self._action_ids = json_dumps(data)

    @classmethod
    def delete_action(cls, system_id: str, action_id: str) -> List[int]:
        """模板里删除某个操作，并返回被变更的模板ID列表"""
        templates = cls.objects.filter(system_id=system_id)
        should_updated_templates = []
        for template in templates:
            action_ids = template.action_ids
            # 要删除的Action不在权限模板里，则忽略
            if action_id not in action_ids:
                continue
            # 移除要删除Action，然后更新
            action_ids.remove(action_id)
            template.action_ids = action_ids
            # 添加到将更新的列表里
            should_updated_templates.append(template)

        # 批量更新权限模板
        if len(should_updated_templates) > 0:
            cls.objects.bulk_update(should_updated_templates, fields=["_action_ids"], batch_size=100)

        return [t.id for t in should_updated_templates]


class PermTemplatePolicyAuthorized(BaseModel):
    """
    权限模板授权
    """

    template_id = models.IntegerField("模板ID")
    subject_type = models.CharField("授权对象类型", max_length=32, choices=SubjectType.get_choices())
    subject_id = models.CharField("授权对象ID", max_length=64)
    system_id = models.CharField("系统ID", max_length=32)
    _data = models.TextField("授权数据", db_column="data")  # 调研压缩的json字段
    _auth_types = models.TextField(
        "模板授权策略的鉴权类型", db_column="auth_types", help_text="JSON存储 {'action_id': auth_type, ...}", default="{}"
    )

    objects = PermTemplatePolicyAuthorizedManager()

    class Meta:
        verbose_name = "权限模板授权"
        verbose_name_plural = "权限模板授权"
        indexes = [
            models.Index(fields=["system_id"]),  # 创建单字段索引
        ]
        unique_together = ["template_id", "subject_type", "subject_id"]
        ordering = ["-updated_time"]

    @property
    def data(self):
        return json.loads(self._data)

    @data.setter
    def data(self, data):
        self._data = json_dumps(data)

    @property
    def auth_types(self) -> Dict[str, str]:
        return json.loads(self._auth_types)

    @auth_types.setter
    def auth_types(self, auth_types: Dict):
        self._auth_types = json_dumps(auth_types)

    @classmethod
    def delete_action(cls, system_id: str, action_id: str, perm_template_ids: List[int]):
        """授权信息里剔除某个系统的某个操作"""
        authorized_policies = cls.objects.filter(template_id__in=perm_template_ids, system_id=system_id)
        should_updated_policies = []
        for ap in authorized_policies:
            data = ap.data
            actions = [a for a in data["actions"] if a.get("id", a.get("action_id")) != action_id]
            data["actions"] = actions
            ap.data = data
            should_updated_policies.append(ap)

        if len(should_updated_policies) > 0:
            cls.objects.bulk_update(should_updated_policies, fields=["_data"], batch_size=20)


class PermTemplatePreUpdateLock(BaseModel):
    """
    模板的预提交信息锁

    1. 获取已有的预提交信息时不能是running
    2. 获取模板预更新的到用户组的预览信息只能是waiting
    3. 模板预更新提交时, 需要从 waiting -> running
    4. 如果模板存在预更新的信息锁, 不能授权到用户组
    5. 删除预提交信息时, 不能是running
    6. 提交用户组的更新信息, 锁只能是 waiting
    7. 如果锁是running, 不能从新提交预更新信息
    """

    template_id = models.IntegerField("模板ID")
    status = models.CharField(
        "类型",
        max_length=32,
        choices=TemplatePreUpdateStatus.get_choices(),
        default=TemplatePreUpdateStatus.WAITING.value,
    )
    action_ids = CompressedJSONField("操作列表", default=None)

    objects = PermTemplatePreUpdateLockManager()

    class Meta:
        verbose_name = "权限模板更新预提交"
        verbose_name_plural = "权限模板更新预提交"
        ordering = ["-created_time"]
        unique_together = ["template_id"]


class PermTemplatePreGroupSync(BaseModel):
    template_id = models.IntegerField("模板ID")
    group_id = models.IntegerField("模板ID")
    status = models.CharField(
        "类型",
        max_length=32,
        choices=TemplatePreUpdateStatus.get_choices(),
        default=TemplatePreUpdateStatus.WAITING.value,
    )
    data = CompressedJSONField("授权数据", default=None)

    objects = PermTemplatePreGroupSyncManager()

    class Meta:
        verbose_name = "权限模板更新用户组同步预提交"
        verbose_name_plural = "权限模板更新用户组同步预提交"
        unique_together = ["template_id", "group_id"]
        ordering = ["-updated_time"]
