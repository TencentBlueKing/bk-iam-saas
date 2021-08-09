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
import mock
from django.test import TestCase

from backend.biz.policy import (
    ConditionBean,
    ConditionBeanList,
    InstanceBean,
    PathNodeBean,
    PathNodeBeanList,
    PolicyBean,
    PolicyBeanList,
    PolicyEmptyException,
    RelatedResourceBean,
)
from backend.common.error_codes import CodeException
from backend.service.models.instance_selection import ChainNode, InstanceSelection
from backend.service.models.resource_type import ResourceTypeDict
from backend.service.policy.query import Attribute
from tests.test_util.factory import (
    AttributeFactory,
    ConditionBeanFactory,
    InstanceBeanFactory,
    InstanceSelectionFactory,
    PolicyBeanFactory,
    RelatedResourceBeanFactory,
)


class InstanceAddSubInstance(TestCase):
    def setUp(self):
        self.instance_factory = InstanceBeanFactory()

    def test_add_instance_true(self):
        instance = self.instance_factory.example()
        new_instance = self.instance_factory.new(
            "host", "主机", [[{"type": "host", "type_name": "主机", "id": "host2", "name": "主机2"}]]
        )

        instance.add_paths(new_instance.path)

        self.assertEqual(len(instance.path), 2)

    def test_add_instance_false(self):
        instance = self.instance_factory.example()

        instance.add_paths(instance.path)

        self.assertEqual(len(instance.path), 1)

    def test_remove_instance_true(self):
        instance = self.instance_factory.new(
            "host",
            "主机",
            [
                [{"type": "host", "type_name": "主机", "id": "host1", "name": "主机1"}],
                [{"type": "host", "type_name": "主机", "id": "host2", "name": "主机2"}],
            ],
        )
        old_instance = self.instance_factory.example()

        instance.remove_paths(old_instance.path)

        self.assertEqual(len(instance.path), 1)

    def test_remove_instance_false(self):
        instance = self.instance_factory.example()
        old_instance = self.instance_factory.new(
            "host", "主机", [[{"type": "host", "type_name": "主机", "id": "host2", "name": "主机2"}]]
        )

        instance.remove_paths(old_instance.path)

        self.assertEqual(len(instance.path), 1)


class ConditionAddSubTest(TestCase):
    def setUp(self):
        self.condition_factory = ConditionBeanFactory()
        self.instance_factory = InstanceBeanFactory()

    def test_condition_add_true(self):
        condition = self.condition_factory.new(instances=[self.instance_factory.example()])
        old_condition = self.condition_factory.new(
            instances=[
                self.instance_factory.new(
                    "host", "主机", [[{"type": "host", "type_name": "主机", "id": "host2", "name": "主机2"}]]
                )
            ]
        )

        condition.add_instances(old_condition.instances)
        self.assertEqual(len(condition.instances), 1)
        self.assertEqual(len(condition.instances[0].path), 2)

        condition = self.condition_factory.new(instances=[self.instance_factory.example()])
        old_condition = self.condition_factory.new(
            instances=[
                self.instance_factory.new(
                    "业务", "biz", [[{"type": "biz", "type_name": "业务", "id": "biz1", "name": "蓝鲸"}]]
                )
            ]
        )

        condition.add_instances(old_condition.instances)

        self.assertEqual(len(condition.instances), 2)

    def test_condition_add_false(self):
        condition = self.condition_factory.new(instances=[self.instance_factory.example()])

        condition.add_instances(condition.instances)

        self.assertEqual(len(condition.instances), 1)

    def test_condition_remove_true(self):
        condition = self.condition_factory.new(
            instances=[
                self.instance_factory.new(
                    "host",
                    "主机",
                    [
                        [{"type": "host", "type_name": "主机", "id": "host1", "name": "主机1"}],
                        [{"type": "host", "type_name": "主机", "id": "host2", "name": "主机2"}],
                    ],
                )
            ]
        )
        old_condition = self.condition_factory.new(instances=[self.instance_factory.example()])

        condition.remove_instances(old_condition.instances)
        self.assertEqual(len(condition.instances[0].path), 1)

    def test_condition_remove_false(self):
        condition = self.condition_factory.new(instances=[self.instance_factory.example()])
        old_condition = self.condition_factory.new(
            instances=[
                self.instance_factory.new(
                    "host", "主机", [[{"type": "host", "type_name": "主机", "id": "host2", "name": "主机2"}]]
                )
            ]
        )
        condition.remove_instances(old_condition.instances)
        self.assertEqual(len(condition.instances), 1)
        self.assertEqual(len(condition.instances[0].path), 1)


