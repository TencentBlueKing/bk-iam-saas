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

from unittest import mock

import pytest

from backend.service.models import System


def _mock_system_service():
    # 由于RoleListQuery调用SystemService 是在类属性声明时就初始化了，那么文件加载时就固定了，Mock不到了
    # 所以不能通过mock底层服务SystemService类
    # 只能直接Mock掉RoleListQuery类的system_svc属性
    with mock.patch("backend.biz.role.RoleListQuery.system_svc") as mocked_service:
        mocked_service.list.return_value = [
            System(id="bk_test", name="bk_test", name_en="bk_test", description="", description_en=""),
            System(id="bk_test1", name="bk_test1", name_en="bk_test1", description="", description_en=""),
            System(id="bk_test2", name="bk_test2", name_en="bk_test2", description="", description_en=""),
        ]
        yield mocked_service


mock_system_service = pytest.fixture(_mock_system_service)
