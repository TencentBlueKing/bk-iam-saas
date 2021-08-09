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
from django.test import TestCase

from backend.biz.policy_tag import AttributeTagBean
from backend.common.error_codes import CodeException
from backend.service.models import (
    PathHelper,
    Policy,
    RelatedResource,
    ResourceCreatorActionConfig,
    ResourceCreatorSingleAction,
    Subject,
    group_paths,
)
from backend.service.models.resource_type import ResourceNode, ResourceTypeDict
from tests.test_util.factory import (
    ActionFactory,
    AttributeFactory,
    ConditionFactory,
    InstanceFactory,
    InstanceSelectionFactory,
    PolicyFactory,
    RelatedResourceTypeFactory,
    ResourceFactory,
    ResourceInstanceFactory,
)


class GroupPathTests(TestCase):
    def test_group_paths(self):
        """
        资源拓扑根据类型分组
        """
        paths = [
            [
                {"system_id": "bk_cmdb", "type": "biz", "id": "biz1"},
                {"system_id": "bk_cmdb", "type": "set", "id": "set1"},
                {"system_id": "bk_cmdb", "type": "module", "id": "module1"},
                {"system_id": "bk_cmdb", "type": "host", "id": "host1"},
            ],
            [{"system_id": "bk_cmdb", "type": "host", "id": "host2"}],
            [
                {"system_id": "bk_cmdb", "type": "biz", "id": "biz1"},
                {"system_id": "bk_cmdb", "type": "set", "id": "set1"},
                {"system_id": "bk_cmdb", "type": "module", "id": "module1"},
                {"system_id": "bk_cmdb", "type": "host", "id": "*"},
            ],
            [
                {"system_id": "bk_cmdb", "type": "biz", "id": "biz1"},
                {"system_id": "bk_cmdb", "type": "set", "id": "set1"},
                {"system_id": "bk_cmdb", "type": "module", "id": "module2"},
            ],
        ]

        instances = group_paths(paths)

        self.assertEqual(len(instances), 2)
        self.assertEqual(instances[0].type, "host")
        self.assertEqual(instances[1].type, "module")
        self.assertEqual(len(instances[0].path), 2)
        self.assertEqual(len(instances[1].path), 2)


class DiffAttributeTests(TestCase):
    def setUp(self):
        self.attribute_factory = AttributeFactory()

    def test_diff_attribute(self):
        new_attribute = self.attribute_factory.new(
            "id", "name", [{"id": "id1", "name": "name1"}, {"id": "id2", "name": "name2"}]
        )

        old_attribute = self.attribute_factory.new(
            "id", "name", [{"id": "id2", "name": "name1"}, {"id": "id3", "name": "name2"}]
        )

        diff_attribute = AttributeTagBean(**new_attribute.dict()).compare_and_tag(
            AttributeTagBean(**old_attribute.dict())
        )

        self.assertEqual(diff_attribute.tag, "unchanged")
        self.assertEqual(diff_attribute.values[0].tag, "add")
        self.assertEqual(diff_attribute.values[1].tag, "unchanged")
        self.assertEqual(diff_attribute.values[2].tag, "delete")


class DiffInstanceTests(TestCase):
    def setUp(self):
        self.instance_factory = InstanceFactory()

    def test_diff_instance(self):
        new_instance = self.instance_factory.new(
            "type",
            "name",
            [
                [{"type": "type", "type_name": "name", "id": "id1", "name": "name1"}],
                [{"type": "type", "type_name": "name", "id": "id2", "name": "name2"}],
            ],
        )

        old_instance = self.instance_factory.new(
            "type",
            "name",
            [
                [{"type": "type", "type_name": "name", "id": "id2", "name": "name2"}],
                [{"type": "type", "type_name": "name", "id": "id3", "name": "name3"}],
            ],
        )

        diff_instance = new_instance.diff(old_instance)

        self.assertEqual(diff_instance.tag, "unchanged")
        self.assertEqual(diff_instance.path[0]["tag"], "add")
        self.assertEqual(diff_instance.path[1]["tag"], "unchanged")
        self.assertEqual(diff_instance.path[2]["tag"], "delete")


