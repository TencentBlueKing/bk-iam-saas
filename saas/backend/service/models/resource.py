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

from typing import Any, Dict, List

from pydantic import BaseModel, Field, validator

ATTRIBUTE_OPERATOR_NAMES = {
    "eq": "Equal",
    "in": "In",
    "starts_with": "Starts with",
    "contains": "Contains",
}


class SystemProviderConfig(BaseModel):
    auth: str
    token: str
    host: str
    healthz: str = ""


class ResourceTypeProviderConfig(BaseModel):
    path: str


class ResourceAttributeOperator(BaseModel):
    id: str
    name: str


class ResourceAttribute(BaseModel):
    id: str
    display_name: str
    type: str = "STRING"
    operators: List[ResourceAttributeOperator] = Field(
        default_factory=lambda: [ResourceAttributeOperator(id="eq", name=ATTRIBUTE_OPERATOR_NAMES["eq"])]
    )

    @validator("type", pre=True, always=True)
    def validate_type(cls, value):  # noqa: N805
        value = (value or "STRING").upper()
        if value not in {"STRING", "USER", "DEPT"}:
            raise ValueError("type only supports STRING, USER and DEPT")
        return value

    @validator("operators", pre=True, always=True)
    def normalize_operators(cls, value):  # noqa: N805
        value = value or ["eq"]
        operators = []
        for operator in value:
            if isinstance(operator, str):
                if operator not in ATTRIBUTE_OPERATOR_NAMES:
                    raise ValueError(f"unsupported operator: {operator}")
                operators.append({"id": operator, "name": ATTRIBUTE_OPERATOR_NAMES.get(operator, operator)})
            else:
                operator_data = dict(operator)
                operator_id = operator_data.get("id", "")
                if operator_id not in ATTRIBUTE_OPERATOR_NAMES:
                    raise ValueError(f"unsupported operator: {operator_id}")
                operator_data["name"] = operator_data.get("name") or ATTRIBUTE_OPERATOR_NAMES.get(
                    operator_id, operator_id
                )
                operators.append(operator_data)
        return operators


class ResourceAttributeValue(BaseModel):
    id: str
    display_name: str


class ResourceInstanceBaseInfo(BaseModel):
    id: str
    display_name: str
    child_type: str = ""


class ResourceInstanceInfo(BaseModel):
    id: str
    # 由于查询某个资源的属性接口是动态传入要查询的属性，属性key是不固定的，属性值可能是list[str/bool/int]/str/bool/int
    attributes: Dict[str, Any]


class ResourceApproverAttribute(BaseModel):
    id: str
    approver: List[str]
