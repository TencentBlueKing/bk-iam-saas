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

from backend.biz.constants import PolicyTag
from backend.biz.policy_tag import (
    AttributeTagBean,
    ConditionTagBean,
    ConditionTagBiz,
    InstanceTagBean,
    PathNodeTagBean,
    PolicyTagBean,
    PolicyTagBeanList,
    RelatedResourceTagBean,
    ValueTagBean,
)
from backend.component import iam
from tests.test_util.factory import AttributeFactory, ConditionFactory, InstanceFactory


class CompareAndTagAttributeTests(TestCase):
    def setUp(self):
        self.attribute_factory = AttributeFactory()

    def test_compare_and_tag_attribute(self):
        new_attribute = self.attribute_factory.new(
            "id", "name", [{"id": "id1", "name": "name1"}, {"id": "id2", "name": "name2"}]
        )

        old_attribute = self.attribute_factory.new(
            "id", "name", [{"id": "id2", "name": "name1"}, {"id": "id3", "name": "name2"}]
        )

        diff_attribute = AttributeTagBean(**new_attribute.dict()).compare_and_tag(
            AttributeTagBean(**old_attribute.dict())
        )

        self.assertEqual(diff_attribute.tag, "unchanged")
        self.assertEqual(diff_attribute.values[0].tag, "add")
        self.assertEqual(diff_attribute.values[1].tag, "unchanged")
        self.assertEqual(diff_attribute.values[2].tag, "delete")


class CompareAndTagInstanceTests(TestCase):
    def setUp(self):
        self.instance_factory = InstanceFactory()

    def test_compare_and_tag_instance(self):
        new_instance = self.instance_factory.new(
            "type",
            "name",
            [
                [{"type": "type", "type_name": "name", "id": "id1", "name": "name1"}],
                [{"type": "type", "type_name": "name", "id": "id2", "name": "name2"}],
            ],
        )

        old_instance = self.instance_factory.new(
            "type",
            "name",
            [
                [{"type": "type", "type_name": "name", "id": "id2", "name": "name2"}],
                [{"type": "type", "type_name": "name", "id": "id3", "name": "name3"}],
            ],
        )

        diff_instance = InstanceTagBean(**new_instance.dict()).compare_and_tag(InstanceTagBean(**old_instance.dict()))

        self.assertEqual(diff_instance.tag, "unchanged")
        self.assertEqual(diff_instance.path[0][-1].tag, "add")
        self.assertEqual(diff_instance.path[1][-1].tag, "unchanged")
        self.assertEqual(diff_instance.path[2][-1].tag, "delete")


class CompareAndTagConditionTests(TestCase):
    def setUp(self):
        self.condition_factory = ConditionFactory()
        self.attribute_factory = AttributeFactory()
        self.instance_factory = InstanceFactory()

    def test_condition_compare_and_tag(self):
        new_condition = self.condition_factory.new(
            instances=[
                self.instance_factory.new(
                    "type", "name", [[{"type": "type", "type_name": "name", "id": "id1", "name": "name1"}]]
                ),
                self.instance_factory.new(
                    "type1", "name", [[{"type": "type1", "type_name": "name", "id": "id1", "name": "name1"}]]
                ),
            ],
            attributes=[
                self.attribute_factory.new("id", "name", [{"id": "id1", "name": "name1"}]),
                self.attribute_factory.new("id1", "name", [{"id": "id1", "name": "name1"}]),
            ],
        )

        old_condition = self.condition_factory.new(
            instances=[
                self.instance_factory.new(
                    "type", "name", [[{"type": "type", "type_name": "name", "id": "id2", "name": "name2"}]]
                ),
                self.instance_factory.new(
                    "type2", "name", [[{"type": "type2", "type_name": "name", "id": "id1", "name": "name1"}]]
                ),
            ],
            attributes=[
                self.attribute_factory.new("id", "name", [{"id": "id1", "name": "name1"}]),
                self.attribute_factory.new("id2", "name", [{"id": "id1", "name": "name1"}]),
            ],
        )

        diff_condition = ConditionTagBean(**new_condition.dict()).compare_and_tag(
            ConditionTagBean(**old_condition.dict())
        )

        self.assertEqual(diff_condition.tag, "unchanged")
        self.assertEqual(len(diff_condition.instances), 3)
        self.assertEqual(diff_condition.instances[0].tag, "unchanged")
        self.assertEqual(diff_condition.instances[1].tag, "add")
        self.assertEqual(diff_condition.instances[2].tag, "delete")
        self.assertEqual(len(diff_condition.attributes), 3)
        self.assertEqual(diff_condition.attributes[0].tag, "unchanged")
        self.assertEqual(diff_condition.attributes[1].tag, "add")
        self.assertEqual(diff_condition.attributes[2].tag, "delete")