class ConditionListAddSubInstance(TestCase):
    def setUp(self):
        self.resource_factory = RelatedResourceBeanFactory()
        self.instance_factory = InstanceBeanFactory()
        self.condition_factory = ConditionBeanFactory()
        self.attribute_factory = AttributeFactory()

    def test_add_instance_any(self):
        resource = self.resource_factory.new("bk_cmdb", "host", "主机")
        condition_list = ConditionBeanList(resource.condition)
        condition_list_2 = ConditionBeanList([self.condition_factory.new(instances=[self.instance_factory.example()])])

        condition_list.add(condition_list_2)

        self.assertEqual(len(condition_list.conditions), 0)

    def test_add_new_condition(self):
        resource = self.resource_factory.new(
            "bk_cmdb", "host", "主机", [self.condition_factory.new(attributes=[self.attribute_factory.example()])]
        )

        condition_list = ConditionBeanList(resource.condition)
        condition_list_2 = ConditionBeanList([self.condition_factory.new(instances=[self.instance_factory.example()])])

        condition_list.add(condition_list_2)

        self.assertEqual(len(condition_list.conditions), 2)

    def test_add_instance_true(self):
        resource = self.resource_factory.new(
            "bk_cmdb", "host", "主机", [self.condition_factory.new(instances=[self.instance_factory.example()])]
        )

        condition_list = ConditionBeanList(resource.condition)
        condition_list_2 = ConditionBeanList(
            [
                self.condition_factory.new(
                    instances=[
                        self.instance_factory.new(
                            "host", "主机", [[{"type": "host", "type_name": "主机", "id": "host2", "name": "主机2"}]]
                        )
                    ]
                )
            ]
        )

        condition_list.add(condition_list_2)
        self.assertEqual(len(condition_list.conditions), 1)
        self.assertEqual(len(condition_list.conditions[0].instances), 1)
        self.assertEqual(len(condition_list.conditions[0].instances[0].path), 2)

    def test_remove_instance_any(self):
        resource = self.resource_factory.new("bk_cmdb", "host", "主机")

        condition_list = ConditionBeanList(resource.condition)
        condition_list_2 = ConditionBeanList([self.condition_factory.new(instances=[self.instance_factory.example()])])

        condition_list.sub(condition_list_2)

        self.assertEqual(len(condition_list.conditions), 0)

    def test_remove_instance_true(self):
        resource = self.resource_factory.new(
            "bk_cmdb", "host", "主机", [self.condition_factory.new(instances=[self.instance_factory.example()])]
        )

        condition_list = ConditionBeanList(resource.condition)
        condition_list_2 = ConditionBeanList([self.condition_factory.new(instances=[self.instance_factory.example()])])

        condition_list.sub(condition_list_2)

        self.assertTrue(condition_list.is_empty)


