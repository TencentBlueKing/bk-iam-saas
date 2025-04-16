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
from mock import Mock, patch

from backend.apps.policy.models import Policy as PolicyModel
from backend.apps.template.models import PermTemplatePolicyAuthorized
from backend.common.time import PERMANENT_SECONDS
from backend.service.constants import AbacPolicyChangeType, AuthType, SubjectType
from backend.service.models import (
    AbacPolicyChangeContent,
    PathNode,
    RbacPolicyChangeContent,
    Subject,
    UniversalPolicyChangedContent,
)
from backend.service.policy.backend import AuthTypeStatistics, BackendPolicyOperationService


class TestAuthTypeStatistics:
    @pytest.mark.parametrize(
        "auth_types,expected_result",
        [
            (["rbac", "abac", "abac", "rbac"], {"abac": 2, "rbac": 2}),
            (["rbac", "abac", "abac", "rbac", "all"], {"abac": 2, "rbac": 2, "all": 1}),
            (["rbac"], {"rbac": 1}),
        ],
    )
    def test_accumulate(self, auth_types, expected_result):
        statistics = AuthTypeStatistics()
        statistics.accumulate(auth_types)

        assert statistics.abac_count == expected_result.get("abac", 0)
        assert statistics.rbac_count == expected_result.get("rbac", 0)
        assert statistics.all_count == expected_result.get("all", 0)

    @pytest.mark.parametrize(
        "auth_types,excepted",
        [
            (["rbac", "abac", "abac", "rbac"], True),
            (["rbac", "abac", "abac", "rbac", "all"], True),
            (["all"], True),
            (["rbac", "rbac"], False),
            (["abac", "abac", "abac"], False),
        ],
    )
    def test_is_all_auth_type(self, auth_types, excepted):
        statistics = AuthTypeStatistics()
        statistics.accumulate(auth_types)

        assert statistics.is_all_auth_type() == excepted

    @pytest.mark.parametrize(
        "auth_types,excepted",
        [
            (["rbac", "abac", "abac", "rbac"], "all"),
            (["rbac", "abac", "abac", "rbac", "all"], "all"),
            (["all"], "all"),
            (["rbac", "rbac"], "rbac"),
            (["abac", "abac", "abac"], "abac"),
        ],
    )
    def test_auth_type(self, auth_types, excepted):
        statistics = AuthTypeStatistics()
        statistics.accumulate(auth_types)

        assert statistics.auth_type() == excepted