class DiffConditionTests(TestCase):
    def setUp(self):
        self.condition_factory = ConditionFactory()
        self.attribute_factory = AttributeFactory()
        self.instance_factory = InstanceFactory()

    def test_condition_diff(self):
        new_condition = self.condition_factory.new(
            instances=[
                self.instance_factory.new(
                    "type", "name", [[{"type": "type", "type_name": "name", "id": "id1", "name": "name1"}]]
                ),
                self.instance_factory.new(
                    "type1", "name", [[{"type": "type1", "type_name": "name", "id": "id1", "name": "name1"}]]
                ),
            ],
            attributes=[
                self.attribute_factory.new("id", "name", [{"id": "id1", "name": "name1"}]),
                self.attribute_factory.new("id1", "name", [{"id": "id1", "name": "name1"}]),
            ],
        )

        old_condition = self.condition_factory.new(
            instances=[
                self.instance_factory.new(
                    "type", "name", [[{"type": "type", "type_name": "name", "id": "id2", "name": "name2"}]]
                ),
                self.instance_factory.new(
                    "type2", "name", [[{"type": "type2", "type_name": "name", "id": "id1", "name": "name1"}]]
                ),
            ],
            attributes=[
                self.attribute_factory.new("id", "name", [{"id": "id1", "name": "name1"}]),
                self.attribute_factory.new("id2", "name", [{"id": "id1", "name": "name1"}]),
            ],
        )

        diff_condition = new_condition.diff(old_condition)

        self.assertEqual(diff_condition.tag, "unchanged")
        self.assertEqual(len(diff_condition.instances), 3)
        self.assertEqual(diff_condition.instances[0].tag, "unchanged")
        self.assertEqual(diff_condition.instances[1].tag, "add")
        self.assertEqual(diff_condition.instances[2].tag, "delete")
        self.assertEqual(len(diff_condition.attributes), 3)
        self.assertEqual(diff_condition.attributes[0].tag, "unchanged")
        self.assertEqual(diff_condition.attributes[1].tag, "add")
        self.assertEqual(diff_condition.attributes[2].tag, "delete")


