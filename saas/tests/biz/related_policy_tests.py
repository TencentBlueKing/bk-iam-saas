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
import mock
from django.test import TestCase

from backend.biz.policy import ConditionBean, InstanceBean, PolicyBean, RelatedResourceBean
from backend.biz.related_policy import RelatedPolicyBiz
from backend.common.time import PERMANENT_SECONDS
from backend.service.constants import SelectionMode
from backend.service.models import Action, Attribute, ChainNode, InstanceSelection, RelatedResourceType
from tests.test_util.factory import ActionFactory, PolicyBeanFactory


class FilterResourceTypeSameTypeTests(TestCase):
    def setUp(self) -> None:
        import uuid

        uuid.uuid4 = mock.Mock(return_value=uuid.UUID("fa17b2cbf38141d7a5a0591573fc0f82"))

    def test_attribute(self):
        svc = RelatedPolicyBiz()
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
                    attributes=[Attribute(id="", name="", values=[{"id": "test1", "name": ""}])],
                ),
                ConditionBean(
                    instances=[],
                    attributes=[Attribute(id="", name="", values=[{"id": "test2", "name": ""}])],
                ),
            ],
        )
        action_rrt = RelatedResourceType(
            id="host",
            system_id="bk_cmdb",
            name="test",
            name_en="test",
            selection_mode=SelectionMode.ATTRIBUTE.value,
        )
        self.assertEqual(
            svc._filter_condition_of_same_type(policy_rrt, action_rrt),
            RelatedResourceBean(
                system_id="bk_cmdb",
                type="host",
                condition=[
                    ConditionBean(
                        instances=[], attributes=[Attribute(id="", name="", values=[{"id": "test2", "name": ""}])]
                    )
                ],
            ),
        )

    def test_instance(self):
        svc = RelatedPolicyBiz()
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
                    attributes=[Attribute(id="", name="", values=[{"id": "test1", "name": ""}])],
                ),
                ConditionBean(
                    instances=[],
                    attributes=[Attribute(id="", name="", values=[{"id": "test2", "name": ""}])],
                ),
            ],
        )
        action_rrt = RelatedResourceType(
            id="host",
            system_id="bk_cmdb",
            name="test",
            name_en="test",
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
        svc = RelatedPolicyBiz()
        policy_rrt = RelatedResourceBean(
            system_id="bk_cmdb",
            type="host",
            condition=[
                ConditionBean(
                    instances=[],
                    attributes=[Attribute(id="", name="", values=[{"id": "test2", "name": ""}])],
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
                    attributes=[Attribute(id="", name="", values=[{"id": "test1", "name": ""}])],
                ),
            ],
        )
        action_rrt = RelatedResourceType(
            id="host",
            system_id="bk_cmdb",
            name="test",
            name_en="test",
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
                        instances=[],
                        attributes=[Attribute(id="", name="", values=[{"id": "test2", "name": ""}])],
                    ),
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
                        attributes=[Attribute(id="", name="", values=[{"id": "test1", "name": ""}])],
                    ),
                ],
            ),
        )

    def test_none(self):
        svc = RelatedPolicyBiz()
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
            name="test",
            name_en="test",
            selection_mode=SelectionMode.ATTRIBUTE.value,
        )
        self.assertEqual(svc._filter_condition_of_same_type(policy_rrt, action_rrt), None)


