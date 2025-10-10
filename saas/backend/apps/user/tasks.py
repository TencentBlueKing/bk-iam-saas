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
from datetime import timedelta
from itertools import groupby
from typing import List, Optional
from urllib.parse import urlencode

from celery import Task, current_app, shared_task
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import F, Q
from django.template.loader import render_to_string
from django.utils import timezone

from backend.apps.organization.models import User
from backend.apps.policy.models import Policy
from backend.apps.role.constants import NotificationTypeEnum
from backend.apps.role.models import Role, RoleUser
from backend.apps.subject.audit import log_user_cleanup_policy_audit_event
from backend.apps.subject_template.models import SubjectTemplateRelation
from backend.apps.user.models import UserPermissionCleanupRecord
from backend.biz.constants import StaffStatus
from backend.biz.group import GroupBiz
from backend.biz.helper import RoleWithPermGroupBiz, get_user_expired_groups_policies
from backend.biz.policy import PolicyOperationBiz, PolicyQueryBiz
from backend.biz.role import RoleBiz, get_global_notification_config
from backend.biz.subject_template import SubjectTemplateBiz
from backend.biz.system import SystemBiz
from backend.common.time import db_time, get_expired_at, need_run_expired_remind
from backend.component import esb
from backend.component.bkbot import send_iam_ticket
from backend.service.constants import RoleType, SubjectType
from backend.service.models import Subject
from backend.util.time import timestamp_to_local
from backend.util.url import url_join

from .constants import UserPermissionCleanupRecordStatusEnum

logger = logging.getLogger("celery")


MAX_USER_PERMISSION_CLEAN_RETRY_COUNT = 3


class SendUserExpireRemindMailTask(Task):
    name = "backend.apps.user.tasks.SendUserExpireRemindMailTask"

    policy_biz = PolicyQueryBiz()
    group_biz = GroupBiz()

    base_url = url_join(settings.APP_URL, "/perm-renewal")

    def run(self, username: str, expired_at_before: int, expired_at_after: int, notification_types: List[str]):
        user = User.objects.filter(username=username).first()
        if not user:
            return

        # 查询用户过期的用户组与权限
        groups, policies = get_user_expired_groups_policies(user, expired_at_before, expired_at_after)
        if not groups and not policies:
            return

        params = {"tab": "group", "source": "notification"}
        if not groups:
            params["tab"] = "custom"
        url = self.base_url + "?" + urlencode(params)

        if NotificationTypeEnum.MAIL.value in notification_types:
            mail_content = render_to_string(
                "user_expired_mail.html",
                {"groups": groups, "policies": policies, "url": url, "user": user, "index_url": settings.APP_URL},
            )
            try:
                esb.send_mail(user.username, "【蓝鲸权限中心】权限续期提醒", mail_content)
            except Exception:  # pylint: disable=broad-except
                logger.exception("send user_group_policy_expire_remind email fail, username=%s", user.username)

        if NotificationTypeEnum.RTX.value in notification_types and settings.BK_BOT_APPROVAL_APIGW_URL:
            content = render_to_string(
                "user_expired_rtx.tpl",
                {"groups": groups, "policies": policies},
            )

            data = {
                "title": "**【蓝鲸权限中心】权限续期提醒**",
                "summary": content,
                "approvers": username,
                "detail_url": url,
                "refuse_url": "",
                "refuse_data": {"action": "refse"},
                "actions": [
                    {
                        "name": "3个月",
                        "callback_url": url_join(
                            settings.BK_IAM_BOT_APPROVAL_CALLBACK_APIGW_URL,
                            "/api/v1/open/application/approval_bot/user/",
                        ),
                        "callback_data": {
                            "username": username,
                            "expired_at_before": expired_at_before,
                            "expired_at_after": expired_at_after,
                            "month": 3,
                        },
                        "confirm_button_info": "你的续期申请已提交，审批中",
                    },
                    {
                        "name": "6个月",
                        "callback_url": url_join(
                            settings.BK_IAM_BOT_APPROVAL_CALLBACK_APIGW_URL,
                            "/api/v1/open/application/approval_bot/user/",
                        ),
                        "callback_data": {
                            "username": username,
                            "expired_at_before": expired_at_before,
                            "expired_at_after": expired_at_after,
                            "month": 6,
                        },
                        "confirm_button_info": "你的续期申请已提交，审批中",
                    },
                    {
                        "name": "1年",
                        "callback_url": url_join(
                            settings.BK_IAM_BOT_APPROVAL_CALLBACK_APIGW_URL,
                            "/api/v1/open/application/approval_bot/user/",
                        ),
                        "callback_data": {
                            "username": username,
                            "expired_at_before": expired_at_before,
                            "expired_at_after": expired_at_after,
                            "month": 12,
                        },
                        "confirm_button_info": "你的续期申请已提交，审批中",
                    },
                ],
            }

            try:
                send_iam_ticket(data)
            except Exception:  # pylint: disable=broad-except
                logger.exception("send user_group_policy_expire_remind rtx fail, username=%s", user.username)


