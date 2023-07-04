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
from typing import Any, Optional

from aenum import LowerStrEnum, auto

from .cache import Cache, CacheEnum, CacheKeyPrefixEnum


class LockTypeEnum(LowerStrEnum):
    PERMISSION_HANDOVER = auto()  # 权限交接
    ORGANIZATION_SYNC = auto()  # 组织同步
    POLICY_ALTER = auto()  # 权限变更
    LONG_TASK_CREATE = auto()  # 长时任务创建
    INIT_GRADE_MANAGER = auto()
    BCS_MANAGER = auto()

    GROUP_UPSERT = auto()
    TEMPLATE_UPSERT = auto()
    ROLE_UPSERT = auto()


class RedisLock:
    """
    基于redis实现的分布式锁
    """

    def __init__(self, type_: str, suffix: Any = None, timeout: Optional[int] = None, blocking=True) -> None:
        """
        type: 锁类型, LockTypeEnum 中的值
        suffix: 实现__str__方法的对象
        """
        key = self._make_key(type_, suffix)
        cache = Cache(CacheEnum.REDIS.value, CacheKeyPrefixEnum.LOCK.value)
        self._lock = cache.lock(key, timeout=timeout)
        self._blocking = blocking

    def _make_key(self, type_: str, suffix: Any) -> str:
        """
        生成key
        """
        return f"{type_}:{suffix}" if suffix is not None else type_

    def __enter__(self):
        assert self._blocking
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

    def acquire(self) -> bool:
        return self._lock.acquire(blocking=self._blocking)

    def release(self):
        self._lock.release()


def gen_permission_handover_lock(key: str) -> RedisLock:
    return RedisLock(LockTypeEnum.PERMISSION_HANDOVER.value, suffix=key, blocking=False)


def gen_organization_sync_lock() -> RedisLock:
    return RedisLock(LockTypeEnum.ORGANIZATION_SYNC.value, timeout=10)


def gen_policy_alter_lock(template_id: int, system_id: str, subject_type: str, subject_id: str) -> RedisLock:
    key = f"{template_id}:{system_id}:{subject_type}:{subject_id}"
    return RedisLock(LockTypeEnum.POLICY_ALTER.value, suffix=key, timeout=10)


def gen_long_task_create_lock(key: str) -> RedisLock:
    return RedisLock(LockTypeEnum.LONG_TASK_CREATE.value, suffix=key, timeout=10)


def gen_init_grade_manager_lock() -> RedisLock:
    return RedisLock(LockTypeEnum.INIT_GRADE_MANAGER.value, timeout=600)


def gen_group_upsert_lock(role_id: int) -> RedisLock:
    return RedisLock(LockTypeEnum.GROUP_UPSERT.value, suffix=str(role_id), timeout=10)


def gen_template_upsert_lock(role_id: int, name: str) -> RedisLock:
    key = f"{role_id}:{name}"
    return RedisLock(LockTypeEnum.TEMPLATE_UPSERT.value, suffix=key, timeout=10)


def gen_role_upsert_lock(name: str) -> RedisLock:
    return RedisLock(LockTypeEnum.TEMPLATE_UPSERT.value, suffix=name, timeout=10)


def gen_bcs_manager_lock() -> RedisLock:
    return RedisLock(LockTypeEnum.BCS_MANAGER.value, timeout=600)