class CompareAndTagConditionsTests(TestCase):
    def test_right(self):
        new_conditions = [
            {
                "id": "1",
                "instances": [],
                "attributes": [
                    {
                        "id": "id2",
                        "name": "name1",
                        "values": [{"id": "id1", "name": "name1"}, {"id": "id2", "name": "name2"}],
                    }
                ],
            },
            {
                "id": "2",
                "instances": [],
                "attributes": [
                    {
                        "id": "id3",
                        "name": "name1",
                        "values": [{"id": "id1", "name": "name1"}, {"id": "id2", "name": "name2"}],
                    }
                ],
            },
            {
                "id": "3",
                "instances": [
                    {
                        "type": "test1",
                        "name": "test1",
                        "path": [[{"type": "test1", "type_name": "test1", "id": "id1", "name": "id1"}]],
                    }
                ],
                "attributes": [
                    {
                        "id": "id2",
                        "name": "name1",
                        "values": [{"id": "id1", "name": "name1"}, {"id": "id2", "name": "name2"}],
                    }
                ],
            },
            {
                "id": "4",
                "instances": [
                    {
                        "type": "test1",
                        "name": "test1",
                        "path": [[{"type": "test1", "type_name": "test1", "id": "id1", "name": "id1"}]],
                    }
                ],
                "attributes": [
                    {
                        "id": "id3",
                        "name": "name1",
                        "values": [{"id": "id1", "name": "name1"}, {"id": "id2", "name": "name2"}],
                    }
                ],
            },
        ]

        old_conditions = [
            {
                "id": "2",
                "instances": [],
                "attributes": [
                    {
                        "id": "id3",
                        "name": "name1",
                        "values": [{"id": "id1", "name": "name1"}, {"id": "id2", "name": "name2"}],
                    }
                ],
            },
            {"id": "3", "instances": [], "attributes": []},
            {
                "id": "4",
                "instances": [
                    {
                        "type": "test1",
                        "name": "test1",
                        "path": [[{"type": "test1", "type_name": "test1", "id": "id1", "name": "id1"}]],
                    }
                ],
                "attributes": [
                    {
                        "id": "id3",
                        "name": "name1",
                        "values": [{"id": "id1", "name": "name1"}, {"id": "id2", "name": "name2"}],
                    }
                ],
            },
            {
                "id": "5",
                "instances": [
                    {
                        "type": "test1",
                        "name": "test1",
                        "path": [[{"type": "test1", "type_name": "test1", "id": "id1", "name": "id1"}]],
                    }
                ],
                "attributes": [
                    {
                        "id": "id4",
                        "name": "name1",
                        "values": [{"id": "id1", "name": "name1"}, {"id": "id2", "name": "name2"}],
                    }
                ],
            },
        ]

        new_conditions = [ConditionTagBean(**c) for c in new_conditions]
        old_conditions = [ConditionTagBean(**c) for c in old_conditions]

        svc = ConditionTagBiz()

        result = [
            ConditionTagBean(**c)
            for c in [
                {
                    "instances": [],
                    "attributes": [
                        {
                            "id": "id2",
                            "name": "name1",
                            "values": [
                                {"id": "id1", "name": "name1", "tag": "add"},
                                {"id": "id2", "name": "name2", "tag": "add"},
                            ],
                            "tag": "add",
                        }
                    ],
                    "id": "1",
                    "tag": "add",
                },
                {
                    "instances": [],
                    "attributes": [
                        {
                            "id": "id3",
                            "name": "name1",
                            "values": [
                                {"id": "id1", "name": "name1", "tag": "unchanged"},
                                {"id": "id2", "name": "name2", "tag": "unchanged"},
                            ],
                            "tag": "unchanged",
                        }
                    ],
                    "id": "2",
                    "tag": "unchanged",
                },
                {
                    "instances": [
                        {
                            "type": "test1",
                            "name": "test1",
                            "name_en": "",
                            "path": [
                                [{"tag": "add", "type": "test1", "type_name": "test1", "id": "id1", "name": "id1"}]
                            ],
                            "tag": "add",
                        }
                    ],
                    "attributes": [
                        {
                            "id": "id2",
                            "name": "name1",
                            "values": [
                                {"id": "id1", "name": "name1", "tag": "add"},
                                {"id": "id2", "name": "name2", "tag": "add"},
                            ],
                            "tag": "add",
                        }
                    ],
                    "id": "3",
                    "tag": "add",
                },
                {"instances": [], "attributes": [], "id": "3", "tag": "delete"},
                {
                    "instances": [
                        {
                            "type": "test1",
                            "name": "test1",
                            "name_en": "",
                            "path": [
                                [
                                    {
                                        "tag": "unchanged",
                                        "type": "test1",
                                        "type_name": "test1",
                                        "id": "id1",
                                        "name": "id1",
                                    }
                                ]
                            ],
                            "tag": "unchanged",
                        }
                    ],
                    "attributes": [
                        {
                            "id": "id3",
                            "name": "name1",
                            "values": [
                                {"id": "id1", "name": "name1", "tag": "unchanged"},
                                {"id": "id2", "name": "name2", "tag": "unchanged"},
                            ],
                            "tag": "unchanged",
                        }
                    ],
                    "id": "4",
                    "tag": "unchanged",
                },
                {
                    "instances": [
                        {
                            "type": "test1",
                            "name": "test1",
                            "name_en": "",
                            "path": [
                                [{"tag": "delete", "type": "test1", "type_name": "test1", "id": "id1", "name": "id1"}]
                            ],
                            "tag": "delete",
                        }
                    ],
                    "attributes": [
                        {
                            "id": "id4",
                            "name": "name1",
                            "values": [
                                {"id": "id1", "name": "name1", "tag": "delete"},
                                {"id": "id2", "name": "name2", "tag": "delete"},
                            ],
                            "tag": "delete",
                        }
                    ],
                    "id": "5",
                    "tag": "delete",
                },
            ]
        ]

        self.assertEqual(svc.compare_and_tag(new_conditions, old_conditions, True), result)


