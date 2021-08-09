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
from django.test import TestCase

from backend.common import time
from backend.common.time import PERMANENT_SECONDS, generate_default_expired_at


class GenerateDefaultExpiredAtTests(TestCase):
    """
    测试generate_default_expired_at方法
    """

    def test_equal_permanent(self):
        """等于永久"""
        # 默认有效期是永久
        expired_at = generate_default_expired_at()
        self.assertEqual(expired_at, PERMANENT_SECONDS)

    def test_less_than_permanent(self):
        """小于永久"""
        # 24小时
        time.DEFAULT_EXPIRED_DURATION = 60 * 60 * 24
        expired_at = generate_default_expired_at()
        self.assertLess(expired_at, PERMANENT_SECONDS)

    def test_greater_than_permanent(self):
        """大于永久"""
        time.DEFAULT_EXPIRED_DURATION = 60 * 60 * 24 + PERMANENT_SECONDS
        expired_at = generate_default_expired_at()
        self.assertEqual(expired_at, PERMANENT_SECONDS)

    def tearDown(self):
        time.DEFAULT_EXPIRED_DURATION = PERMANENT_SECONDS
