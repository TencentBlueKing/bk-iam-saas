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

from collections import defaultdict
from typing import Any, Dict, List, Type

from backend.common.error_codes import error_codes
from backend.service.constants import ANY_ID, PolicyEnvConditionType
from backend.util.json import json_dumps

from .environment import BaseEnvCondition, HMSEnvCondition, TZEnvCondition, WeekdayEnvCondition

ENV_TYPE_CONDITION_MAP: Dict[str, Type[BaseEnvCondition]] = {
    PolicyEnvConditionType.TZ.value: TZEnvCondition,
    PolicyEnvConditionType.HMS.value: HMSEnvCondition,
    PolicyEnvConditionType.WEEKDAY.value: WeekdayEnvCondition,
}


class ResourceExpressionTranslator:
    """
    翻译资源条件到后端表达式
    """

    def translate(self, system_id: str, resource_groups: List[Dict]) -> str:
        """
        resource_groups: [
          {
            "id: "",
            "related_resource_types": [
              {
                "system_id": "string",
                "type": "string",
                "name": "string",
                "condition": [
                  {
                    "id": "string",
                    "instances": [
                      {
                        "type": "string",
                        "name": "string",
                        "path": [
                          [
                            {
                              "type": "string",
                              "type_name": "string",
                              "id": "string",
                              "name": "string"
                            }
                          ]
                        ]
                      }
                    ],
                    "attributes": [
                      {
                        "id": "string",
                        "name": "string",
                        "values": [
                          {
                            "id": "string",
                            "name": "string"
                          }
                        ]
                      }
                    ]
                  }
                ]
              }
            ]
          }
        ]
        """
        content = [self._translate_resource_group(system_id, r) for r in resource_groups]
        if len(content) == 0:
            expression: Any = content
        elif len(content) == 1:
            expression = content[0]
        else:
            expression = {"OR": {"content": content}}

        return json_dumps(expression)

    def _translate_resource_group(self, system_id: str, resource_group: Dict[str, Any]) -> Dict[str, Any]:
        content = [self._translate_related_resource_types(resource_group["related_resource_types"])]
        env_expressions = self._translate_environments(system_id, resource_group["environments"])
        content.extend(env_expressions)
        if len(content) == 1:
            return content[0]

        return {"AND": {"content": content}}

    def _translate_environments(self, system_id: str, environments: List[Dict[str, Any]]) -> List[Dict]:
        expressions = []
        for env in environments:
            for condition in env["condition"]:
                translator = ENV_TYPE_CONDITION_MAP[condition["type"]](
                    system_id, [v["value"] for v in condition["values"]]
                )
                expressions.extend(translator.trans())
        return expressions

    def _translate_related_resource_types(self, related_resource_types: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        转换一个 resource_group 中的条件
        """
        content = [self._translate_condition(r) for r in related_resource_types]
        if len(content) == 1:
            return content[0]

        return {"AND": {"content": content}}

    def _translate_condition(self, resource: Dict) -> Dict:  # noqa: C901, PLR0912
        """
        表达式转换，转换 SaaS 的条件为后端的表达式
        """
        system_id, _type = resource["system_id"], resource["type"]

        # 条件为空，表示任意
        if len(resource["condition"]) == 0:
            return {"Any": {self._gen_field_name(system_id, _type, "id"): []}}

        content = []

        for c in resource["condition"]:  # 多个项之间是 OR
            # 转换实例选择，每个 path 中的链路之间是 OR
            instance_content = []
            for i in c["instances"]:
                instance_content.append(self._translate_instance(system_id, _type, i))

            if len(instance_content) == 0:
                instance = {}
            elif len(instance_content) == 1:
                instance = instance_content[0]
            else:
                instance = {"OR": {"content": instance_content}}

            # 转换属性选择，每个属性之间是 AND
            attribute_content = []
            for a in c["attributes"]:
                attribute_content.append(self._translate_attribute(system_id, _type, a))

            if len(attribute_content) == 0:
                attribute = {}
            elif len(attribute_content) == 1:
                attribute = attribute_content[0]
            else:
                attribute = {"AND": {"content": attribute_content}}

            # instance 与 attribute 之间 AND
            if instance and attribute:
                content.append({"AND": {"content": [instance, attribute]}})
                continue

            if instance and not attribute:
                content.append(instance)
                continue

            if not instance and attribute:
                content.append(attribute)
                continue

            raise error_codes.INVALID_ARGS.format("instance and attribute must not be both empty")

        if len(content) == 1:
            return content[0]

        # 多组 condition 之间是 OR
        return {"OR": {"content": content}}

    def _gen_field_name(self, system_id: str, _type: str, _id: str):
        return ".".join([system_id, _type, _id])

    def _translate_attribute(self, system_id: str, _type: str, attribute: Dict) -> Dict:
        """
        转换单个 attribute
        """
        values = [one["id"] for one in attribute["values"]]

        if len(values) == 0:
            raise error_codes.INVALID_ARGS.format("values must not empty")

        if isinstance(values[0], bool):
            # bool 属性值只能有一个
            if len(values) != 1:
                raise error_codes.INVALID_ARGS.format("bool value must has one")
            return {"Bool": {self._gen_field_name(system_id, _type, attribute["id"]): values}}

        if isinstance(values[0], (int, float)):
            return {"NumericEquals": {self._gen_field_name(system_id, _type, attribute["id"]): values}}

        if isinstance(values[0], str):
            return {"StringEquals": {self._gen_field_name(system_id, _type, attribute["id"]): values}}

        raise error_codes.INVALID_ARGS.format("values only support (bool, int, float, str)")

    def _translate_instance(self, system_id: str, _type: str, instance: Dict) -> Dict[str, Any]:
        """
        转换单个 instance
        """
        content: List[Dict[str, Any]] = []

        ids = []  # 合并只有 id 的条件
        paths = []  # 合并最后一级为*的 path
        path_ids = defaultdict(list)  # 合并 path 相同的 id

        for p in instance["path"]:
            # 最后一个节点是叶子节点
            if p[-1]["type"] == _type:
                # 如果路径上只有一个节点，且为叶子节点，直接使用 StringEquals
                if len(p) == 1:
                    ids.append(p[0]["id"])
                else:
                    valid_path_without_last_node(p[:-1])

                    path = translate_path(p[:-1])

                    # 如果叶子节点是任意，只是用路径 StringPrefix
                    if p[-1]["id"] == ANY_ID:
                        paths.append(path)
                        continue

                    # 具有相同路径前缀的叶子节点，聚合到一个 AND 的条件中
                    path_ids[path].append(p[-1]["id"])
            else:
                valid_path_without_last_node(p)

                paths.append(translate_path(p))

        if ids:
            content.append({"StringEquals": {self._gen_field_name(system_id, _type, "id"): ids}})

        if paths:
            content.append({"StringPrefix": {self._gen_field_name(system_id, _type, "_bk_iam_path_"): paths}})

        for path, ids in path_ids.items():
            content.append(
                {
                    "AND": {
                        "content": [
                            {"StringEquals": {self._gen_field_name(system_id, _type, "id"): ids}},
                            {"StringPrefix": {self._gen_field_name(system_id, _type, "_bk_iam_path_"): [path]}},
                        ]
                    }
                }
            )

        if len(content) == 0:
            raise error_codes.INVALID_ARGS.format("instance path must not be empty")

        if len(content) == 1:
            return content[0]

        return {"OR": {"content": content}}


def translate_path(path_nodes: List[Dict]) -> str:
    """
    转换 path 层级到字符串表示
    """
    path = ["/"]
    for n in path_nodes:
        path.append("{},{}/".format(n["type"], n["id"]))
    return "".join(path)


def valid_path_without_last_node(path_nodes: List[Dict]):
    """
    校验路径数据，必须排除路径最后的叶子节点 (叶子节点是可以为 * 的)

    1. 路径的中间节点不能为 *
    2. 路径中不能存在重复的节点
    """
    node_set = set()

    for n in path_nodes:
        # 校验节点数据不能重复
        ns = "{},{}".format(n["type"], n["id"])
        if ns in node_set:
            raise error_codes.INVALID_ARGS.format("path: {} nodes must not repeat".format(translate_path(path_nodes)))

        node_set.add(ns)
