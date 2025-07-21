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

import pytest
from blue_krill.web.std_error import APIError
from django.conf import settings
from mock import MagicMock, Mock, patch

from backend.biz.instance_selection import ChainNodeBean, InstanceSelectionBean, InstanceSelectionBiz
from backend.biz.policy import PolicyBeanList
from backend.biz.resource import ResourceBiz, ResourceNodeAttributeDictBean, ResourceNodeBean
from backend.trans.open import OpenCommonTrans, OpenPolicy, OpenRelatedResource, OpenResourcePathNode


class TestOpenCommonTrans:
    def test_to_policies(self):
        trans = OpenCommonTrans(settings.BK_APP_TENANT_ID)
        policies = trans._to_policies(
            [
                OpenPolicy(
                    system_id="system",
                    action_id="action1",
                    related_resource_types=[
                        OpenRelatedResource(
                            system_id="system",
                            type="type",
                            paths=[[OpenResourcePathNode(system_id="system", type="type", id="id", name="name")]],
                        )
                    ],
                )
            ]
        )

        assert len(policies) == 1
        assert policies[0].action_id == "action1"
        assert (
            len(policies[0].resource_groups[0].related_resource_types[0].condition[0].instances[0].path[0].__root__)
            == 1
        )

    def test_to_policy_list(self):
        trans = OpenCommonTrans(settings.BK_APP_TENANT_ID)
        trans.action_check_biz.check = Mock(return_value=None)

        with (
            patch.object(
                PolicyBeanList, "fill_empty_fields", MagicMock(side_effect=lambda: None)
            ) as fake_fill_empty_fields,
            patch.object(
                PolicyBeanList, "check_instance_selection", MagicMock(side_effect=lambda: None)
            ) as fake_check_instance_selection,
        ):
            policy_list = trans._to_policy_list(
                "system",
                [
                    OpenPolicy(
                        system_id="system",
                        action_id="action1",
                        related_resource_types=[
                            OpenRelatedResource(
                                system_id="system",
                                type="type",
                                paths=[[OpenResourcePathNode(system_id="system", type="type", id="id", name="name")]],
                            )
                        ],
                    )
                ],
            )

            fake_fill_empty_fields.assert_called()
            fake_check_instance_selection.assert_called()

        assert policy_list.system_id == "system"
        assert len(policy_list.policies) == 1
        assert policy_list.policies[0].action_id == "action1"
        assert (
            len(
                policy_list.policies[0]
                .resource_groups[0]
                .related_resource_types[0]
                .condition[0]
                .instances[0]
                .path[0]
                .__root__
            )
            == 1
        )


class TestOpenRelatedResource:
    def test_fill_instance_system_ok(self):
        rr = OpenRelatedResource(
            system_id="system", type="type", paths=[[OpenResourcePathNode(type="type", id="id", name="name")]]
        )
        rr.fill_instance_system(
            [
                InstanceSelectionBean(
                    id="id",
                    system_id="system",
                    name="",
                    name_en="",
                    ignore_iam_path=False,
                    resource_type_chain=[ChainNodeBean(system_id="system", id="type")],
                )
            ]
        )

        assert rr.paths[0][0].system_id == "system"

    def test_fill_instance_system_not_match(self):
        rr = OpenRelatedResource(
            system_id="system", type="type", paths=[[OpenResourcePathNode(type="type", id="id", name="name")]]
        )

        with pytest.raises(APIError):
            rr.fill_instance_system(
                [
                    InstanceSelectionBean(
                        id="id",
                        system_id="system",
                        name="",
                        name_en="",
                        ignore_iam_path=False,
                        resource_type_chain=[ChainNodeBean(system_id="system", id="test")],
                    )
                ]
            )

    def test_fill_instance_system_multi_selection(self):
        rr = OpenRelatedResource(
            system_id="system", type="type", paths=[[OpenResourcePathNode(type="type", id="id", name="name")]]
        )

        with pytest.raises(APIError):
            rr.fill_instance_system(
                [
                    InstanceSelectionBean(
                        id="1",
                        system_id="system",
                        name="",
                        name_en="",
                        ignore_iam_path=False,
                        resource_type_chain=[ChainNodeBean(system_id="system", id="type")],
                    ),
                    InstanceSelectionBean(
                        id="2",
                        system_id="system",
                        name="",
                        name_en="",
                        ignore_iam_path=False,
                        resource_type_chain=[ChainNodeBean(system_id="system1", id="type")],
                    ),
                ]
            )

    def test_fill_instance_name(self):
        rr = OpenRelatedResource(
            system_id="system", type="type", paths=[[OpenResourcePathNode(system_id="system", type="type", id="id")]]
        )
        with patch.object(
            ResourceBiz,
            "fetch_resource_name",
            MagicMock(
                side_effect=lambda _, raise_not_found_exception: ResourceNodeAttributeDictBean(
                    data={ResourceNodeBean(system_id="system", type="type", id="id"): "name"}
                )
            ),
        ) as fake_fetch_resource_name:
            rr.fill_instance_name(settings.BK_APP_TENANT_ID)

            fake_fetch_resource_name.assert_called()

        assert rr.paths[0][0].name == "name"


class TestOpenPolicy:
    def test_fill_instance_system(self):
        p = OpenPolicy(
            system_id="system",
            action_id="action1",
            related_resource_types=[
                OpenRelatedResource(
                    system_id="system",
                    type="type",
                    paths=[[OpenResourcePathNode(type="type", id="id", name="name")]],
                )
            ],
        )

        with patch.object(
            InstanceSelectionBiz,
            "list_by_action_resource_type",
            MagicMock(
                side_effect=lambda *args: [
                    InstanceSelectionBean(
                        id="id",
                        system_id="system",
                        name="",
                        name_en="",
                        ignore_iam_path=False,
                        resource_type_chain=[ChainNodeBean(system_id="system", id="type")],
                    )
                ]
            ),
        ) as fake_list_by_action_resource_type:
            p.fill_instance_system(settings.BK_APP_TENANT_ID)

            fake_list_by_action_resource_type.assert_called()

        assert p.related_resource_types[0].paths[0][0].system_id == "system"

    def test_fill_instance_name(self):
        p = OpenPolicy(
            system_id="system",
            action_id="action1",
            related_resource_types=[
                OpenRelatedResource(
                    system_id="system",
                    type="type",
                    paths=[[OpenResourcePathNode(system_id="system", type="type", id="id")]],
                )
            ],
        )

        with patch.object(
            ResourceBiz,
            "fetch_resource_name",
            MagicMock(
                side_effect=lambda _, raise_not_found_exception: ResourceNodeAttributeDictBean(
                    data={ResourceNodeBean(system_id="system", type="type", id="id"): "name"}
                )
            ),
        ) as fake_fetch_resource_name:
            p.fill_instance_name(settings.BK_APP_TENANT_ID)

            fake_fetch_resource_name.assert_called()

        assert p.related_resource_types[0].paths[0][0].name == "name"
