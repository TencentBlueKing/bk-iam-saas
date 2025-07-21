"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云 - 权限中心 (BlueKing-IAM) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import uuid

import mock
from django.conf import settings
from django.test import TestCase

from backend.biz.policy import ConditionBean, InstanceBean, PathNodeBean, PolicyBean, RelatedResourceBean
from backend.biz.related_policy import RelatedPolicyBiz
from backend.common.time import PERMANENT_SECONDS
from backend.service.action import ActionList
from backend.service.constants import DEFAULT_RESOURCE_GROUP_ID, SelectionMode
from backend.service.models import Action, Attribute, InstanceSelection, RelatedResourceType
from backend.service.models.instance_selection import ChainNode


class DependingActionCheckPathTests(TestCase):
    def test_check_path_same_type_1(self):
        svc = RelatedPolicyBiz(settings.BK_APP_TENANT_ID)
        path = [
            PathNodeBean(system_id="bk_cmdb", type="host", id="host1"),
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
        self.assertEqual(
            svc._check_path_by_instance_selection(path, selections),
            [PathNodeBean(system_id="bk_cmdb", type="host", id="host1")],
        )

    def test_check_path_same_type_2(self):
        svc = RelatedPolicyBiz(settings.BK_APP_TENANT_ID)
        path = [
            PathNodeBean(system_id="bk_cmdb", type="biz", id="biz1"),
            PathNodeBean(system_id="bk_cmdb", type="set", id="set1"),
            PathNodeBean(system_id="bk_cmdb", type="module", id="module1"),
            PathNodeBean(system_id="bk_cmdb", type="host", id="host1"),
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
        self.assertEqual(svc._check_path_by_instance_selection(path, selections), None)

    def test_check_path_same_type_4(self):
        svc = RelatedPolicyBiz(settings.BK_APP_TENANT_ID)
        path = [
            PathNodeBean(system_id="bk_cmdb", type="biz", id="biz1"),
            PathNodeBean(system_id="bk_cmdb", type="set", id="set1"),
            PathNodeBean(system_id="bk_cmdb", type="module", id="module1"),
            PathNodeBean(system_id="bk_cmdb", type="host", id="host1"),
        ]
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
            )
        ]
        self.assertEqual(
            svc._check_path_by_instance_selection(path, selections),
            [
                PathNodeBean(system_id="bk_cmdb", type="biz", id="biz1"),
                PathNodeBean(system_id="bk_cmdb", type="set", id="set1"),
                PathNodeBean(system_id="bk_cmdb", type="module", id="module1"),
                PathNodeBean(system_id="bk_cmdb", type="host", id="host1"),
            ],
        )

    def test_check_path_same_type_5(self):
        svc = RelatedPolicyBiz(settings.BK_APP_TENANT_ID)
        path = [
            PathNodeBean(system_id="bk_job", type="biz", id="biz1"),
            PathNodeBean(system_id="bk_cmdb", type="set", id="set1"),
            PathNodeBean(system_id="bk_cmdb", type="module", id="module1"),
            PathNodeBean(system_id="bk_cmdb", type="host", id="host1"),
        ]
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
            )
        ]
        self.assertEqual(svc._check_path_by_instance_selection(path, selections), None)

    def test_check_path_same_type_6(self):
        svc = RelatedPolicyBiz(settings.BK_APP_TENANT_ID)
        path = [
            PathNodeBean(system_id="bk_cmdb", type="biz", id="biz1"),
            PathNodeBean(system_id="bk_cmdb", type="host", id="host1"),
        ]
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
                    ChainNode(system_id="bk_cmdb", id="host"),
                ],
            ),
        ]
        self.assertEqual(
            svc._check_path_by_instance_selection(path, selections),
            [
                PathNodeBean(system_id="bk_cmdb", type="biz", id="biz1"),
                PathNodeBean(system_id="bk_cmdb", type="host", id="host1"),
            ],
        )

    def test_check_path_different_type_1(self):
        svc = RelatedPolicyBiz(settings.BK_APP_TENANT_ID)
        path = [
            PathNodeBean(system_id="bk_cmdb", type="biz", id="biz1"),
            PathNodeBean(system_id="bk_cmdb", type="host", id="host1"),
        ]
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
                ],
            ),
            InstanceSelection(
                id="test2",
                system_id="bk_cmdb",
                name="test2",
                name_en="test2",
                ignore_iam_path=False,
                resource_type_chain=[ChainNode(system_id="bk_cmdb", id="biz")],
            ),
        ]
        self.assertEqual(
            svc._check_path_by_instance_selection(path, selections),
            [PathNodeBean(system_id="bk_cmdb", type="biz", id="biz1")],
        )


