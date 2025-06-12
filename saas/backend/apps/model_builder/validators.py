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

from collections import defaultdict
from typing import Dict, List, Tuple

from django.utils.translation import gettext as _

from backend.apps.model_builder.constants import ModelSectionEnum
from backend.apps.model_builder.models import MockSystemModel
from backend.common.error_codes import error_codes
from backend.service.constants import SelectionMode
from backend.service.instance_selection import InstanceSelectionService
from backend.service.resource_type import ResourceTypeService


def validate_system(_id: str, data: Dict):
    model = MockSystemModel.objects.get(id=_id)

    if data.get("id") != model.system_id:
        raise error_codes.VALIDATE_ERROR.format("system id can't be changed")


def validate_action(_id: str, data: Dict):
    model = MockSystemModel.objects.get(id=_id)

    # if related_actions not empty, check all action_id exists
    if data.get("related_actions"):
        valid, message = model.ids_exists_in_section(ModelSectionEnum.ACTION.value, data["related_actions"])
        if not valid:
            raise error_codes.VALIDATE_ERROR.format(
                f"check id from model section {ModelSectionEnum.ACTION.value} fail: {message}"
            )

    # if related_resource_types not empty
    if data.get("related_resource_types"):
        for related_resource_type in data["related_resource_types"]:
            rt_system_id = related_resource_type["system_id"]
            rt_id = related_resource_type["id"]

            # 1. system resource_type exists
            _system_id_resource_type_id_exists(model, rt_system_id, rt_id)

            if related_resource_type.get("selection_mode") in (
                "",
                SelectionMode.ALL.value,
                SelectionMode.INSTANCE.value,
            ):
                if not related_resource_type.get("related_instance_selections"):
                    raise error_codes.VALIDATE_ERROR.format(
                        f"system_id:{rt_system_id}/id:{rt_id}'s selection_mode is empty/all/instance, "
                        "related_instance_selections should not be empty"
                    )

                for instance_selection in related_resource_type["related_instance_selections"]:
                    is_system_id = instance_selection["system_id"]
                    is_id = instance_selection["id"]

                    # 2. instance_selection exists
                    _system_id_instance_selection_id_exists(model, is_system_id, is_id)


def _system_id_instance_selection_id_exists(
    model: MockSystemModel, system_id: str, instance_selection_id: str
) -> None:
    if system_id == model.data["system"]["id"]:
        valid, _ = model.ids_exists_in_section(ModelSectionEnum.INSTANCE_SELECTION.value, [instance_selection_id])
        if not valid:
            raise error_codes.VALIDATE_ERROR.format(
                f"resource_type system_id={system_id}, id={instance_selection_id} not exist in model"
            )
    else:
        svc = InstanceSelectionService()
        data = svc.list_raw_by_system(system_id)

        for instance_selection in data:
            if instance_selection_id == instance_selection.id:
                return

        raise error_codes.VALIDATE_ERROR.format(
            f"instance_selection system_id={system_id}, id={instance_selection_id} "
            "not exist in system={system_id}'s model"
        )


def _system_id_resource_type_id_exists(model: MockSystemModel, system_id: str, resource_type_id: str) -> None:
    # my own system
    if system_id == model.data["system"]["id"]:
        valid, _ = model.ids_exists_in_section(ModelSectionEnum.RESOURCE_TYPE.value, [resource_type_id])
        if not valid:
            raise error_codes.VALIDATE_ERROR.format(
                f"resource_type system_id={system_id}, id={resource_type_id} not exist in model"
            )
    # external system
    else:
        svc = ResourceTypeService()
        data = svc.get_system_resource_type_list_map([system_id])

        resource_type_dict: Dict[Tuple[str, str], Dict] = defaultdict(dict)
        for _system_id, resource_types in data.items():
            for rt in resource_types:
                resource_type_dict[(_system_id, rt.id)] = rt

        if (system_id, resource_type_id) not in resource_type_dict:
            raise error_codes.VALIDATE_ERROR.format(
                f"resource_type system_id={system_id}, id={resource_type_id} not exist in model"
            )


def validate_instance_selection(_id: str, data: Dict):
    """
    check all the resource_types in chain exist
    """
    model = MockSystemModel.objects.get(id=_id)
    for resource_type in data["resource_type_chain"]:
        system_id = resource_type["system_id"]
        rt_id = resource_type["id"]

        _system_id_resource_type_id_exists(model, system_id, rt_id)


def validate_common_actions(_id: str, data: List):
    s = set()
    for common_action in data:
        for action in common_action["actions"]:
            s.add(action["id"])

    # check all the action_id in s exists!!!!
    model = MockSystemModel.objects.get(id=_id)
    valid, message = model.ids_exists_in_section(ModelSectionEnum.ACTION.value, s)
    if not valid:
        raise error_codes.VALIDATE_ERROR.format(
            f"check id from model section {ModelSectionEnum.ACTION.value} fail: {message}"
        )