current_app.tasks.register(SendUserExpireRemindMailTask())


@shared_task(ignore_result=True)
def user_group_policy_expire_remind():
    """
    用户的用户组, 自定义权限过期检查
    """
    # 获取配置
    notification_config = get_global_notification_config()

    if not need_run_expired_remind(notification_config):
        return

    expired_at_before = get_expired_at(notification_config["expire_days_before"])
    expired_at_after = get_expired_at(notification_config["expire_days_after"] * -1)

    username_set = set()  # 用于去重

    # 1. 查询有自定义授权的用户
    qs = Policy.objects.filter(subject_type=SubjectType.USER.value).only("subject_id")
    paginator = Paginator(qs, 1000)

    for i in paginator.page_range:
        for p in paginator.page(i):
            username = p.subject_id

            if username in username_set:
                continue

            username_set.add(username)
            SendUserExpireRemindMailTask().delay(
                username, expired_at_before, expired_at_after, notification_config["notification_types"]
            )

    # 2. 查询用户组成员过期
    group_biz = GroupBiz()
    group_subjects = group_biz.list_group_subject_before_expired_at(expired_at_before)
    for gs in group_subjects:
        if gs.subject.type != SubjectType.USER.value:
            continue

        # 判断过期时间是否在区间内
        if gs.expired_at < expired_at_after:
            continue

        username = gs.subject.id
        if username in username_set:
            continue

        username_set.add(username)
        SendUserExpireRemindMailTask().delay(
            username, expired_at_before, expired_at_after, notification_config["notification_types"]
        )


@shared_task(ignore_result=True)
def user_cleanup_expired_policy():
    """
    清理用户的长时间过期策略
    """
    policy_query_biz = PolicyQueryBiz()
    policy_operation_biz = PolicyOperationBiz()

    expired_at = int(db_time()) - settings.MAX_EXPIRED_POLICY_DELETE_TIME
    task_id = user_cleanup_expired_policy.request.id

    # 分页遍历有授权的用户
    qs = Policy.objects.filter(subject_type=SubjectType.USER.value).only("subject_id")
    paginator = Paginator(qs, 100)

    if not paginator.count:
        return

    username_set = set()  # 用于去重
    for i in paginator.page_range:
        for p in paginator.page(i):
            username = p.subject_id

            # 去重
            if username in username_set:
                continue

            username_set.add(username)

            user = User.objects.filter(staff_status=StaffStatus.IN.value, username=username).first()
            if not user:
                continue

            subject = Subject.from_username(username)

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