class CompareConditionTests(TestCase):
    def setUp(self):
        self.condition_factory = ConditionFactory()
        self.attribute_factory = AttributeFactory()
        self.instance_factory = InstanceFactory()

    def test_condition_compare_ok(self):
        old_condition = new_condition = self.condition_factory.example()
        self.assertTrue(new_condition.compare(old_condition))

    def test_export_1_false(self):
        """
        从第一个return返回false
        """
        new_condition = self.condition_factory.new()

        old_condition = self.condition_factory.new(
            instances=[
                self.instance_factory.new(
                    "biz", "", [[{"type": "biz", "type_name": "业务", "id": "biz1", "name": "蓝鲸"}]]
                )
            ]
        )
        self.assertFalse(new_condition.compare(old_condition))

    def test_export_2_false(self):
        new_condition = self.condition_factory.new(
            instances=[
                self.instance_factory.new(
                    "host", "", [[{"type": "biz", "type_name": "业务", "id": "biz1", "name": "蓝鲸"}]]
                )
            ]
        )

        old_condition = self.condition_factory.new(
            instances=[
                self.instance_factory.new(
                    "biz", "", [[{"type": "biz", "type_name": "业务", "id": "biz1", "name": "蓝鲸"}]]
                )
            ]
        )
        self.assertFalse(new_condition.compare(old_condition))

    def test_export_3_false(self):
        new_condition = self.condition_factory.new(
            instances=[
                self.instance_factory.new(
                    "biz",
                    "",
                    [
                        [{"type": "biz", "type_name": "业务", "id": "biz1", "name": "蓝鲸"}],
                        [{"type": "biz", "type_name": "业务", "id": "biz2", "name": "蓝鲸"}],
                    ],
                )
            ]
        )

        old_condition = self.condition_factory.new(
            instances=[
                self.instance_factory.new(
                    "biz", "", [[{"type": "biz", "type_name": "业务", "id": "biz1", "name": "蓝鲸"}]]
                )
            ]
        )
        self.assertFalse(new_condition.compare(old_condition))

    def test_export_4_false(self):
        new_condition = self.condition_factory.new(
            instances=[
                self.instance_factory.new(
                    "biz",
                    "",
                    [
                        [
                            {"type": "biz", "type_name": "业务", "id": "biz1", "name": "蓝鲸"},
                            {"type": "biz", "type_name": "业务", "id": "biz2", "name": "蓝鲸"},
                        ],
                    ],
                )
            ]
        )

        old_condition = self.condition_factory.new(
            instances=[
                self.instance_factory.new(
                    "biz", "", [[{"type": "biz", "type_name": "业务", "id": "biz1", "name": "蓝鲸"}]]
                )
            ]
        )
        self.assertFalse(new_condition.compare(old_condition))

    def test_export_5_false(self):
        new_condition = self.condition_factory.new(
            instances=[
                self.instance_factory.new(
                    "biz", "", [[{"type": "biz", "type_name": "业务", "id": "biz1", "name": "蓝鲸"}]]
                )
            ]
        )

        old_condition = self.condition_factory.new(
            instances=[
                self.instance_factory.new(
                    "biz", "", [[{"type": "biz", "type_name": "业务", "id": "biz2", "name": "蓝鲸"}]]
                )
            ]
        )
        self.assertFalse(new_condition.compare(old_condition))

    def test_export_6_false(self):
        new_condition = self.condition_factory.new(
            attributes=[
                self.attribute_factory.new("id", "", [{"id": "biz1", "name": "蓝鲸"}]),
                self.attribute_factory.new("id", "", [{"id": "biz2", "name": "蓝鲸"}]),
            ]
        )

        old_condition = self.condition_factory.new(
            attributes=[self.attribute_factory.new("id", "", [{"id": "biz1", "name": "蓝鲸"}])]
        )
        self.assertFalse(new_condition.compare(old_condition))

    def test_export_7_false(self):
        new_condition = self.condition_factory.new(
            attributes=[self.attribute_factory.new("host", "", [{"id": "biz1", "name": "蓝鲸"}])]
        )

        old_condition = self.condition_factory.new(
            attributes=[self.attribute_factory.new("biz", "", [{"id": "biz1", "name": "蓝鲸"}])]
        )
        self.assertFalse(new_condition.compare(old_condition))

    def test_export_8_false(self):
        new_condition = self.condition_factory.new(
            attributes=[self.attribute_factory.new("biz", "", [{"id": "biz1", "name": "蓝鲸"}])]
        )

        old_condition = self.condition_factory.new(
            attributes=[
                self.attribute_factory.new("biz", "", [{"id": "biz1", "name": "蓝鲸"}, {"id": "biz2", "name": "蓝鲸"}])
            ]
        )
        self.assertFalse(new_condition.compare(old_condition))

    def test_export_9_false(self):
        new_condition = self.condition_factory.new(
            attributes=[self.attribute_factory.new("biz", "", [{"id": "biz1", "name": "蓝鲸"}])]
        )

        old_condition = self.condition_factory.new(
            attributes=[self.attribute_factory.new("biz", "", [{"id": "biz2", "name": "蓝鲸"}])]
        )
        self.assertFalse(new_condition.compare(old_condition))


class CompareResourceTests(TestCase):
    def test_compare(self):
        new_resource = old_resource = ResourceFactory().example()
        self.assertTrue(new_resource.compare(old_resource))


class InstanceAddRemoveInstance(TestCase):
    def setUp(self):
        self.instance_factory = InstanceFactory()

    def test_add_instance_true(self):
        instance = self.instance_factory.example()

        is_modified = instance.add_instance(
            self.instance_factory.new(
                "host", "主机", [[{"type": "host", "type_name": "主机", "id": "host2", "name": "主机2"}]]
            )
        )

        self.assertTrue(is_modified)
        self.assertEqual(len(instance.path), 2)

    def test_add_instance_false(self):
        instance = self.instance_factory.example()

        is_modified = instance.add_instance(self.instance_factory.example())

        self.assertFalse(is_modified)

    def test_remove_instance_true(self):
        instance = self.instance_factory.new(
            "host",
            "主机",
            [
                [{"type": "host", "type_name": "主机", "id": "host1", "name": "主机1"}],
                [{"type": "host", "type_name": "主机", "id": "host2", "name": "主机2"}],
            ],
        )

        is_modified = instance.remove_instance(self.instance_factory.example())

        self.assertTrue(is_modified)
        self.assertEqual(len(instance.path), 1)

    def test_remove_instance_false(self):
        instance = self.instance_factory.example()

        is_modified = instance.remove_instance(
            self.instance_factory.new(
                "host", "主机", [[{"type": "host", "type_name": "主机", "id": "host2", "name": "主机2"}]]
            )
        )

        self.assertFalse(is_modified)


