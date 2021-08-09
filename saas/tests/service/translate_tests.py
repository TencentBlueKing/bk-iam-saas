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

from django.test import TestCase

from backend.service.utils.translate import ResourceExpressionTranslator
from tests.test_util.factory import AttributeFactory, ConditionFactory, InstanceFactory, ResourceFactory


class TransferAttributeTests(TestCase):
    """
    测试_translate_attribute方法
    """

    def setUp(self):
        self.translator = ResourceExpressionTranslator()
        self.attribute_factory = AttributeFactory()

    def test_empty_values_err(self):
        """空值属性"""
        attribute = self.attribute_factory.new_dict("id", "name")

        with self.assertRaises(Exception):
            self.translator._translate_attribute(attribute)

    def test_multi_bool_err(self):
        """多值bool"""
        attribute = self.attribute_factory.new_dict(
            "id", "name", [{"id": True, "name": ""}, {"id": False, "name": ""}]
        )

        with self.assertRaises(Exception):
            self.translator._translate_attribute(attribute)

    def test_wrong_type_err(self):
        """错误的值类型"""
        attribute = self.attribute_factory.new_dict("id", "name", [{"id": set(), "name": ""}])

        with self.assertRaises(Exception):
            self.translator._translate_attribute(attribute)

    def test_string_ok(self):
        """string值"""
        attribute = self.attribute_factory.new_dict(
            "id", "name", [{"id": "id1", "name": ""}, {"id": "id2", "name": ""}]
        )

        expression = self.translator._translate_attribute(attribute)

        self.assertEqual(expression, {"StringEquals": {"id": ["id1", "id2"]}})

    def test_number_ok(self):
        """int float"""
        attribute = self.attribute_factory.new_dict("id", "name", [{"id": 1, "name": ""}, {"id": 1.1, "name": ""}])

        expression = self.translator._translate_attribute(attribute)

        self.assertEqual(expression, {"NumericEquals": {"id": [1, 1.1]}})

    def test_bool_ok(self):
        """bool"""
        attribute = self.attribute_factory.new_dict("id", "name", [{"id": True, "name": ""}])

        expression = self.translator._translate_attribute(attribute)

        self.assertEqual(expression, {"Bool": {"id": [True]}})


class TransferInstanceTests(TestCase):
    """测试_translate_instance方法"""

    def setUp(self):
        self.translator = ResourceExpressionTranslator()
        self.instance_factory = InstanceFactory()

    def test_empty_path_err(self):
        """
        空拓扑路径
        """
        instance = self.instance_factory.new_dict("host", "主机")

        with self.assertRaises(Exception):
            self.translator._translate_instance("host", instance)

    def test_id_ok(self):
        """
        实例id转换
        """
        instance = self.instance_factory.new_dict(
            "host", "主机", [[{"type": "host", "type_name": "主机", "id": "host1", "name": "主机1"}]]
        )

        expression = self.translator._translate_instance("host", instance)

        self.assertEqual(
            expression["StringEquals"]["id"],
            ["host1"],
        )

    def test_id_with_path_ok(self):
        """
        带路径的实例
        """
        instance = self.instance_factory.new_dict(
            "host",
            "主机",
            [
                [
                    {"type": "biz", "type_name": "业务", "id": "biz1", "name": "蓝鲸"},
                    {"type": "host", "type_name": "主机", "id": "host2", "name": "主机2"},
                ],
            ],
        )

        expression = self.translator._translate_instance("host", instance)

        self.assertEqual(expression["AND"]["content"][0], {"StringEquals": {"id": ["host2"]}})
        self.assertEqual(expression["AND"]["content"][1], {"StringPrefix": {"_bk_iam_path_": ["/biz,biz1/"]}})

    def test_path_ok(self):
        """前缀拓扑"""
        instance = self.instance_factory.new_dict(
            "set",
            "集群",
            [
                [
                    {"type": "biz", "type_name": "业务", "id": "biz1", "name": "蓝鲸"},
                    {"type": "set", "type_name": "集群", "id": "set1", "name": "集群1"},
                ],
            ],
        )

        expression = self.translator._translate_instance("host", instance)

        self.assertEqual(expression["StringPrefix"]["_bk_iam_path_"], ["/biz,biz1/set,set1/"])

    def test_path_with_any_id_ok(self):
        """路径中叶子节点为任意"""
        instance = self.instance_factory.new_dict(
            "set",
            "集群",
            [
                [
                    {"type": "biz", "type_name": "业务", "id": "biz1", "name": "蓝鲸"},
                    {"type": "set", "type_name": "集群", "id": "set1", "name": "集群1"},
                    {"type": "host", "type_name": "主机", "id": "*", "name": ""},
                ],
            ],
        )

        expression = self.translator._translate_instance("host", instance)

        self.assertEqual(expression["StringPrefix"]["_bk_iam_path_"], ["/biz,biz1/set,set1/"])

    def test_or_condition_ok(self):
        """组合条件"""
        instance = self.instance_factory.new_dict(
            "host",
            "主机",
            [
                [{"type": "host", "type_name": "主机", "id": "host1", "name": "主机1"}],
                [
                    {"type": "biz", "type_name": "业务", "id": "biz1", "name": "蓝鲸"},
                    {"type": "host", "type_name": "主机", "id": "host2", "name": "主机2"},
                ],
            ],
        )

        expression = self.translator._translate_instance("host", instance)

        self.assertEqual(len(expression["OR"]["content"]), 2)