class FilterResourceTypeSameTypeTests(TestCase):
    def setUp(self) -> None:
        import uuid

        uuid.uuid4 = mock.Mock(return_value=uuid.UUID("fa17b2cbf38141d7a5a0591573fc0f82"))

    def test_attribute(self):
        svc = RelatedPolicyBiz(settings.BK_APP_TENANT_ID)
        policy_rrt = RelatedResourceBean(
            system_id="bk_cmdb",
            type="host",
            condition=[
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
                    instances=[],
                    attributes=[Attribute(id="", name="", values=[{"id": "test2", "name": "test2"}])],
                ),
            ],
        )
        action_rrt = RelatedResourceType(
            id="host",
            system_id="bk_cmdb",
            name_alias="test",
            name_alias_en="test",
            selection_mode=SelectionMode.ATTRIBUTE.value,
        )
        self.assertEqual(
            svc._filter_condition_of_same_type(policy_rrt, action_rrt),
            RelatedResourceBean(
                system_id="bk_cmdb",
                type="host",
                condition=[
                    ConditionBean(
                        instances=[], attributes=[Attribute(id="", name="", values=[{"id": "test2", "name": "test2"}])]
                    )
                ],
            ),
        )

    def test_instance(self):
        svc = RelatedPolicyBiz(settings.BK_APP_TENANT_ID)
        policy_rrt = RelatedResourceBean(
            system_id="bk_cmdb",
            type="host",
            condition=[
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
                    instances=[],
                    attributes=[Attribute(id="", name="", values=[{"id": "test2", "name": "test2"}])],
                ),
            ],
        )
        action_rrt = RelatedResourceType(
            id="host",
            system_id="bk_cmdb",
            name_alias="test",
            name_alias_en="test",
            selection_mode=SelectionMode.INSTANCE.value,
            instance_selections=[
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
                )
            ],
        )
        self.assertEqual(
            svc._filter_condition_of_same_type(policy_rrt, action_rrt),
            RelatedResourceBean(
                system_id="bk_cmdb",
                type="host",
                condition=[
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
                ],
            ),
        )

    def test_all(self):
        svc = RelatedPolicyBiz(settings.BK_APP_TENANT_ID)
        policy_rrt = RelatedResourceBean(
            system_id="bk_cmdb",
            type="host",
            condition=[
                ConditionBean(
                    instances=[],
                    attributes=[Attribute(id="", name="", values=[{"id": "test2", "name": "test2"}])],
                ),
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
            ],
        )
        action_rrt = RelatedResourceType(
            id="host",
            system_id="bk_cmdb",
            name_alias="test",
            name_alias_en="test",
            selection_mode=SelectionMode.ALL.value,
            instance_selections=[
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
                )
            ],
        )
        self.assertEqual(
            svc._filter_condition_of_same_type(policy_rrt, action_rrt),
            RelatedResourceBean(
                system_id="bk_cmdb",
                type="host",
                condition=[
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
                            InstanceBean(type="host", path=[[{"system_id": "bk_cmdb", "type": "host", "id": "host3"}]])
                        ],
                        attributes=[Attribute(id="", name="", values=[{"id": "test1", "name": "test1"}])],
                    ),
                    ConditionBean(
                        instances=[],
                        attributes=[Attribute(id="", name="", values=[{"id": "test2", "name": "test2"}])],
                    ),
                ],
            ),
        )

    def test_none(self):
        svc = RelatedPolicyBiz(settings.BK_APP_TENANT_ID)
        policy_rrt = RelatedResourceBean(
            system_id="bk_cmdb",
            type="host",
            condition=[
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
            ],
        )
        action_rrt = RelatedResourceType(
            id="host",
            system_id="bk_cmdb",
            name_alias="test",
            name_alias_en="test",
            selection_mode=SelectionMode.ATTRIBUTE.value,
        )
        self.assertEqual(svc._filter_condition_of_same_type(policy_rrt, action_rrt), None)


