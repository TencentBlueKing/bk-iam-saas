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

from typing import List

from django.db import models
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _

from backend.common.error_codes import error_codes
from backend.service.constants import TemplatePreUpdateStatus
from backend.service.models import Subject


class PermTemplateManager(models.Manager):
    def get_or_404(self, id: int):
        return get_object_or_404(self.all(), id=id)

    def query_template_ids(self, system_id: str, action_id: str):
        query_action_id = f'"{action_id}"'
        return self.filter(system_id=system_id, _action_ids__contains=query_action_id).values_list("id")


class PermTemplatePolicyAuthorizedManager(models.Manager):
    def filter_by_subject(self, subject: Subject) -> QuerySet:
        return self.filter(subject_type=subject.type, subject_id=subject.id)

    def filter_by_template(self, template_id: int) -> QuerySet:
        return self.filter(template_id=template_id)

    def count_by_template(self, template_id: int) -> int:
        return self.filter(template_id=template_id).count()

    def query_exists_subject(self, template_id: int, subject_ids: List[str]) -> List[Subject]:
        """
        查询模板存在的成员
        """
        query = self.filter(template_id=template_id, subject_id__in=subject_ids).values_list(
            "subject_type", "subject_id"
        )
        return [Subject(type=one[0], id=one[1]) for one in query]

    def query_exists_template_auth(self, subject: Subject, template_ids: List[int]) -> List[int]:
        """
        查询subject已存在的授权, 返回授权的模板id
        """
        query = (
            self.filter_by_subject(subject).filter(template_id__in=template_ids).values_list("template_id", flat=True)
        )
        return list(query)

    def get_by_subject_template(self, subject: Subject, template_id: int):
        """
        获取subject指定的模板授权信息
        """
        return get_object_or_404(self.filter_by_subject(subject), template_id=template_id)


class PermTemplatePreGroupSyncManager(models.Manager):
    def get_by_group_template(self, group_id: int, template_id: int) -> QuerySet:
        return self.filter(template_id=template_id, group_id=group_id).first()

    def filter_by_template(self, template_id: int) -> QuerySet:
        return self.filter(template_id=template_id)

    def update_status(self, id: int, status: str):
        self.filter(id=id).update(status=status)

    def delete_by_template(self, template_id: int):
        self.filter(template_id=template_id).delete()


class PermTemplatePreUpdateLockManager(models.Manager):
    def filter_exists_template_ids(self, template_ids: List[int]) -> List[int]:
        return list(self.filter(template_id__in=template_ids).values_list("template_id", flat=True))

    def acquire_lock_not_running_or_raise(self, template_id: int):
        """
        获取非running状态的锁, 如果锁是running则raise
        """
        lock = self.filter(template_id=template_id).first()
        if lock and lock.status == TemplatePreUpdateStatus.RUNNING.value:
            raise error_codes.VALIDATE_ERROR.format(_("更新任务正在运行!"))
        return lock

    def acquire_lock_waiting_or_raise(self, template_id: int):
        """
        获取waiting状态的锁, 如果锁不是waiting则raise
        """
        lock = self.filter(template_id=template_id).first()
        if not lock or lock.status != TemplatePreUpdateStatus.WAITING.value:
            raise error_codes.VALIDATE_ERROR.format(_("预提交的任务不存在!"))
        return lock

    def acquire_lock_or_raise(self, template_id: int):
        lock = self.filter(template_id=template_id).first()
        if not lock:
            raise error_codes.VALIDATE_ERROR.format(_("预提交的任务不存在!"))
        return lock

    def raise_if_exists(self, template_id: int):
        if self.filter(template_id=template_id).exists():
            raise error_codes.VALIDATE_ERROR.format(_("权限模板正在更新, 不能进行下一步操作!"))

    def update_waiting_to_running(self, template_id: int) -> bool:
        """
        更新waiting到running
        返回是否有更新到数据
        """
        count = self.filter(template_id=template_id, status=TemplatePreUpdateStatus.WAITING.value).update(
            status=TemplatePreUpdateStatus.RUNNING.value
        )
        return bool(count)