class ConditionAddRemoveTest(TestCase):
    def setUp(self):
        self.condition_factory = ConditionFactory()
        self.instance_factory = InstanceFactory()

    def test_condition_add_instance_true(self):
        condition = self.condition_factory.new(instances=[self.instance_factory.example()])

        is_modified = condition.add_instance(
            self.instance_factory.new(
                "host", "主机", [[{"type": "host", "type_name": "主机", "id": "host2", "name": "主机2"}]]
            )
        )

        self.assertTrue(is_modified)
        self.assertEqual(len(condition.instances[0].path), 2)

        condition = self.condition_factory.new(instances=[self.instance_factory.example()])

        is_modified = condition.add_instance(
            self.instance_factory.new("业务", "biz", [[{"type": "biz", "type_name": "业务", "id": "biz1", "name": "蓝鲸"}]])
        )

        self.assertTrue(is_modified)
        self.assertEqual(len(condition.instances), 2)

    def test_condition_add_instance_false(self):
        condition = self.condition_factory.new(instances=[self.instance_factory.example()])

        is_modified = condition.add_instance(self.instance_factory.example())

        self.assertFalse(is_modified)

    def test_condition_remove_instance_true(self):
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

        is_modified = condition.remove_instance(self.instance_factory.example())

        self.assertTrue(is_modified)
        self.assertEqual(len(condition.instances[0].path), 1)

    def test_condition_remove_instance_false(self):
        condition = self.condition_factory.new(instances=[self.instance_factory.example()])

        is_modified = condition.remove_instance(
            self.instance_factory.new(
                "host", "主机", [[{"type": "host", "type_name": "主机", "id": "host2", "name": "主机2"}]]
            )
        )

        self.assertFalse(is_modified)


class RelatedResourceAddRemoveInstance(TestCase):
    def setUp(self):
        self.resource_factory = ResourceFactory()
        self.instance_factory = InstanceFactory()
        self.condition_factory = ConditionFactory()
        self.attribute_factory = AttributeFactory()

    def test_add_instance_any(self):
        resource = self.resource_factory.new("bk_cmdb", "host", "主机")

        is_modified = resource.add_instance(self.instance_factory.example())

        self.assertFalse(is_modified)
        self.assertEqual(len(resource.condition), 0)

    def test_add_instance_new_condition(self):
        resource = self.resource_factory.new(
            "bk_cmdb", "host", "主机", [self.condition_factory.new(attributes=[self.attribute_factory.example()])]
        )

        is_modified = resource.add_instance(self.instance_factory.example())

        self.assertTrue(is_modified)

    def test_add_instance_true(self):
        resource = self.resource_factory.new(
            "bk_cmdb", "host", "主机", [self.condition_factory.new(instances=[self.instance_factory.example()])]
        )

        is_modified = resource.add_instance(
            self.instance_factory.new(
                "host", "主机", [[{"type": "host", "type_name": "主机", "id": "host2", "name": "主机2"}]]
            )
        )

        self.assertTrue(is_modified)

    def test_remove_instance_any(self):
        resource = self.resource_factory.new("bk_cmdb", "host", "主机")

        is_modified = resource.remove_instance(self.instance_factory.example())

        self.assertFalse(is_modified)

    def test_remove_instance_true(self):
        resource = self.resource_factory.new(
            "bk_cmdb", "host", "主机", [self.condition_factory.new(instances=[self.instance_factory.example()])]
        )

        is_modified = resource.remove_instance(self.instance_factory.example())

        self.assertTrue(is_modified)
        self.assertTrue(resource.is_empty())