def validate_actions_groups(_id: str, data: List):
    s = set()
    for d in data:
        for action in d["actions"]:
            if action["id"] in s:
                raise error_codes.VALIDATE_ERROR.format(f"duplicate action_id={action['id']} in actions")
            s.add(action["id"])

        if d.get("sub_groups"):
            for group in d["sub_groups"]:
                for action in group["actions"]:
                    if action["id"] in s:
                        raise error_codes.VALIDATE_ERROR.format(
                            f"duplicate action_id={action['id']} in sub_groups.actions"
                        )
                    s.add(action["id"])

    # check all the action_id in s exists!!!!
    model = MockSystemModel.objects.get(id=_id)
    valid, message = model.ids_exists_in_section(ModelSectionEnum.ACTION.value, s)
    if not valid:
        raise error_codes.VALIDATE_ERROR.format(
            f"check id from model section {ModelSectionEnum.ACTION.value} fail: {message}"
        )


def _get_actions_from_common_actions(data: Dict) -> List[str]:
    common_actions = data.get(ModelSectionEnum.COMMON_ACTIONS.value)
    if not common_actions:
        return []

    actions = []
    for d in common_actions:
        actions.extend(d.get("actions", []))

    return [a["id"] for a in actions]


def _get_actions_from_action_groups(data: Dict) -> List[str]:
    action_groups = data.get(ModelSectionEnum.ACTION_GROUPS.value)
    if not action_groups:
        return []

    actions = []
    for d in action_groups:
        for aid in d["actions"]:
            actions.append(aid["id"])

        for sd in d.get("sub_groups", []):
            for said in sd["actions"]:
                actions.append(said["id"])
    return actions


def _get_resource_types_from_action(data: Dict) -> List[Tuple[str, str]]:
    actions = data.get(ModelSectionEnum.ACTION.value)
    if not actions:
        return []

    resource_types = []
    for action in actions:
        for rrt in action.get("related_resource_types", None) or []:
            resource_types.append((rrt["system_id"], rrt["id"]))

    return resource_types


def _get_instance_selections_from_action(data: Dict) -> List[Tuple[str, str]]:
    actions = data.get(ModelSectionEnum.ACTION.value)
    if not actions:
        return []

    instance_selections = []
    for action in actions:
        for rrt in action.get("related_resource_types", None) or []:
            for ris in rrt.get("related_instance_selections", None) or []:
                instance_selections.append((ris["system_id"], ris["id"]))

    return instance_selections


def _get_resource_type_from_instance_selection(data: Dict) -> List[Tuple[str, str]]:
    instance_selections = data.get(ModelSectionEnum.INSTANCE_SELECTION.value)
    if not instance_selections:
        return []

    resource_types = []
    for instance_selection in instance_selections:
        for rt in instance_selection.get("resource_type_chain", []):
            resource_types.append((rt["system_id"], rt["id"]))

    return resource_types


def validate_delete_part(_id: str, _type: str, _type_id: str):
    """
    需要检查引用, 依赖关系如下:
    resource_type - [instance_selection, action]
    instance_selection - [action]
    action - [common_actions, action_groups]
    """
    model = MockSystemModel.objects.get(id=_id)
    data = model.data

    if _type == ModelSectionEnum.ACTION.value:
        # common_actions
        if _type_id in _get_actions_from_common_actions(data):
            raise error_codes.VALIDATE_ERROR.format(
                _("操作(action) id={_type_id} 在常用操作(common_actions)中被引用").format(
                    _type_id=_type_id,
                )
            )

        if _type_id in _get_actions_from_action_groups(data):
            raise error_codes.VALIDATE_ERROR.format(
                _("操作(action) id={_type_id} 在操作组(action_groups)中被引用").format(
                    _type_id=_type_id,
                )
            )

    elif _type == ModelSectionEnum.INSTANCE_SELECTION.value:
        if (model.system_id, _type_id) in _get_instance_selections_from_action(data):
            raise error_codes.VALIDATE_ERROR.format(
                _("实例视图(instance_selection) id={_type_id} 在操作(action)中被引用").format(
                    _type_id=_type_id,
                )
            )
    elif _type == ModelSectionEnum.RESOURCE_TYPE.value:
        if (model.system_id, _type_id) in _get_resource_type_from_instance_selection(data):
            raise error_codes.VALIDATE_ERROR.format(
                _("资源类型(resource_type) id={_type_id} 在实例视图(instance_selection)中被引用").format(
                    _type_id=_type_id,
                )
            )

        if (model.system_id, _type_id) in _get_resource_types_from_action(data):
            raise error_codes.VALIDATE_ERROR.format(
                _("资源类型(resource_type) id={_type_id} 在操作(action)中被引用").format(
                    _type_id=_type_id,
                )
            )