class UserPermissionCleaner:
    """
    用户权限清理
    """

    system_biz = SystemBiz()
    policy_query_biz = PolicyQueryBiz()
    policy_operation_biz = PolicyOperationBiz()

    group_biz = GroupBiz()
    role_biz = RoleBiz()
    role_with_perm_group_biz = RoleWithPermGroupBiz()
    subject_template_biz = SubjectTemplateBiz()

    def __init__(self, username: str) -> None:
        record = UserPermissionCleanupRecord.objects.get(username=username)

        self._record = record
        self._subject = Subject.from_username(username)

    def clean(self, before_at: Optional[int] = None):
        # 有其他的任务在处理, 忽略
        if self._record.status == UserPermissionCleanupRecordStatusEnum.RUNNING.value:
            return

        # 更新失败, 不处理
        if not UserPermissionCleanupRecord.objects.filter(
            username=self._subject.id, status=self._record.status
        ).update(status=UserPermissionCleanupRecordStatusEnum.RUNNING.value):
            return

        try:
            self._clean_policy()
            self._clean_group(before_at)
            self._clean_subject_group(before_at)
            self._clean_role(before_at)
        except Exception as e:  # pylint: disable=broad-except
            self._record.status = UserPermissionCleanupRecordStatusEnum.FAILED.value
            self._record.error_info = str(e)
            self._record.save(update_fields=["status", "error_info"])
        else:
            self._record.status = UserPermissionCleanupRecordStatusEnum.SUCCEED.value
            self._record.save(update_fields=["status"])

    def _clean_policy(self):
        """
        清理自定义权限, 临时权限
        """

        # 遍历所有系统, 查询系统的策略, 删除
        systems = self.system_biz.list()
        for system in systems:
            system_id = system.id

            # 删除自定义权限
            policies = self.policy_query_biz.list_by_subject(system_id, self._subject)
            if policies:
                self.policy_operation_biz.delete_by_ids(system_id, self._subject, [p.policy_id for p in policies])

            # 删除临时权限
            temporary_policies = self.policy_query_biz.list_temporary_by_subject(system_id, self._subject)
            if temporary_policies:
                self.policy_operation_biz.delete_temporary_policies_by_ids(
                    system_id, self._subject, [p.policy_id for p in temporary_policies]
                )

    def _clean_subject_group(self, before_at: Optional[int] = None):
        """
        清理人员模版
        """
        query = SubjectTemplateRelation.objects.filter(subject_type=self._subject.type, subject_id=self._subject.id)
        if before_at:
            query = query.filter(created_time__lte=timestamp_to_local(before_at))

        template_ids = list(query.values_list("template_id", flat=True))

        for template_id in template_ids:
            self.subject_template_biz.delete_members(template_id, [self._subject])

    def _clean_group(self, before_at: Optional[int] = None):
        """
        清理用户组
        """

        # 查询所有的用户组id, 删除
        while True:
            _, groups = self.group_biz.list_paging_subject_group(self._subject, limit=1000)
            for group in groups:
                if before_at and group.created_time.timestamp() > before_at:
                    continue
                self.group_biz.remove_members(str(group.id), [self._subject])

            if len(groups) < 1000:
                break

    def _clean_role(self, before_at: Optional[int] = None):
        """
        清理角色
        """

        # 查询所有的角色, 按角色类型清理
        username = self._subject.id
        roles = self.role_biz.list_user_role(username)
        role_ids = [role.id for role in roles]
        if before_at:
            role_ids = list(
                RoleUser.objects.filter(
                    role_id__in=role_ids,
                    username=username,
                    created_time__lte=timestamp_to_local(before_at),
                ).values_list("role_id", flat=True)
            )

        roles = Role.objects.filter(id__in=role_ids)

        for role in roles:
            if role.type in (
                RoleType.GRADE_MANAGER.value,
                RoleType.SUBSET_MANAGER.value,
            ):
                self.role_with_perm_group_biz.delete_role_member(role, username)

            elif role.type == RoleType.SUPER_MANAGER.value:
                self.role_biz.delete_super_manager_member(username)

            elif role.type == RoleType.SYSTEM_MANAGER.value:
                members = self.role_biz.list_members_by_role_id(role.id)
                members.remove(username)
                self.role_biz.modify_system_manager_members(role_id=role.id, members=members)


@shared_task(ignore_result=True)
def user_permission_clean(username: str, before_at: int = None):
    """
    清理用户权限
    """
    UserPermissionCleaner(username).clean(before_at)


@shared_task(ignore_result=True)
def check_user_permission_clean_task():
    """
    检查用户权限清理任务
    """
    hour_before = timezone.now() - timedelta(hours=1)

    qs = UserPermissionCleanupRecord.objects.filter(
        created_time__lt=hour_before, retry_count__lte=MAX_USER_PERMISSION_CLEAN_RETRY_COUNT
    ).filter(~Q(status=UserPermissionCleanupRecordStatusEnum.SUCCEED.value))

    qs.update(status=UserPermissionCleanupRecordStatusEnum.CREATED.value, retry_count=F("retry_count") + 1)  # 重置status

    for r in qs:
        user_permission_clean(r.username)


@shared_task(ignore_result=True)
def clean_user_permission_clean_record():
    # 删除3天之前已完成的记录
    day_before = timezone.now() - timedelta(days=30)
    UserPermissionCleanupRecord.objects.filter(
        created_time__lt=day_before, status=UserPermissionCleanupRecordStatusEnum.SUCCEED.value
    ).delete()