class InstanceCheckSelection(TestCase):
    def setUp(self):
        self.instance_selection_factory = InstanceSelectionFactory()
        self.instance_factory = InstanceBeanFactory()
        self.resource_factory = RelatedResourceBeanFactory()

    def test_path_display(self):
        instance = self.instance_factory.example()
        node_list = PathNodeBeanList(instance.path[0])
        path_display = node_list.display()
        self.assertEqual(path_display, "host:主机1")

    def test_check_selections_export_1(self):
        """
        检查实例视图, 实例的节点的类型与资源类型一样
        """
        instance = self.instance_factory.example()
        rrt = self.resource_factory.example()
        selections = [self.instance_selection_factory.new("1", "1", False, [])]
        instance.check_instance_selection(rrt.system_id, rrt.type, selections, True)

    def test_check_selections_export_2(self):
        instance = self.instance_factory.new(
            "host",
            "主机",
            [
                [
                    {"system_id": "bk_cmdb", "type": "biz", "type_name": "biz", "id": "biz1", "name": "biz1"},
                    {"system_id": "bk_cmdb", "type": "set", "type_name": "set", "id": "set1", "name": "set1"},
                    {
                        "system_id": "bk_cmdb",
                        "type": "module",
                        "type_name": "module",
                        "id": "module1",
                        "name": "module1",
                    },
                    {"system_id": "bk_cmdb", "type": "host", "type_name": "host", "id": "host1", "name": "host1"},
                ]
            ],
        )
        rrt = self.resource_factory.example()
        selections = [self.instance_selection_factory.example()]
        instance.check_instance_selection(rrt.system_id, rrt.type, selections, True)

    def test_check_selections_export_3(self):
        instance = self.instance_factory.new(
            "host",
            "主机",
            [
                [
                    {"system_id": "bk_cmdb", "type": "biz", "type_name": "biz", "id": "biz1", "name": "biz1"},
                    {"system_id": "bk_cmdb", "type": "set", "type_name": "set", "id": "set1", "name": "set1"},
                    {
                        "system_id": "bk_cmdb",
                        "type": "module",
                        "type_name": "module",
                        "id": "module1",
                        "name": "module1",
                    },
                    {"system_id": "bk_cmdb", "type": "host", "type_name": "host", "id": "host1", "name": "host1"},
                ]
            ],
        )
        rrt = self.resource_factory.example()
        selections = [self.instance_selection_factory.example()]
        selections[0].ignore_iam_path = True
        instance.check_instance_selection(rrt.system_id, rrt.type, selections, True)
        self.assertEqual(len(instance.path[0]), 1)

    def test_check_selections_export_4(self):
        instance = self.instance_factory.new(
            "host",
            "主机",
            [
                [
                    {"system_id": "bk_cmdb", "type": "biz", "type_name": "biz", "id": "biz1", "name": "biz1"},
                    {"system_id": "bk_cmdb", "type": "set", "type_name": "set", "id": "set1", "name": "set1"},
                ]
            ],
        )
        rrt = self.resource_factory.example()
        selections = [self.instance_selection_factory.example()]
        selections[0].ignore_iam_path = True
        instance.check_instance_selection(rrt.system_id, rrt.type, selections, True)
        self.assertEqual(len(instance.path[0]), 2)

    def test_check_selections_err(self):
        instance = self.instance_factory.new(
            "host", "主机", [[{"system_id": "bk_cmdb", "type": "set", "type_name": "set", "id": "set1", "name": "set1"}]]
        )
        rrt = self.resource_factory.example()
        selections = [self.instance_selection_factory.example()]
        try:
            instance.check_instance_selection(rrt.system_id, rrt.type, selections, True)
        except CodeException as e:
            self.assertEqual(e.message, "参数校验失败: set:set1 could not match any instance selection")


class InstanceTests(TestCase):
    def setUp(self):
        self.instance_factory = InstanceBeanFactory()

    def test_get_system_set(self):
        instance = self.instance_factory.example()

        self.assertEqual(instance.get_system_id_set(), {"bk_cmdb"})

    def test_fill_type_name(self):
        instance = self.instance_factory.new(
            "host", "主机", [[{"system_id": "bk_cmdb", "type": "host", "type_name": "主机", "id": "*", "name": "主机1"}]]
        )

        resource_type_dict = ResourceTypeDict(
            data={("bk_cmdb", "host"): {"name": "host_test", "name_en": "host_test_en"}}
        )

        instance.fill_empty_fields(resource_type_dict)
        self.assertEqual(instance.name, "host_test")
        self.assertEqual(instance.name_en, "host_test_en")
        self.assertEqual(instance.path[0][0].type_name, "host_test")
        self.assertEqual(instance.path[0][0].type_name_en, "host_test_en")

    def test_sub(self):
        instance = self.instance_factory.new(
            "host",
            "主机",
            [
                [
                    {"system_id": "bk_cmdb", "type": "biz", "type_name": "biz", "id": "biz1", "name": "biz1"},
                    {"system_id": "bk_cmdb", "type": "set", "type_name": "set", "id": "set1", "name": "set1"},
                ],
                [{"system_id": "bk_cmdb", "type": "host", "type_name": "主机", "id": "host1", "name": "主机1"}],
            ],
        )

        instance.remove_paths(self.instance_factory.example().path)

        self.assertEqual(len(instance.path), 1)


