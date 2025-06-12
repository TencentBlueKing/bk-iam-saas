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
from typing import Dict, List, Optional

import pytest
from blue_krill.web.std_error import APIError
from django.test import TestCase

from backend.service.utils.translate import ResourceExpressionTranslator, valid_path_without_last_node


def new_attribute_dict(_id: str, name: str, values: Optional[List[Dict]] = None) -> Dict:
    return {"id": _id, "name": name, "values": values or []}


class TransferAttributeTests(TestCase):
    """
    测试_translate_attribute方法
    """

    def setUp(self):
        self.translator = ResourceExpressionTranslator()

    def test_empty_values_err(self):
        """空值属性"""
        attribute = new_attribute_dict("id", "name")

        with pytest.raises(APIError):
            self.translator._translate_attribute("system", "type", attribute)

    def test_multi_bool_err(self):
        """多值bool"""
        attribute = new_attribute_dict("id", "name", [{"id": True, "name": ""}, {"id": False, "name": ""}])

        with pytest.raises(APIError):
            self.translator._translate_attribute("system", "type", attribute)

    def test_wrong_type_err(self):
        """错误的值类型"""
        attribute = new_attribute_dict("id", "name", [{"id": set(), "name": ""}])

        with pytest.raises(APIError):
            self.translator._translate_attribute("system", "type", attribute)

    def test_string_ok(self):
        """string值"""
        attribute = new_attribute_dict("id", "name", [{"id": "id1", "name": ""}, {"id": "id2", "name": ""}])

        expression = self.translator._translate_attribute("system", "type", attribute)

        self.assertEqual(expression, {"StringEquals": {"system.type.id": ["id1", "id2"]}})

    def test_number_ok(self):
        """int float"""
        attribute = new_attribute_dict("id", "name", [{"id": 1, "name": ""}, {"id": 1.1, "name": ""}])

        expression = self.translator._translate_attribute("system", "type", attribute)

        self.assertEqual(expression, {"NumericEquals": {"system.type.id": [1, 1.1]}})

    def test_bool_ok(self):
        """bool"""
        attribute = new_attribute_dict("id", "name", [{"id": True, "name": ""}])

        expression = self.translator._translate_attribute("system", "type", attribute)

        self.assertEqual(expression, {"Bool": {"system.type.id": [True]}})


def new_instance_dict(_type: str, name: str, paths: Optional[List[List[Dict]]] = None) -> Dict:
    return {
        "name": name,
        "type": _type,
        "path": paths or [],
    }


