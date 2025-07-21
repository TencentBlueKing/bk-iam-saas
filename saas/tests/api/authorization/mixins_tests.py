# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云 - 权限中心 (BlueKing-IAM) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import mock
import pytest
from django.conf import settings
from rest_framework import exceptions

from backend.api.authorization.constants import OperateEnum
from backend.api.authorization.mixins import AllowItem, AuthorizationAPIAllowListCheckMixin, AuthViewMixin
from backend.apps.role.models import Role
from backend.biz.policy import PolicyBean, PolicyBeanList
from backend.service.models.subject import Subject

pytestmark = pytest.mark.django_db


@pytest.fixture
def mock_tenant_id():
    with mock.patch("backend.mixins.tenant.TenantMixin.tenant_id", return_value=settings.BK_APP_TENANT_ID):
        yield


class TestAllowItem:
    @pytest.mark.parametrize(
        "object_id,match_object_id,expected_result",
        [
            ("*", "test", True),
            ("test", "test", True),
            ("test", "test1", False),
            ("starts_with:test", "test1", True),
            ("starts_with:test", "tes1t", False),
            ("abc:test", "test", False),
        ],
    )
    def test_allow_item(self, object_id, match_object_id, expected_result):
        result = AllowItem(object_id).match(match_object_id)

        assert result == expected_result


class TestAuthorizationAPIAllowListCheckMixin:
    def test_verify_api(self):
        mixin = AuthorizationAPIAllowListCheckMixin()
        mixin._list_system_allow_list = mock.Mock(return_value=[AllowItem("test")])

        mixin.verify_api("system", "test", "authorization_instance")
        with pytest.raises(exceptions.PermissionDenied):
            mixin.verify_api("system", "test1", "authorization_instance")

    def test_verify_api_by_object_ids(self):
        mixin = AuthorizationAPIAllowListCheckMixin()
        mixin._list_system_allow_list = mock.Mock(return_value=[AllowItem("test"), AllowItem("test1")])

        mixin.verify_api_by_object_ids("system", ["test", "test1"], "authorization_instance")
        with pytest.raises(exceptions.PermissionDenied):
            mixin.verify_api_by_object_ids("system", ["test", "test1", "test2"], "authorization_instance")


class TestAuthViewMixin:
    def test_grant_or_revoke_admin(self, mock_tenant_id):
        mixin = AuthViewMixin()
        result = mixin.grant_or_revoke(
            OperateEnum.GRANT.value,
            Subject(type="user", id="admin"),
            PolicyBeanList(settings.BK_APP_TENANT_ID, "system", []),
        )
        assert result == []

    def test_grant_or_revoke_user(self, mock_tenant_id):
        with (
            mock.patch("backend.biz.policy.PolicyOperationBiz.alter", return_value=None),
            mock.patch("backend.biz.policy.PolicyQueryBiz.list_by_subject", return_value=[]),
        ):
            mixin = AuthViewMixin()
            mixin._check_or_sync_user = mock.Mock(return_value=None)

            result = mixin.grant_or_revoke(
                OperateEnum.GRANT.value,
                Subject(type="user", id="test"),
                PolicyBeanList(settings.BK_APP_TENANT_ID, "system", []),
            )
            assert result == []

    def test_grant_or_revoke_group(self, mock_tenant_id):
        with (
            mock.patch("backend.biz.policy.PolicyOperationBiz.alter", return_value=None),
            mock.patch("backend.biz.policy.PolicyQueryBiz.list_by_subject", return_value=[]),
        ):
            mixin = AuthViewMixin()
            mixin._check_scope = mock.Mock(return_value=None)

            result = mixin.grant_or_revoke(
                OperateEnum.GRANT.value,
                Subject(type="group", id="1"),
                PolicyBeanList(settings.BK_APP_TENANT_ID, "system", []),
            )
            assert result == []

    def test_grant_or_revoke_user_revoke(self, mock_tenant_id):
        with (
            mock.patch("backend.biz.policy.PolicyOperationBiz.revoke", return_value=[]),
        ):
            mixin = AuthViewMixin()
            mixin._check_or_sync_user = mock.Mock(return_value=None)
            result = mixin.grant_or_revoke(
                OperateEnum.REVOKE.value,
                Subject(type="user", id="test"),
                PolicyBeanList(settings.BK_APP_TENANT_ID, "system", []),
            )
            assert result == []

    def test_check_scope_assert_group(self, mock_tenant_id):
        mixin = AuthViewMixin()
        with pytest.raises(AssertionError):
            mixin._check_scope(
                Subject(type="user", id="test"), PolicyBeanList(settings.BK_APP_TENANT_ID, "system", [])
            )

    def test_check_scope(self, mock_tenant_id):
        with (
            mock.patch("backend.biz.role.RoleBiz.get_role_by_group_id", return_value=Role()),
            mock.patch("backend.trans.role.RoleAuthScopeTrans.from_policy_list", return_value=None),
            mock.patch("backend.biz.role.RoleBiz.incr_update_auth_scope", return_value=None),
        ):
            mixin = AuthViewMixin()
            mixin._check_scope(Subject(type="group", id="1"), PolicyBeanList(settings.BK_APP_TENANT_ID, "system", []))

    def test_policy_response(self):
        mixin = AuthViewMixin()
        resp = mixin.policy_response(PolicyBean(id="create_host", related_resource_types=[]))
        assert resp.data == {"policy_id": 0, "statistics": {"instance_count": 0}}

    def test_batch_policy_response(self):
        mixin = AuthViewMixin()
        resp = mixin.batch_policy_response(
            [
                PolicyBean(id="create_host", related_resource_types=[]),
                PolicyBean(id="delete_host", related_resource_types=[]),
            ]
        )
        assert resp.data == [
            {
                "action": {"id": "create_host"},
                "policy_id": 0,
                "statistics": {"instance_count": 0},
            },
            {
                "action": {"id": "delete_host"},
                "policy_id": 0,
                "statistics": {"instance_count": 0},
            },
        ]