class RelatedResourceTypeTests(TestCase):
    def setUp(self):
        self.instance_selection_factory = InstanceSelectionFactory()
        self.related_resource_type_factory = RelatedResourceTypeFactory()

    def test_filter(self):
        rrt = self.related_resource_type_factory.new(
            "host",
            "bk_cmdb",
            [
                self.instance_selection_factory.new(
                    "test1",
                    "bk_cmdb",
                    True,
                    [
                        {"system_id": "bk_cmdb", "id": "biz"},
                        {"system_id": "bk_cmdb", "id": "set"},
                        {"system_id": "bk_cmdb", "id": "module"},
                        {"system_id": "bk_cmdb", "id": "host"},
                    ],
                ),
                self.instance_selection_factory.new(
                    "test2",
                    "bk_cmdb",
                    True,
                    [{"system_id": "bk_cmdb", "id": "biz"}, {"system_id": "bk_cmdb", "id": "set"}],
                ),
                self.instance_selection_factory.new(
                    "test3",
                    "bk_cmdb",
                    True,
                    [
                        {"system_id": "bk_job", "id": "biz"},
                        {"system_id": "bk_cmdb", "id": "set"},
                        {"system_id": "bk_cmdb", "id": "module"},
                        {"system_id": "bk_cmdb", "id": "host"},
                    ],
                ),
                self.instance_selection_factory.new(
                    "test3",
                    "bk_cmdb",
                    False,
                    [{"system_id": "bk_cmdb", "id": "biz"}, {"system_id": "bk_cmdb", "id": "set"}],
                ),
            ],
        )

        self.assertEqual(len(rrt.instance_selections), 2)

    def test_ignore_iam_none(self):
        rrt = self.related_resource_type_factory.new("host", "system_id", [])
        self.assertEqual(rrt.instance_selections, [])


class InstanceCheckSelection(TestCase):
    def setUp(self):
        self.instance_selection_factory = InstanceSelectionFactory()
        self.instance_factory = InstanceFactory()
        self.resource_factory = ResourceFactory()

    def test_path_display(self):
        instance = self.instance_factory.example()
        path_display = instance._path_display(
            [{"type_name": "type1", "name": "name1"}, {"type_name": "type2", "name": "name2"}]
        )
        self.assertEqual(path_display, "type1:name1/type2:name2")

    def test_check_selections_export_1(self):
        """
        检查实例视图, 实例的节点的类型与资源类型一样
        """
        instance = self.instance_factory.example()
        rrt = self.resource_factory.example()
        selections = [self.instance_selection_factory.new("1", "1", False, [])]
        instance.check_selection_ignore_path(rrt, selections)

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
        instance.check_selection_ignore_path(rrt, selections)

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
        instance.check_selection_ignore_path(rrt, selections)
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
        instance.check_selection_ignore_path(rrt, selections)
        self.assertEqual(len(instance.path[0]), 2)

    def test_check_selections_err(self):
        instance = self.instance_factory.new(
            "host", "主机", [[{"system_id": "bk_cmdb", "type": "set", "type_name": "set", "id": "set1", "name": "set1"}]]
        )
        rrt = self.resource_factory.example()
        selections = [self.instance_selection_factory.example()]
        try:
            instance.check_selection_ignore_path(rrt, selections)
        except CodeException as e:
            self.assertEqual(e.message, "参数校验失败: set:set1 could not match any instance selection")


