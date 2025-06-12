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
from django.urls import reverse

pytestmark = pytest.mark.django_db


class TestSystemViewSet:
    def test_list_for_staff(self, api_client, mock_system_service):
        url = reverse("system.list_system")
        response = api_client.get(url)
        assert len(response.data) == 3

    def test_list_for_system_manager(self, gen_api_client_for_system_manager, mock_system_service):
        url = reverse("system.list_system")
        api_client = gen_api_client_for_system_manager("bk_test")
        response = api_client.get(url)
        assert len(response.data) == 1
