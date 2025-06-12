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

from aenum import LowerStrEnum, auto, skip
from django.test import TestCase

from backend.util.enum import ChoicesEnum


class TestChoicesEnum(TestCase):
    def test_define_choice_label(self):
        """正常定义_choice_label"""

        class TestEnum(ChoicesEnum):
            T1 = "t1"
            T2 = "t2"
            T3 = "t3"

            _choices_labels = skip(((T1, "test1"), (T2, "test2"), (T3, "test3")))

        expected_choices = (("t1", "test1"), ("t2", "test2"), ("t3", "test3"))
        self.assertEqual(TestEnum.T2.value, "t2")
        self.assertEqual(TestEnum.get_choices(), expected_choices)
        self.assertEqual(TestEnum.get_choice_label(TestEnum.T2.value), "test2")
        self.assertEqual(TestEnum.get_choice_label(TestEnum.T2), "test2")
        self.assertEqual(TestEnum.T2.label, "test2")

    def test_not_define_choice_label(self):
        """无定义_choice_label"""

        class TestEnum(ChoicesEnum):
            T1 = "t1"
            T2 = "t2"
            T3 = "t3"

        expected_choices = (("t1", "t1"), ("t2", "t2"), ("t3", "t3"))
        self.assertEqual(TestEnum.T2.value, "t2")
        self.assertEqual(TestEnum.get_choices(), expected_choices)
        self.assertEqual(TestEnum.get_choice_label(TestEnum.T2.value), "t2")
        self.assertEqual(TestEnum.get_choice_label(TestEnum.T2), "t2")
        self.assertEqual(TestEnum.T2.label, "t2")

    def test_auto(self):
        """使用auto"""

        class TestEnum(ChoicesEnum, LowerStrEnum):
            TL1 = auto()
            TL2 = auto()
            TL3 = auto()

            _choices_labels = skip(((TL1, "test1"), (TL2, "test2"), (TL3, "test3")))

        expected_choices = (("tl1", "test1"), ("tl2", "test2"), ("tl3", "test3"))
        self.assertEqual(TestEnum.TL2.value, "tl2")
        self.assertEqual(TestEnum.get_choices(), expected_choices)
        self.assertEqual(TestEnum.get_choice_label(TestEnum.TL2.value), "test2")
        self.assertEqual(TestEnum.get_choice_label(TestEnum.TL2), "test2")
        self.assertEqual(TestEnum.TL2.label, "test2")

    def test_auto_mixing_str(self):
        """使用混合auto和字符串"""

        class TestEnum(ChoicesEnum, LowerStrEnum):
            TL1 = auto()
            TL2 = "test_lower2"
            TL3 = auto()

            _choices_labels = skip(((TL1, "test1"), (TL2, "test2"), (TL3, "test3")))

        expected_choices = (("tl1", "test1"), ("test_lower2", "test2"), ("tl3", "test3"))
        self.assertEqual(TestEnum.TL2.value, "test_lower2")
        self.assertEqual(TestEnum.get_choices(), expected_choices)
        self.assertEqual(TestEnum.get_choice_label(TestEnum.TL2.value), "test2")
        self.assertEqual(TestEnum.get_choice_label(TestEnum.TL2), "test2")
        self.assertEqual(TestEnum.TL2.label, "test2")