class InstanceTests(TestCase):
    def setUp(self):
        self.instance_factory = InstanceFactory()

    def test_get_system_set(self):
        instance = self.instance_factory.example()

        self.assertEqual(instance.get_system_set(), {"bk_cmdb"})

    def test_fill_type_name(self):
        instance = self.instance_factory.new(
            "host", "主机", [[{"system_id": "bk_cmdb", "type": "host", "type_name": "主机", "id": "*", "name": "主机1"}]]
        )

        resource_type_dict = ResourceTypeDict(
            data={("bk_cmdb", "host"): {"name": "host_test", "name_en": "host_test_en"}}
        )

        instance.fill_type_name(resource_type_dict)
        self.assertEqual(instance.name, "host_test")
        self.assertEqual(instance.name_en, "host_test_en")
        self.assertEqual(instance.path[0][0]["type_name"], "host_test")
        self.assertEqual(instance.path[0][0]["type_name_en"], "host_test_en")

    def test_fill_node_name(self):
        instance = self.instance_factory.example()

        resource_info_name_dict = {
            ResourceNode(**{"system_id": "bk_cmdb", "type": "host", "id": "host1"}): "host_name"
        }

        instance.fill_node_name(resource_info_name_dict)
        self.assertEqual(instance.path[0][0]["name"], "host_name")

    def test_list_resource_node(self):
        instance = self.instance_factory.example()
        nodes = instance.list_resource_node()
        self.assertEqual(len(nodes), 1)

    def test_contains(self):
        instance = self.instance_factory.example()
        self.assertTrue(instance in instance)

        new_instance = self.instance_factory.new(
            "host", "主机", [[{"system_id": "bk_cmdb", "type": "host", "type_name": "主机", "id": "*", "name": "主机1"}]]
        )

        self.assertFalse(new_instance in instance)

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

        instance -= self.instance_factory.example()

        self.assertEqual(len(instance.path), 1)


class PathHelperTests(TestCase):
    def setUp(self):
        self.instance_selection_factory = InstanceSelectionFactory()
        self.resource_factory = ResourceFactory()

    def test_multi_leaf_node_ok(self):
        """
        测试多级叶子节点相同的情况
        比如用户管理的部门下的部门
        """
        path = [
            {"system_id": "bk_cmdb", "type": "biz"},
            {"system_id": "bk_cmdb", "type": "set"},
            {"system_id": "bk_cmdb", "type": "module"},
            {"system_id": "bk_cmdb", "type": "host"},
            {"system_id": "bk_cmdb", "type": "host"},
        ]

        selection = self.instance_selection_factory.example()

        rrt = self.resource_factory.example()

        helper = PathHelper(path)
        ok, path = helper.check_selection_ignore_path(rrt, selection)

        self.assertTrue(ok)

    def test_multi_leaf_node_false(self):
        """
        测试多级叶子节点相同的情况
        """
        path = [
            {"system_id": "bk_cmdb", "type": "biz"},
            {"system_id": "bk_cmdb", "type": "set"},
            {"system_id": "bk_cmdb", "type": "module"},
            {"system_id": "bk_cmdb", "type": "host"},
            {"system_id": "bk_cmdb", "type": "test"},
        ]

        selection = self.instance_selection_factory.example()

        rrt = self.resource_factory.example()

        helper = PathHelper(path)
        ok, path = helper.check_selection_ignore_path(rrt, selection)

        self.assertFalse(ok)


class ActionTests(TestCase):
    def setUp(self):
        self.action_factory = ActionFactory()


class ResourceInstanceTests(TestCase):
    def setUp(self):
        self.resource_instance_factory = ResourceInstanceFactory()

    def test_get_system_set(self):
        ri = self.resource_instance_factory.example()
        systems = ri.get_system_set()
        self.assertEqual(systems, {"bk_cmdb"})

    def test_fill_type_name(self):
        ri = self.resource_instance_factory.example()
        resource_type_dict = ResourceTypeDict(
            data={("bk_cmdb", "host"): {"name": "host_test", "name_en": "host_test_en"}}
        )
        ri.fill_type_name(resource_type_dict)
        self.assertEqual(ri.type_name, "host_test")
        self.assertEqual(ri.instances[0].path[0][0]["type_name"], "host_test")


