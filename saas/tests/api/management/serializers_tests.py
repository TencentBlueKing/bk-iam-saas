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
from rest_framework.serializers import ValidationError

from backend.api.management.serializers import ManagementRoleScopeAuthorizationSLZ
from tests.test_util.contextlib import nullcontext as does_not_raise


@pytest.mark.parametrize(
    "resources, expected",
    [
        # 与资源实例无关
        ([], does_not_raise()),
        # 关联一个资源类型，且实例为无限制
        ([{"system": "bk_test", "type": "test_resource_type", "paths": []}], pytest.raises(ValidationError)),
        # 关联一个资源类型，且有具体实例
        (
            [
                {
                    "system": "bk_test",
                    "type": "test_resource_type",
                    "paths": [[{"system": "bk_test", "type": "test_resource_type", "id": "test", "name": "test"}]],
                }
            ],
            does_not_raise(),
        ),
        # 关联多个资源实例，且所有都是无限制
        (
            [
                {"system": "bk_test", "type": "test_resource_type1", "paths": []},
                {"system": "bk_test", "type": "test_resource_type2", "paths": []},
            ],
            pytest.raises(ValidationError),
        ),
        # 关联多个资源类型，有一个不为无限制
        (
            [
                {
                    "system": "bk_test",
                    "type": "test_resource_type1",
                    "paths": [[{"system": "bk_test", "type": "test_resource_type1", "id": "test", "name": "test"}]],
                },
                {"system": "bk_test", "type": "test_resource_type2", "paths": []},
            ],
            does_not_raise(),
        ),
        # 关联多个资源类型，每个都不是无限制
        (
            [
                {
                    "system": "bk_test",
                    "type": "test_resource_type1",
                    "paths": [[{"system": "bk_test", "type": "test_resource_type1", "id": "test", "name": "test"}]],
                },
                {
                    "system": "bk_test",
                    "type": "test_resource_type2",
                    "paths": [[{"system": "bk_test", "type": "test_resource_type2", "id": "test", "name": "test"}]],
                },
            ],
            does_not_raise(),
        ),
    ],
)
def test_management_role_scope_authorization_slz_resources(resources, expected):
    data = {"system": "bk_test", "actions": [{"id": "test_action"}], "resources": resources}
    with expected:
        ManagementRoleScopeAuthorizationSLZ(data=data).is_valid(raise_exception=True)