class PathNodeBeanListperTests(TestCase):
    def setUp(self):
        self.instance_selection_factory = InstanceSelectionFactory()
        self.resource_factory = RelatedResourceBeanFactory()

    def test_multi_leaf_node_ok(self):
        """
        测试多级叶子节点相同的情况
        比如用户管理的部门下的部门
        """
        path = [
            {"system_id": "bk_cmdb", "type": "biz", "id": "", "name": ""},
            {"system_id": "bk_cmdb", "type": "set", "id": "", "name": ""},
            {"system_id": "bk_cmdb", "type": "module", "id": "", "name": ""},
            {"system_id": "bk_cmdb", "type": "host", "id": "", "name": ""},
            {"system_id": "bk_cmdb", "type": "host", "id": "", "name": ""},
        ]

        selection = self.instance_selection_factory.example()

        rrt = self.resource_factory.example()

        helper = PathNodeBeanList([PathNodeBean(**one) for one in path])
        ok = helper.match_selection(rrt.system_id, rrt.type, selection)

        self.assertTrue(ok)

    def test_multi_leaf_node_false(self):
        """
        测试多级叶子节点相同的情况
        """
        path = [
            {"system_id": "bk_cmdb", "type": "biz", "id": "", "name": ""},
            {"system_id": "bk_cmdb", "type": "set", "id": "", "name": ""},
            {"system_id": "bk_cmdb", "type": "module", "id": "", "name": ""},
            {"system_id": "bk_cmdb", "type": "host", "id": "", "name": ""},
            {"system_id": "bk_cmdb", "type": "test", "id": "", "name": ""},
        ]

        selection = self.instance_selection_factory.example()

        rrt = self.resource_factory.example()

        helper = PathNodeBeanList([PathNodeBean(**one) for one in path])
        ok = helper.match_selection(rrt.system_id, rrt.type, selection)

        self.assertFalse(ok)


class ConditionTests(TestCase):
    def setUp(self):
        self.condition_factory = ConditionBeanFactory()
        self.instance_factory = InstanceBeanFactory()

    def test_get_system_set(self):
        condition = self.condition_factory.example()
        systems = condition.get_system_id_set()
        self.assertEqual(systems, {"bk_cmdb"})

        condition = self.condition_factory.new()
        systems = condition.get_system_id_set()
        self.assertEqual(systems, set())


class RelatedResourceTests(TestCase):
    def setUp(self):
        self.resource_factory = RelatedResourceBeanFactory()
        self.condition_factory = ConditionBeanFactory()
        self.instance_selection_factory = InstanceSelectionFactory()
        self.attribute_factory = AttributeFactory()

    def test_check_selection_ignore_path(self):
        resource = self.resource_factory.example()
        selection = self.instance_selection_factory.example()
        resource.check_selection([selection], True)

        resource = self.resource_factory.new(
            "bk_cmdb", "host", "主机", [self.condition_factory.new(attributes=[self.attribute_factory.example()])]
        )
        resource.check_selection([selection], True)

    def test_get_system_set(self):
        resource = self.resource_factory.example()
        systems = resource.get_system_id_set()
        self.assertEqual(systems, {"bk_cmdb"})


