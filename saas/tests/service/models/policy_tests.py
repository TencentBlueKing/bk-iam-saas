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
from copy import deepcopy

import pytest

from backend.service.constants import AbacPolicyChangeType, AuthType
from backend.service.models.instance_selection import InstanceSelection, PathResourceType
from backend.service.models.policy import (
    AbacPolicyChangeContent,
    Attribute,
    Condition,
    Environment,
    Instance,
    PathNode,
    PathNodeList,
    RbacPolicyChangeContent,
    RelatedResource,
    ResourceGroup,
    ResourceGroupList,
    UniversalPolicy,
    UniversalPolicyChangedContent,
    Value,
)


@pytest.fixture()
def path_node():
    return PathNode(
        id="id",
        name="name",
        system_id="system_id",
        type="type",
    )


class TestPathNode:
    def test_equals(self, path_node: PathNode):
        assert path_node == path_node
        copied_path_node = deepcopy(path_node)
        copied_path_node.type = "type1"
        assert path_node != copied_path_node
        copied_path_node = deepcopy(path_node)
        copied_path_node.system_id = "system_id1"
        assert path_node != copied_path_node

    def test_to_path_resource_type(self, path_node: PathNode):
        assert path_node.to_path_resource_type() == PathResourceType(system_id="system_id", id="type")

    def test_match_resource_type(self, path_node: PathNode):
        assert path_node.match_resource_type("system_id", "type")


@pytest.fixture()
def path_node_list(path_node):
    copied_path_node = deepcopy(path_node)
    copied_path_node.type = "type1"
    return PathNodeList(__root__=[path_node, copied_path_node])


@pytest.fixture()
def instance_selection():
    return InstanceSelection(
        id="id",
        system_id="system_id",
        name="name",
        name_en="name_en",
        ignore_iam_path=False,
        resource_type_chain=[{"system_id": "system_id", "id": "type"}, {"system_id": "system_id", "id": "type1"}],
    )


class TestPathNodeList:
    def test_match_selection(self, path_node_list: PathNodeList, instance_selection: InstanceSelection):
        copied_path_node_list = deepcopy(path_node_list)
        copied_path_node_list.pop(1)
        assert copied_path_node_list.match_selection("system_id", "type", instance_selection)
        assert path_node_list.match_selection("system_id", "type", instance_selection)

    def test_ignore_path(self, path_node_list: PathNodeList, instance_selection: InstanceSelection):
        instance_selection.ignore_iam_path = True
        new_path_node_list = path_node_list.ignore_path(instance_selection)
        assert len(new_path_node_list) == 1
        assert new_path_node_list[0].type == "type1"


class TestInstance:
    def test_ignore_path_true(self, path_node_list: PathNodeList, instance_selection: InstanceSelection):
        instance = Instance(type="type1", path=[path_node_list])
        instance_selection.ignore_iam_path = True
        instance.ignore_path("system_id", "type1", [instance_selection])
        assert len(instance.path[0]) == 1
        assert instance.path[0][0].type == "type1"

    def test_ignore_path_diff_type(self, path_node_list: PathNodeList, instance_selection: InstanceSelection):
        instance = Instance(type="type1", path=[path_node_list])
        instance_selection.ignore_iam_path = True
        instance.ignore_path("system_id", "type2", [instance_selection])
        assert len(instance.path[0]) == 2


class TestDataGenerator:
    @classmethod
    def gen_only_attr_related_resource_data(cls):
        """生成只包含attribute的relatedResource数据"""
        return RelatedResource(
            system_id="s_id",
            type="rt_id",
            condition=[
                Condition(
                    id="97395903b0b84c0187284cb213dfa28a",
                    instances=[],
                    attributes=[Attribute(id="attr_id", name="name_id", values=[Value(id="id", name="name")])],
                )
            ],
        )

    @classmethod
    def gen_path_node(cls, _id, replace=False):
        """生成节点"""
        if replace:
            return PathNode(id=_id, name=f"r_name{_id}", system_id="s_id", type=f"rt_id{_id}")

        return PathNode(id=f"r_id{_id}", name=f"r_name{_id}", system_id="s_id", type=f"rt_id{_id}")

    @classmethod
    def gen_only_path_related_resource_data(cls):
        """生成只包含资源路径的RelatedResource数据"""
        return RelatedResource(
            system_id="s_id",
            type="rt_id",
            condition=[
                Condition(
                    id="97395903b0b84c0187284cb213dfa28a",
                    instances=[
                        Instance(
                            type="rt_id",
                            path=[
                                PathNodeList(__root__=[cls.gen_path_node("1"), cls.gen_path_node("*", replace=True)]),
                                PathNodeList(__root__=[cls.gen_path_node("3"), cls.gen_path_node("2")]),
                            ],
                        )
                    ],
                    attributes=[],
                )
            ],
        )