class PolicyTagBeanListTests(TestCase):
    def test_merge(self):
        new_policy_list = PolicyTagBeanList(
            "system_id",
            [
                PolicyTagBean(
                    **{
                        "type": "edit",
                        "id": "edit_host",
                        "name": "编辑主机",
                        "description": "",
                        "related_resource_types": [],
                        "environment": {},
                        "expired_at": 31536000,
                    }
                ),
                PolicyTagBean(
                    **{
                        "type": "edit",
                        "id": "view_host",
                        "name": "查看主机",
                        "description": "",
                        "related_resource_types": [],
                        "environment": {},
                        "expired_at": 31536000,
                    }
                ),
            ],
        )

        old_policy_list = PolicyTagBeanList(
            "system_id",
            [
                PolicyTagBean(
                    **{
                        "type": "edit",
                        "id": "view_host",
                        "name": "查看主机",
                        "description": "",
                        "related_resource_types": [{"system_id": "bk_cmdb", "type": "host", "condition": []}],
                        "environment": {},
                        "policy_id": 1,
                        "expired_at": 31536000,
                    }
                ),
                PolicyTagBean(
                    **{
                        "type": "edit",
                        "id": "delete_host",
                        "name": "查看主机",
                        "description": "",
                        "related_resource_types": [],
                        "environment": {},
                        "expired_at": 31536000,
                    }
                ),
            ],
        )

        policy_list = old_policy_list.merge(new_policy_list)
        self.assertEquals(len(policy_list.policies), 3)
        self.assertEquals(policy_list.policies[0].tag, "update")

    def test_fill_empty_fields(self):
        from backend.util.cache import cache_dictionary

        cache_dictionary.clear()

        iam.list_action = mock.Mock(
            return_value=[
                {
                    "description": "",
                    "description_en": "",
                    "id": "view_host",
                    "name": "查看主机",
                    "name_en": "view_host",
                    "related_actions": [],
                    "related_resource_types": [
                        {
                            "id": "host",
                            "instance_selections": [],
                            "name": "主机",
                            "name_en": "host",
                            "scope": None,
                            "system_id": "bk_cmdb",
                        }
                    ],
                    "type": "view",
                    "version": 0,
                },
            ]
        )

        iam.list_resource_type = mock.Mock(return_value={"bk_cmdb": [{"id": "host", "name": "主机", "name_en": "host"}]})

        policy = PolicyTagBean(
            **{
                "id": "view_host",
                "related_resource_types": [
                    {
                        "system_id": "bk_cmdb",
                        "type": "host",
                        "condition": [
                            {
                                "instances": [
                                    {
                                        "type": "host",
                                        "path": [
                                            [{"id": "host1", "name": "主机1", "system_id": "bk_cmdb", "type": "host"}]
                                        ],
                                    }
                                ],
                                "attributes": [
                                    {"id": "os", "name": "os", "values": [{"id": "linux", "name": "linux"}]}
                                ],
                                "id": "6280159a089847b99648faf3b5ff9e35",
                            }
                        ],
                    }
                ],
            }
        )

        policy_list = PolicyTagBeanList("bk_cmdb", [policy])
        policy_list.fill_empty_fields()

        want = [
            PolicyTagBean(
                id="view_host",
                related_resource_types=[
                    RelatedResourceTagBean(
                        system_id="bk_cmdb",
                        type="host",
                        condition=[
                            ConditionTagBean(
                                instances=[
                                    InstanceTagBean(
                                        type="host",
                                        path=[
                                            [
                                                PathNodeTagBean(
                                                    id="host1",
                                                    name="主机1",
                                                    system_id="bk_cmdb",
                                                    type="host",
                                                    type_name="主机",
                                                    type_name_en="host",
                                                    tag="",
                                                )
                                            ]
                                        ],
                                        name="主机",
                                        name_en="host",
                                        tag="",
                                    )
                                ],
                                attributes=[
                                    AttributeTagBean(
                                        id="os",
                                        name="os",
                                        values=[ValueTagBean(id="linux", name="linux", tag="")],
                                        tag="",
                                    )
                                ],
                                id="6280159a089847b99648faf3b5ff9e35",
                                tag="",
                            )
                        ],
                        name="主机",
                        name_en="host",
                        selection_mode="instance",
                    )
                ],
                policy_id=0,
                expired_at=0,
                type="view",
                name="查看主机",
                name_en="view_host",
                description="",
                description_en="",
                expired_display="",
                tag="",
            )
        ]

        self.assertEquals(policy_list.policies, want)

    def test_sub(self):
        policies = [
            PolicyTagBean(
                **{
                    "id": "view_host",
                    "related_resource_types": [
                        {
                            "system_id": "bk_cmdb",
                            "type": "host",
                            "condition": [
                                {
                                    "instances": [
                                        {
                                            "type": "host",
                                            "path": [
                                                [
                                                    {
                                                        "id": "host1",
                                                        "name": "主机1",
                                                        "system_id": "bk_cmdb",
                                                        "type": "host",
                                                    }
                                                ],
                                                [
                                                    {
                                                        "id": "host2",
                                                        "name": "主机2",
                                                        "system_id": "bk_cmdb",
                                                        "type": "host",
                                                    }
                                                ],
                                            ],
                                        }
                                    ],
                                    "attributes": [
                                        {"id": "os", "name": "os", "values": [{"id": "linux", "name": "linux"}]}
                                    ],
                                    "id": "6280159a089847b99648faf3b5ff9e35",
                                }
                            ],
                        }
                    ],
                }
            ),
            PolicyTagBean(
                **{
                    "id": "edit_host",
                    "related_resource_types": [
                        {
                            "system_id": "bk_cmdb",
                            "type": "host",
                            "condition": [
                                {
                                    "instances": [
                                        {
                                            "type": "host",
                                            "path": [
                                                [
                                                    {
                                                        "id": "host1",
                                                        "name": "主机1",
                                                        "system_id": "bk_cmdb",
                                                        "type": "host",
                                                    }
                                                ]
                                            ],
                                        }
                                    ],
                                    "attributes": [
                                        {"id": "os", "name": "os", "values": [{"id": "linux", "name": "linux"}]}
                                    ],
                                    "id": "6280159a089847b99648faf3b5ff9e35",
                                }
                            ],
                        }
                    ],
                }
            ),
        ]

        policies2 = [
            PolicyTagBean(
                **{
                    "id": "view_host",
                    "related_resource_types": [
                        {
                            "system_id": "bk_cmdb",
                            "type": "host",
                            "condition": [
                                {
                                    "instances": [
                                        {
                                            "type": "host",
                                            "path": [
                                                [
                                                    {
                                                        "id": "host2",
                                                        "name": "主机2",
                                                        "system_id": "bk_cmdb",
                                                        "type": "host",
                                                    }
                                                ]
                                            ],
                                        }
                                    ],
                                    "attributes": [
                                        {"id": "os", "name": "os", "values": [{"id": "linux", "name": "linux"}]}
                                    ],
                                    "id": "6280159a089847b99648faf3b5ff9e35",
                                }
                            ],
                        }
                    ],
                }
            ),
            PolicyTagBean(
                **{
                    "id": "edit_host",
                    "related_resource_types": [
                        {
                            "system_id": "bk_cmdb",
                            "type": "host",
                            "condition": [
                                {
                                    "instances": [
                                        {
                                            "type": "host",
                                            "path": [
                                                [
                                                    {
                                                        "id": "host1",
                                                        "name": "主机1",
                                                        "system_id": "bk_cmdb",
                                                        "type": "host",
                                                    }
                                                ]
                                            ],
                                        }
                                    ],
                                    "attributes": [
                                        {"id": "os", "name": "os", "values": [{"id": "linux", "name": "linux"}]}
                                    ],
                                    "id": "6280159a089847b99648faf3b5ff9e35",
                                }
                            ],
                        }
                    ],
                }
            ),
        ]

        sub_list = PolicyTagBeanList("bk_cmdb", policies).sub(PolicyTagBeanList("bk_cmdb", policies2))

        want = [
            PolicyTagBean(
                id="view_host",
                related_resource_types=[
                    RelatedResourceTagBean(
                        system_id="bk_cmdb",
                        type="host",
                        condition=[
                            ConditionTagBean(
                                instances=[
                                    InstanceTagBean(
                                        type="host",
                                        path=[
                                            [
                                                PathNodeTagBean(
                                                    id="host1",
                                                    name="主机1",
                                                    system_id="bk_cmdb",
                                                    type="host",
                                                    type_name="",
                                                    type_name_en="",
                                                    tag="",
                                                )
                                            ]
                                        ],
                                        name="",
                                        name_en="",
                                        tag="",
                                    )
                                ],
                                attributes=[
                                    AttributeTagBean(
                                        id="os",
                                        name="os",
                                        values=[ValueTagBean(id="linux", name="linux", tag="")],
                                        tag="",
                                    )
                                ],
                                id="6280159a089847b99648faf3b5ff9e35",
                                tag="",
                            )
                        ],
                        name="",
                        name_en="",
                        selection_mode="",
                    )
                ],
                policy_id=0,
                expired_at=0,
                type="",
                name="",
                name_en="",
                description="",
                description_en="",
                expired_display="",
                tag="",
            )
        ]

        self.assertEquals(sub_list.policies, want)

    def test_add(self):
        policies = [
            PolicyTagBean(
                **{
                    "id": "view_host",
                    "related_resource_types": [
                        {
                            "system_id": "bk_cmdb",
                            "type": "host",
                            "condition": [
                                {
                                    "instances": [
                                        {
                                            "type": "host",
                                            "path": [
                                                [
                                                    {
                                                        "id": "host1",
                                                        "name": "主机1",
                                                        "system_id": "bk_cmdb",
                                                        "type": "host",
                                                    }
                                                ],
                                                [
                                                    {
                                                        "id": "host2",
                                                        "name": "主机2",
                                                        "system_id": "bk_cmdb",
                                                        "type": "host",
                                                    }
                                                ],
                                            ],
                                        }
                                    ],
                                    "attributes": [
                                        {"id": "os", "name": "os", "values": [{"id": "linux", "name": "linux"}]}
                                    ],
                                    "id": "6280159a089847b99648faf3b5ff9e35",
                                }
                            ],
                        }
                    ],
                }
            )
        ]

        policies2 = [
            PolicyTagBean(
                **{
                    "id": "view_host",
                    "related_resource_types": [
                        {
                            "system_id": "bk_cmdb",
                            "type": "host",
                            "condition": [
                                {
                                    "instances": [
                                        {
                                            "type": "host",
                                            "path": [
                                                [
                                                    {
                                                        "id": "host2",
                                                        "name": "主机2",
                                                        "system_id": "bk_cmdb",
                                                        "type": "host",
                                                    }
                                                ],
                                                [
                                                    {
                                                        "id": "host3",
                                                        "name": "主机3",
                                                        "system_id": "bk_cmdb",
                                                        "type": "host",
                                                    }
                                                ],
                                            ],
                                        }
                                    ],
                                    "attributes": [
                                        {"id": "os", "name": "os", "values": [{"id": "linux", "name": "linux"}]}
                                    ],
                                    "id": "6280159a089847b99648faf3b5ff9e35",
                                }
                            ],
                        }
                    ],
                }
            ),
            PolicyTagBean(
                **{
                    "id": "edit_host",
                    "related_resource_types": [
                        {
                            "system_id": "bk_cmdb",
                            "type": "host",
                            "condition": [
                                {
                                    "instances": [
                                        {
                                            "type": "host",
                                            "path": [
                                                [
                                                    {
                                                        "id": "host1",
                                                        "name": "主机1",
                                                        "system_id": "bk_cmdb",
                                                        "type": "host",
                                                    }
                                                ]
                                            ],
                                        }
                                    ],
                                    "attributes": [
                                        {"id": "os", "name": "os", "values": [{"id": "linux", "name": "linux"}]}
                                    ],
                                    "id": "6280159a089847b99648faf3b5ff9e35",
                                }
                            ],
                        }
                    ],
                }
            ),
        ]

        add_list = PolicyTagBeanList("bk_cmdb", policies).add(PolicyTagBeanList("bk_cmdb", policies2))
        want = [
            PolicyTagBean(
                id="view_host",
                related_resource_types=[
                    RelatedResourceTagBean(
                        system_id="bk_cmdb",
                        type="host",
                        condition=[
                            ConditionTagBean(
                                instances=[
                                    InstanceTagBean(
                                        type="host",
                                        path=[
                                            [
                                                PathNodeTagBean(
                                                    id="host1",
                                                    name="主机1",
                                                    system_id="bk_cmdb",
                                                    type="host",
                                                    type_name="",
                                                    type_name_en="",
                                                    tag="",
                                                )
                                            ],
                                            [
                                                PathNodeTagBean(
                                                    id="host2",
                                                    name="主机2",
                                                    system_id="bk_cmdb",
                                                    type="host",
                                                    type_name="",
                                                    type_name_en="",
                                                    tag="",
                                                )
                                            ],
                                            [
                                                PathNodeTagBean(
                                                    id="host3",
                                                    name="主机3",
                                                    system_id="bk_cmdb",
                                                    type="host",
                                                    type_name="",
                                                    type_name_en="",
                                                    tag="",
                                                )
                                            ],
                                        ],
                                        name="",
                                        name_en="",
                                        tag="",
                                    )
                                ],
                                attributes=[
                                    AttributeTagBean(
                                        id="os",
                                        name="os",
                                        values=[ValueTagBean(id="linux", name="linux", tag="")],
                                        tag="",
                                    )
                                ],
                                id="6280159a089847b99648faf3b5ff9e35",
                                tag="",
                            )
                        ],
                        name="",
                        name_en="",
                        selection_mode="",
                    )
                ],
                policy_id=0,
                expired_at=0,
                type="",
                name="",
                name_en="",
                description="",
                description_en="",
                expired_display="",
                tag="",
            ),
            PolicyTagBean(
                id="edit_host",
                related_resource_types=[
                    RelatedResourceTagBean(
                        system_id="bk_cmdb",
                        type="host",
                        condition=[
                            ConditionTagBean(
                                instances=[
                                    InstanceTagBean(
                                        type="host",
                                        path=[
                                            [
                                                PathNodeTagBean(
                                                    id="host1",
                                                    name="主机1",
                                                    system_id="bk_cmdb",
                                                    type="host",
                                                    type_name="",
                                                    type_name_en="",
                                                    tag="",
                                                )
                                            ]
                                        ],
                                        name="",
                                        name_en="",
                                        tag="",
                                    )
                                ],
                                attributes=[
                                    AttributeTagBean(
                                        id="os",
                                        name="os",
                                        values=[ValueTagBean(id="linux", name="linux", tag="")],
                                        tag="",
                                    )
                                ],
                                id="6280159a089847b99648faf3b5ff9e35",
                                tag="",
                            )
                        ],
                        name="",
                        name_en="",
                        selection_mode="",
                    )
                ],
                policy_id=0,
                expired_at=0,
                type="",
                name="",
                name_en="",
                description="",
                description_en="",
                expired_display="",
                tag="",
            ),
        ]

        self.assertEquals(add_list.policies, want)

    def test_set_tag(self):
        policy = PolicyTagBean(
            **{
                "id": "view_host",
                "related_resource_types": [
                    {
                        "system_id": "bk_cmdb",
                        "type": "host",
                        "condition": [
                            {
                                "instances": [
                                    {
                                        "type": "host",
                                        "path": [
                                            [{"id": "host1", "name": "主机1", "system_id": "bk_cmdb", "type": "host"}]
                                        ],
                                    }
                                ],
                                "attributes": [
                                    {"id": "os", "name": "os", "values": [{"id": "linux", "name": "linux"}]}
                                ],
                                "id": "6280159a089847b99648faf3b5ff9e35",
                            }
                        ],
                    }
                ],
            }
        )

        policy_list = PolicyTagBeanList("bk_cmdb", [policy])
        policy_list.set_tag(PolicyTag.ADD.value)
        want = [
            PolicyTagBean(
                id="view_host",
                related_resource_types=[
                    RelatedResourceTagBean(
                        system_id="bk_cmdb",
                        type="host",
                        condition=[
                            ConditionTagBean(
                                instances=[
                                    InstanceTagBean(
                                        type="host",
                                        path=[
                                            [
                                                PathNodeTagBean(
                                                    id="host1",
                                                    name="主机1",
                                                    system_id="bk_cmdb",
                                                    type="host",
                                                    type_name="",
                                                    type_name_en="",
                                                    tag="add",
                                                )
                                            ]
                                        ],
                                        name="",
                                        name_en="",
                                        tag="add",
                                    )
                                ],
                                attributes=[
                                    AttributeTagBean(
                                        id="os",
                                        name="os",
                                        values=[ValueTagBean(id="linux", name="linux", tag="add")],
                                        tag="add",
                                    )
                                ],
                                id="6280159a089847b99648faf3b5ff9e35",
                                tag="add",
                            )
                        ],
                        name="",
                        name_en="",
                        selection_mode="",
                    )
                ],
                policy_id=0,
                expired_at=0,
                type="",
                name="",
                name_en="",
                description="",
                description_en="",
                expired_display="",
                tag="add",
            )
        ]

        self.assertEquals(policy_list.policies, want)