class PolicyTests(TestCase):
    def setUp(self):
        self.policy_factory = PolicyBeanFactory()
        self.resource_factory = RelatedResourceBeanFactory()
        self.condition_factory = ConditionBeanFactory()
        self.attribute_factory = AttributeFactory()

    def test_set_expired_at(self):
        policy = self.policy_factory.example()
        policy.set_expired_at(4102444800)
        self.assertEqual(policy.expired_at, 4102444800)

    def test_has(self):
        policy = self.policy_factory.new("create_host", [])
        self.assertTrue(policy.has_related_resource_types(policy.related_resource_types))

        policy = self.policy_factory.example()
        self.assertTrue(policy.has_related_resource_types(policy.related_resource_types))

        new_policy = self.policy_factory.new(
            "view_host",
            [
                self.resource_factory.new(
                    "bk_cmdb",
                    "host",
                    "主机",
                    [self.condition_factory.new(attributes=[self.attribute_factory.example()])],
                )
            ],
        )

        self.assertFalse(new_policy.has_related_resource_types(policy.related_resource_types))

    def test_diff(self):
        policy = self.policy_factory.new("create_host", [])
        policy.remove_related_resource_types(policy.related_resource_types)

        policy = self.policy_factory.example()
        with self.assertRaises(PolicyEmptyException):
            policy.remove_related_resource_types(policy.related_resource_types)

    def test_get_system_set(self):
        policy = self.policy_factory.new("create_host", [])
        systems = policy.get_system_id_set()
        self.assertEqual(systems, set())


class PolicyListTests(TestCase):
    def test_right(self):
        new_policy_list = PolicyBeanList(
            "system_id",
            [
                PolicyBean(
                    **{
                        "type": "edit",
                        "id": "edit_host",
                        "name": "编辑主机",
                        "description": "",
                        "related_resource_types": [],
                        "environment": {},
                        "expired_at": 31536000,
                    }
                ),
                PolicyBean(
                    **{
                        "type": "edit",
                        "id": "view_host",
                        "name": "查看主机",
                        "description": "",
                        "related_resource_types": [],
                        "environment": {},
                        "expired_at": 31536000,
                    }
                ),
            ],
        )

        old_policy_list = PolicyBeanList(
            "system_id",
            [
                PolicyBean(
                    **{
                        "type": "edit",
                        "id": "view_host",
                        "name": "查看主机",
                        "description": "",
                        "related_resource_types": [{"system_id": "bk_cmdb", "type": "host", "condition": []}],
                        "environment": {},
                        "policy_id": 1,
                        "expired_at": 31536000,
                    }
                ),
                PolicyBean(
                    **{
                        "type": "edit",
                        "id": "delete_host",
                        "name": "查看主机",
                        "description": "",
                        "related_resource_types": [],
                        "environment": {},
                        "expired_at": 31536000,
                    }
                ),
            ],
        )

        create_policy_list, update_policy_list = old_policy_list.split_to_creation_and_update_for_grant(
            new_policy_list
        )

        self.assertListEqual(
            create_policy_list.policies,
            [
                PolicyBean(
                    **{
                        "type": "edit",
                        "id": "edit_host",
                        "name": "编辑主机",
                        "description": "",
                        "related_resource_types": [],
                        "environment": {},
                        "expired_at": 31536000,
                    }
                )
            ],
        )

        self.assertListEqual(update_policy_list.policies, [])

    def test_expired_at(self):
        new_policy_list = PolicyBeanList(
            "system_id",
            [
                PolicyBean(
                    **{
                        "type": "edit",
                        "id": "edit_host",
                        "name": "编辑主机",
                        "description": "",
                        "related_resource_types": [],
                        "environment": {},
                        "expired_at": 31536002,
                    }
                ),
                PolicyBean(
                    **{
                        "type": "view",
                        "id": "view_host",
                        "name": "查看主机",
                        "description": "",
                        "related_resource_types": [],
                        "environment": {},
                        "expired_at": 31536000,
                    }
                ),
            ],
        )

        old_policy_list = PolicyBeanList(
            "system_id",
            [
                PolicyBean(
                    **{
                        "type": "edit",
                        "id": "edit_host",
                        "name": "编辑主机",
                        "description": "",
                        "related_resource_types": [],
                        "environment": {},
                        "policy_id": 1,
                        "expired_at": 31536001,
                    }
                ),
                PolicyBean(
                    **{
                        "type": "view",
                        "id": "view_host",
                        "name": "查看主机",
                        "description": "",
                        "related_resource_types": [],
                        "environment": {},
                        "policy_id": 2,
                        "expired_at": 31536000,
                    }
                ),
            ],
        )

        create_policy_list, update_policy_list = old_policy_list.split_to_creation_and_update_for_grant(
            new_policy_list
        )

        self.assertListEqual(create_policy_list.policies, [])

        self.assertListEqual(
            update_policy_list.policies,
            [
                PolicyBean(
                    **{
                        "type": "edit",
                        "id": "edit_host",
                        "name": "编辑主机",
                        "description": "",
                        "related_resource_types": [],
                        "environment": {},
                        "expired_at": 31536002,
                        "policy_id": 1,
                    }
                )
            ],
        )


