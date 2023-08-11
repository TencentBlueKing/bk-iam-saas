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
from typing import List

import pytest
from blue_krill.web.std_error import APIError
from mock import Mock

from backend.biz.policy import (
    ConditionBean,
    ConditionBeanList,
    InstanceBean,
    InstanceBeanList,
    PathNodeBean,
    PathNodeBeanList,
    PolicyBean,
    PolicyBeanList,
    PolicyBeanListMixin,
    PolicyEmptyException,
    RelatedResourceBean,
    RelatedResourceBeanList,
    ResourceGroupBean,
    ResourceGroupBeanList,
    ResourceTypeInstanceCount,
    group_paths,
)
from backend.biz.resource import ResourceNodeAttributeDictBean, ResourceNodeBean
from backend.common.time import PERMANENT_SECONDS, expired_at_display
from backend.service.action import ActionList
from backend.service.constants import DEFAULT_RESOURCE_GROUP_ID, SelectionMode
from backend.service.models import PathResourceType, ResourceTypeDict
from backend.service.models.action import Action, RelatedResourceType
from backend.service.models.instance_selection import InstanceSelection


@pytest.fixture()
def path_node_bean():
    return PathNodeBean(
        id="id", name="name", system_id="system_id", type="type", type_name="type_name", type_name_en="type_name_en"
    )


@pytest.fixture()
def resource_type_dict():
    return ResourceTypeDict(data={("system_id", "type"): {"name": "name_test", "name_en": "name_en_test"}})


class TestPathNodeBean:
    def test_fill_empty_fields(self, path_node_bean: PathNodeBean, resource_type_dict: ResourceTypeDict):
        path_node_bean.fill_empty_fields(resource_type_dict)
        assert path_node_bean.type_name == "name_test" and path_node_bean.type_name_en == "name_en_test"

    @pytest.mark.parametrize(
        "resource_system_id, resource_type_id, expected",
        [
            ("system_id", "type", True),
            ("system_id_no", "type", False),
            ("system_id", "type_no", False),
        ],
    )
    def test_match_resource_type(self, path_node_bean: PathNodeBean, resource_system_id, resource_type_id, expected):
        assert path_node_bean.match_resource_type(resource_system_id, resource_type_id) == expected

    def test_to_path_resource_type(self, path_node_bean: PathNodeBean):
        assert path_node_bean.to_path_resource_type() == PathResourceType(
            system_id=path_node_bean.system_id, id=path_node_bean.type
        )


@pytest.fixture()
def path_node_bean_list(path_node_bean: PathNodeBean):
    path_node_bean1 = path_node_bean.copy(deep=True)
    path_node_bean1.id = "id1"
    path_node_bean1.name = "name1"
    path_node_bean1.type = "type1"
    path_node_bean1.type_name = "type_name1"
    path_node_bean1.type_name_en = "type_name_en1"
    return PathNodeBeanList(
        __root__=[
            path_node_bean.copy(deep=True),
            path_node_bean1,
        ]
    )


def gen_instance_selection(chian: List, ignore_iam_path=False) -> InstanceSelection:
    return InstanceSelection(
        id="id",
        system_id="system_id",
        name="name",
        name_en="name_en",
        ignore_iam_path=ignore_iam_path,
        resource_type_chain=chian,
    )


class TestPathNodeBeanList:
    def test_dict(self, path_node_bean_list: PathNodeBeanList):
        assert path_node_bean_list.dict() == [
            {
                "id": "id",
                "name": "name",
                "system_id": "system_id",
                "type": "type",
                "type_name": "type_name",
                "type_name_en": "type_name_en",
            },
            {
                "id": "id1",
                "name": "name1",
                "system_id": "system_id",
                "type": "type1",
                "type_name": "type_name1",
                "type_name_en": "type_name_en1",
            },
        ]

    def test_to_path_string(self, path_node_bean_list: PathNodeBeanList):
        assert path_node_bean_list.to_path_string() == "/type,id/type1,id1/"

    def test_to_path_resource_types(self, path_node_bean_list: PathNodeBeanList):
        assert path_node_bean_list._to_path_resource_types() == [
            PathResourceType(system_id="system_id", id="type"),
            PathResourceType(system_id="system_id", id="type1"),
        ]

    def test_display(self, path_node_bean_list: PathNodeBeanList):
        assert path_node_bean_list.display() == "type:name/type1:name1"

    def test_match_selection_one_node(self, path_node_bean_list: PathNodeBeanList):
        path_node_bean_list.__root__.pop()
        assert path_node_bean_list.match_selection("system_id", "type", None)

    @pytest.mark.parametrize(
        "instance_selection, expected",
        [
            (
                gen_instance_selection(
                    [{"system_id": "system_id", "id": "type"}, {"system_id": "system_id", "id": "type1"}]
                ),
                True,
            ),
            (gen_instance_selection([{"system_id": "system_id", "id": "type"}]), False),
        ],
    )
    def test_match_selection(self, path_node_bean_list: PathNodeBeanList, instance_selection, expected):
        assert path_node_bean_list.match_selection("system_id", "type", instance_selection) == expected

    @pytest.mark.parametrize(
        "instance_selection, start, end",
        [
            (
                gen_instance_selection(
                    [{"system_id": "system_id", "id": "type"}, {"system_id": "system_id", "id": "type1"}],
                    ignore_iam_path=True,
                ),
                1,
                2,
            ),
            (gen_instance_selection([{"system_id": "system_id", "id": "type"}]), 0, 2),
        ],
    )
    def test_ignore_path(self, path_node_bean_list: PathNodeBeanList, instance_selection, start, end):
        assert path_node_bean_list.ignore_path(instance_selection).__root__ == path_node_bean_list.__root__[start:end]


