# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import pytest
from django.test.utils import override_settings

from backend.component.util import remove_notification_exemption_user


@pytest.mark.parametrize(
    "usernames, expected",
    [
        # Case 1: List without any exempt users
        (["user1", "user2"], ["user1", "user2"]),
        # Case 2: List with some exempt users
        (["exempt_user1", "user1", "exempt_user2", "user2"], ["user1", "user2"]),
        # Case 3: List with only exempt users
        (["exempt_user1", "exempt_user2"], []),
        # Case 4: List with mixed cases and spaces
        (["Exempt_User1", " user1 ", "ExEmPt_UsEr2", " user2 ", " exempt_user3 "], [" user1 ", " user2 "]),
        # Case 5: Empty list
        ([], []),
    ],
)
def test_remove_notification_exemption_user(usernames, expected):
    with override_settings(BK_NOTIFICATION_EXEMPTION_USERS=["exempt_user1", "exempt_user2", "exempt_user3 "]):
        result = remove_notification_exemption_user(usernames)
        assert result == expected