class RelatedResourceCloneAndFilterTests(TestCase):
    def setUp(self):
        self.instance_factory = InstanceBeanFactory()

    def test_right_1(self):
        conditions = [ConditionBean(instances=[self.instance_factory.example()], attributes=[])]
        resource_type = RelatedResourceBean(condition=conditions, type="type", system_id="system")
        selections = []
        self.assertEqual(resource_type.clone_and_filter_by_instance_selections(selections, True), None)

    def test_right_2(self):
        import uuid

        uuid.uuid4 = mock.Mock(return_value=uuid.UUID("fa17b2cbf38141d7a5a0591573fc0f82"))

        conditions = [
            ConditionBean(
                instances=[
                    InstanceBean(
                        type="host",
                        path=[
                            [{"system_id": "bk_cmdb", "type": "set", "id": "set1"}],
                            [
                                {"system_id": "bk_cmdb", "type": "biz", "id": "biz1"},
                                {"system_id": "bk_cmdb", "type": "set", "id": "set1"},
                                {"system_id": "bk_cmdb", "type": "module", "id": "module1"},
                                {"system_id": "bk_cmdb", "type": "host", "id": "host1"},
                            ],
                        ],
                    ),
                    InstanceBean(type="biz", path=[[{"system_id": "bk_cmdb", "type": "biz", "id": "biz1"}]]),
                ],
                attributes=[],
            ),
            ConditionBean(
                instances=[
                    InstanceBean(type="host", path=[[{"system_id": "bk_cmdb", "type": "host", "id": "host3"}]])
                ],
                attributes=[Attribute(id="", name="", values=[{"id": "test1", "name": "test1"}])],
            ),
            ConditionBean(
                instances=[
                    InstanceBean(
                        type="host",
                        path=[
                            [
                                {"system_id": "bk_cmdb", "type": "biz", "id": "biz1"},
                                {"system_id": "bk_cmdb", "type": "set", "id": "set1"},
                                {"system_id": "bk_cmdb", "type": "module", "id": "module1"},
                                {"system_id": "bk_cmdb", "type": "host", "id": "host2"},
                            ],
                        ],
                    ),
                ],
                attributes=[Attribute(id="", name="", values=[{"id": "test2", "name": "test2"}])],
            ),
        ]
        resource_type = RelatedResourceBean(condition=conditions, type="bk_cmdb", system_id="host")
        selections = [
            InstanceSelection(
                id="test1",
                system_id="bk_cmdb",
                name="test1",
                name_en="test1",
                ignore_iam_path=False,
                resource_type_chain=[
                    ChainNode(system_id="bk_cmdb", id="biz"),
                    ChainNode(system_id="bk_cmdb", id="set"),
                    ChainNode(system_id="bk_cmdb", id="module"),
                    ChainNode(system_id="bk_cmdb", id="host"),
                ],
            ),
            InstanceSelection(
                id="test2",
                system_id="bk_cmdb",
                name="test2",
                name_en="test2",
                ignore_iam_path=False,
                resource_type_chain=[
                    ChainNode(system_id="bk_cmdb", id="biz"),
                    ChainNode(system_id="bk_cmdb", id="set"),
                ],
            ),
        ]
        new_rt = resource_type.clone_and_filter_by_instance_selections(selections)
        self.assertEqual(
            new_rt.condition,
            [
                ConditionBean(
                    instances=[
                        InstanceBean(
                            type="host",
                            path=[
                                [
                                    {"system_id": "bk_cmdb", "type": "biz", "id": "biz1"},
                                    {"system_id": "bk_cmdb", "type": "set", "id": "set1"},
                                    {"system_id": "bk_cmdb", "type": "module", "id": "module1"},
                                    {"system_id": "bk_cmdb", "type": "host", "id": "host1"},
                                ],
                            ],
                        ),
                        InstanceBean(type="biz", path=[[{"system_id": "bk_cmdb", "type": "biz", "id": "biz1"}]]),
                    ],
                    attributes=[],
                ),
                ConditionBean(
                    instances=[
                        InstanceBean(
                            type="host",
                            path=[
                                [
                                    {"system_id": "bk_cmdb", "type": "biz", "id": "biz1"},
                                    {"system_id": "bk_cmdb", "type": "set", "id": "set1"},
                                    {"system_id": "bk_cmdb", "type": "module", "id": "module1"},
                                    {"system_id": "bk_cmdb", "type": "host", "id": "host2"},
                                ],
                            ],
                        ),
                    ],
                    attributes=[Attribute(id="", name="", values=[{"id": "test2", "name": "test2"}])],
                ),
            ],
        )