class TestBackendPolicyOperationService:
    @pytest.mark.parametrize(
        "changed_policies,excepted",
        [
            # empty
            (
                # changed_policies
                [
                    UniversalPolicyChangedContent(
                        action_id="a",
                    )
                ],
                # excepted
                [],
            ),
            # only create action
            (
                # changed_policies
                [
                    UniversalPolicyChangedContent(
                        action_id="a",
                        rbac=RbacPolicyChangeContent(
                            created=[PathNode(id="r_id", name="r_name", system_id="s_id", type="rt_id")],
                        ),
                    )
                ],
                # excepted
                [
                    {
                        "resource": {"system_id": "s_id", "type": "rt_id", "id": "r_id"},
                        "created_action_ids": ["a"],
                        "deleted_action_ids": [],
                    }
                ],
            ),
            # only delete action
            (
                # changed_policies
                [
                    UniversalPolicyChangedContent(
                        action_id="a",
                        rbac=RbacPolicyChangeContent(
                            deleted=[PathNode(id="r_id", name="r_name", system_id="s_id", type="rt_id")],
                        ),
                    )
                ],
                # excepted
                [
                    {
                        "resource": {"system_id": "s_id", "type": "rt_id", "id": "r_id"},
                        "created_action_ids": [],
                        "deleted_action_ids": ["a"],
                    }
                ],
            ),
            # both create and delete action
            (
                # changed_policies
                [
                    UniversalPolicyChangedContent(
                        action_id="a",
                        rbac=RbacPolicyChangeContent(
                            created=[PathNode(id="r_id", name="r_name", system_id="s_id", type="rt_id")],
                            deleted=[PathNode(id="r_id", name="r_name", system_id="s_id", type="rt_id")],
                        ),
                    )
                ],
                # excepted
                [
                    {
                        "resource": {"system_id": "s_id", "type": "rt_id", "id": "r_id"},
                        "created_action_ids": ["a"],
                        "deleted_action_ids": ["a"],
                    }
                ],
            ),
            # mult resource
            (
                # changed_policies
                [
                    UniversalPolicyChangedContent(
                        action_id="a1",
                        rbac=RbacPolicyChangeContent(
                            created=[PathNode(id="r_id1", name="r_name", system_id="s_id", type="rt_id")],
                            deleted=[PathNode(id="r_id2", name="r_name", system_id="s_id", type="rt_id")],
                        ),
                    ),
                    UniversalPolicyChangedContent(
                        action_id="a2",
                        rbac=RbacPolicyChangeContent(
                            created=[PathNode(id="r_id2", name="r_name", system_id="s_id", type="rt_id")],
                            deleted=[PathNode(id="r_id1", name="r_name", system_id="s_id", type="rt_id")],
                        ),
                    ),
                ],
                # excepted
                [
                    {
                        "resource": {"system_id": "s_id", "type": "rt_id", "id": "r_id1"},
                        "created_action_ids": ["a1"],
                        "deleted_action_ids": ["a2"],
                    },
                    {
                        "resource": {"system_id": "s_id", "type": "rt_id", "id": "r_id2"},
                        "created_action_ids": ["a2"],
                        "deleted_action_ids": ["a1"],
                    },
                ],
            ),
        ],
    )
    def test_generate_rbac_data(self, changed_policies, excepted):
        svc = BackendPolicyOperationService()
        resource_action_data = svc.generate_rbac_data(changed_policies)

        assert resource_action_data == excepted

    @pytest.mark.parametrize(
        "changed_policies,excepted",
        [
            # empty
            (
                # changed_policies
                [],
                # excepted
                ([], [], []),
            ),
            # create
            (
                # changed_policies
                [
                    UniversalPolicyChangedContent(
                        action_id="a",
                        abac=AbacPolicyChangeContent(
                            change_type=AbacPolicyChangeType.CREATED.value,
                            resource_expression="re",
                        ),
                    )
                ],
                # excepted
                (
                    [
                        {
                            "action_id": "a",
                            "resource_expression": "re",
                            "environment": "",
                            "expired_at": PERMANENT_SECONDS,
                        }
                    ],
                    [],
                    [],
                ),
            ),
            # update
            (
                # changed_policies
                [
                    UniversalPolicyChangedContent(
                        action_id="a",
                        abac=AbacPolicyChangeContent(
                            change_type=AbacPolicyChangeType.UPDATED.value,
                            id=1,
                            resource_expression="re",
                        ),
                    )
                ],
                # excepted
                (
                    [],
                    [
                        {
                            "id": 1,
                            "action_id": "a",
                            "resource_expression": "re",
                            "environment": "",
                            "expired_at": PERMANENT_SECONDS,
                        }
                    ],
                    [],
                ),
            ),
            # delete
            (
                # changed_policies
                [
                    UniversalPolicyChangedContent(
                        action_id="a",
                        abac=AbacPolicyChangeContent(
                            change_type=AbacPolicyChangeType.DELETED.value,
                            id=1,
                        ),
                    )
                ],
                # excepted
                (
                    [],
                    [],
                    [1],
                ),
            ),
            # all
            (
                # changed_policies
                [
                    UniversalPolicyChangedContent(
                        action_id="a",
                        abac=AbacPolicyChangeContent(
                            change_type=AbacPolicyChangeType.CREATED.value,
                            resource_expression="re",
                        ),
                    ),
                    UniversalPolicyChangedContent(
                        action_id="a",
                        abac=AbacPolicyChangeContent(
                            change_type=AbacPolicyChangeType.UPDATED.value,
                            id=1,
                            resource_expression="re",
                        ),
                    ),
                    UniversalPolicyChangedContent(
                        action_id="a",
                        abac=AbacPolicyChangeContent(
                            change_type=AbacPolicyChangeType.DELETED.value,
                            id=1,
                        ),
                    ),
                ],
                # excepted
                (
                    [
                        {
                            "action_id": "a",
                            "resource_expression": "re",
                            "environment": "",
                            "expired_at": PERMANENT_SECONDS,
                        }
                    ],
                    [
                        {
                            "id": 1,
                            "action_id": "a",
                            "resource_expression": "re",
                            "environment": "",
                            "expired_at": PERMANENT_SECONDS,
                        }
                    ],
                    [1],
                ),
            ),
        ],
    )
    def test_generate_abac_data(self, changed_policies, excepted):
        svc = BackendPolicyOperationService()
        resource_action_data = svc.generate_abac_data(changed_policies)

        assert resource_action_data == excepted

    @pytest.mark.parametrize(
        "changed_policy_auth_types,custom_policy_auth_types,template_policy_auth_types,excepted",
        [
            # params all
            (
                # changed_policy_auth_types
                {"test1": AuthType.ALL.value, "test2": AuthType.ALL.value},
                # custom_policy_auth_types
                None,
                # template_policy_auth_types
                None,
                # excepted
                AuthType.ALL.value,
            ),
            # custom policy all
            (
                # changed_policy_auth_types
                {"test1": AuthType.ABAC.value},
                # custom_policy_auth_types
                [{"action_id": "test3", "auth_type": AuthType.ALL.value}],
                # template_policy_auth_types
                None,
                # excepted
                AuthType.ALL.value,
            ),
            # template policy all
            (
                # changed_policy_auth_types
                {"test1": AuthType.ABAC.value},
                # custom_policy_auth_types
                [{"action_id": "test3", "auth_type": AuthType.ABAC.value}],
                # template_policy_auth_types
                [{"template_id": 1, "_auth_types": '{"test1": "all"}'}],
                # excepted
                AuthType.ALL.value,
            ),
            # abac
            (
                # changed_policy_auth_types
                {"test1": AuthType.ABAC.value},
                # custom_policy_auth_types
                [{"action_id": "test3", "auth_type": AuthType.ABAC.value}],
                # template_policy_auth_types
                [{"template_id": 1, "_auth_types": '{"test1": "abac"}'}],
                # excepted
                AuthType.ABAC.value,
            ),
        ],
    )
    def test_calculate_auth_type(
        self, changed_policy_auth_types, custom_policy_auth_types, template_policy_auth_types, excepted
    ):
        policy_qs = Mock(spec=PolicyModel.objects)
        policy_qs.filter.return_value = policy_qs
        policy_qs.values.return_value = custom_policy_auth_types

        template_qs = Mock(spec=PermTemplatePolicyAuthorized.objects)
        template_qs.filter.return_value = template_qs
        template_qs.values.return_value = template_policy_auth_types

        with (
            patch("backend.apps.policy.models.Policy.objects", policy_qs),
            patch("backend.apps.template.models.PermTemplatePolicyAuthorized.objects", template_qs),
        ):
            svc = BackendPolicyOperationService()
            auth_type = svc._calculate_auth_type(
                Subject(type=SubjectType.GROUP.value, id="1"), 0, "test", changed_policy_auth_types
            )
            assert auth_type == excepted

        if custom_policy_auth_types:
            policy_qs.values.assert_called()

        if template_policy_auth_types:
            template_qs.values.assert_called()

    def test_alter_backend_policies_error(self):
        svc = BackendPolicyOperationService()
        with pytest.raises(AssertionError):
            svc.alter_backend_policies(Subject(type=SubjectType.USER.value, id="1"), 0, "test", [])

    def test_alter_backend_policies_ok(self):
        svc = BackendPolicyOperationService()
        with (
            patch.object(svc, "_calculate_auth_type", return_value=AuthType.ABAC.value),
            patch("backend.component.iam.alter_group_policies_v2") as mock_alter_group_policies_v2,
        ):
            svc.alter_backend_policies(
                Subject(type=SubjectType.GROUP.value, id="1"),
                0,
                "test",
                [
                    UniversalPolicyChangedContent(
                        action_id="a",
                        abac=AbacPolicyChangeContent(
                            change_type=AbacPolicyChangeType.CREATED.value,
                            resource_expression="re",
                        ),
                    ),
                    UniversalPolicyChangedContent(
                        action_id="a",
                        abac=AbacPolicyChangeContent(
                            change_type=AbacPolicyChangeType.UPDATED.value,
                            id=1,
                            resource_expression="re",
                        ),
                    ),
                    UniversalPolicyChangedContent(
                        action_id="a",
                        abac=AbacPolicyChangeContent(
                            change_type=AbacPolicyChangeType.DELETED.value,
                            id=1,
                        ),
                    ),
                ],
            )

            mock_alter_group_policies_v2.assert_called()