@pytest.fixture()
def instance_bean(path_node_bean: PathNodeBean):
    path_node_bean1 = path_node_bean.copy(deep=True)
    path_node_bean1.id = "id1"
    path_node_bean1.name = "name1"
    path_node_bean1.type = "type1"
    path_node_bean1.type_name = "type_name1"
    path_node_bean1.type_name_en = "type_name_en1"
    return InstanceBean(path=[[path_node_bean.copy(deep=True), path_node_bean1]], type="type")


def gen_paths():
    return [
        [
            PathNodeBean(
                id="id",
                name="name",
                system_id="system_id",
                type="type",
                type_name="type_name",
                type_name_en="type_name_en",
            ),
            PathNodeBean(
                id="id1",
                name="name1",
                system_id="system_id",
                type="type1",
                type_name="type_name1",
                type_name_en="type_name_en1",
            ),
        ]
    ]


class TestInstanceBean:
    def test_fill_empty_fields(self, instance_bean: InstanceBean, resource_type_dict: ResourceTypeDict):
        instance_bean.fill_empty_fields(resource_type_dict)
        assert instance_bean.name == "name_test"
        assert instance_bean.name_en == "name_en_test"
        assert instance_bean.path[0][0].type_name == "name_test"
        assert instance_bean.path[0][0].type_name_en == "name_en_test"
        assert instance_bean.path[0][1].type_name == ""
        assert instance_bean.path[0][1].type_name_en == ""

    def test_iter_path_node(self, instance_bean: InstanceBean):
        assert list(instance_bean.iter_path_node()) == instance_bean.path[0].__root__

    def test_get_system_id_set(self, instance_bean: InstanceBean):
        assert instance_bean.get_system_id_set() == {"system_id"}

    @pytest.mark.parametrize(
        "paths, length",
        [
            (gen_paths(), 1),
            ([[gen_paths()[0][0]]], 2),
        ],
    )
    def test_add_paths(self, instance_bean: InstanceBean, paths, length):
        instance_bean.add_paths([PathNodeBeanList(__root__=p) for p in paths])
        assert len(instance_bean.path) == length

    @pytest.mark.parametrize(
        "paths, length",
        [
            (gen_paths(), 0),
            ([[gen_paths()[0][0]]], 1),
        ],
    )
    def test_remove_paths(self, instance_bean: InstanceBean, paths, length):
        instance_bean.remove_paths([PathNodeBeanList(__root__=p) for p in paths])
        assert len(instance_bean.path) == length

    def test_is_empty(self, instance_bean: InstanceBean):
        assert not instance_bean.is_empty
        instance_bean.path.pop()
        assert instance_bean.is_empty

    def test_count(self, instance_bean: InstanceBean):
        assert instance_bean.count() == 1

    @pytest.mark.parametrize(
        "instance_selection, length",
        [
            (
                gen_instance_selection(
                    [{"system_id": "system_id", "id": "type"}, {"system_id": "system_id", "id": "type1"}]
                ),
                1,
            ),
            (gen_instance_selection([{"system_id": "system_id", "id": "type"}]), 0),
        ],
    )
    def test_clone_and_filter_by_instance_selections(self, instance_bean: InstanceBean, instance_selection, length):
        instance_bean1 = instance_bean.clone_and_filter_by_instance_selections(
            "system_id", "type", [instance_selection]
        )
        if instance_bean1 is not None:
            assert len(instance_bean1.path) == length
        else:
            assert 0 == length

    @pytest.mark.parametrize(
        "instance_selection, raise_exception",
        [
            (
                gen_instance_selection(
                    [{"system_id": "system_id", "id": "type"}, {"system_id": "system_id", "id": "type1"}]
                ),
                False,
            ),
            (gen_instance_selection([{"system_id": "system_id", "id": "type"}]), True),
        ],
    )
    def test_check_instance_selection(self, instance_bean: InstanceBean, instance_selection, raise_exception):
        try:
            instance_bean.check_instance_selection("system_id", "type", [instance_selection])
            assert not raise_exception
        except APIError:
            assert raise_exception

    @pytest.mark.parametrize(
        "renamed_resources, result",
        [
            (
                {
                    PathNodeBean(
                        id="id",
                        name="name",
                        system_id="system_id",
                        type="type",
                        type_name="type_name",
                        type_name_en="type_name_en",
                    ): "test"
                },
                True,
            ),
            ({}, False),
        ],
    )
    def test_update_resource_name(self, instance_bean: InstanceBean, renamed_resources, result):
        assert instance_bean.update_resource_name(renamed_resources) == result
        if result:
            assert instance_bean.path[0][0].name == "test"


