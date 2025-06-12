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

from typing import Any, List

from celery import shared_task
from django.conf import settings
from django.core.paginator import Paginator
from pydantic.tools import parse_obj_as

from backend.apps.group.models import Group, GroupAuthorizeLock
from backend.biz.group import GroupBiz
from backend.biz.policy import PolicyBean, PolicyOperationBiz
from backend.biz.template import TemplateBiz
from backend.common.time import db_time
from backend.long_task.constants import TaskType
from backend.long_task.tasks import StepTask, register_handler
from backend.service.models import Subject

from .audit import log_group_cleanup_member_audit_event


@shared_task(ignore_result=True)
def group_cleanup_expired_member():
    """
    用户组清理长时间过期的成员
    """
    biz = GroupBiz()

    expired_at = int(db_time()) - settings.MAX_EXPIRED_POLICY_DELETE_TIME
    task_id = group_cleanup_expired_member.request.id
    limit = 100

    # 分页遍历所有的用户组
    qs = Group.objects.all()
    paginator = Paginator(qs, limit)

    if not paginator.count:
        return

    for i in paginator.page_range:
        for group in paginator.page(i):
            # 查询指定过期时间之前的成员数量
            count = biz.get_member_count_before_expired_at(group.id, expired_at)
            if count == 0:
                continue

            # 分页删除过期的成员
            for offset in range(0, count, limit):
                _, members = biz.list_paging_members_before_expired_at(group.id, expired_at, limit, offset)
                subjects = parse_obj_as(List[Subject], members)
                biz.remove_members(str(group.id), subjects)

                # 记审计信息
                log_group_cleanup_member_audit_event(task_id, group, subjects)


@register_handler(TaskType.GROUP_AUTHORIZATION.value)
class GroupAuthorizationTask(StepTask):
    """
    权限模板授权
    """

    template_biz = TemplateBiz()
    policy_biz = PolicyOperationBiz()

    def __init__(self, subject, key):
        self.subject = Subject.parse_obj(subject)
        self.key = key

    def get_params(self) -> List[Any]:
        group_id = int(self.subject.id)
        return list(GroupAuthorizeLock.objects.filter(group_id=group_id, key=self.key).values_list("id", flat=True))

    def run(self, item: Any):
        lock = GroupAuthorizeLock.objects.get(id=item)

        template_id = lock.template_id
        system_id = lock.system_id
        policies = parse_obj_as(List[PolicyBean], lock.data["actions"])
        # 授权
        if template_id != 0:
            self.template_biz.grant_subject(system_id, template_id, self.subject, policies)
        else:
            self.policy_biz.alter(system_id, self.subject, policies)

        lock.delete()

    def on_success(self):
        pass