class ConditionTests(TestCase):
    def setUp(self):
        self.condition_factory = ConditionFactory()
        self.instance_factory = InstanceFactory()

    def test_merge_instances(self):
        condition = self.condition_factory.example()
        instance = self.instance_factory.new(
            "biz", "业务", [[{"system_id": "bk_cmdb", "type": "biz", "type_name": "业务", "id": "biz1", "name": "业务1"}]]
        )
        condition.merge_instances([instance])
        self.assertEqual(len(condition.instances), 2)

    def test_has_instances(self):
        condition = self.condition_factory.example()
        instance = self.instance_factory.example()
        self.assertTrue(condition.has_instances([instance]))

        instance = self.instance_factory.new(
            "biz", "业务", [[{"system_id": "bk_cmdb", "type": "biz", "type_name": "业务", "id": "biz1", "name": "业务1"}]]
        )
        self.assertFalse(condition.has_instances([instance]))

        instance = self.instance_factory.new(
            "host", "主机", [[{"system_id": "bk_cmdb", "type": "host", "type_name": "主机", "id": "host2", "name": "主机2"}]]
        )
        self.assertFalse(condition.has_instances([instance]))

    def test_remove_instance(self):
        condition = self.condition_factory.example()
        instance = self.instance_factory.example()
        condition.remove_instances([instance])
        self.assertEqual(len(condition.instances), 0)

    def test_list_resource_node(self):
        condition = self.condition_factory.example()
        nodes = condition.list_resource_node()
        self.assertEqual(len(nodes), 1)

    def test_get_system_set(self):
        condition = self.condition_factory.example()
        systems = condition.get_system_set()
        self.assertEqual(systems, {"bk_cmdb"})

        condition = self.condition_factory.new()
        systems = condition.get_system_set()
        self.assertEqual(systems, set())


class RelatedResourceTests(TestCase):
    def setUp(self):
        self.resource_factory = ResourceFactory()
        self.condition_factory = ConditionFactory()
        self.resource_instance_factory = ResourceInstanceFactory()
        self.instance_selection_factory = InstanceSelectionFactory()
        self.attribute_factory = AttributeFactory()

    def test_merge_conditions(self):
        resource = self.resource_factory.new("bk_cmdb", "host", "主机")
        condition = self.condition_factory.example()
        resource.merge_conditions([condition])
        self.assertTrue(resource.is_any())

        resource = self.resource_factory.example()
        resource.merge_conditions([], True)
        self.assertTrue(resource.is_any())

    def test_remove_conditions(self):
        resource = self.resource_factory.new("bk_cmdb", "host", "主机")
        resource.remove_conditions([])
        self.assertTrue(resource.is_empty())

        resource = self.resource_factory.new("bk_cmdb", "host", "主机")
        condition = self.condition_factory.example()
        resource.remove_conditions([condition])
        self.assertTrue(resource.is_any())

        resource = self.resource_factory.example()
        resource.remove_conditions([condition])
        self.assertTrue(resource.is_empty())

    def test_has_conditions(self):
        resource = self.resource_factory.example()
        self.assertFalse(resource.has_conditions([]))

        resource = self.resource_factory.new("bk_cmdb", "host", "主机")
        condition = self.condition_factory.example()
        self.assertTrue(resource.has_conditions([condition]))

        resource = self.resource_factory.example()
        self.assertTrue(resource.has_conditions([condition]))

    def test_set_empty(self):
        resource = self.resource_factory.example()
        resource.set_empty()
        self.assertTrue(resource.is_empty())
        self.assertEqual(len(resource.condition), 0)

    def test_set_tag(self):
        resource = self.resource_factory.example()
        resource.set_tag_update()
        self.assertEqual(resource.get_tag(), "update")

        resource.set_tag_unchanged()
        self.assertEqual(resource.get_tag(), "unchanged")

        resource.set_tag_delete()
        self.assertEqual(resource.get_tag(), "delete")

    def test_fill_resource_node_name(self):
        resource = self.resource_factory.example()

        resource_info_name_dict = {
            ResourceNode(**{"system_id": "bk_cmdb", "type": "host", "id": "host1"}): "host_name"
        }

        resource.fill_resource_node_name(resource_info_name_dict)
        self.assertEqual(resource.condition[0].instances[0].path[0][0]["name"], "host_name")

    def test_list_resource_node(self):
        resource = self.resource_factory.example()
        nodes = resource.list_resource_node()
        self.assertEqual(len(nodes), 1)

    def test_from_resource_instance(self):
        ri = self.resource_instance_factory.example()
        resource = RelatedResource.from_resource_instance(ri)
        self.assertEqual(resource.system_id, "bk_cmdb")
        self.assertEqual(resource.type, "host")

    def test_check_selection_ignore_path(self):
        resource = self.resource_factory.example()
        selection = self.instance_selection_factory.example()
        resource.check_selection_ignore_path([selection])

        resource = self.resource_factory.new(
            "bk_cmdb", "host", "主机", [self.condition_factory.new(attributes=[self.attribute_factory.example()])]
        )
        resource.check_selection_ignore_path([selection])

    def test_get_system_set(self):
        resource = self.resource_factory.example()
        resource.set_empty()
        systems = resource.get_system_set()
        self.assertEqual(systems, {"bk_cmdb"})


