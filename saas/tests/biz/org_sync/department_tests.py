"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-权限中心(BlueKing-IAM) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from collections import defaultdict

import pytest

from backend.apps.organization.models import Department, DepartmentMember
from backend.biz.org_sync.department import DBDepartmentSyncExactInfo


@pytest.fixture
def department_list():
    return [
        Department(id=1, parent_id=None),
        Department(id=2, parent_id=1),
        Department(id=3, parent_id=1),
        Department(id=4, parent_id=2),
        Department(id=5, parent_id=2),
        Department(id=4, parent_id=1),
    ]


@pytest.fixture
def department_members():
    return [
        DepartmentMember(department_id=1, user_id="admin"),
        DepartmentMember(department_id=1, user_id="admin1"),
        DepartmentMember(department_id=2, user_id="admin"),
        DepartmentMember(department_id=3, user_id="admin"),
        DepartmentMember(department_id=4, user_id="admin"),
        DepartmentMember(department_id=5, user_id="admin"),
    ]


class TestDBDepartmentSyncExactInfo:
    def test_calculate_children(self, department_list):
        root, children_map = DBDepartmentSyncExactInfo._calculate_children(None, department_list)
        assert root == {1}
        assert children_map == {1: [2, 3, 4], 2: [4, 5]}

    def test_calculate_ancestors(self, department_list):
        children_map = defaultdict(list)
        children_map.update({1: [2, 3, 4], 2: [4, 5]})

        ancestors_map = DBDepartmentSyncExactInfo._calculate_ancestors(None, department_list, {1}, children_map)
        assert ancestors_map == {1: [], 2: [1], 3: [1], 4: [1, 2], 5: [1, 2]}

    def test_calculate_member_count(self, department_members):
        member_count_map = DBDepartmentSyncExactInfo._calculate_member_count(None, department_members)
        assert member_count_map == {1: 2, 2: 1, 3: 1, 4: 1, 5: 1}

    def test_calculate_recursive_member_count(self, department_members):
        ancestors_map = defaultdict(list)
        ancestors_map.update({1: [], 2: [1], 3: [1], 4: [1, 2], 5: [1, 2]})

        recursive_member_count_map = DBDepartmentSyncExactInfo._calculate_recursive_member_count(
            None, department_members, ancestors_map
        )
        assert recursive_member_count_map == {1: 2, 2: 1, 3: 1, 4: 1, 5: 1}
