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

from backend.util.basic import chunked


class TestChunked(TestCase):
    def test_div_chunk_size(self):
        """能完整分块"""
        data = [1, 2, 3, 4, 5, 6]
        chunk_size = 3
        expected_result = [[1, 2, 3], [4, 5, 6]]
        self.assertEqual(chunked(data, chunk_size), expected_result)

    def test_not_div_chunk_size(self):
        """无法刚好完整分块"""
        data = [1, 2, 3, 4, 5, 6, 7, 8]
        chunk_size = 3
        expected_result = [[1, 2, 3], [4, 5, 6], [7, 8]]
        self.assertEqual(chunked(data, chunk_size), expected_result)

    def test_empty_data(self):
        """测试空数据是否正常分块"""
        data = []
        chunk_size = 3
        expected_result = []
        self.assertEqual(chunked(data, chunk_size), expected_result)
