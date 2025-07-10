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

from backend.biz.org_sync.util import convert_list_for_mptt


@pytest.fixture
def node_list():
    return [(1, None), (2, 1), (3, 1), (4, 2), (5, 2), (4, 1)]


class TestConvertListForMptt:
    def test_convert_list_for_mptt(self, node_list):
        result = convert_list_for_mptt(node_list)

        assert result == [1, 2, 3, 4, 4, 5]

    def test_convert_list_for_mptt_reverse(self, node_list):
        result = convert_list_for_mptt(node_list, True)

        assert result == [5, 4, 4, 3, 2, 1]
