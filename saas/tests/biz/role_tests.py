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
from django.test import TestCase

from backend.apps.role.models import Role
from backend.biz.policy import InstanceBean
from backend.biz.role import ActionScopeDiffer, RoleListQuery, RoleScopeSystemActions
from backend.service.constants import ACTION_ALL, SYSTEM_ALL, RoleType


class TestInstanceDiff(TestCase):
    def test_instance(self):
        template_instances = [
            InstanceBean(
                type="",
                path=[
                    [
                        {"type": "biz", "id": "biz1"},
                        {"type": "set", "id": "set1"},
                        {"type": "module", "id": "module1"},
                        {"type": "host", "id": "host1"},
                    ]
                ],
            ),
            InstanceBean(type="", path=[[{"type": "biz", "id": "biz2"}, {"type": "set", "id": "set2"}]]),
        ]

        scope_instances = [
            InstanceBean(type="", path=[[{"type": "biz", "id": "biz1"}]]),
            InstanceBean(type="", path=[[{"type": "biz", "id": "biz2"}]]),
        ]

        self.assertTrue(ActionScopeDiffer(None, None)._diff_instances(template_instances, scope_instances))

    def test_false(self):
        template_instances = [
            InstanceBean(
                type="",
                path=[
                    [
                        {"type": "biz", "id": "biz1"},
                        {"type": "set", "id": "set1"},
                        {"type": "module", "id": "module1"},
                        {"type": "host", "id": "host1"},
                    ]
                ],
            ),
            InstanceBean(type="", path=[[{"type": "biz", "id": "biz3"}, {"type": "set", "id": "set2"}]]),
        ]

        scope_instances = [
            InstanceBean(type="", path=[[{"type": "biz", "id": "biz1"}]]),
            InstanceBean(type="", path=[[{"type": "biz", "id": "biz2"}]]),
        ]

        self.assertFalse(ActionScopeDiffer(None, None)._diff_instances(template_instances, scope_instances))


@pytest.fixture
def role_scope_system_action_system_all():
    return RoleScopeSystemActions(systems={SYSTEM_ALL: set()})


@pytest.fixture
def role_scope_system_action_action_all():
    return RoleScopeSystemActions(systems={"system": {ACTION_ALL}})


@pytest.fixture
def role_scope_system_action_normal():
    return RoleScopeSystemActions(systems={"system": {"action"}})


class TestRoleScopeSystemActions:
    def test_has_system(self, role_scope_system_action_system_all, role_scope_system_action_action_all):
        assert role_scope_system_action_system_all.has_system("system")

        assert role_scope_system_action_action_all.has_system("system")
        assert not role_scope_system_action_action_all.has_system("test")

    def test_is_all_action(
        self, role_scope_system_action_system_all, role_scope_system_action_action_all, role_scope_system_action_normal
    ):
        assert role_scope_system_action_system_all.is_all_action("system")

        assert role_scope_system_action_action_all.is_all_action("system")
        assert not role_scope_system_action_action_all.is_all_action("test")

        assert not role_scope_system_action_normal.is_all_action("system")

    def test_list_action_id(
        self, role_scope_system_action_system_all, role_scope_system_action_action_all, role_scope_system_action_normal
    ):
        assert role_scope_system_action_system_all.list_action_id("system") == []

        assert role_scope_system_action_action_all.list_action_id("system") == [ACTION_ALL]
        assert role_scope_system_action_action_all.list_action_id("test") == []

        assert role_scope_system_action_normal.list_action_id("system") == ["action"]


class TestRoleListQuery:
    def test_list_scope_action_id(self, role_scope_system_action_system_all, role_scope_system_action_normal):
        role = Role(type=RoleType.STAFF.value)
        q = RoleListQuery(role=role)
        assert q.list_scope_action_id("system") == [ACTION_ALL]

        role = Role(type=RoleType.GRADE_MANAGER.value)
        q = RoleListQuery(role=role)
        q.get_scope_system_actions = mock.Mock(return_value=role_scope_system_action_normal)
        assert q.list_scope_action_id("test") == []

        role = Role(type=RoleType.GRADE_MANAGER.value)
        q = RoleListQuery(role=role)
        q.get_scope_system_actions = mock.Mock(return_value=role_scope_system_action_system_all)
        assert q.list_scope_action_id("system") == [ACTION_ALL]

        role = Role(type=RoleType.GRADE_MANAGER.value)
        q = RoleListQuery(role=role)
        q.get_scope_system_actions = mock.Mock(return_value=role_scope_system_action_normal)
        assert q.list_scope_action_id("system") == ["action"]
