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
import logging
import traceback

from celery import shared_task
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from backend.apps.organization.models import SubjectToDelete, SyncErrorLog, SyncRecord
from backend.apps.role.models import RoleGroupMember, RoleScope, RoleUser, ScopeSubject
from backend.biz.org_sync.department import DBDepartmentSyncExactInfo, DBDepartmentSyncService
from backend.biz.org_sync.department_member import DBDepartmentMemberSyncService
from backend.biz.org_sync.iam_department import IAMBackendDepartmentSyncService
from backend.biz.org_sync.iam_user import IAMBackendUserSyncService
from backend.biz.org_sync.iam_user_department import IAMBackendUserDepartmentSyncService
from backend.biz.org_sync.syncer import Syncer
from backend.biz.org_sync.user import DBUserSyncService
from backend.biz.org_sync.user_leader import DBUserLeaderSyncService
from backend.common.lock import gen_organization_sync_lock
from backend.component import iam
from backend.service.constants import SubjectType
from backend.util.json import json_dumps

from .constants import SYNC_TASK_DEFAULT_EXECUTOR, SyncTaskStatus, SyncType

logger = logging.getLogger("celery")


@shared_task(ignore_result=True)
def sync_organization(executor: str = SYNC_TASK_DEFAULT_EXECUTOR) -> int:
    try:
        # 分布式锁，避免同一时间该任务多个worker执行
        with gen_organization_sync_lock():  # type: ignore[attr-defined]
            # Note: 虽然拿到锁了，但是还是得确定没有正在运行的任务才可以（因为10秒后锁自动释放了）
            record = SyncRecord.objects.filter(type=SyncType.Full.value, status=SyncTaskStatus.Running.value).first()
            if record is not None:
                return record.id
            # 添加执行记录
            record = SyncRecord.objects.create(
                executor=executor, type=SyncType.Full.value, status=SyncTaskStatus.Running.value
            )

    except Exception:  # pylint: disable=broad-except
        traceback_msg = traceback.format_exc()
        exception_msg = "sync_organization cache lock error"
        logger.exception(exception_msg)
        # 获取分布式锁失败时，需要创建一条失败记录
        record = SyncRecord.objects.create(
            executor=executor, type=SyncType.Full.value, status=SyncTaskStatus.Failed.value
        )
        SyncErrorLog.objects.create_error_log(record.id, exception_msg, traceback_msg)
        return record.id

    try:
        # 1. SaaS 从用户管理同步组织架构
        # 用户
        user_sync_service = DBUserSyncService()
        # 部门
        department_sync_service = DBDepartmentSyncService()
        # 部门与用户关系
        department_member_sync_service = DBDepartmentMemberSyncService()
        # 用户与Leader关系
        user_leader_service = DBUserLeaderSyncService()

        # 开始执行同步变更
        with transaction.atomic():
            services = [
                user_sync_service,
                department_sync_service,
                department_member_sync_service,
                user_leader_service,
            ]
            # 执行DB变更
            for service in services:
                service.sync_to_db()

            # 计算和同步部门的冗余数据
            DBDepartmentSyncExactInfo().sync_to_db()

        # 2. SaaS 将DB存储的组织架构同步给IAM后台
        iam_backend_user_sync_service = IAMBackendUserSyncService()
        iam_backend_department_sync_service = IAMBackendDepartmentSyncService()
        iam_backend_user_department_sync_service = IAMBackendUserDepartmentSyncService()
        iam_services = [
            iam_backend_user_sync_service,
            iam_backend_department_sync_service,
            iam_backend_user_department_sync_service,
        ]

        for iam_service in iam_services:
            iam_service.sync_to_iam_backend()

        sync_status, exception_msg, traceback_msg = SyncTaskStatus.Succeed.value, "", ""
    except Exception:  # pylint: disable=broad-except
        sync_status = SyncTaskStatus.Failed.value
        exception_msg = "sync_organization error"
        logger.exception(exception_msg)
        traceback_msg = traceback.format_exc()

    SyncRecord.objects.filter(id=record.id).update(status=sync_status, updated_time=timezone.now())
    if sync_status == SyncTaskStatus.Failed.value:
        SyncErrorLog.objects.create_error_log(record.id, exception_msg, traceback_msg)

    return record.id


