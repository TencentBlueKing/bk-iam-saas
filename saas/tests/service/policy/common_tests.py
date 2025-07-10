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
from mock import patch

from backend.service.constants import AbacPolicyChangeType
from backend.service.models import AbacPolicyChangeContent, Policy, UniversalPolicyChangedContent
from backend.service.policy.common import UniversalPolicyChangedContentAnalyzer


class TestUniversalPolicyChangedContentAnalyzer:
    @pytest.mark.parametrize(
        "create_policies,mock_action_auth_types,expected_result",
        [
            # empty
            ([], {}, []),
            # ok
            (
                # create_policies
                [Policy(action_id="test", policy_id=1, expired_at=1, resource_groups=[])],
                # mock_action_auth_types
                {"test": "abac"},
                # expected_result
                [
                    UniversalPolicyChangedContent(
                        action_id="test",
                        auth_type="abac",
                        abac=AbacPolicyChangeContent(
                            change_type=AbacPolicyChangeType.CREATED.value,
                            resource_expression="[]",
                        ),
                        rbac=None,
                    )
                ],
            ),
        ],
    )
    def test_cal_for_created(self, create_policies, mock_action_auth_types, expected_result):
        analyzer = UniversalPolicyChangedContentAnalyzer()
        with patch.object(analyzer, "_query_action_auth_types", return_value=mock_action_auth_types):
            result = analyzer.cal_for_created("system_id", create_policies)
            assert result == expected_result

    @pytest.mark.parametrize(
        "delete_policies,mock_action_auth_types,expected_result",
        [
            # empty
            ([], {}, []),
            # ok
            (
                # delete_policies
                [Policy(action_id="test", policy_id=1, expired_at=1, resource_groups=[])],
                # mock_action_auth_types
                {"test": "abac"},
                # expected_result
                [
                    UniversalPolicyChangedContent(
                        action_id="test",
                        auth_type="none",
                        abac=AbacPolicyChangeContent(change_type=AbacPolicyChangeType.DELETED.value, id=0),
                        rbac=None,
                    )
                ],
            ),
        ],
    )
    def test_cal_cal_for_deleted(self, delete_policies, mock_action_auth_types, expected_result):
        analyzer = UniversalPolicyChangedContentAnalyzer()
        with patch.object(analyzer, "_query_action_auth_types", return_value=mock_action_auth_types):
            result = analyzer.cal_for_deleted("system_id", delete_policies)
            assert result == expected_result

    @pytest.mark.parametrize(
        "update_policies,mock_action_auth_types,expected_result",
        [
            # ok
            (
                # update_policies
                [
                    (
                        Policy(action_id="test", policy_id=1, expired_at=1, resource_groups=[]),
                        Policy(action_id="test", policy_id=1, expired_at=1, resource_groups=[]),
                    )
                ],
                # mock_action_auth_types
                {"test": "abac"},
                # expected_result
                [
                    UniversalPolicyChangedContent(
                        action_id="test",
                        auth_type="abac",
                        abac=AbacPolicyChangeContent(
                            change_type=AbacPolicyChangeType.UPDATED.value,
                            resource_expression="[]",
                        ),
                        rbac=None,
                    )
                ],
            ),
        ],
    )
    def test_cal_cal_for_updated(self, update_policies, mock_action_auth_types, expected_result):
        analyzer = UniversalPolicyChangedContentAnalyzer()
        with patch.object(analyzer, "_query_action_auth_types", return_value=mock_action_auth_types):
            result = analyzer.cal_for_updated("system_id", update_policies)
            assert result == expected_result
