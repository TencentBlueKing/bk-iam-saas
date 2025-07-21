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
import logging
from typing import Dict, List

from django.db import models
from django.db.models import TextField
from mptt.models import MPTTModel, TreeForeignKey

from backend.apps.organization.constants import (
    SYNC_TASK_DEFAULT_EXECUTOR,
    SyncTaskStatus,
    SyncType,
    TriggerType,
)
from backend.apps.organization.managers import SyncErrorLogManager
from backend.common.constants import DEFAULT_TENANT_ID
from backend.common.models import TimestampedModel
from backend.util.json import json_dumps

logger = logging.getLogger("app")


class User(TimestampedModel):
    """用户信息表"""

    tenant_id = models.CharField("租户 ID", max_length=64, default=DEFAULT_TENANT_ID)

    username = models.CharField("用户名", max_length=255, primary_key=True)
    full_name = models.CharField("姓名", max_length=255, null=True, blank=True, default="")
    display_name = models.CharField("展示名", max_length=255, null=True, blank=True, default="")

    class Meta:
        ordering = ["username"]
        verbose_name = "用户信息"
        verbose_name_plural = "用户信息"

    @property
    def departments(self):
        """获取用户加入的部门"""
        dept_ids = DepartmentMember.objects.filter(username=self.username).values_list("department_id", flat=True)
        return Department.objects.filter(id__in=dept_ids)

    @property
    def ancestor_department_ids(self) -> List[int]:
        """获取用户加入的部门，包括其祖先部门"""
        # 查询用户直接加入的部门
        direct_department_ids = DepartmentMember.objects.filter(username=self.username).values_list(
            "department_id", flat=True
        )
        # 查询所有部门的祖先，包括直接部门自身
        department_id_set = set(direct_department_ids)
        if department_id_set:
            for dept in Department.objects.filter(id__in=direct_department_ids):
                department_id_set.update(dept.ancestor_ids)
        # 仅仅需要 ID 字段，则直接返回
        return list(department_id_set)


class TimestampMPTTModel(MPTTModel):
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Department(TimestampMPTTModel):
    """部门信息表"""

    tenant_id = models.CharField("租户 ID", max_length=64, default=DEFAULT_TENANT_ID)

    id = models.IntegerField("部门 ID", primary_key=True)
    name = models.CharField("部门名称", max_length=255)
    parent = TreeForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="children")

    # 冗余字段
    ancestors = models.TextField("祖先", help_text="List[Dict[id,name]] 的 Json 存储")
    child_count = models.IntegerField("子部门数量 (非递归)", default=0)
    member_count = models.IntegerField("部门下用户数 (非递归)", default=0)
    recursive_member_count = models.IntegerField("(递归) 部门下用户数", default=0)

    class Meta:
        ordering = ["id"]
        verbose_name = "部门表"
        verbose_name_plural = "部门表"

    def __str__(self):
        return f"{self.id}-{self.name}"

    def parse_ancestors(self) -> List[Dict]:
        """解析祖先 JSON"""
        if self.ancestors:
            try:
                return json.loads(self.ancestors)
            except Exception:  # pylint: disable=broad-except
                logger.exception("parse_ancestors ancestors: %s, department_id: %s fail", self.ancestors, self.id)
                return []
        return []

    @property
    def ancestor_ids(self) -> List[int]:
        return [i["id"] for i in self.parse_ancestors()]

    @property
    def full_name(self):
        """如：总公司/子公司/分公司"""
        departments = [i["name"] for i in self.parse_ancestors()]
        departments.append(self.name)
        return "/".join(departments)

    @property
    def members(self):
        if self.member_count == 0:
            return []
        usernames = list(DepartmentMember.objects.filter(department_id=self.id).values_list("username", flat=True))
        return User.objects.filter(username__in=usernames)

    @property
    def recursive_members(self):
        if self.recursive_member_count == 0:
            return []
        ids = list(self.get_descendants(include_self=True).values_list("id", flat=True))
        usernames = list(DepartmentMember.objects.filter(department_id__in=ids).values_list("username", flat=True))
        return User.objects.filter(username__in=usernames)


class DepartmentRelationMPTTTree(models.Model):
    """部门关系树记录表，用于自增 tree_id 的分配"""

    tenant_id = models.CharField("租户 ID", max_length=64, default=DEFAULT_TENANT_ID)


class DepartmentMember(models.Model):
    """部门成员表"""

    tenant_id = models.CharField("租户 ID", max_length=64, default=DEFAULT_TENANT_ID)

    department_id = models.IntegerField("部门 ID", db_index=True)
    username = models.CharField("用户名", max_length=255, db_index=True)


class SyncRecord(TimestampedModel):
    """同步记录"""

    tenant_id = models.CharField("租户 ID", max_length=64, default=DEFAULT_TENANT_ID)

    executor = models.CharField("执行者", max_length=64, default=SYNC_TASK_DEFAULT_EXECUTOR)
    type = models.CharField("同步任务类型", choices=SyncType.get_choices(), default=SyncType.Full.value, max_length=16)
    status = models.CharField(
        "任务状态", choices=SyncTaskStatus.get_choices(), default=SyncTaskStatus.Running.value, max_length=16
    )

    class Meta:
        ordering = ["-id"]
        verbose_name = "组织架构同步记录"
        verbose_name_plural = "组织架构同步记录"

    @property
    def detail(self) -> Dict:
        """同步异常日志详情"""
        if self.status != SyncTaskStatus.Failed.value:
            return {}

        sync_error_log = SyncErrorLog.objects.filter(sync_record_id=self.id).first()
        if sync_error_log is not None:
            return sync_error_log.log

        return {}

    @property
    def cost_time(self) -> int:
        return int((self.updated_time - self.created_time).total_seconds())

    @property
    def trigger_type(self) -> str:
        if self.executor == SYNC_TASK_DEFAULT_EXECUTOR:
            return TriggerType.PERIODIC_TASK.value

        return TriggerType.MANUAL_SYNC.value


class SyncErrorLog(models.Model):
    """同步异常记录"""

    tenant_id = models.CharField("租户 ID", max_length=64, default=DEFAULT_TENANT_ID)

    sync_record_id = models.IntegerField("同步记录 id", db_index=True)
    _log = TextField("日志详情", db_column="log")

    objects = SyncErrorLogManager()

    @property
    def log(self) -> dict:
        return json.loads(self._log)

    @log.setter
    def log(self, log):
        self._log = json_dumps(log)


class SubjectToDelete(TimestampedModel):
    """待删除的 Subject"""

    tenant_id = models.CharField("租户 ID", max_length=64, default=DEFAULT_TENANT_ID)

    subject_id = models.CharField("Subject ID", max_length=255)
    subject_type = models.CharField("Subject Type", max_length=64)

    class Meta:
        verbose_name = "待删除的 Subject"
        verbose_name_plural = "待删除的 Subject"
        unique_together = ["subject_type", "subject_id"]
