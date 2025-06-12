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
from typing import Dict, List, Tuple, Union

from django.db import models

from backend.apps.model_builder.constants import ModelSectionEnum, ModelSectionTypeDict, ModelSectionTypeList
from backend.common.models import BaseModel
from backend.util.json import json_dumps


class MockSystemModel(BaseModel):
    """页面接入建模数据
    注意: 同一个人可以创建多个, 只需要sysetm_id不一样即可; system_id+owner唯一
    """

    system_id = models.CharField("系统ID(system_id)", max_length=128, default="test")
    owner = models.CharField("所有者", max_length=64)
    _data = models.TextField("模型数据", db_column="data")

    class Meta:
        verbose_name = "页面接入建模数据"
        verbose_name_plural = "页面接入建模数据"

        unique_together = ["system_id", "owner"]

    @property
    def system(self) -> Dict:
        return self.data.get(ModelSectionEnum.SYSTEM.value, {})

    @property
    def data(self) -> Dict:
        if not self._data:
            return {}
        return json.loads(self._data)

    @data.setter
    def data(self, data: Dict):
        self._data = json_dumps(data)

    def add_or_update_section(self, section: str, data: Union[List, Dict]) -> None:
        """
        {
            "system": {},
            "common_actions": {},
            "action_groups": {},
            "resource_type": [{id=x}, {id=y}],
            "action": [{id=x}, {id=y}],
            "instance_selection": [{id=x}, {id=y}]
        }
        """
        # do set key=value
        if section in ModelSectionTypeDict:
            self._set_section(section, data)

        # append v3 data into key=[v1, v2]
        if section in ModelSectionTypeList:
            assert isinstance(data, Dict)
            self._update_or_append_record_to_section(section, data["id"], data)

    def delete_from_section(self, section: str, _id: str) -> None:
        # del key
        if section in ModelSectionTypeDict:
            self._delete_section(section)

        # del v2 from key=[v1, v2, v3]
        if section in ModelSectionTypeList:
            self._delete_record_from_section(section, _id)

    def ids_exists_in_section(self, section: str, ids: List[str]) -> Tuple[bool, str]:
        data = self.data
        if not data.get(section):
            return False, f"section {section} not exists"

        if section not in ModelSectionTypeList:
            return False, f"section {section} not support"

        s = set()
        for record in data[section]:
            s.add(record["id"])

        for id in ids:
            if id not in s:
                return False, f"id {id} not exist"

        return True, "ok"

    # system / action_groups / common_actions 直接set
    def _set_section(self, section: str, data: Union[List, Dict]) -> None:
        x = self.data
        x[section] = data
        self.data = x

    def _delete_section(self, section: str) -> None:
        x = self.data
        if section in x:
            del x[section]
            self.data = x

    def _delete_record_from_section(self, section: str, _id: str) -> None:
        id_exists_idx = -1
        for idx, record in enumerate(self.data[section]):
            if record["id"] == _id:
                id_exists_idx = idx
                break

        if id_exists_idx != -1:
            x = self.data
            del x[section][id_exists_idx]
            self.data = x
            return

    # resource_type / instance_selection / action 保存下来是列表, 需要根据ID set或更新
    def _update_or_append_record_to_section(self, section: str, _id: str, data: Union[List, Dict]) -> None:
        section_data = self.data.get(section)
        if not section_data:
            self._set_section(section, [data])
            return

        id_exists_idx = -1
        for idx, record in enumerate(self.data[section]):
            if record["id"] == _id:
                id_exists_idx = idx
                break

        x = self.data
        if id_exists_idx == -1:
            x[section].append(data)
        else:
            x[section][id_exists_idx] = data
        self.data = x

    def data_to_preview_json(self) -> List[Dict]:
        data = self.data

        # 有序的, 必须保证顺序
        preview_json = []
        if data.get(ModelSectionEnum.SYSTEM.value):
            preview_json.append(
                {
                    "type": ModelSectionEnum.SYSTEM.value,
                    "name": ModelSectionEnum.get_choice_label(ModelSectionEnum.SYSTEM.value),
                    "data": data.get(ModelSectionEnum.SYSTEM.value),
                }
            )

        _list_type = [
            ModelSectionEnum.RESOURCE_TYPE.value,
            ModelSectionEnum.INSTANCE_SELECTION.value,
            ModelSectionEnum.ACTION.value,
            ModelSectionEnum.ACTION_GROUPS.value,
            ModelSectionEnum.COMMON_ACTIONS.value,
        ]

        for _type in _list_type:
            if data.get(_type):
                preview_json.append(
                    {"type": _type, "name": ModelSectionEnum.get_choice_label(_type), "data": data.get(_type)}
                )

        return preview_json

    def data_to_migrate_json(self) -> Dict:
        data = self.data

        json_data = {"system_id": data["system"]["id"], "operations": []}

        # NOTE: the order matters

        if data.get(ModelSectionEnum.SYSTEM.value):
            json_data["operations"].append({"operation": "upsert_system", "data": data[ModelSectionEnum.SYSTEM.value]})

        _list_type_operation = [
            (ModelSectionEnum.RESOURCE_TYPE.value, "upsert_resource_type"),
            (ModelSectionEnum.INSTANCE_SELECTION.value, "upsert_instance_selection"),
            (ModelSectionEnum.ACTION.value, "upsert_action"),
        ]

        for _type, op in _list_type_operation:
            if data.get(_type):
                for d in data[_type]:
                    json_data["operations"].append({"operation": op, "data": d})

        _dict_type_operation = [
            (ModelSectionEnum.ACTION_GROUPS.value, "upsert_action_groups"),
            (ModelSectionEnum.COMMON_ACTIONS.value, "upsert_common_actions"),
        ]

        for _type, op in _dict_type_operation:
            if data.get(_type):
                json_data["operations"].append({"operation": op, "data": data[_type]})

        return json_data