@pytest.fixture()
def instance_bean_list(instance_bean: InstanceBean):
    instance_bean1 = instance_bean.copy(deep=True)
    instance_bean1.type = "type1"
    return InstanceBeanList([instance_bean.copy(deep=True), instance_bean1])


class TestInstanceBeanList:
    def test_get(self, instance_bean_list: InstanceBeanList):
        assert instance_bean_list.get("type").type == "type"
        assert instance_bean_list.get("test") is None

    def test_add(self, instance_bean_list: InstanceBeanList):
        instance_bean_list1 = InstanceBeanList([instance_bean_list.instances.pop()])
        instance_bean_list._instance_dict.pop("type1")
        assert len(instance_bean_list.instances) == 1

        instance_bean_list.add(instance_bean_list1)
        assert len(instance_bean_list.instances) == 2

        instance_bean_list.add(instance_bean_list1)
        assert instance_bean_list.instances[1].type == "type1"
        assert len(instance_bean_list.instances[1].path) == 1

        instance_bean_list1 = InstanceBeanList([instance_bean_list.instances.pop()])
        instance_bean_list._instance_dict.pop("type1")
        assert len(instance_bean_list.instances) == 1

        instance_bean_list1.instances[0].type = "type"
        instance_bean_list1.instances[0].path[0][-1].id = "id2"
        instance_bean_list.add(instance_bean_list1)
        assert len(instance_bean_list.instances) == 1
        assert len(instance_bean_list.instances[0].path) == 2

    def test_sub(self, instance_bean_list: InstanceBeanList):
        instance_bean_list1 = InstanceBeanList([instance_bean_list.instances.pop()])
        instance_bean_list._instance_dict.pop("type1")
        assert len(instance_bean_list.instances) == 1

        instance_bean_list1.instances[0].type = "type"
        instance_bean_list1._instance_dict.pop("type1")
        instance_bean_list1._instance_dict["type"] = instance_bean_list1.instances[0]
        instance_bean_list.sub(instance_bean_list1)
        assert len(instance_bean_list.instances) == 0


@pytest.fixture()
def condition_bean(instance_bean: InstanceBean):
    return ConditionBean(instances=[instance_bean.copy(deep=True)], attributes=[])


class TestConditionBean:
    def test_fill_empty_fields(self, condition_bean: ConditionBean):
        resource_type_dict = ResourceTypeDict(data={("system_id", "type"): {"name": "test", "name_en": "test_en"}})
        condition_bean = condition_bean.copy(deep=True)
        condition_bean.fill_empty_fields(resource_type_dict)
        assert condition_bean.instances[0].path[0][0].type_name == "test"
        assert condition_bean.instances[0].path[0][0].type_name_en == "test_en"

    def test_get_system_id_set(self, condition_bean: ConditionBean):
        system_id_set = condition_bean.get_system_id_set()
        assert system_id_set == {"system_id"}

    def test_add_instances(self, condition_bean: ConditionBean, instance_bean: InstanceBean):
        condition_bean.add_instances([instance_bean])
        assert len(condition_bean.instances) == 1
        assert len(condition_bean.instances[0].path) == 1

    def test_remove_instances(self, condition_bean: ConditionBean, instance_bean: InstanceBean):
        condition_bean.remove_instances([instance_bean])
        assert len(condition_bean.instances) == 0

    def test_count_instance(self, condition_bean: ConditionBean):
        assert condition_bean.count_instance("type") == 1


@pytest.fixture()
def condition_bean_list(condition_bean: ConditionBean):
    return ConditionBeanList([condition_bean.copy(deep=True)])


class TestConditionBeanList:
    def test_init_empty(self):
        condition_bean_list = ConditionBeanList([])
        assert condition_bean_list.is_any
        assert not condition_bean_list.is_empty

    def test_init(self, condition_bean_list: ConditionBeanList):
        assert not condition_bean_list.is_any
        assert not condition_bean_list.is_empty

    def test_add(self, condition_bean_list: ConditionBeanList):
        new_condition = condition_bean_list.conditions[0].copy(deep=True)
        new_condition.instances[0].path[0][-1].id = "test"
        condition_bean_list.add(ConditionBeanList([new_condition]))
        assert len(condition_bean_list.conditions) == 1
        assert len(condition_bean_list.conditions[0].instances) == 1
        assert len(condition_bean_list.conditions[0].instances[0].path) == 2

    def test_sub(self, condition_bean_list: ConditionBeanList):
        condition_bean_list.sub(condition_bean_list)
        assert condition_bean_list.is_empty

    def test_remove_by_ids(self, condition_bean_list: ConditionBeanList):
        condition_bean_list.remove_by_ids(condition_bean_list.conditions[0].id)
        assert condition_bean_list.is_empty