class InstanceCloneAndFilterTests(TestCase):
    def test_clone_and_filter_by_selections_1(self):
        selections = [
            InstanceSelection(
                id="test1",
                system_id="bk_cmdb",
                name="test1",
                name_en="test1",
                ignore_iam_path=True,
                resource_type_chain=[
                    ChainNode(system_id="bk_cmdb", id="biz"),
                    ChainNode(system_id="bk_cmdb", id="set"),
                    ChainNode(system_id="bk_cmdb", id="module"),
                    ChainNode(system_id="bk_cmdb", id="host"),
                ],
            )
        ]
        path = [
            {"system_id": "bk_cmdb", "type": "host", "id": "host1", "name": "host1"},
        ]
        instance = InstanceBean(path=[path], type="host")
        new_instance = instance.clone_and_filter_by_instance_selections("bk_cmdb", "host", selections)
        self.assertEqual(
            new_instance.path,
            [[PathNodeBean(**{"system_id": "bk_cmdb", "type": "host", "id": "host1", "name": "host1"})]],
        )

    def test_clone_and_filter_by_selections_2(self):
        path = [
            {"system_id": "bk_cmdb", "type": "biz", "id": "biz1", "name": "biz1"},
            {"system_id": "bk_cmdb", "type": "set", "id": "set1", "name": "set1"},
            {"system_id": "bk_cmdb", "type": "module", "id": "module1", "name": "module1"},
            {"system_id": "bk_cmdb", "type": "host", "id": "host1", "name": "host1"},
        ]
        selections = [
            InstanceSelection(
                id="test1",
                system_id="bk_cmdb",
                name="test1",
                name_en="test1",
                ignore_iam_path=True,
                resource_type_chain=[
                    ChainNode(system_id="bk_cmdb", id="biz"),
                    ChainNode(system_id="bk_cmdb", id="host"),
                ],
            )
        ]
        instance = InstanceBean(path=[path], type="host")
        new_instance = instance.clone_and_filter_by_instance_selections("bk_cmdb", "host", selections)
        self.assertEqual(new_instance, None)

    def test_clone_and_filter_by_selections_3(self):
        path = [
            {"system_id": "bk_cmdb", "type": "biz", "id": "biz1", "name": "biz1"},
            {"system_id": "bk_cmdb", "type": "set", "id": "set1", "name": "set1"},
            {"system_id": "bk_cmdb", "type": "module", "id": "module1", "name": "module1"},
            {"system_id": "bk_cmdb", "type": "host", "id": "host1", "name": "host1"},
        ]
        selections = [
            InstanceSelection(
                id="test1",
                system_id="bk_cmdb",
                name="test1",
                name_en="test1",
                ignore_iam_path=True,
                resource_type_chain=[
                    ChainNode(system_id="bk_cmdb", id="biz"),
                    ChainNode(system_id="bk_cmdb", id="set"),
                    ChainNode(system_id="bk_cmdb", id="module"),
                    ChainNode(system_id="bk_cmdb", id="host"),
                ],
            )
        ]
        instance = InstanceBean(path=[path], type="host")
        new_instance = instance.clone_and_filter_by_instance_selections("bk_cmdb", "host", selections)
        self.assertEqual(new_instance.path, [[PathNodeBean(**one) for one in path]])
