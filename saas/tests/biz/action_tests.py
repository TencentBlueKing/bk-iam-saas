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

import mock
from django.conf import settings
from django.test import TestCase

from backend.biz.action import ActionBean
from backend.biz.action_group import ActionGroupBean, ActionGroupBiz


class ActionGroupTests(TestCase):
    def test_empty(self):
        from backend.component import iam

        iam.get_action_groups = mock.Mock(return_value=[])

        svc = ActionGroupBiz(settings.BK_APP_TENANT_ID)

        action = ActionBean(
            description="",
            description_en="",
            id="view_host",
            name="编辑主机",
            name_en="edit_host",
            related_actions=[],
            related_resource_types=[],
            type="delete",
            version=0,
        )

        ag = svc.list_by_actions("bk_cmdb", [action])
        self.assertEqual(
            ag,
            [
                ActionGroupBean(
                    name="未分类",
                    name_en="uncategorized",
                    actions=[
                        ActionBean(
                            id="view_host",
                            name="编辑主机",
                            name_en="edit_host",
                            description="",
                            description_en="",
                            type="delete",
                            related_resource_types=[],
                            related_actions=[],
                            expired_at=None,
                            tag="unchecked",
                        )
                    ],
                    sub_groups=[],
                )
            ],
        )

    def test_ag(self):
        self.maxDiff = None
        from backend.component import iam

        iam.get_action_groups = mock.Mock(
            return_value=[
                {
                    "name": "1",
                    "name_en": "1",
                    "actions": [{"id": "a"}],
                    "sub_groups": [
                        {
                            "name": "2",
                            "name_en": "2",
                            "actions": [{"id": "b"}],
                            "sub_groups": [{"name": "3", "name_en": "3", "actions": [{"id": "c"}]}],
                        }
                    ],
                },
                {"name": "2", "name_en": "2", "actions": [{"id": "e"}], "sub_groups": []},
            ]
        )

        actions = [
            ActionBean(
                description="",
                description_en="",
                id="a",
                name="a",
                name_en="a",
                related_actions=[],
                related_resource_types=[],
                type="delete",
                version=0,
            ),
            ActionBean(
                description="",
                description_en="",
                id="b",
                name="b",
                name_en="b",
                related_actions=[],
                related_resource_types=[],
                type="delete",
                version=0,
            ),
            ActionBean(
                description="",
                description_en="",
                id="c",
                name="c",
                name_en="c",
                related_actions=[],
                related_resource_types=[],
                type="delete",
                version=0,
            ),
            ActionBean(
                description="",
                description_en="",
                id="d",
                name="d",
                name_en="d",
                related_actions=[],
                related_resource_types=[],
                type="delete",
                version=0,
            ),
        ]

        svc = ActionGroupBiz(settings.BK_APP_TENANT_ID)

        ag = svc.list_by_actions("bk_cmdb", actions)

        self.assertEqual(
            ag,
            [
                ActionGroupBean(
                    name="1",
                    name_en="1",
                    actions=[
                        ActionBean(
                            id="a",
                            name="a",
                            name_en="a",
                            description="",
                            description_en="",
                            type="delete",
                            related_resource_types=[],
                            related_actions=[],
                            expired_at=None,
                            tag="unchecked",
                        )
                    ],
                    sub_groups=[
                        ActionGroupBean(
                            name="2",
                            name_en="2",
                            actions=[
                                ActionBean(
                                    id="b",
                                    name="b",
                                    name_en="b",
                                    description="",
                                    description_en="",
                                    type="delete",
                                    related_resource_types=[],
                                    related_actions=[],
                                    expired_at=None,
                                    tag="unchecked",
                                )
                            ],
                            sub_groups=[
                                ActionGroupBean(
                                    name="3",
                                    name_en="3",
                                    actions=[
                                        ActionBean(
                                            id="c",
                                            name="c",
                                            name_en="c",
                                            description="",
                                            description_en="",
                                            type="delete",
                                            related_resource_types=[],
                                            related_actions=[],
                                            expired_at=None,
                                            tag="unchecked",
                                        )
                                    ],
                                    sub_groups=[],
                                )
                            ],
                        )
                    ],
                ),
                ActionGroupBean(
                    name="未分类",
                    name_en="uncategorized",
                    actions=[
                        ActionBean(
                            id="d",
                            name="d",
                            name_en="d",
                            description="",
                            description_en="",
                            type="delete",
                            related_resource_types=[],
                            related_actions=[],
                            expired_at=None,
                            tag="unchecked",
                        )
                    ],
                    sub_groups=[],
                ),
            ],
        )