@pytest.fixture()
def related_resource_bean(condition_bean: ConditionBean):
    return RelatedResourceBean(system_id="system_id", type="type", condition=[condition_bean.copy(deep=True)])


class TestRelatedResourceBean:
    def test_fill_empty_fields(self, related_resource_bean: RelatedResourceBean, resource_type_dict: ResourceTypeDict):
        rrt = RelatedResourceType(system_id="system_id", id="type", name="name", name_en="name_en")
        related_resource_bean.fill_empty_fields(rrt, resource_type_dict)
        assert related_resource_bean.selection_mode == SelectionMode.INSTANCE.value
        assert related_resource_bean.name == "name_test"
        assert related_resource_bean.name_en == "name_en_test"
        assert related_resource_bean.condition[0].instances[0].name == "name_test"

    def test_get_system_id_set(self, related_resource_bean: RelatedResourceBean):
        assert related_resource_bean.get_system_id_set() == {"system_id"}

    @pytest.mark.parametrize(
        "instance_selection, raise_exception",
        [
            (
                gen_instance_selection(
                    [{"system_id": "system_id", "id": "type"}, {"system_id": "system_id", "id": "type1"}]
                ),
                False,
            ),
            (gen_instance_selection([{"system_id": "system_id", "id": "type"}]), True),
        ],
    )
    def test_check_selection(self, related_resource_bean: RelatedResourceBean, instance_selection, raise_exception):
        try:
            related_resource_bean.check_selection([instance_selection])
            assert not raise_exception
        except APIError:
            assert raise_exception

    def test_count_instance(self, related_resource_bean: RelatedResourceBean):
        assert related_resource_bean.count_instance() == 1

    @pytest.mark.parametrize(
        "instance_selection, length",
        [
            (
                gen_instance_selection(
                    [{"system_id": "system_id", "id": "type"}, {"system_id": "system_id", "id": "type1"}]
                ),
                1,
            ),
            (gen_instance_selection([{"system_id": "system_id", "id": "type"}]), 0),
        ],
    )
    def test_clone_and_filter_by_instance_selections(
        self, related_resource_bean: RelatedResourceBean, instance_selection, length
    ):
        instance_bean1 = related_resource_bean.clone_and_filter_by_instance_selections([instance_selection])
        if instance_bean1 is not None:
            assert len(related_resource_bean.condition[0].instances[0].path) == length
        else:
            assert 0 == length

    def test_iter_path_list(self, related_resource_bean: RelatedResourceBean):
        _list = list(related_resource_bean.iter_path_list())
        assert len(_list) == 1

    @pytest.mark.parametrize(
        "renamed_resources, result",
        [
            (
                {
                    PathNodeBean(
                        id="id",
                        name="name",
                        system_id="system_id",
                        type="type",
                        type_name="type_name",
                        type_name_en="type_name_en",
                    ): "test"
                },
                True,
            ),
            ({}, False),
        ],
    )
    def test_update_resource_name(self, related_resource_bean: RelatedResourceBean, renamed_resources, result):
        assert related_resource_bean.update_resource_name(renamed_resources) == result
        if result:
            assert related_resource_bean.condition[0].instances[0].path[0][0].name == "test"


@pytest.fixture()
def related_resource_bean_list(related_resource_bean: RelatedResourceBean):
    return RelatedResourceBeanList([related_resource_bean.copy(deep=True)])


class TestRelatedResourceBeanList:
    def test_get_condition_list(self, related_resource_bean_list: RelatedResourceBeanList):
        condition_list = related_resource_bean_list.get_condition_list("system_id", "type")
        assert condition_list

    def test_add(self, related_resource_bean_list: RelatedResourceBeanList):
        new_related_resource_bean_list = deepcopy(related_resource_bean_list)
        related_resource_bean_list.add(new_related_resource_bean_list)
        assert len(related_resource_bean_list._condition_list_dict) == 1

    def test_sub(self, related_resource_bean_list: RelatedResourceBeanList):
        new_related_resource_bean_list = deepcopy(related_resource_bean_list)
        related_resource_bean_list.sub(new_related_resource_bean_list)
        assert related_resource_bean_list.is_empty


@pytest.fixture()
def policy_bean(related_resource_bean: RelatedResourceBean):
    return PolicyBean(action_id="action_id", related_resource_types=[related_resource_bean.copy(deep=True)])


