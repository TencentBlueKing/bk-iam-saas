# -*- coding: utf-8 -*-
from typing import List

from django.utils.translation import gettext as _
from pydantic.tools import parse_obj_as

from backend.common.cache import Cache, CacheEnum, CacheKeyPrefixEnum
from backend.common.error_codes import error_codes
from backend.util.uuid import gen_uuid

from .policy import PolicyBean, PolicyBeanList


class ApplicationPolicyListCache:
    """接入系统操作申请缓存：用于是临时缓存无权限跳转申请内容"""

    timeout = 10 * 60  # 十分钟

    def __init__(self):
        self.cache = Cache(CacheEnum.REDIS.value, CacheKeyPrefixEnum.UNAUTHORIZED_JUMP_APPLICATION.value)

    def get(self, cache_id: str) -> PolicyBeanList:
        """获取缓存里申请的策略"""
        data = self.cache.get(cache_id)
        if data is None:
            raise error_codes.INVALID_ARGS.format(_("该申请链接已失效，请重新发起申请。"))

        system_id, policies = data["system_id"], data["policies"]

        return PolicyBeanList(system_id=system_id, policies=parse_obj_as(List[PolicyBean], policies))

    def set(self, policy_list: PolicyBeanList) -> str:
        """缓存申请的策略"""
        # 生成唯一的缓存ID
        cache_id = gen_uuid()
        # 转为Dict进行缓存
        data = {"system_id": policy_list.system_id, "policies": [p.dict() for p in policy_list.policies]}
        # 设置缓存
        self.cache.set(cache_id, data, timeout=self.timeout)

        return cache_id
