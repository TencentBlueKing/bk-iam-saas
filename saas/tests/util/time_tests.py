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
import pytest

from backend.util.time import utc_string_to_timestamp


@pytest.mark.parametrize(
    "utc_string, expected",
    [
        ("2025-01-07T08:41:18Z", 1736239278),
        ("2025-01-07T09:03:44Z", 1736240624),
        ("2025-01-02T10:00:15Z", 1735812015),
        ("2025-01-08T03:42:02Z", 1736307722),
    ],
)
def test_utc_string_to_timestamp(utc_string: str, expected: int):
    assert utc_string_to_timestamp(utc_string) == expected