class TestPolicyBean:
    def test_dict(self, policy_bean: PolicyBean):
        data = policy_bean.dict()
        assert "id" in data

    def test_fill_empty_fields(self, policy_bean: PolicyBean, resource_type_dict: ResourceTypeDict):
        action = Action(
            id="action_id",
            name="action_name",
            name_en="action_name_en",
            description="",
            description_en="",
            related_resource_types=[
                RelatedResourceType(system_id="system_id", id="type", name="name", name_en="name_en")
            ],
        )
        policy_bean.fill_empty_fields(action, resource_type_dict)
        assert policy_bean.name == "action_name"
        assert policy_bean.name_en == "action_name_en"
        assert policy_bean.resource_groups[0].related_resource_types[0].name == "name_test"

    def test_get_system_id_set(self, policy_bean: PolicyBean):
        assert policy_bean.get_system_id_set() == {"system_id"}

    def test_get_related_resource_type(self, policy_bean: PolicyBean):
        assert policy_bean.get_related_resource_type(DEFAULT_RESOURCE_GROUP_ID, "system_id", "type")

    def test_set_expired_at(self, policy_bean: PolicyBean):
        policy_bean.set_expired_at(PERMANENT_SECONDS)
        assert policy_bean.expired_at == PERMANENT_SECONDS
        assert policy_bean.expired_display == expired_at_display(PERMANENT_SECONDS)

    def test_is_unrelated(self, policy_bean: PolicyBean):
        assert not policy_bean.resource_groups.is_unrelated()

    def test_set_related_resource_type(self, policy_bean: PolicyBean, related_resource_bean: RelatedResourceBean):
        related_resource_bean.condition = []
        policy_bean.resource_groups[0].set_related_resource_type(related_resource_bean)
        assert len(policy_bean.resource_groups[0].related_resource_types[0].condition) == 0

    def test_add_related_resource_types(self, policy_bean: PolicyBean, related_resource_bean: RelatedResourceBean):
        related_resource_bean.condition[0].instances[0].path[0][-1].id = "id2"
        policy_bean.resource_groups[0].add_related_resource_types([related_resource_bean])
        assert len(policy_bean.resource_groups[0].related_resource_types[0].condition[0].instances[0].path) == 2

    def test_has_related_resource_types(self, policy_bean: PolicyBean):
        assert policy_bean.resource_groups[0].has_related_resource_types(
            policy_bean.resource_groups[0].related_resource_types
        )
        policy_bean.resource_groups[0].related_resource_types = []
        assert policy_bean.resource_groups[0].has_related_resource_types(
            policy_bean.resource_groups[0].related_resource_types
        )

    def test_remove_related_resource_types(self, policy_bean: PolicyBean):
        try:
            policy_bean.resource_groups[0].remove_related_resource_types(
                policy_bean.resource_groups[0].related_resource_types
            )
            raise AssertionError()
        except PolicyEmptyException:
            assert True

        policy_bean.resource_groups[0].related_resource_types = []
        try:
            policy_bean.resource_groups[0].remove_related_resource_types(
                policy_bean.resource_groups[0].related_resource_types
            )
            raise AssertionError()
        except PolicyEmptyException:
            assert True

    def test_list_path_node(self, policy_bean: PolicyBean):
        assert len(policy_bean.list_path_node()) == 2

    @pytest.mark.parametrize(
        "instance_selection, raise_exception",
        [
            (
                gen_instance_selection(
                    [{"system_id": "system_id", "id": "type"}, {"system_id": "system_id", "id": "type1"}]
                ),
                False,
            ),
            (gen_instance_selection([{"system_id": "system_id", "id": "type"}]), True),
        ],
    )
    def test_check_instance_selection(self, policy_bean: PolicyBean, instance_selection, raise_exception):
        try:
            policy_bean.check_instance_selection(
                Action(
                    id="",
                    name="",
                    name_en="",
                    description="",
                    description_en="",
                    related_resource_types=[
                        RelatedResourceType(
                            system_id="system_id",
                            id="type",
                            name="",
                            name_en="",
                            instance_selections=[instance_selection],
                        )
                    ],
                )
            )
            assert not raise_exception
        except APIError:
            assert raise_exception

    def test_list_resource_type_instance_count(self, policy_bean: PolicyBean):
        counts = policy_bean.list_resource_type_instance_count()
        assert counts == [ResourceTypeInstanceCount(type="type", count=1)]

        policy_bean.resource_groups = ResourceGroupBeanList(__root__=[])

        counts = policy_bean.list_resource_type_instance_count()
        assert counts == [ResourceTypeInstanceCount(type="", count=0)]

    @pytest.mark.parametrize(
        "renamed_resources, result",
        [
            (
                {
                    PathNodeBean(
                        id="id",
                        name="name",
                        system_id="system_id",
                        type="type",
                        type_name="type_name",
                        type_name_en="type_name_en",
                    ): "test"
                },
                True,
            ),
            ({}, False),
        ],
    )
    def test_update_resource_name(self, policy_bean: PolicyBean, renamed_resources, result):
        assert policy_bean.update_resource_name(renamed_resources) == result
        if result:
            assert (
                policy_bean.resource_groups[0].related_resource_types[0].condition[0].instances[0].path[0][0].name
                == "test"
            )