class TestUniversalPolicy:
    @pytest.mark.parametrize(
        "resource_groups,action_auth_type,expected",
        [
            # Action类型为ABAC
            (
                # resource_groups
                [],
                # action_auth_type
                AuthType.ABAC.value,
                # expected
                True,
            ),
            # 与资源实例无关
            (
                # resource_groups
                [],
                # action_auth_type
                AuthType.RBAC.value,
                # expected
                True,
            ),
            # 关联多种资源类型 - 基于多分组
            (
                # resource_groups
                [
                    ResourceGroup(related_resource_types=[]),
                    ResourceGroup(related_resource_types=[]),
                ],
                # action_auth_type
                AuthType.RBAC.value,
                # expected
                True,
            ),
            # 关联多种资源类型 - 基于只有一组
            (
                # resource_groups
                [
                    ResourceGroup(
                        related_resource_types=[
                            RelatedResource(system_id="s1", type="rt1", condition=[]),
                            RelatedResource(system_id="s1", type="rt2", condition=[]),
                        ]
                    ),
                ],
                # action_auth_type
                AuthType.RBAC.value,
                # expected
                True,
            ),
            # 环境属性
            (
                # resource_groups
                [
                    ResourceGroup(
                        related_resource_types=[RelatedResource(system_id="s1", type="rt1", condition=[])],
                        environments=[Environment(type="e_type", condition=[])],
                    ),
                ],
                # action_auth_type
                AuthType.RBAC.value,
                # expected
                True,
            ),
            # Any策略
            (
                # resource_groups
                [
                    ResourceGroup(
                        related_resource_types=[RelatedResource(system_id="s1", type="rt1", condition=[])],
                    ),
                ],
                # action_auth_type
                AuthType.RBAC.value,
                # expected
                True,
            ),
            # RBAC策略
            (
                # resource_groups
                [
                    ResourceGroup(
                        related_resource_types=[
                            RelatedResource(
                                system_id="s1", type="rt1", condition=[Condition(instances=[], attributes=[])]
                            )
                        ],
                    ),
                ],
                # action_auth_type
                AuthType.RBAC.value,
                # expected
                False,
            ),
        ],
    )
    def test_is_absolute_abac(self, resource_groups, action_auth_type, expected):
        resource_group_list = ResourceGroupList(__root__=resource_groups)
        is_absolute_abac = UniversalPolicy._is_absolute_abac(resource_group_list, action_auth_type)

        assert is_absolute_abac == expected

    @pytest.mark.parametrize(
        "auth_type,expected",
        [
            ("rbac", False),
            ("none", False),
            ("abac", True),
            ("all", True),
        ],
    )
    def test_has_abac(self, auth_type, expected):
        p = UniversalPolicy(
            action_id="a",
            policy_id=0,
            expired_at=0,
            resource_groups=ResourceGroupList(__root__=[]),
            expression_resource_groups=ResourceGroupList(__root__=[]),
            auth_type=auth_type,
        )
        assert p.has_abac() == expected

    @pytest.mark.parametrize(
        "auth_type,expected",
        [
            ("rbac", True),
            ("none", False),
            ("abac", False),
            ("all", True),
        ],
    )
    def test_has_rbac(self, auth_type, expected):
        p = UniversalPolicy(
            action_id="a",
            policy_id=0,
            expired_at=0,
            resource_groups=ResourceGroupList(__root__=[]),
            instances=[],
            auth_type=auth_type,
        )
        assert p.has_rbac() == expected

    @pytest.mark.parametrize(
        "has_abac,has_rbac,expected",
        [
            (True, True, AuthType.ALL.value),
            (True, False, AuthType.ABAC.value),
            (False, True, AuthType.RBAC.value),
            (False, False, AuthType.NONE.value),
        ],
    )
    def test_calculate_auth_type(self, has_abac, has_rbac, expected):
        auth_type = UniversalPolicy._calculate_auth_type(has_abac, has_rbac)

        assert auth_type == expected

    @pytest.mark.parametrize(
        "related_resource,expected",
        [
            # 包含属性
            (
                # related_resource
                TestDataGenerator.gen_only_attr_related_resource_data(),
                # expected
                (
                    # expression_resource_groups
                    [ResourceGroup(related_resource_types=[TestDataGenerator.gen_only_attr_related_resource_data()])],
                    # rbac_instances
                    [],
                ),
            ),
            # 仅仅RBAC
            (
                # related_resource
                TestDataGenerator.gen_only_path_related_resource_data(),
                # expected
                (
                    # expression_resource_groups
                    [],
                    # rbac_instances
                    [
                        TestDataGenerator.gen_path_node("1"),
                        TestDataGenerator.gen_path_node("2"),
                    ],
                ),
            ),
        ],
    )
    def test_parse_abac_and_rbac(self, related_resource, expected):
        expression_resource_groups, rbac_instances = UniversalPolicy._parse_abac_and_rbac(related_resource)

        assert expression_resource_groups == ResourceGroupList(__root__=expected[0])
        assert set(rbac_instances) == set(expected[1])

    @pytest.mark.parametrize(
        "new,old,expected",
        [
            # Create
            (
                # new(auth_type, abac_data, rbac_data)
                (
                    AuthType.ABAC.value,
                    [ResourceGroup(related_resource_types=[TestDataGenerator.gen_only_attr_related_resource_data()])],
                    [],
                ),
                # old(auth_type, abac_data, rbac_data)
                (AuthType.NONE.value, [], []),
                # expected(auth_type, abac_data, rbac_data)
                (
                    AuthType.ABAC.value,
                    AbacPolicyChangeContent(
                        change_type=AbacPolicyChangeType.CREATED.value,
                        resource_expression='{"StringEquals":{"s_id.rt_id.attr_id":["id"]}}',
                    ),
                    None,
                ),
            ),
            # Update
            (
                # new
                (
                    AuthType.ABAC.value,
                    [ResourceGroup(related_resource_types=[TestDataGenerator.gen_only_attr_related_resource_data()])],
                    [],
                ),
                # old
                (AuthType.ABAC.value, [ResourceGroup(related_resource_types=[])], []),
                # expected
                (
                    AuthType.ABAC.value,
                    AbacPolicyChangeContent(
                        id=1,
                        change_type=AbacPolicyChangeType.UPDATED.value,
                        resource_expression='{"StringEquals":{"s_id.rt_id.attr_id":["id"]}}',
                    ),
                    None,
                ),
            ),
            # Delete
            (
                # new
                (AuthType.NONE.value, [], []),
                # old
                (
                    AuthType.ABAC.value,
                    [ResourceGroup(related_resource_types=[TestDataGenerator.gen_only_attr_related_resource_data()])],
                    [],
                ),
                # expected
                (
                    AuthType.NONE.value,
                    AbacPolicyChangeContent(id=1, change_type=AbacPolicyChangeType.DELETED.value),
                    None,
                ),
            ),
            # RBAC: Create
            (
                # new
                (AuthType.RBAC.value, [], [TestDataGenerator.gen_path_node("1")]),
                # old
                (AuthType.RBAC.value, [], []),
                # expected
                (
                    AuthType.RBAC.value,
                    None,
                    RbacPolicyChangeContent(created=[TestDataGenerator.gen_path_node("1")]),
                ),
            ),
            # RBAC: Delete
            (
                # new
                (AuthType.RBAC.value, [], []),
                # old
                (AuthType.RBAC.value, [], [TestDataGenerator.gen_path_node("1")]),
                # expected
                (
                    AuthType.RBAC.value,
                    None,
                    RbacPolicyChangeContent(deleted=[TestDataGenerator.gen_path_node("1")]),
                ),
            ),
        ],
    )
    def test_calculate_pre_changed_content(self, new, old, expected):
        new_policy = UniversalPolicy(
            action_id="a_id",
            policy_id=0,
            expired_at=0,
            resource_groups=ResourceGroupList(__root__=[]),
            auth_type=new[0],
            expression_resource_groups=ResourceGroupList(__root__=new[1]),
            instances=new[2],
        )

        old_policy = UniversalPolicy(
            action_id="a_id",
            policy_id=0,
            backend_policy_id=1,
            expired_at=0,
            resource_groups=ResourceGroupList(__root__=[]),
            auth_type=old[0],
            expression_resource_groups=ResourceGroupList(__root__=old[1]),
            instances=old[2],
        )

        expected_changed_content = UniversalPolicyChangedContent(
            action_id="a_id",
            auth_type=expected[0],
            abac=expected[1],
            rbac=expected[2],
        )

        policy_changed_content = new_policy.calculate_pre_changed_content("mock_system", old_policy)
        assert policy_changed_content == expected_changed_content
