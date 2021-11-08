from django.test import TestCase

from backend.biz.policy_tag import ConditionTagBean, ConditionTagBiz


class DiffConditionsTests(TestCase):
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
                                [{"tag": "add", "type": "test1", "type_name": "test1", "id": "id1", "name": "id1"}],
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
                                ],
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
                                [{"tag": "delete", "type": "test1", "type_name": "test1", "id": "id1", "name": "id1"}],
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
