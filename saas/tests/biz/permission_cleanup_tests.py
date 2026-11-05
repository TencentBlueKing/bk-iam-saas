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

from backend.apps.policy.models import Policy as PolicyModel
from backend.biz.permission_cleanup import SubjectGroupPermissionCleanupBiz, SubjectPolicyPermissionCleanupBiz
from backend.service.models import Subject

SUBJECT = Subject.from_username("tester")


class TestSubjectGroupPermissionCleanupBiz:
    @pytest.fixture()
    def biz(self):
        biz = SubjectGroupPermissionCleanupBiz()
        biz.group_biz = mock.Mock()
        return biz

    def test_partial_failed(self, biz):
        def remove_members(group_id, subjects):
            if group_id == "2":
                raise Exception("error")

        biz.group_biz.remove_members.side_effect = remove_members
        with mock.patch("backend.biz.permission_cleanup.log_group_event") as log_event:
            removed, failed = biz.clean(SUBJECT, [1, 2, 3])

        assert (removed, failed) == ([1, 3], [2])
        log_event.assert_called_once()
        assert log_event.call_args[0][2] == [1, 3]
        # 不覆盖 username, 事件 username 即为被清理的用户，保证审计接口可按用户查询
        assert "username" not in log_event.call_args[1]

    def test_all_failed_no_audit(self, biz):
        biz.group_biz.remove_members.side_effect = Exception("error")
        with mock.patch("backend.biz.permission_cleanup.log_group_event") as log_event:
            removed, failed = biz.clean(SUBJECT, [1])

        assert (removed, failed) == ([], [1])
        log_event.assert_not_called()

    def test_audit_failed(self, biz):
        with mock.patch("backend.biz.permission_cleanup.log_group_event", side_effect=Exception("error")):
            removed, failed = biz.clean(SUBJECT, [1])

        assert (removed, failed) == ([1], [])


@pytest.mark.django_db
class TestSubjectPolicyPermissionCleanupBiz:
    @pytest.fixture()
    def biz(self):
        biz = SubjectPolicyPermissionCleanupBiz()
        biz.svc = mock.Mock()
        with mock.patch("backend.biz.permission_cleanup.gen_policy_alter_lock"), mock.patch(
            "backend.biz.policy.PolicyBeanList.fill_empty_fields"
        ):
            yield biz

    @pytest.fixture()
    def policies(self):
        def create(system_id, subject_id, action_id):
            return PolicyModel.objects.create(
                subject_type="user", subject_id=subject_id, system_id=system_id, action_id=action_id, _resources="[]"
            )

        return [
            create("bk_test", SUBJECT.id, "view"),
            create("bk_test", SUBJECT.id, "edit"),
            create("bk_test", "other", "view"),
            create("bk_other", SUBJECT.id, "view"),
        ]

    def test_by_policy_ids(self, biz, policies):
        policy_ids = [policies[0].id, policies[2].id, policies[3].id, 99999]
        with mock.patch("backend.biz.permission_cleanup.log_user_event") as log_event:
            removed, failed = biz.clean(SUBJECT, "bk_test", policy_ids=policy_ids)

        assert (removed, failed) == ([policies[0].id], [])
        biz.svc.delete_by_ids.assert_called_once_with("bk_test", SUBJECT, [policies[0].id])
        assert [p["policy_id"] for p in log_event.call_args[0][3]] == [policies[0].id]

    def test_by_action_id(self, biz, policies):
        with mock.patch("backend.biz.permission_cleanup.log_user_event"):
            removed, failed = biz.clean(SUBJECT, "bk_test", action_id="edit")

        assert (removed, failed) == ([policies[1].id], [])

    def test_no_match(self, biz, policies):
        with mock.patch("backend.biz.permission_cleanup.log_user_event") as log_event:
            removed, failed = biz.clean(SUBJECT, "bk_test", action_id="delete")

        assert (removed, failed) == ([], [])
        biz.svc.delete_by_ids.assert_not_called()
        log_event.assert_not_called()

    def test_delete_failed(self, biz, policies):
        biz.svc.delete_by_ids.side_effect = Exception("error")
        with mock.patch("backend.biz.permission_cleanup.log_user_event") as log_event:
            removed, failed = biz.clean(SUBJECT, "bk_test", policy_ids=[policies[0].id, policies[1].id])

        assert (removed, failed) == ([], [policies[0].id, policies[1].id])
        log_event.assert_not_called()

    def test_audit_failed(self, biz, policies):
        with mock.patch("backend.biz.permission_cleanup.log_user_event", side_effect=Exception("error")):
            removed, failed = biz.clean(SUBJECT, "bk_test", action_id="view")

        assert (removed, failed) == ([policies[0].id], [])
