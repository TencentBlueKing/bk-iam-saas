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
from django.core.cache import caches

from .cache import CacheEnum, CacheKeyPrefixEnum


class LockTypeEnum(LowerStrEnum):
    PERMISSION_HANDOVER = auto()  # 权限交接
    ORGANIZATION_SYNC = auto()  # 组织同步
    POLICY_ALETER = auto()  # 权限变更
    LONG_TASK_CREATE = auto()  # 长时任务创建


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
        self._lock = caches[CacheEnum.REDIS.value].lock(key, timeout=timeout)
        self._blocking = blocking

    def _make_key(self, type_: str, suffix: Any) -> str:
        """
        生成key
        """
        key = f"{CacheKeyPrefixEnum.LOCK.value}:{type_}"
        if suffix is not None:
            key += f":{suffix}"
        return key

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


def gen_policy_alert_lock(key: str) -> RedisLock:
    return RedisLock(LockTypeEnum.POLICY_ALETER.value, suffix=key, timeout=10)


def gen_long_task_create_lock(key: str) -> RedisLock:
    return RedisLock(LockTypeEnum.LONG_TASK_CREATE.value, suffix=key, timeout=10)