@pytest.fixture()
def policy_bean_list(policy_bean: PolicyBean):
    return PolicyBeanList("system_id", [policy_bean])


class TestPolicyBeanList:
    def test_get_system_id_set(self, policy_bean_list: PolicyBeanList):
        assert policy_bean_list.get_system_id_set() == {"system_id"}

    def test_get(self, policy_bean_list: PolicyBeanList):
        assert policy_bean_list.get("action_id")

    def test_split_to_creation_and_update_for_grant(self, policy_bean_list: PolicyBeanList):
        new_policy_list = deepcopy(policy_bean_list)
        new_policy_list.policies[0].action_id = "action_id2"
        cp, up = policy_bean_list.split_to_creation_and_update_for_grant(new_policy_list)
        assert len(cp.policies) == 1
        assert cp.policies[0].action_id == "action_id2"
        assert len(up.policies) == 0

        new_policy_list = deepcopy(policy_bean_list)
        cp, up = policy_bean_list.split_to_creation_and_update_for_grant(new_policy_list)
        assert len(cp.policies) == 0
        assert len(up.policies) == 0

        new_policy_list = deepcopy(policy_bean_list)
        new_policy_list.policies[0].resource_groups[0].related_resource_types[0].condition[0].instances[0].path[0][
            -1
        ].id = "id2"
        cp, up = policy_bean_list.split_to_creation_and_update_for_grant(new_policy_list)
        assert len(cp.policies) == 0
        assert len(up.policies) == 1
        assert len(up.policies[0].resource_groups[0].related_resource_types[0].condition[0].instances[0].path) == 2

        new_policy_list = deepcopy(policy_bean_list)
        new_policy_list.policies[0].set_expired_at(123)
        cp, up = policy_bean_list.split_to_creation_and_update_for_grant(new_policy_list)
        assert len(cp.policies) == 0
        assert len(up.policies) == 1

    def test_split_to_update_and_delete_for_revoke(self, policy_bean_list: PolicyBeanList):
        up, du = policy_bean_list.split_to_update_and_delete_for_revoke(policy_bean_list)
        assert len(up.policies) == 0
        assert len(du.policies) == 1

        new_policy_list = deepcopy(policy_bean_list)
        new_policy_list.policies[0].resource_groups[0].related_resource_types[0].condition[0].instances[0].path[0][
            -1
        ].id = "id2"
        up, du = new_policy_list.split_to_update_and_delete_for_revoke(policy_bean_list)
        assert len(up.policies) == 1
        assert len(du.policies) == 0

        new_policy_list.policies[0].resource_groups[0].related_resource_types = []
        up, du = new_policy_list.split_to_update_and_delete_for_revoke(new_policy_list)
        assert len(up.policies) == 0
        assert len(du.policies) == 1

    def test_add(self, policy_bean_list: PolicyBeanList):
        new_policy_list = deepcopy(policy_bean_list)
        new_policy_list.policies[0].resource_groups[0].related_resource_types[0].condition[0].instances[0].path[0][
            -1
        ].id = "id2"
        policy_bean_list.add(new_policy_list)
        assert (
            len(
                policy_bean_list.policies[0]
                .resource_groups[0]
                .related_resource_types[0]
                .condition[0]
                .instances[0]
                .path
            )
            == 2
        )

    def test_sub(self, policy_bean_list: PolicyBeanList):
        new_policy_list = deepcopy(policy_bean_list)
        new_policy_list.policies[0].action_id = "action_id2"
        subtraction = policy_bean_list.sub(new_policy_list)
        assert len(subtraction.policies) == 0

        subtraction = new_policy_list.sub(policy_bean_list)
        assert len(subtraction.policies) == 1

        new_policy_list = deepcopy(policy_bean_list)
        new_path = deepcopy(
            new_policy_list.policies[0].resource_groups[0].related_resource_types[0].condition[0].instances[0].path[0]
        )
        new_path[-1].id = "id2"
        new_policy_list.policies[0].resource_groups[0].related_resource_types[0].condition[0].instances[0].path.append(
            new_path
        )
        subtraction = new_policy_list.sub(policy_bean_list)
        assert len(subtraction.policies) == 1
        assert (
            len(subtraction.policies[0].resource_groups[0].related_resource_types[0].condition[0].instances[0].path)
            == 1
        )
        assert (
            subtraction.policies[0]
            .resource_groups[0]
            .related_resource_types[0]
            .condition[0]
            .instances[0]
            .path[0][-1]
            .id
            == "id2"
        )

    def test_list_path_node(self, policy_bean_list: PolicyBeanList):
        nodes = policy_bean_list._list_path_node()
        assert len(nodes) == 2