class FilterConditionDifferentTypeTests(TestCase):
    def test_right_1(self):
        svc = RelatedPolicyBiz(settings.BK_APP_TENANT_ID)
        conditions = [ConditionBean(instances=[], attributes=[])]
        selections = []
        self.assertEqual(svc._filter_condition_of_different_type_by_instance_selection(conditions, selections), [])

    def test_right_2(self):
        import uuid

        uuid.uuid4 = mock.Mock(return_value=uuid.UUID("fa17b2cbf38141d7a5a0591573fc0f82"))

        svc = RelatedPolicyBiz(settings.BK_APP_TENANT_ID)
        conditions = [
            ConditionBean(
                instances=[
                    InstanceBean(
                        type="host",
                        path=[
                            [{"system_id": "bk_cmdb", "type": "set", "id": "set1"}],
                            [
                                {"system_id": "bk_cmdb", "type": "biz", "id": "biz1"},
                                {"system_id": "bk_cmdb", "type": "host", "id": "host1"},
                            ],
                            [
                                {"system_id": "bk_cmdb", "type": "biz", "id": "biz1"},
                                {"system_id": "bk_cmdb", "type": "host", "id": "host2"},
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
                attributes=[],
            ),
            ConditionBean(
                instances=[
                    InstanceBean(
                        type="host",
                        path=[
                            [
                                {"system_id": "bk_cmdb", "type": "biz", "id": "biz2"},
                                {"system_id": "bk_cmdb", "type": "set", "id": "set1"},
                                {"system_id": "bk_cmdb", "type": "module", "id": "module1"},
                                {"system_id": "bk_cmdb", "type": "host", "id": "host2"},
                            ],
                        ],
                    ),
                ],
                attributes=[],
            ),
        ]
        selections = [
            InstanceSelection(
                id="test2",
                system_id="bk_cmdb",
                name="test2",
                name_en="test2",
                ignore_iam_path=False,
                resource_type_chain=[ChainNode(system_id="bk_cmdb", id="biz")],
            ),
        ]
        self.assertEqual(
            svc._filter_condition_of_different_type_by_instance_selection(conditions, selections),
            [
                ConditionBean(
                    id="fa17b2cbf38141d7a5a0591573fc0f82",
                    instances=[
                        InstanceBean(
                            type="biz",
                            path=[
                                [{"system_id": "bk_cmdb", "type": "biz", "id": "biz1"}],
                                [{"system_id": "bk_cmdb", "type": "biz", "id": "biz2"}],
                            ],
                        ),
                    ],
                    attributes=[],
                ),
            ],
        )


class FilterResourceTypeDifferentTypeTests(TestCase):
    def test_attribute(self):
        svc = RelatedPolicyBiz(settings.BK_APP_TENANT_ID)
        policy_rrt = RelatedResourceBean(system_id="bk_cmdb", type="host", condition=[])
        action_rrt = RelatedResourceType(
            id="biz",
            system_id="bk_cmdb",
            name_alias="test",
            name_alias_en="test",
            selection_mode=SelectionMode.ATTRIBUTE.value,
        )
        self.assertEqual(svc._filter_condition_of_different_type([policy_rrt], action_rrt), None)

    def test_one_rrt(self):
        import uuid

        uuid.uuid4 = mock.Mock(return_value=uuid.UUID("fa17b2cbf38141d7a5a0591573fc0f82"))

        svc = RelatedPolicyBiz(settings.BK_APP_TENANT_ID)
        policy_rrt = RelatedResourceBean(
            system_id="bk_cmdb",
            type="host",
            condition=[
                ConditionBean(
                    instances=[],
                    attributes=[Attribute(id="", name="", values=[{"id": "test2", "name": "test2"}])],
                ),
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
            ],
        )
        action_rrt = RelatedResourceType(
            id="biz",
            system_id="bk_cmdb",
            name_alias="test",
            name_alias_en="test",
            selection_mode=SelectionMode.ALL.value,
            instance_selections=[
                InstanceSelection(
                    id="test1",
                    system_id="bk_cmdb",
                    name="test1",
                    name_en="test1",
                    ignore_iam_path=False,
                    resource_type_chain=[ChainNode(system_id="bk_cmdb", id="biz")],
                )
            ],
        )
        self.assertEqual(
            svc._filter_condition_of_different_type([policy_rrt], action_rrt),
            RelatedResourceBean(
                system_id="bk_cmdb",
                type="biz",
                condition=[
                    ConditionBean(
                        id="fa17b2cbf38141d7a5a0591573fc0f82",
                        instances=[
                            InstanceBean(type="biz", path=[[{"system_id": "bk_cmdb", "type": "biz", "id": "biz1"}]]),
                        ],
                        attributes=[],
                    ),
                ],
            ),
        )

    def test_multi_rrt(self):
        import uuid

        uuid.uuid4 = mock.Mock(return_value=uuid.UUID("fa17b2cbf38141d7a5a0591573fc0f82"))

        svc = RelatedPolicyBiz(settings.BK_APP_TENANT_ID)
        policy_rrts = [
            RelatedResourceBean(
                system_id="bk_cmdb",
                type="host",
                condition=[
                    ConditionBean(
                        instances=[
                            InstanceBean(
                                type="host",
                                path=[
                                    [
                                        {"system_id": "bk_cmdb", "type": "set", "id": "set1"},
                                        {"system_id": "bk_cmdb", "type": "host", "id": "host1"},
                                    ],
                                    [
                                        {"system_id": "bk_cmdb", "type": "biz", "id": "biz1"},
                                        {"system_id": "bk_cmdb", "type": "set", "id": "set1"},
                                        {"system_id": "bk_cmdb", "type": "module", "id": "module1"},
                                        {"system_id": "bk_cmdb", "type": "host", "id": "host1"},
                                    ],
                                ],
                            ),
                            InstanceBean(type="biz", path=[[{"system_id": "bk_cmdb", "type": "biz", "id": "biz2"}]]),
                        ],
                        attributes=[],
                    ),
                ],
            ),
            RelatedResourceBean(
                system_id="bk_job",
                type="job",
                condition=[
                    ConditionBean(
                        instances=[
                            InstanceBean(
                                type="job",
                                path=[
                                    [{"system_id": "bk_job", "type": "job", "id": "job1"}],
                                    [
                                        {"system_id": "bk_cmdb", "type": "biz", "id": "biz1"},
                                        {"system_id": "bk_job", "type": "set", "id": "job2"},
                                    ],
                                ],
                            ),
                            InstanceBean(type="biz", path=[[{"system_id": "bk_cmdb", "type": "biz", "id": "biz2"}]]),
                        ],
                        attributes=[],
                    ),
                ],
            ),
        ]
        action_rrt = RelatedResourceType(
            id="biz",
            system_id="bk_cmdb",
            name_alias="test",
            name_alias_en="test",
            selection_mode=SelectionMode.ALL.value,
            instance_selections=[
                InstanceSelection(
                    id="test1",
                    system_id="bk_cmdb",
                    name="test1",
                    name_en="test1",
                    ignore_iam_path=False,
                    resource_type_chain=[ChainNode(system_id="bk_cmdb", id="biz")],
                )
            ],
        )
        self.assertEqual(
            svc._filter_condition_of_different_type(policy_rrts, action_rrt),
            RelatedResourceBean(
                system_id="bk_cmdb",
                type="biz",
                condition=[
                    ConditionBean(
                        id="fa17b2cbf38141d7a5a0591573fc0f82",
                        instances=[
                            InstanceBean(
                                type="biz",
                                path=[
                                    [{"system_id": "bk_cmdb", "type": "biz", "id": "biz1"}],
                                    [{"system_id": "bk_cmdb", "type": "biz", "id": "biz2"}],
                                ],
                            ),
                        ],
                        attributes=[],
                    ),
                ],
            ),
        )

    def test_multi_rrt_none(self):
        svc = RelatedPolicyBiz(settings.BK_APP_TENANT_ID)
        policy_rrts = [
            RelatedResourceBean(
                system_id="bk_cmdb",
                type="host",
                condition=[
                    ConditionBean(
                        instances=[
                            InstanceBean(
                                type="host",
                                path=[
                                    [
                                        {"system_id": "bk_cmdb", "type": "set", "id": "set1"},
                                        {"system_id": "bk_cmdb", "type": "host", "id": "host1"},
                                    ],
                                    [
                                        {"system_id": "bk_cmdb", "type": "biz", "id": "biz1"},
                                        {"system_id": "bk_cmdb", "type": "set", "id": "set1"},
                                        {"system_id": "bk_cmdb", "type": "module", "id": "module1"},
                                        {"system_id": "bk_cmdb", "type": "host", "id": "host1"},
                                    ],
                                ],
                            ),
                            InstanceBean(type="biz", path=[[{"system_id": "bk_cmdb", "type": "biz", "id": "biz2"}]]),
                        ],
                        attributes=[],
                    ),
                ],
            ),
            RelatedResourceBean(
                system_id="bk_job",
                type="job",
                condition=[
                    ConditionBean(
                        instances=[
                            InstanceBean(
                                type="job",
                                path=[
                                    [{"system_id": "bk_job", "type": "job", "id": "job1"}],
                                    [
                                        {"system_id": "bk_cmdb", "type": "biz", "id": "biz3"},
                                        {"system_id": "bk_job", "type": "set", "id": "job2"},
                                    ],
                                ],
                            ),
                            InstanceBean(type="biz", path=[[{"system_id": "bk_cmdb", "type": "biz", "id": "biz4"}]]),
                        ],
                        attributes=[],
                    ),
                ],
            ),
        ]
        action_rrt = RelatedResourceType(
            id="biz",
            system_id="bk_cmdb",
            name_alias="test",
            name_alias_en="test",
            selection_mode=SelectionMode.ALL.value,
            instance_selections=[
                InstanceSelection(
                    id="test1",
                    system_id="bk_cmdb",
                    name="test1",
                    name_en="test1",
                    ignore_iam_path=False,
                    resource_type_chain=[ChainNode(system_id="bk_cmdb", id="biz")],
                )
            ],
        )
        self.assertEqual(svc._filter_condition_of_different_type(policy_rrts, action_rrt), None)


class MergeMultiConditionsTests(TestCase):
    def test_empty(self):
        svc = RelatedPolicyBiz(settings.BK_APP_TENANT_ID)
        rrt_conditions = [
            [
                ConditionBean(
                    instances=[
                        InstanceBean(
                            type="biz",
                            path=[
                                [{"system_id": "bk_cmdb", "type": "biz", "id": "biz1"}],
                                [{"system_id": "bk_cmdb", "type": "biz", "id": "biz2"}],
                            ],
                        ),
                    ],
                    attributes=[],
                ),
            ],
            [
                ConditionBean(
                    instances=[
                        InstanceBean(type="biz", path=[[{"system_id": "bk_cmdb", "type": "biz", "id": "biz3"}]])
                    ],
                    attributes=[],
                ),
            ],
            [
                ConditionBean(
                    instances=[
                        InstanceBean(type="biz", path=[[{"system_id": "bk_cmdb", "type": "biz", "id": "biz4"}]])
                    ],
                    attributes=[],
                ),
            ],
        ]
        self.assertEqual(svc._merge_multi_conditions(rrt_conditions), [])

    def test_right(self):
        svc = RelatedPolicyBiz(settings.BK_APP_TENANT_ID)
        rrt_conditions = [
            [
                ConditionBean(
                    instances=[
                        InstanceBean(
                            type="biz",
                            path=[
                                [{"system_id": "bk_cmdb", "type": "biz", "id": "biz1"}],
                                [{"system_id": "bk_cmdb", "type": "biz", "id": "biz2"}],
                            ],
                        ),
                        InstanceBean(
                            type="host",
                            path=[
                                [{"system_id": "bk_cmdb", "type": "host", "id": "host1"}],
                                [{"system_id": "bk_cmdb", "type": "host", "id": "host2"}],
                            ],
                        ),
                    ],
                    attributes=[],
                ),
            ],
            [
                ConditionBean(
                    instances=[
                        InstanceBean(
                            type="biz",
                            path=[
                                [{"system_id": "bk_cmdb", "type": "biz", "id": "biz3"}],
                                [{"system_id": "bk_cmdb", "type": "biz", "id": "biz2"}],
                            ],
                        ),
                        InstanceBean(
                            type="host",
                            path=[[{"system_id": "bk_cmdb", "type": "host", "id": "host3"}]],
                        ),
                    ],
                    attributes=[],
                ),
            ],
            [
                ConditionBean(
                    instances=[
                        InstanceBean(
                            type="biz",
                            path=[
                                [{"system_id": "bk_cmdb", "type": "biz", "id": "biz4"}],
                                [{"system_id": "bk_cmdb", "type": "biz", "id": "biz2"}],
                            ],
                        ),
                        InstanceBean(
                            type="host",
                            path=[[{"system_id": "bk_cmdb", "type": "host", "id": "host4"}]],
                        ),
                    ],
                    attributes=[],
                ),
            ],
        ]
        self.assertEqual(
            svc._merge_multi_conditions(rrt_conditions),
            [
                ConditionBean(
                    instances=[
                        InstanceBean(type="biz", path=[[{"system_id": "bk_cmdb", "type": "biz", "id": "biz2"}]])
                    ],
                    attributes=[],
                )
            ],
        )


class CreateDependingPolicyTests(TestCase):
    def test_branch_1(self):
        policy = PolicyBean(
            id="create_host",
            related_resource_types=[],
            environment={},
            expired_at=PERMANENT_SECONDS,
        )
        action = Action(
            id="multi_rrt",
            name="test",
            name_en="test",
            description="test",
            description_en="test",
            type="create",
            related_resource_types=[
                RelatedResourceType(
                    id="biz",
                    system_id="bk_cmdb",
                    name_alias="test",
                    name_alias_en="test",
                ),
                RelatedResourceType(
                    id="host",
                    system_id="bk_cmdb",
                    name_alias="test",
                    name_alias_en="test",
                ),
            ],
            related_actions=[],
        )

        svc = RelatedPolicyBiz(settings.BK_APP_TENANT_ID)
        self.assertEqual(svc._create_related_policy(policy, action), None)

    def test_branch_2(self):
        policy = PolicyBean(
            id="create_host",
            related_resource_types=[],
            environment={},
            expired_at=PERMANENT_SECONDS,
        )
        action = Action(
            id="empty",
            name="test",
            name_en="test",
            description="test",
            description_en="test",
            type="create",
            related_resource_types=[],
            related_actions=[],
        )

        svc = RelatedPolicyBiz(settings.BK_APP_TENANT_ID)
        self.assertEqual(
            svc._create_related_policy(policy, action),
            PolicyBean(
                id="empty",
                related_resource_types=[],
                environment={},
                expired_at=policy.expired_at,
            ),
        )

    def test_branch_3(self):
        policy = PolicyBean(
            id="create_host",
            related_resource_types=[],
            environment={},
            expired_at=PERMANENT_SECONDS,
        )
        action = Action(
            id="empty",
            name="test",
            name_en="test",
            description="test",
            description_en="test",
            type="create",
            related_resource_types=[
                RelatedResourceType(
                    id="biz",
                    system_id="bk_cmdb",
                    name_alias="test",
                    name_alias_en="test",
                )
            ],
            related_actions=[],
        )

        svc = RelatedPolicyBiz(settings.BK_APP_TENANT_ID)
        self.assertEqual(svc._create_related_policy(policy, action), None)

    def test_branch_4(self):
        import uuid

        uuid.uuid4 = mock.Mock(return_value=uuid.UUID("00000000000000000000000000000000"))

        policy = PolicyBean(
            id="edit_host",
            related_resource_types=[
                RelatedResourceBean(
                    system_id="bk_cmdb",
                    type="host",
                    condition=[],
                )
            ],
            environment={},
            expired_at=PERMANENT_SECONDS,
        )
        action = Action(
            id="view_host",
            name="test",
            name_en="test",
            description="test",
            description_en="test",
            type="",
            related_resource_types=[
                RelatedResourceType(
                    id="host",
                    system_id="bk_cmdb",
                    name_alias="test",
                    name_alias_en="test",
                )
            ],
            related_actions=[],
        )

        svc = RelatedPolicyBiz(settings.BK_APP_TENANT_ID)
        self.assertEqual(
            svc._create_related_policy(policy, action),
            PolicyBean(
                id="view_host",
                related_resource_types=[
                    RelatedResourceBean(
                        system_id="bk_cmdb",
                        type="host",
                        condition=[],
                    )
                ],
                environment={},
                expired_at=PERMANENT_SECONDS,
            ),
        )

    def test_branch_5(self):
        import uuid

        uuid.uuid4 = mock.Mock(return_value=uuid.UUID("00000000000000000000000000000000"))

        policy = PolicyBean(
            id="edit_host",
            related_resource_types=[
                RelatedResourceBean(
                    system_id="bk_cmdb",
                    type="host",
                    condition=[
                        ConditionBean(
                            instances=[
                                InstanceBean(
                                    type="host",
                                    path=[
                                        [
                                            {"system_id": "bk_cmdb", "type": "biz", "id": "biz2"},
                                            {"system_id": "bk_cmdb", "type": "set", "id": "set1"},
                                            {"system_id": "bk_cmdb", "type": "module", "id": "module1"},
                                            {"system_id": "bk_cmdb", "type": "host", "id": "host2"},
                                        ],
                                    ],
                                ),
                            ],
                            attributes=[],
                        )
                    ],
                )
            ],
            environment={},
            expired_at=PERMANENT_SECONDS,
        )
        action = Action(
            id="view_host",
            name="test",
            name_en="test",
            description="test",
            description_en="test",
            type="",
            related_resource_types=[
                RelatedResourceType(
                    id="host",
                    system_id="bk_cmdb",
                    name_alias="test",
                    name_alias_en="test",
                    instance_selections=[
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
                        )
                    ],
                )
            ],
            related_actions=[],
        )

        svc = RelatedPolicyBiz(settings.BK_APP_TENANT_ID)
        self.assertEqual(
            svc._create_related_policy(policy, action),
            PolicyBean(
                id="view_host",
                related_resource_types=[
                    RelatedResourceBean(
                        system_id="bk_cmdb",
                        type="host",
                        condition=[
                            ConditionBean(
                                instances=[
                                    InstanceBean(
                                        type="host",
                                        path=[
                                            [
                                                {"system_id": "bk_cmdb", "type": "biz", "id": "biz2"},
                                                {"system_id": "bk_cmdb", "type": "set", "id": "set1"},
                                                {"system_id": "bk_cmdb", "type": "module", "id": "module1"},
                                                {"system_id": "bk_cmdb", "type": "host", "id": "host2"},
                                            ],
                                        ],
                                    ),
                                ],
                                attributes=[],
                            )
                        ],
                    )
                ],
                environment={},
                expired_at=PERMANENT_SECONDS,
            ),
        )

    def test_branch_6(self):
        import uuid

        uuid.uuid4 = mock.Mock(return_value=uuid.UUID("00000000000000000000000000000000"))

        policy = PolicyBean(
            id="edit_host",
            related_resource_types=[
                RelatedResourceBean(
                    system_id="bk_cmdb",
                    type="host",
                    condition=[
                        ConditionBean(
                            instances=[
                                InstanceBean(
                                    type="host",
                                    path=[
                                        [
                                            {"system_id": "bk_cmdb", "type": "biz", "id": "biz2"},
                                            {"system_id": "bk_cmdb", "type": "set", "id": "set1"},
                                            {"system_id": "bk_cmdb", "type": "module", "id": "module1"},
                                            {"system_id": "bk_cmdb", "type": "host", "id": "host2"},
                                        ],
                                    ],
                                ),
                            ],
                            attributes=[],
                        )
                    ],
                )
            ],
            environment={},
            expired_at=PERMANENT_SECONDS,
        )
        action = Action(
            id="view_biz",
            name="test",
            name_en="test",
            description="test",
            description_en="test",
            type="",
            related_resource_types=[
                RelatedResourceType(
                    id="biz",
                    system_id="bk_cmdb",
                    name_alias="test",
                    name_alias_en="test",
                    instance_selections=[
                        InstanceSelection(
                            id="test1",
                            system_id="bk_cmdb",
                            name="test1",
                            name_en="test1",
                            ignore_iam_path=False,
                            resource_type_chain=[ChainNode(system_id="bk_cmdb", id="biz")],
                        )
                    ],
                )
            ],
            related_actions=[],
        )

        svc = RelatedPolicyBiz(settings.BK_APP_TENANT_ID)
        self.assertEqual(
            svc._create_related_policy(policy, action),
            PolicyBean(
                id="view_biz",
                related_resource_types=[
                    RelatedResourceBean(
                        system_id="bk_cmdb",
                        type="biz",
                        condition=[
                            ConditionBean(
                                id="00000000000000000000000000000000",
                                instances=[
                                    InstanceBean(
                                        type="biz",
                                        path=[[{"system_id": "bk_cmdb", "type": "biz", "id": "biz2"}]],
                                    ),
                                ],
                                attributes=[],
                            )
                        ],
                    )
                ],
                environment={},
                expired_at=PERMANENT_SECONDS,
            ),
        )

    def test_branch_7(self):
        policy = PolicyBean(
            id="edit_host",
            related_resource_types=[
                RelatedResourceBean(
                    system_id="bk_cmdb",
                    type="host",
                    condition=[
                        ConditionBean(
                            instances=[
                                InstanceBean(
                                    type="host",
                                    path=[
                                        [
                                            {"system_id": "bk_cmdb", "type": "biz", "id": "biz2"},
                                            {"system_id": "bk_cmdb", "type": "set", "id": "set1"},
                                            {"system_id": "bk_cmdb", "type": "module", "id": "module1"},
                                            {"system_id": "bk_cmdb", "type": "host", "id": "host2"},
                                        ],
                                    ],
                                ),
                            ],
                            attributes=[],
                        )
                    ],
                )
            ],
            environment={},
            expired_at=PERMANENT_SECONDS,
        )
        action = Action(
            id="view_biz",
            name="test",
            name_en="test",
            description="test",
            description_en="test",
            type="",
            related_resource_types=[
                RelatedResourceType(
                    id="biz",
                    system_id="bk_cmdb",
                    name_alias="test",
                    name_alias_en="test",
                    instance_selections=[
                        InstanceSelection(
                            id="test1",
                            system_id="bk_cmdb",
                            name="test1",
                            name_en="test1",
                            ignore_iam_path=False,
                            resource_type_chain=[ChainNode(system_id="bk_cmdb", id="set")],
                        )
                    ],
                )
            ],
            related_actions=[],
        )

        svc = RelatedPolicyBiz(settings.BK_APP_TENANT_ID)
        self.assertEqual(svc._create_related_policy(policy, action), None)

    def test_create_recommend_policies(self):
        policy = PolicyBean(
            id="edit_host",
            related_resource_types=[
                RelatedResourceBean(
                    system_id="bk_cmdb",
                    type="host",
                    condition=[
                        ConditionBean(
                            instances=[
                                InstanceBean(
                                    type="host",
                                    path=[
                                        [
                                            {"system_id": "bk_cmdb", "type": "host", "id": "host1"},
                                        ],
                                    ],
                                ),
                            ],
                            attributes=[],
                        )
                    ],
                )
            ],
            environment={},
            expired_at=PERMANENT_SECONDS,
        )
        action = Action(
            id="view_host",
            name="test",
            name_en="test",
            description="test",
            description_en="test",
            type="",
            related_resource_types=[
                RelatedResourceType(
                    id="host",
                    system_id="bk_cmdb",
                    name_alias="test",
                    name_alias_en="test",
                    instance_selections=[
                        InstanceSelection(
                            id="test1",
                            system_id="bk_cmdb",
                            name="test1",
                            name_en="test1",
                            ignore_iam_path=False,
                            resource_type_chain=[ChainNode(system_id="bk_cmdb", id="host")],
                        )
                    ],
                )
            ],
            related_actions=[],
        )

        action1 = action.copy(deep=True)
        action1.id = "edit_host"

        uuid.uuid4 = mock.Mock(return_value=uuid.UUID(DEFAULT_RESOURCE_GROUP_ID))

        svc = RelatedPolicyBiz(settings.BK_APP_TENANT_ID)
        recommend_policies = svc.create_recommend_policies(policy, ActionList([action, action1]), ["view_host"])

        self.assertEqual(len(recommend_policies), 1)
