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
import json
from unittest import mock

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django_dynamic_fixture import G

from backend.apps.action.management.commands.cleanup_deleted_action import compute_to_remove
from backend.apps.policy.models import Policy as PolicyModel
from backend.apps.role.models import Role, RoleScope
from backend.apps.template.models import PermTemplate, PermTemplatePolicyAuthorized
from backend.component import iam
from backend.service.constants import ACTION_ALL, AuthType, RoleScopeType, RoleType, SubjectType
from backend.util.json import json_dumps

pytestmark = pytest.mark.django_db

SYSTEM_ID = "bk_test"
OTHER_SYSTEM_ID = "bk_other"
EXISTING_ACTION = "existing_action"
DELETED_ACTION = "deleted_action"


def mock_iam_action_ids(action_ids):
    """mock IAM 返回的 Action 列表；绕过 iam.list_action 的缓存，直接打桩被装饰的原始函数"""
    return mock.patch.object(
        iam.list_action, "__wrapped__", return_value=[{"id": action_id} for action_id in action_ids]
    )


def run_cleanup(**kwargs):
    options = {
        "system_id": SYSTEM_ID,
        "action_ids": "",
        "all_deleted": True,
        "dry_run": False,
        "yes": True,
        "clean_backend": False,
    }
    options.update(kwargs)
    return call_command("cleanup_deleted_action", **options)


def create_role_scope(content):
    role = G(Role, type=RoleType.GRADE_MANAGER.value, name="test_role", code="test_role")
    return G(
        RoleScope,
        role_id=role.id,
        type=RoleScopeType.AUTHORIZATION.value,
        content=json_dumps(content),
    )


class TestComputeToRemove:
    def test_auto_mode_keeps_action_all(self):
        assert compute_to_remove([ACTION_ALL, DELETED_ACTION], set(), {EXISTING_ACTION}) == {DELETED_ACTION}

    def test_explicit_mode_keeps_action_all(self):
        assert compute_to_remove([ACTION_ALL, DELETED_ACTION], {ACTION_ALL, DELETED_ACTION}, set()) == {DELETED_ACTION}


class TestCleanupDeletedActionCommand:
    def test_action_all_in_action_ids_rejected(self):
        with pytest.raises(CommandError, match="cannot be specified"):
            run_cleanup(action_ids=ACTION_ALL)

    def test_refuse_when_iam_returns_empty_action_list(self):
        policy = G(
            PolicyModel,
            subject_type=SubjectType.USER.value,
            subject_id="user",
            system_id=SYSTEM_ID,
            action_id=DELETED_ACTION,
            _resources=json_dumps([]),
        )

        with mock_iam_action_ids([]):
            with pytest.raises(CommandError, match="NO action"):
                run_cleanup()

        assert PolicyModel.objects.filter(id=policy.id).exists()

    def test_action_ids_still_exists_rejected(self):
        with mock_iam_action_ids([EXISTING_ACTION]):
            with pytest.raises(CommandError, match="still exist"):
                run_cleanup(action_ids=EXISTING_ACTION)

    def test_dry_run_does_not_write(self):
        role_scope = create_role_scope(
            [
                {
                    "system_id": SYSTEM_ID,
                    "actions": [
                        {"id": DELETED_ACTION, "related_resource_types": []},
                        {"id": EXISTING_ACTION, "related_resource_types": []},
                    ],
                }
            ]
        )
        original_scope_content = role_scope.content

        template = G(
            PermTemplate,
            name="test_template",
            system_id=SYSTEM_ID,
            _action_ids=json_dumps([DELETED_ACTION, EXISTING_ACTION]),
        )
        original_action_ids = template._action_ids

        policy = G(
            PolicyModel,
            subject_type=SubjectType.USER.value,
            subject_id="user",
            system_id=SYSTEM_ID,
            action_id=DELETED_ACTION,
            _resources=json_dumps([]),
        )

        with mock_iam_action_ids([EXISTING_ACTION]):
            run_cleanup(dry_run=True, yes=False)

        role_scope.refresh_from_db()
        template.refresh_from_db()
        assert role_scope.content == original_scope_content
        assert template._action_ids == original_action_ids
        assert PolicyModel.objects.filter(id=policy.id).exists()

    def test_role_scope_keeps_action_all_and_other_system(self):
        role_scope = create_role_scope(
            [
                {
                    "system_id": SYSTEM_ID,
                    "actions": [
                        {"id": ACTION_ALL, "related_resource_types": []},
                        {"id": DELETED_ACTION, "related_resource_types": []},
                        {"id": EXISTING_ACTION, "related_resource_types": []},
                    ],
                },
                {
                    "system_id": OTHER_SYSTEM_ID,
                    "actions": [
                        {"id": DELETED_ACTION, "related_resource_types": []},
                        {"id": ACTION_ALL, "related_resource_types": []},
                    ],
                },
            ]
        )

        with mock_iam_action_ids([EXISTING_ACTION]):
            run_cleanup()

        role_scope.refresh_from_db()
        scopes = {scope["system_id"]: scope for scope in json.loads(role_scope.content)}
        assert [a["id"] for a in scopes[SYSTEM_ID]["actions"]] == [ACTION_ALL, EXISTING_ACTION]
        # 其他系统的数据（包括已删除 action 与 "*"）不应被修改
        assert [a["id"] for a in scopes[OTHER_SYSTEM_ID]["actions"]] == [DELETED_ACTION, ACTION_ALL]

    def test_template_keeps_action_all(self):
        template = G(
            PermTemplate,
            name="test_template",
            system_id=SYSTEM_ID,
            _action_ids=json_dumps([ACTION_ALL, DELETED_ACTION, EXISTING_ACTION]),
        )

        with mock_iam_action_ids([EXISTING_ACTION]):
            run_cleanup()

        template.refresh_from_db()
        assert template.action_ids == [ACTION_ALL, EXISTING_ACTION]

    def test_template_policy_authorized_cleans_data_and_auth_types(self):
        authorized_policy = G(
            PermTemplatePolicyAuthorized,
            template_id=1,
            subject_type=SubjectType.USER.value,
            subject_id="user",
            system_id=SYSTEM_ID,
            _data=json_dumps(
                {
                    "actions": [
                        {"id": ACTION_ALL, "related_resource_types": []},
                        {"id": EXISTING_ACTION, "related_resource_types": []},
                        {"id": DELETED_ACTION, "related_resource_types": []},
                    ]
                }
            ),
            _auth_types=json_dumps(
                {
                    ACTION_ALL: AuthType.ABAC.value,
                    EXISTING_ACTION: AuthType.ABAC.value,
                    DELETED_ACTION: AuthType.ABAC.value,
                }
            ),
        )

        with mock_iam_action_ids([EXISTING_ACTION]):
            run_cleanup()

        authorized_policy.refresh_from_db()
        assert [a["id"] for a in authorized_policy.data["actions"]] == [ACTION_ALL, EXISTING_ACTION]
        assert authorized_policy.auth_types == {
            ACTION_ALL: AuthType.ABAC.value,
            EXISTING_ACTION: AuthType.ABAC.value,
        }