class TransferInstanceTests(TestCase):
    """测试_translate_instance方法"""

    def setUp(self):
        self.translator = ResourceExpressionTranslator()

    def test_empty_path_err(self):
        """
        空拓扑路径
        """
        instance = new_instance_dict("host", "主机")

        with pytest.raises(APIError):
            self.translator._translate_instance("system", "host", instance)

    def test_id_ok(self):
        """
        实例id转换
        """
        instance = new_instance_dict(
            "host", "主机", [[{"type": "host", "type_name": "主机", "id": "host1", "name": "主机1"}]]
        )

        expression = self.translator._translate_instance("system", "host", instance)

        self.assertEqual(
            expression["StringEquals"]["system.host.id"],
            ["host1"],
        )

    def test_id_with_path_ok(self):
        """
        带路径的实例
        """
        instance = new_instance_dict(
            "host",
            "主机",
            [
                [
                    {"type": "biz", "type_name": "业务", "id": "biz1", "name": "蓝鲸"},
                    {"type": "host", "type_name": "主机", "id": "host2", "name": "主机2"},
                ],
            ],
        )

        expression = self.translator._translate_instance("system", "host", instance)

        self.assertEqual(expression["AND"]["content"][0], {"StringEquals": {"system.host.id": ["host2"]}})
        self.assertEqual(
            expression["AND"]["content"][1], {"StringPrefix": {"system.host._bk_iam_path_": ["/biz,biz1/"]}}
        )

    def test_path_ok(self):
        """前缀拓扑"""
        instance = new_instance_dict(
            "set",
            "集群",
            [
                [
                    {"type": "biz", "type_name": "业务", "id": "biz1", "name": "蓝鲸"},
                    {"type": "set", "type_name": "集群", "id": "set1", "name": "集群1"},
                ],
            ],
        )

        expression = self.translator._translate_instance("system", "host", instance)

        self.assertEqual(expression["StringPrefix"]["system.host._bk_iam_path_"], ["/biz,biz1/set,set1/"])

    def test_path_with_any_id_ok(self):
        """路径中叶子节点为任意"""
        instance = new_instance_dict(
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

        expression = self.translator._translate_instance("system", "host", instance)

        self.assertEqual(expression["StringPrefix"]["system.host._bk_iam_path_"], ["/biz,biz1/set,set1/"])

    def test_or_condition_ok(self):
        """组合条件"""
        instance = new_instance_dict(
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

        expression = self.translator._translate_instance("system", "host", instance)

        self.assertEqual(len(expression["OR"]["content"]), 2)


def new_resource_dict(system_id: str, _type: str, name: str, condition: Optional[List[Dict]] = None) -> Dict:
    return {"system_id": system_id, "type": _type, "name": name, "condition": condition or []}


def new_condition_dict(instances: Optional[List[Dict]] = None, attributes: Optional[List[Dict]] = None) -> Dict:
    return {"instances": instances or [], "attributes": attributes or []}


class TransferConditionTests(TestCase):
    def setUp(self):
        self.translator = ResourceExpressionTranslator()

    def test_empty_condition_ok(self):
        """
        任意
        """
        resource = new_resource_dict("bk_cmdb", "host", "主机")

        expression = self.translator._translate_condition(resource)

        self.assertEqual(
            expression["Any"]["bk_cmdb.host.id"],
            [],
        )

    def test_instance_ok(self):
        """
        只有instance
        """
        resource = new_resource_dict(
            "bk_cmdb",
            "host",
            "主机",
            [
                new_condition_dict(
                    instances=[
                        new_instance_dict(
                            "host",
                            "主机",
                            [
                                [
                                    {
                                        "system_id": "bk_cmdb",
                                        "type": "host",
                                        "type_name": "主机",
                                        "id": "host1",
                                        "name": "主机1",
                                    }
                                ]
                            ],
                        )
                    ]
                )
            ],
        )

        expression = self.translator._translate_condition(resource)

        self.assertTrue(
            "StringEquals" in expression,
        )

    def test_attribute_ok(self):
        """
        只有attribute
        """
        resource = new_resource_dict(
            "bk_cmdb",
            "host",
            "主机",
            [new_condition_dict(attributes=[new_attribute_dict("os", "os", [{"id": "linux", "name": "linux"}])])],
        )

        expression = self.translator._translate_condition(resource)
        self.assertTrue(
            "StringEquals" in expression,
        )

    def test_instance_and_attribute_ok(self):
        """
        instance and attribute
        """
        resource = new_resource_dict(
            "bk_cmdb",
            "host",
            "主机",
            [
                new_condition_dict(
                    attributes=[new_attribute_dict("os", "os", [{"id": "linux", "name": "linux"}])],
                    instances=[
                        new_instance_dict(
                            "host",
                            "主机",
                            [
                                [
                                    {
                                        "system_id": "bk_cmdb",
                                        "type": "host",
                                        "type_name": "主机",
                                        "id": "host1",
                                        "name": "主机1",
                                    }
                                ]
                            ],
                        )
                    ],
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
        resource = new_resource_dict(
            "bk_cmdb",
            "host",
            "主机",
            [
                new_condition_dict(
                    instances=[
                        new_instance_dict(
                            "host",
                            "主机",
                            [
                                [
                                    {
                                        "system_id": "bk_cmdb",
                                        "type": "host",
                                        "type_name": "主机",
                                        "id": "host1",
                                        "name": "主机1",
                                    }
                                ]
                            ],
                        )
                    ]
                ),
                new_condition_dict(attributes=[new_attribute_dict("os", "os", [{"id": "linux", "name": "linux"}])]),
            ],
        )

        expression = self.translator._translate_condition(resource)

        self.assertTrue(
            "OR" in expression,
        )


class TransferResourcesTests(TestCase):
    def test_translate_ok(self):
        resources = [
            new_resource_dict(
                "bk_cmdb",
                "host",
                "主机",
                [
                    new_condition_dict(
                        attributes=[new_attribute_dict("os", "os", [{"id": "linux", "name": "linux"}])],
                        instances=[
                            new_instance_dict(
                                "host",
                                "主机",
                                [
                                    [
                                        {
                                            "system_id": "bk_cmdb",
                                            "type": "host",
                                            "type_name": "主机",
                                            "id": "host1",
                                            "name": "主机1",
                                        }
                                    ]
                                ],
                            )
                        ],
                    )
                ],
            )
        ]

        translator = ResourceExpressionTranslator()

        expression = translator.translate("bk_cmdb", [{"related_resource_types": resources, "environments": []}])
        self.assertEqual(
            expression,
            json.dumps(
                {
                    "AND": {
                        "content": [
                            {"StringEquals": {"bk_cmdb.host.id": ["host1"]}},
                            {"StringEquals": {"bk_cmdb.host.os": ["linux"]}},
                        ]
                    }
                },
                separators=(",", ":"),
            ),
        )

    def test_environment_ok(self):
        env = [
            {
                "condition": [
                    {"type": "tz", "values": [{"value": "Asia/Shanghai"}]},
                    {"type": "hms", "values": [{"value": "00:00:00"}, {"value": "12:00:00"}]},
                    {"type": "weekday", "values": [{"value": 0}, {"value": 1}, {"value": 3}]},
                ]
            }
        ]

        translator = ResourceExpressionTranslator()
        exp = translator._translate_environments("bk_cmdb", env)
        assert exp == [
            {"StringEquals": {"bk_cmdb._bk_iam_env_.tz": ["Asia/Shanghai"]}},
            {"NumericGte": {"bk_cmdb._bk_iam_env_.hms": [0]}},
            {"NumericLte": {"bk_cmdb._bk_iam_env_.hms": [120000]}},
            {"NumericEquals": {"bk_cmdb._bk_iam_env_.weekday": [0, 1, 3]}},
        ]


class TestValidPathWithoutLastNode:
    def test_node_repeat(self):
        nodes = [{"type": "type1", "id": "id1"}, {"type": "type1", "id": "id2"}, {"type": "type1", "id": "id1"}]
        with pytest.raises(APIError):
            valid_path_without_last_node(nodes)

    def test_ok(self):
        nodes = [{"type": "type1", "id": "id1"}, {"type": "type1", "id": "id2"}]
        valid_path_without_last_node(nodes)