def test_group_paths():
    paths = [
        [
            {
                "system_id": "system_id",
                "name": "name",
                "type_name_en": "type_name_en",
                "type_name": "type_name",
                "type": "type",
                "id": "id",
            },
            {
                "system_id": "system_id",
                "name": "name",
                "type_name_en": "type_name_en",
                "type_name": "type_name",
                "type": "type1",
                "id": "id2",
            },
        ]
    ]
    assert len(group_paths(paths)) == 1

    paths = [
        [
            {
                "system_id": "system_id",
                "name": "name",
                "type_name_en": "type_name_en",
                "type_name": "type_name",
                "type": "type",
                "id": "id",
            },
            {
                "system_id": "system_id",
                "name": "name",
                "type_name_en": "type_name_en",
                "type_name": "type_name",
                "type": "type1",
                "id": "id2",
            },
        ],
        [
            {
                "system_id": "system_id",
                "name": "name",
                "type_name_en": "type_name_en",
                "type_name": "type_name",
                "type": "type",
                "id": "id",
            },
            {
                "system_id": "system_id",
                "name": "name",
                "type_name_en": "type_name_en",
                "type_name": "type_name",
                "type": "type1",
                "id": "*",
            },
        ],
    ]
    assert len(group_paths(paths)) == 2

    paths = [
        [
            {
                "system_id": "system_id",
                "name": "name",
                "type_name_en": "type_name_en",
                "type_name": "type_name",
                "type": "type",
                "id": "id",
            },
            {
                "system_id": "system_id",
                "name": "name",
                "type_name_en": "type_name_en",
                "type_name": "type_name",
                "type": "type1",
                "id": "id2",
            },
        ],
        [
            {
                "system_id": "system_id",
                "name": "name",
                "type_name_en": "type_name_en",
                "type_name": "type_name",
                "type": "type",
                "id": "id",
            }
        ],
    ]
    assert len(group_paths(paths)) == 2


class TestResourceGroupBeanList:
    def test_get_by_id(self, policy_bean: PolicyBean):
        resource_group = policy_bean.resource_groups.get_by_id(DEFAULT_RESOURCE_GROUP_ID)
        assert resource_group

    def test_pop_by_id(self, policy_bean: PolicyBean):
        resource_group = policy_bean.resource_groups.pop_by_id(DEFAULT_RESOURCE_GROUP_ID)
        assert resource_group
        assert len(policy_bean.resource_groups) == 0

    def test_issuper(self, policy_bean: PolicyBean):
        assert policy_bean.resource_groups.is_super_set(policy_bean.resource_groups)
        copied_policy = deepcopy(policy_bean)
        copied_policy.resource_groups[0].related_resource_types[0].condition = []
        assert not policy_bean.resource_groups.is_super_set(copied_policy.resource_groups)

    def test_is_unrelated(self, policy_bean: PolicyBean):
        assert not policy_bean.resource_groups.is_unrelated()
        policy_bean.resource_groups = ResourceGroupBeanList.parse_obj([])
        assert policy_bean.resource_groups.is_unrelated()

    def test_list_thin_resource_type(self, policy_bean: PolicyBean):
        assert policy_bean.resource_groups.get_thin_resource_types()

    def test_contains(self, policy_bean: PolicyBean):
        assert policy_bean.resource_groups[0] in policy_bean.resource_groups
        copied_policy = deepcopy(policy_bean)
        copied_policy.resource_groups[0].related_resource_types[0].condition = []
        assert copied_policy.resource_groups[0] not in policy_bean.resource_groups

    def test_add(self, policy_bean: PolicyBean):
        resource_groups = policy_bean.resource_groups + policy_bean.resource_groups
        assert len(resource_groups) == 1
        copied_resource_groups = deepcopy(policy_bean.resource_groups)
        copied_resource_groups[0].id = "abc"
        copied_resource_groups[0].related_resource_types[0].condition = []
        resource_groups = policy_bean.resource_groups + copied_resource_groups
        assert len(resource_groups) == 1

    def test_sub(self, policy_bean: PolicyBean):
        try:
            policy_bean.resource_groups - policy_bean.resource_groups
            raise AssertionError()
        except PolicyEmptyException:
            assert True


@pytest.fixture()
def related_group_bean(related_resource_bean: RelatedResourceBean):
    return ResourceGroupBean(related_resource_types=[related_resource_bean.copy(deep=True)])


class TestResourceGroupBean:
    @pytest.mark.parametrize(
        "renamed_resources, result",
        [
            (
                {
                    PathNodeBean(
                        id="id",
                        name="name",
                        system_id="system_id",
                        type="type",
                        type_name="type_name",
                        type_name_en="type_name_en",
                    ): "test"
                },
                True,
            ),
            ({}, False),
        ],
    )
    def test_update_resource_name(self, related_group_bean: ResourceGroupBean, renamed_resources, result):
        assert related_group_bean.update_resource_name(renamed_resources) == result
        if result:
            assert related_group_bean.related_resource_types[0].condition[0].instances[0].path[0][0].name == "test"

    @pytest.mark.parametrize(
        "instance_selection, raise_exception",
        [
            (
                gen_instance_selection(
                    [{"system_id": "system_id", "id": "type"}, {"system_id": "system_id", "id": "type1"}]
                ),
                False,
            ),
            (gen_instance_selection([{"system_id": "system_id", "id": "type"}]), True),
        ],
    )
    def test_check_instance_selection(
        self, related_group_bean: ResourceGroupBean, instance_selection, raise_exception
    ):
        try:
            related_group_bean.check_instance_selection(
                Action(
                    id="",
                    name="",
                    name_en="",
                    description="",
                    description_en="",
                    related_resource_types=[
                        RelatedResourceType(
                            system_id="system_id",
                            id="type",
                            name="",
                            name_en="",
                            instance_selections=[instance_selection],
                        )
                    ],
                )
            )
            assert not raise_exception
        except APIError:
            assert raise_exception


