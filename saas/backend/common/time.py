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

import datetime
import math
import time
from typing import Any, Dict

from django.db import connection
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext

# 分钟、小时、天的秒数
MINUTE_SECONDS = 60
HOUR_SECONDS = 60 * 60
DAY_SECONDS = 24 * 60 * 60

# 即将过期时长
EXPIRE_SOON_SECONDS = 15 * DAY_SECONDS  # 15天

# 永久：2100-01-01 00:00:00 的时间戳
# 默认过期时长(单位：秒)
PERMANENT_SECONDS = 4102444800
DEFAULT_EXPIRED_DURATION = 365 * DAY_SECONDS  # 1年

EXPIRED = _("已过期")
PERMANENT = _("永久")

WEEKDAYS = {
    0: "monday",
    1: "tuesday",
    2: "wednesday",
    3: "thursday",
    4: "friday",
    5: "saturday",
    6: "sunday",
}


def expired_at_display(expired_at: int, since_time: int = 0):
    """
    过期时间显示
    """
    if expired_at >= PERMANENT_SECONDS:
        return str(PERMANENT)

    if not since_time:
        since_time = int(time.time())

    total_second = expired_at - since_time

    if total_second < 0:
        return str(EXPIRED)

    return seconds_to_display_str(total_second)


def seconds_to_display_str(total_second: int) -> str:
    if total_second >= PERMANENT_SECONDS:
        return str(PERMANENT)

    if total_second < MINUTE_SECONDS:
        return ngettext("{total_second} second", "{total_second} seconds", total_second).format(
            total_second=total_second
        )

    if total_second < HOUR_SECONDS:
        total_minute = math.floor(total_second / MINUTE_SECONDS)
        return ngettext("{total_minute} minute", "{total_minute} minutes", total_minute).format(
            total_minute=total_minute
        )

    if total_second < DAY_SECONDS:
        total_hour = int(total_second / HOUR_SECONDS)
        total_minute = math.floor((total_second % HOUR_SECONDS) / MINUTE_SECONDS)
        if total_minute == 0:
            return ngettext("{total_hour} hour", "{total_hour} hours", total_hour).format(total_hour=total_hour)

        return "{} {}".format(
            ngettext("{total_hour} hour", "{total_hour} hours", total_hour).format(total_hour=total_hour),
            ngettext("{total_minute} minute", "{total_minute} minutes", total_minute).format(
                total_minute=total_minute
            ),
        )

    total_day = math.ceil(total_second / DAY_SECONDS)
    return ngettext("{total_day} day", "{total_day} days", total_day).format(total_day=total_day)


def get_period_start_end(days):
    """
    获取今天和结束时间日期的datetime
    """
    today = timezone.localtime()
    end_time = datetime.datetime.combine(today, datetime.time.max)
    start_time = datetime.datetime.combine(today, datetime.time.min) - datetime.timedelta(days=days)
    return start_time, end_time


def generate_default_expired_at():
    """
    获取默认授权的有效期
    """
    # 计算过期时间
    expired_at = int(time.time()) + DEFAULT_EXPIRED_DURATION

    # 如果时间戳大于PERMANENT_SECONDS则直接是永久即可
    if expired_at > PERMANENT_SECONDS:
        return PERMANENT_SECONDS

    return expired_at


def db_time():
    with connection.cursor() as cursor:
        cursor.execute("select current_timestamp")
        return cursor.fetchone()[0].timestamp()


def get_soon_expire_ts() -> int:
    return int(time.time()) + EXPIRE_SOON_SECONDS


def get_expired_at(days: int) -> int:
    return int(time.time()) + days * DAY_SECONDS


def need_run_expired_remind(config: Dict[str, Any]) -> bool:
    # 如果没有开启用户组过期提醒, 直接返回
    if not config["enable"]:
        return False

    # 判断当前是星期几, 如果不在发送周期内, 直接返回
    current_time = timezone.localtime(timezone.now())
    if WEEKDAYS[current_time.weekday()] not in config["send_days"]:
        return False

    # 如果不在调度时间内, 不发送提醒
    hour, minute = [int(i) for i in config["send_time"].split(":")]
    schedule_time = timezone.localtime(timezone.now()).replace(hour=hour, minute=minute, second=0, microsecond=0)

    # 执行时间小于调度时间不执行, 当前时间超过调度时间10分钟不执行
    return not (current_time < schedule_time or current_time - schedule_time > datetime.timedelta(minutes=5))
