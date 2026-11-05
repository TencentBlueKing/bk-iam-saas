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

from backend.api.admin.serializers import (
    AdminSubjectGroupCleanupSLZ,
    AdminSubjectPolicyCleanupSLZ,
    AdminSubjectPolicyQuerySLZ,
)


class TestAdminSubjectPolicyQuerySLZ:
    def test_valid(self):
        slz = AdminSubjectPolicyQuerySLZ(data={"system_id": "bk_test"})
        assert slz.is_valid()
        assert "action_id" not in slz.validated_data

    def test_valid_with_action_id(self):
        slz = AdminSubjectPolicyQuerySLZ(data={"system_id": "bk_test", "action_id": "view"})
        assert slz.is_valid()
        assert slz.validated_data["action_id"] == "view"

    @pytest.mark.parametrize("data", [{"action_id": "view"}, {"system_id": "bk_test", "action_id": ""}])
    def test_invalid(self, data):
        slz = AdminSubjectPolicyQuerySLZ(data=data)
        assert not slz.is_valid()


class TestAdminSubjectGroupCleanupSLZ:
    def test_dedup(self):
        slz = AdminSubjectGroupCleanupSLZ(data={"username": "tester", "group_ids": [2, 1, 2]})
        assert slz.is_valid()
        assert slz.validated_data["group_ids"] == [2, 1]

    @pytest.mark.parametrize("group_ids", [[], [0], list(range(1, 102)), [1] * 101])
    def test_invalid(self, group_ids):
        slz = AdminSubjectGroupCleanupSLZ(data={"username": "tester", "group_ids": group_ids})
        assert not slz.is_valid()


class TestAdminSubjectPolicyCleanupSLZ:
    @pytest.mark.parametrize("extra", [{"action_id": "view"}, {"policy_ids": [1, 2]}])
    def test_valid(self, extra):
        slz = AdminSubjectPolicyCleanupSLZ(data={"username": "tester", "system_id": "bk_test", **extra})
        assert slz.is_valid()

    @pytest.mark.parametrize(
        "extra",
        [{}, {"action_id": "view", "policy_ids": [1]}, {"policy_ids": []}, {"policy_ids": list(range(1, 202))}],
    )
    def test_invalid(self, extra):
        slz = AdminSubjectPolicyCleanupSLZ(data={"username": "tester", "system_id": "bk_test", **extra})
        assert not slz.is_valid()