class PolicyTests(TestCase):
    def setUp(self):
        self.policy_factory = PolicyFactory()
        self.resource_factory = ResourceFactory()
        self.condition_factory = ConditionFactory()
        self.resource_instance_factory = ResourceInstanceFactory()
        self.attribute_factory = AttributeFactory()

    def test_set_expired_at(self):
        policy = self.policy_factory.example()
        policy.set_expired_at(4102444800)
        self.assertEqual(policy.expired_at, 4102444800)

    def test_set_tag(self):
        policy = self.policy_factory.example()
        policy.set_tag_update()
        self.assertEqual(policy.tag, "update")

        policy.set_tag_unchanged()
        self.assertEqual(policy.tag, "unchanged")

        policy.set_tag_delete()
        self.assertEqual(policy.tag, "delete")

        policy.set_tag_add()
        self.assertEqual(policy.tag, "add")

    def test_to_backend_dict(self):
        policy = self.policy_factory.example()
        data = policy.to_backend_dict()
        self.assertEqual(data["action_id"], "view_host")

    def test_from_db_model(self):
        policy = self.policy_factory.example()
        m = policy.to_db_model("bk_cmdb", Subject(**{"type": "user", "id": "admin"}))
        p = Policy.from_db_model(m)
        self.assertEqual(p.id, "view_host")

    def test_to_db_model(self):
        policy = self.policy_factory.example()
        m = policy.to_db_model("bk_cmdb", Subject(**{"type": "user", "id": "admin"}))
        self.assertEqual(m.action_id, "view_host")

    def test_has(self):
        policy = self.policy_factory.new("create_host", [])
        self.assertTrue(policy.has(policy))

        policy = self.policy_factory.example()
        self.assertTrue(policy.has(policy))

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
        self.assertFalse(new_policy.has(policy))

    def test_diff(self):
        policy = self.policy_factory.new("create_host", [])
        self.assertTrue(policy.diff(policy))

        policy = self.policy_factory.example()
        self.assertTrue(policy.diff(policy))

    def test_fill_resource_node_name(self):
        policy = self.policy_factory.example()

        resource_info_name_dict = {
            ResourceNode(**{"system_id": "bk_cmdb", "type": "host", "id": "host1"}): "host_name"
        }

        policy.fill_resource_node_name(resource_info_name_dict)
        self.assertEqual(policy.related_resource_types[0].condition[0].instances[0].path[0][0]["name"], "host_name")

    def test_add_resources_instance(self):
        policy = self.policy_factory.example()
        ri = self.resource_instance_factory.example()
        self.assertTrue(policy.add_resources_instance([ri]))

    def test_remove_resources_instance(self):
        policy = self.policy_factory.example()
        ri = self.resource_instance_factory.example()
        self.assertFalse(policy.remove_resources_instance([ri]))

    def test_get_system_set(self):
        policy = self.policy_factory.new("create_host", [])
        systems = policy.get_system_set()
        self.assertEqual(systems, set())


class ResourceCreatorActionConfigTests(TestCase):
    def test_get_resource_type_actions_map(self):
        rcac = ResourceCreatorActionConfig(
            **{
                "id": "test",
                "actions": [{"id": "test1", "required": False}, {"id": "test2", "required": False}],
                "sub_resource_types": [
                    {
                        "id": "test3",
                        "actions": [{"id": "test4", "required": False}, {"id": "test5", "required": False}],
                        "sub_resource_types": [],
                    }
                ],
            }
        )

        result = rcac.get_resource_type_actions_map()
        self.assertEqual(
            result,
            {
                "test": [
                    ResourceCreatorSingleAction(**{"id": "test1", "required": False}),
                    ResourceCreatorSingleAction(**{"id": "test2", "required": False}),
                ],
                "test3": [
                    ResourceCreatorSingleAction(**{"id": "test4", "required": False}),
                    ResourceCreatorSingleAction(**{"id": "test5", "required": False}),
                ],
            },
        )