@shared_task(ignore_result=True)
def sync_new_users():
    """
    定时同步新增用户
    """
    # 已有全量任务在执行，则无需再执行单用户同步
    if SyncRecord.objects.filter(type=SyncType.Full.value, status=SyncTaskStatus.Running.value).exists():
        return
    try:
        Syncer().sync_new_users()
    except Exception:  # pylint: disable=broad-except
        logger.exception("sync_new_users error")


@shared_task(ignore_result=True)
def clean_subject_to_delete():
    """
    定时清理被删除的用户
    """
    max_create_time = timezone.now() - timezone.timedelta(days=settings.SUBJECT_DELETE_DAYS)
    subjects = list(SubjectToDelete.objects.filter(created_time__lt=max_create_time))

    # TODO 校验用户管理是不是真的已经删除对应的subject

    # 分割对应的subject
    usernames = [one.subject_id for one in subjects if one.subject_type == SubjectType.USER.value]
    department_ids = [one.subject_id for one in subjects if one.subject_type == SubjectType.DEPARTMENT.value]

    # 清理用户相关数据
    if usernames:
        # 删除用户所属角色的成员
        RoleUser.objects.filter(username__in=usernames).delete()

        # 删除用户属于角色的授权范围
        role_scope_ids = list(
            ScopeSubject.objects.filter(subject_type=SubjectType.USER.value, subject_id__in=usernames).values_list(
                "role_scope_id", flat=True
            )
        )
        if role_scope_ids:
            scopes = list(RoleScope.objects.filter(id__in=role_scope_ids))
            for scope in scopes:
                scope_subjects = json.loads(scope.content)
                scope.content = json_dumps(
                    [
                        one
                        for one in scope_subjects
                        if one["type"] != SubjectType.USER.value or one["id"] not in usernames
                    ]
                )

            RoleScope.objects.bulk_update(scopes, ["content"], batch_size=100)
            ScopeSubject.objects.filter(subject_type=SubjectType.USER.value, subject_id__in=usernames).delete()

        # 删除冗余用户组关系表
        RoleGroupMember.objects.filter(subject_type=SubjectType.USER.value, subject_id__in=usernames).delete()

    # 清理部门相关数据
    if department_ids:
        # 删除用户属于角色的授权范围
        role_scope_ids = list(
            ScopeSubject.objects.filter(
                subject_type=SubjectType.DEPARTMENT.value, subject_id__in=department_ids
            ).values_list("role_scope_id", flat=True)
        )
        if role_scope_ids:
            scopes = list(RoleScope.objects.filter(id__in=role_scope_ids))
            for scope in scopes:
                scope_subjects = json.loads(scope.content)
                scope.content = json_dumps(
                    [
                        one
                        for one in scope_subjects
                        if one["type"] != SubjectType.DEPARTMENT.value or one["id"] not in department_ids
                    ]
                )

            RoleScope.objects.bulk_update(scopes, ["content"], batch_size=100)
            ScopeSubject.objects.filter(subject_type=SubjectType.USER.value, subject_id__in=usernames).delete()

        # 删除冗余用户组关系表
        RoleGroupMember.objects.filter(
            subject_type=SubjectType.DEPARTMENT.value, subject_id__in=department_ids
        ).delete()

    if subjects:
        # 删除待删除的subject
        SubjectToDelete.objects.filter(id__in=[one.id for one in subjects]).delete()

        # 清理后台subject数据
        deleted_subjects = [{"type": one.subject_type, "id": one.subject_id} for one in subjects]
        iam.delete_subjects_by_auto_paging(deleted_subjects)

    # TODO 处理事务
    # TODO 确认后台在subject template group相关数据被删除
