# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云 - 权限中心 (BlueKing-IAM) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from unittest import mock

import pytest

from backend.service.models import System


@pytest.fixture
def mock_system_service():
    with mock.patch(
        "backend.service.system.SystemService.list",
        return_value=[
            System(id="bk_test", name="bk_test", name_en="bk_test", description="", description_en=""),
            System(id="bk_test1", name="bk_test1", name_en="bk_test1", description="", description_en=""),
            System(id="bk_test2", name="bk_test2", name_en="bk_test2", description="", description_en=""),
        ],
    ):
        yield
