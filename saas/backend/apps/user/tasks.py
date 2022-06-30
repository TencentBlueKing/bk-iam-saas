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
from itertools import groupby
from urllib.parse import urlencode

from celery import task
from django.conf import settings
from django.core.paginator import Paginator
from django.template.loader import render_to_string

from backend.apps.organization.constants import StaffStatus
from backend.apps.organization.models import User
from backend.apps.subject.audit import log_user_cleanup_policy_audit_event
from backend.biz.group import GroupBiz
from backend.biz.policy import PolicyOperationBiz, PolicyQueryBiz
from backend.common.time import db_time, get_soon_expire_ts
from backend.component import esb
from backend.service.constants import SubjectType
from backend.service.models import Subject
from backend.util.url import url_join

logger = logging.getLogger("celery")


@task(ignore_result=True)
def user_group_policy_expire_remind():
    """
    用户的用户组, 自定义权限过期检查
    """
    policy_biz = PolicyQueryBiz()
    group_biz = GroupBiz()

    # 分页遍历所有的用户
    qs = User.objects.filter(staff_status=StaffStatus.IN.value)
    paginator = Paginator(qs, 100)

    base_url = url_join(settings.APP_URL, "/perm-renewal")

    if not paginator.count:
        return

    expired_at = get_soon_expire_ts()
    for i in paginator.page_range:
        for user in paginator.page(i):
            subject = Subject(type=SubjectType.USER.value, id=user.username)

            groups = group_biz.list_subject_group_before_expired_at(subject, expired_at)

            policies = policy_biz.list_expired(subject, expired_at)

            if not groups and not policies:
                continue

            params = {"tab": "group", "source": "email"}
            if not groups:
                params["tab"] = "custom"
            url = base_url + "?" + urlencode(params)

            mail_content = render_to_string(
                "user_expired_mail.html",
                {"groups": groups, "policies": policies, "url": url, "user": user, "index_url": settings.APP_URL},
            )
            try:
                esb.send_mail(user.username, "蓝鲸权限中心续期提醒", mail_content)
            except Exception:  # pylint: disable=broad-except
                logger.exception("send user_group_policy_expire_remind email fail, username=%s", user.username)


@task(ignore_result=True)
def user_cleanup_expired_policy():
    """
    清理用户的长时间过期策略
    """
    policy_query_biz = PolicyQueryBiz()
    policy_operation_biz = PolicyOperationBiz()

    expired_at = int(db_time()) - settings.MAX_EXPIRED_POLICY_DELETE_TIME
    task_id = user_cleanup_expired_policy.request.id

    # 分页遍历所有的用户
    qs = User.objects.filter(staff_status=StaffStatus.IN.value)
    paginator = Paginator(qs, 100)

    if not paginator.count:
        return

    for i in paginator.page_range:
        for user in paginator.page(i):
            subject = Subject(type=SubjectType.USER.value, id=user.username)

            # 查询用户指定过期时间之前的所有策略
            policies = policy_query_biz.list_expired(subject, expired_at)
            if not policies:
                continue

            # 分系统删除过期的策略
            sorted_policies = sorted(policies, key=lambda p: p.system.id)
            for system_id, per_policies in groupby(sorted_policies, lambda p: p.system.id):
                per_policies = list(per_policies)
                policy_operation_biz.delete_by_ids(system_id, subject, [p.id for p in per_policies])

                # 记审计信息
                log_user_cleanup_policy_audit_event(task_id, user, system_id, per_policies)
