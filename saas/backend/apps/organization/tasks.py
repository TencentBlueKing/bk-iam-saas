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
import traceback

from celery import task
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone

from backend.apps.organization.models import SyncRecord, SyncErrorRecord
from backend.biz.org_sync.department import DBDepartmentSyncExactInfo, DBDepartmentSyncService
from backend.biz.org_sync.department_member import DBDepartmentMemberSyncService
from backend.biz.org_sync.iam_department import IAMBackendDepartmentSyncService
from backend.biz.org_sync.iam_user import IAMBackendUserSyncService
from backend.biz.org_sync.iam_user_department import IAMBackendUserDepartmentSyncService
from backend.biz.org_sync.syncer import Syncer
from backend.biz.org_sync.user import DBUserSyncService
from backend.biz.org_sync.user_leader import DBUserLeaderSyncService

from .constants import SYNC_TASK_DEFAULT_EXECUTOR, SyncTaskLockKey, SyncTaskStatus, SyncType

logger = logging.getLogger("celery")


@task(ignore_result=True)
def sync_organization(executor: str = SYNC_TASK_DEFAULT_EXECUTOR):
    try:
        # 分布式锁，避免同一时间该任务多个worker执行
        with cache.lock(SyncTaskLockKey.Full.value, timeout=10):  # type: ignore[attr-defined]
            # Note: 虽然拿到锁了，但是还是得确定没有正在运行的任务才可以（因为10秒后锁自动释放了）
            if SyncRecord.objects.filter(type=SyncType.Full.value, status=SyncTaskStatus.Running.value).exists():
                return
            # 添加执行记录
            record = SyncRecord.objects.create(
                executor=executor, type=SyncType.Full.value, status=SyncTaskStatus.Running.value
            )
            record_id = record.id
            create_time = record.created_time

    except Exception:  # pylint: disable=broad-except
        traceback_msg = traceback.format_exc()
        exception_msg = "sync_organization cache lock error"
        logger.exception(exception_msg)
        # 获取分布式锁失败时，需要创建一条失败记录
        record = SyncRecord.objects.create(executor=executor, type=SyncType.Full.value,
                                           status=SyncTaskStatus.Failed.value)
        SyncErrorRecord.objects.create(sync_record_id=record.id,
                                       error_msg=f"exception_msg:{exception_msg}-traceback_msg:{traceback_msg}")
        return
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

        SyncRecord.objects.filter(id=record_id).update(status=SyncTaskStatus.Succeed.value, updated_time=timezone.now(),
                                                       total_time=timezone.now()-create_time)

    except Exception:  # pylint: disable=broad-except
        exception_msg = "sync_organization error"
        traceback_msg = traceback.format_exc()
        logger.exception(exception_msg)
        SyncRecord.objects.filter(id=record_id).update(status=SyncTaskStatus.Failed.value, updated_time=timezone.now(),
                                                       total_time=timezone.now()-create_time)
        SyncErrorRecord.objects.create(sync_record_id=record.id,
                                       error_msg=f"exception_msg:{exception_msg}-traceback_msg:{traceback_msg}")


@task(ignore_result=True)
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