class FilterConditionDifferentTypeTests(TestCase):
    def test_right_1(self):
        svc = RelatedPolicyBiz()
        conditions = [ConditionBean(instances=[], attributes=[])]
        selections = []
        self.assertEqual(svc._filter_condition_of_different_type_by_instance_selection(conditions, selections), [])

    def test_right_2(self):
        import uuid

        uuid.uuid4 = mock.Mock(return_value=uuid.UUID("fa17b2cbf38141d7a5a0591573fc0f82"))

        svc = RelatedPolicyBiz()
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
        svc = RelatedPolicyBiz()
        policy_rrt = RelatedResourceBean(system_id="bk_cmdb", type="host", condition=[])
        action_rrt = RelatedResourceType(
            id="biz",
            system_id="bk_cmdb",
            name="test",
            name_en="test",
            selection_mode=SelectionMode.ATTRIBUTE.value,
        )
        self.assertEqual(svc._filter_condition_of_different_type([policy_rrt], action_rrt), None)

    def test_one_rrt(self):
        import uuid

        uuid.uuid4 = mock.Mock(return_value=uuid.UUID("fa17b2cbf38141d7a5a0591573fc0f82"))

        svc = RelatedPolicyBiz()
        policy_rrt = RelatedResourceBean(
            system_id="bk_cmdb",
            type="host",
            condition=[
                ConditionBean(
                    instances=[],
                    attributes=[Attribute(id="", name="", values=[{"id": "test2", "name": ""}])],
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
                    attributes=[Attribute(id="", name="", values=[{"id": "test1", "name": ""}])],
                ),
            ],
        )
        action_rrt = RelatedResourceType(
            id="biz",
            system_id="bk_cmdb",
            name="test",
            name_en="test",
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

        svc = RelatedPolicyBiz()
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
        action_rrt = action_rrt = RelatedResourceType(
            id="biz",
            system_id="bk_cmdb",
            name="test",
            name_en="test",
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
        svc = RelatedPolicyBiz()
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
        action_rrt = action_rrt = RelatedResourceType(
            id="biz",
            system_id="bk_cmdb",
            name="test",
            name_en="test",
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
        svc = RelatedPolicyBiz()
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
        import uuid

        uuid.uuid4 = mock.Mock(return_value=uuid.UUID("fa17b2cbf38141d7a5a0591573fc0f82"))

        svc = RelatedPolicyBiz()
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
        policy = PolicyBean(id="create_host", related_resource_types=[], expired_at=PERMANENT_SECONDS)
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
                    name="test",
                    name_en="test",
                ),
                RelatedResourceType(
                    id="host",
                    system_id="bk_cmdb",
                    name="test",
                    name_en="test",
                ),
            ],
            related_actions=[],
        )

        svc = RelatedPolicyBiz()
        self.assertEqual(svc._create_related_policy(policy, action), None)

    def test_branch_2(self):
        policy = PolicyBean(
            id="create_host",
            related_resource_types=[],
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

        svc = RelatedPolicyBiz()
        self.assertEqual(
            svc._create_related_policy(policy, action),
            PolicyBean(
                id="empty",
                related_resource_types=[],
                expired_at=policy.expired_at,
            ),
        )

    def test_branch_3(self):
        policy = PolicyBean(
            id="create_host",
            related_resource_types=[],
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
                    name="test",
                    name_en="test",
                )
            ],
            related_actions=[],
        )

        svc = RelatedPolicyBiz()
        self.assertEqual(svc._create_related_policy(policy, action), None)

    def test_branch_4(self):
        policy = PolicyBean(
            id="edit_host",
            related_resource_types=[
                RelatedResourceBean(
                    system_id="bk_cmdb",
                    type="host",
                    condition=[],
                )
            ],
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
                    name="test",
                    name_en="test",
                )
            ],
            related_actions=[],
        )

        svc = RelatedPolicyBiz()
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
                expired_at=PERMANENT_SECONDS,
            ),
        )

    def test_branch_5(self):
        import uuid

        uuid.uuid4 = mock.Mock(return_value=uuid.UUID("fa17b2cbf38141d7a5a0591573fc0f82"))

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
                    name="test",
                    name_en="test",
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

        svc = RelatedPolicyBiz()
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
                expired_at=PERMANENT_SECONDS,
            ),
        )

    def test_branch_6(self):
        import uuid

        uuid.uuid4 = mock.Mock(return_value=uuid.UUID("fa17b2cbf38141d7a5a0591573fc0f82"))

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
                    name="test",
                    name_en="test",
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

        svc = RelatedPolicyBiz()
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
                                id="fa17b2cbf38141d7a5a0591573fc0f82",
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
                    name="test",
                    name_en="test",
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

        svc = RelatedPolicyBiz()
        self.assertEqual(svc._create_related_policy(policy, action), None)


class CreateRelatedPoliciesTests(TestCase):
    def test_create_related_policies_empty(self):
        action_factory = ActionFactory()
        action = action_factory.example()
        action.id = "action"

        policy_factory = PolicyBeanFactory()
        policy = policy_factory.example()
        policy.action_id = "policy"

        svc = RelatedPolicyBiz()
        with mock.patch.object(svc.action_svc, "list") as mock_func:
            mock_func.return_value = [action]

            related_policies = svc.create_related_policies("test", policy)

            self.assertEqual(related_policies, [])

        action.related_actions = []
        policy.action_id = "action"

        with mock.patch.object(svc.action_svc, "list") as mock_func:
            mock_func.return_value = [action]

            svc = RelatedPolicyBiz()
            related_policies = svc.create_related_policies("test", policy)

            self.assertEqual(related_policies, [])

    def test_create_related_policies_ok(self):
        action_factory = ActionFactory()
        action = action_factory.example()
        action.id = "action1"
        action.related_actions = ["action2", "action3"]

        action2 = action_factory.example()
        action2.id = "action2"

        policy_factory = PolicyBeanFactory()
        policy = policy_factory.example()
        policy.action_id = "action1"

        policy2 = policy_factory.example()
        policy2.action_id = "action2"

        svc = RelatedPolicyBiz()
        with mock.patch.object(svc.action_svc, "list") as mock_func, mock.patch.object(
            svc, "_create_related_policy"
        ) as mock_create:
            mock_func.return_value = [action, action2]
            mock_create.return_value = policy2

            related_policies = svc.create_related_policies("test", policy)
            self.assertEqual(len(related_policies), 1)
            self.assertEqual(related_policies[0], policy2)