class TransferConditionTests(TestCase):
    def setUp(self):
        self.translator = ResourceExpressionTranslator()

        self.instance_factory = InstanceFactory()
        self.attribute_factory = AttributeFactory()
        self.condition_factory = ConditionFactory()
        self.resource_factory = ResourceFactory()

    def test_empty_condition_ok(self):
        """
        任意
        """
        resource = self.resource_factory.new_dict("bk_cmdb", "host", "主机")

        expression = self.translator._translate_condition(resource)

        self.assertEqual(
            expression["Any"]["id"],
            [],
        )

    def test_instance_ok(self):
        """
        只有instance
        """
        resource = self.resource_factory.new_dict(
            "bk_cmdb",
            "host",
            "主机",
            [self.condition_factory.new_dict(instances=[self.instance_factory.example().dict()])],
        )

        expression = self.translator._translate_condition(resource)

        self.assertTrue(
            "StringEquals" in expression,
        )

    def test_attribute_ok(self):
        """
        只有attribute
        """
        resource = self.resource_factory.new_dict(
            "bk_cmdb",
            "host",
            "主机",
            [self.condition_factory.new_dict(attributes=[self.attribute_factory.example().dict()])],
        )

        expression = self.translator._translate_condition(resource)
        self.assertTrue(
            "StringEquals" in expression,
        )

    def test_instance_and_attribute_ok(self):
        """
        instance and attribute
        """
        resource = self.resource_factory.new_dict(
            "bk_cmdb",
            "host",
            "主机",
            [
                self.condition_factory.new_dict(
                    attributes=[self.attribute_factory.example().dict()],
                    instances=[self.instance_factory.example().dict()],
                )
            ],
        )

        expression = self.translator._translate_condition(resource)

        self.assertTrue(
            "AND" in expression,
        )

    def test_or_condition_ok(self):
        """
        多个条件组合
        """
        resource = self.resource_factory.new_dict(
            "bk_cmdb",
            "host",
            "主机",
            [
                self.condition_factory.new_dict(instances=[self.instance_factory.example().dict()]),
                self.condition_factory.new_dict(attributes=[self.attribute_factory.example().dict()]),
            ],
        )

        expression = self.translator._translate_condition(resource)

        self.assertTrue(
            "OR" in expression,
        )


class TransferResourcesTests(TestCase):
    def test_translate_ok(self):
        resources = [ResourceFactory().example().dict()]

        translator = ResourceExpressionTranslator()

        expression = translator.translate(resources)
        self.assertEqual(
            expression,
            json.dumps(
                [
                    {
                        "system": "bk_cmdb",
                        "type": "host",
                        "expression": {
                            "AND": {
                                "content": [{"StringEquals": {"id": ["host1"]}}, {"StringEquals": {"os": ["linux"]}}]
                            }
                        },
                    }
                ],
                separators=(",", ":"),
            ),
        )
