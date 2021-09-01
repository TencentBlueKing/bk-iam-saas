from typing import List

import pytest

from backend.biz.policy import InstanceBean, InstanceBeanList, PathNodeBean, PathNodeBeanList
from backend.common.error_codes import APIException
from backend.service.models import PathResourceType, ResourceTypeDict
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
        nodes=[
            path_node_bean,
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
        path_node_bean_list.nodes.pop()
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
        assert path_node_bean_list.ignore_path(instance_selection) == path_node_bean_list.nodes[start:end]


@pytest.fixture()
def instance_bean(path_node_bean: PathNodeBean):
    path_node_bean1 = path_node_bean.copy(deep=True)
    path_node_bean1.id = "id1"
    path_node_bean1.name = "name1"
    path_node_bean1.type = "type1"
    path_node_bean1.type_name = "type_name1"
    path_node_bean1.type_name_en = "type_name_en1"
    return InstanceBean(path=[[path_node_bean, path_node_bean1]], type="type")


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
        assert list(instance_bean.iter_path_node()) == instance_bean.path[0]

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
        instance_bean.add_paths(paths)
        assert len(instance_bean.path) == length

    @pytest.mark.parametrize(
        "paths, length",
        [
            (gen_paths(), 0),
            ([[gen_paths()[0][0]]], 1),
        ],
    )
    def test_remove_paths(self, instance_bean: InstanceBean, paths, length):
        instance_bean.remove_paths(paths)
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
        except APIException:
            assert raise_exception

    def test_check_instance_selection_ignore_path(self, instance_bean: InstanceBean):
        instance_selection = gen_instance_selection(
            [{"system_id": "system_id", "id": "type"}, {"system_id": "system_id", "id": "type1"}], ignore_iam_path=True
        )
        instance_bean.check_instance_selection("system_id", "type", [instance_selection], ignore_path=True)
        assert len(instance_bean.path[0]) == 1


@pytest.fixture()
def instance_bean_list(instance_bean: InstanceBean):
    instance_bean1 = instance_bean.copy(deep=True)
    instance_bean1.type = "type1"
    return InstanceBeanList([instance_bean, instance_bean1])


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


"""
PolicyBeanList sub
1. 需要sub没有关联资源类型的操作
2. 需要sub都是任意的操作
"""