@pytest.fixture()
def policy_bean_list_mixin(policy_bean: PolicyBean):
    return PolicyBeanListMixin("system_id", [policy_bean.copy(deep=True)])


class TestPolicyBeanListMixin:
    @pytest.mark.parametrize(
        "instance_selection, raise_exception",
        [
            (
                gen_instance_selection(
                    [{"system_id": "system_id", "id": "type"}, {"system_id": "system_id", "id": "type1"}]
                ),
                False,
            ),
            (gen_instance_selection([{"system_id": "system_id", "id": "type"}]), True),
        ],
    )
    def test_check_instance_selection(
        self, policy_bean_list_mixin: PolicyBeanListMixin, instance_selection, raise_exception
    ):
        policy_bean_list_mixin.action_svc.new_action_list = Mock(
            return_value=ActionList(
                [
                    Action(
                        id="action_id",
                        name="",
                        name_en="",
                        description="",
                        description_en="",
                        related_resource_types=[
                            RelatedResourceType(
                                system_id="system_id",
                                id="type",
                                name="",
                                name_en="",
                                instance_selections=[instance_selection],
                            )
                        ],
                    )
                ]
            )
        )

        try:
            policy_bean_list_mixin.check_instance_selection()
            assert not raise_exception
        except APIError:
            assert raise_exception

    @pytest.mark.parametrize(
        "resource_name_dict, raise_exception",
        [
            (
                ResourceNodeAttributeDictBean(
                    data={
                        ResourceNodeBean(id="id", system_id="system_id", type="type"): "name",
                        ResourceNodeBean(id="id1", system_id="system_id", type="type1"): "name1",
                    }
                ),
                False,
            ),
            (
                ResourceNodeAttributeDictBean(
                    data={
                        ResourceNodeBean(id="id", system_id="system_id", type="type"): "name",
                        ResourceNodeBean(id="id1", system_id="system_id", type="type1"): "test",
                    }
                ),
                True,
            ),
            (
                ResourceNodeAttributeDictBean(data={}),
                False,
            ),
        ],
    )
    def test_check_resource_name(
        self, policy_bean_list_mixin: PolicyBeanListMixin, resource_name_dict, raise_exception
    ):
        policy_bean_list_mixin.resource_biz.fetch_resource_name = Mock(return_value=resource_name_dict)
        try:
            policy_bean_list_mixin.check_resource_name()
            assert not raise_exception
        except APIError:
            assert raise_exception

    def test_check_instance_count_limit(self, policy_bean_list_mixin: PolicyBeanListMixin):
        assert policy_bean_list_mixin.check_instance_count_limit() is None

    def test_get_renamed_resources(self, policy_bean_list_mixin: PolicyBeanListMixin):
        policy_bean_list_mixin.resource_biz.fetch_resource_name = Mock(
            return_value=ResourceNodeAttributeDictBean(
                data={
                    ResourceNodeBean(id="id", system_id="system_id", type="type"): "name",
                    ResourceNodeBean(id="id1", system_id="system_id", type="type1"): "test",
                }
            )
        )
        renamed_resources = policy_bean_list_mixin.get_renamed_resources()
        assert renamed_resources == {
            PathNodeBean(
                id="id1",
                name="name1",
                system_id="system_id",
                type="type1",
                type_name="type_name1",
                type_name_en="type_name_en1",
            ): "test"
        }

    @pytest.mark.parametrize(
        "resource_name_dict, result",
        [
            (
                ResourceNodeAttributeDictBean(
                    data={
                        ResourceNodeBean(id="id", system_id="system_id", type="type"): "name",
                        ResourceNodeBean(id="id1", system_id="system_id", type="type1"): "name1",
                    }
                ),
                False,
            ),
            (
                ResourceNodeAttributeDictBean(
                    data={
                        ResourceNodeBean(id="id", system_id="system_id", type="type"): "name",
                        ResourceNodeBean(id="id1", system_id="system_id", type="type1"): "test",
                    }
                ),
                True,
            ),
        ],
    )
    def test_auto_update_resource_name(self, policy_bean_list_mixin: PolicyBeanListMixin, resource_name_dict, result):
        policy_bean_list_mixin.resource_biz.fetch_resource_name = Mock(return_value=resource_name_dict)
        assert bool(policy_bean_list_mixin.auto_update_resource_name()) == result
