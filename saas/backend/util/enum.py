# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云 - 权限中心 (BlueKing-IAM) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

Note: 继承 ChoicesEnum 的枚举在遍历成员时，将会包括_choices_labels 这个枚举项，需要判断去除
目前 python3.6 不支持 _ignore_，只有>=3.7 才支持，引入包 aenum 来解决这个问题
aenum 包完全兼容 Python 默认的 Enum 的，https://github.com/ethanfurman/aenum
# from aenum import StrEnum 支持 Auto default value is member name
# from aenum import LowerStrEnum 支持 Auto default value is member name, lower-cased
"""

from typing import TYPE_CHECKING

from aenum import auto

# 由于 mypy 无法支持 aenum，所以需要在类型检测时使用原始类代替
# https://github.com/ethanfurman/aenum/issues/10#issuecomment-869209856
# TODO: 待 blue-krill 开源后使用其 StructuredEnum 进行重构，
#  同时需要搜索所有注释了`# type: ignore[attr-defined]`的地方，
#  若是因为枚举值在定义时使用了 ChoicesEnum 而导致必须忽略 mypy 检查的，则删除
if TYPE_CHECKING:
    from enum import Enum
else:
    from aenum import Enum


class ChoicesEnum(Enum):
    """Enum with choices
    Example：
        from aenum import skip
        class TestEnum(ChoicesEnum):
            T1 = "t1"
            T2 = "t2"
            T3 = "t3"

            _choices_labels = skip((
                (T1, "test1"),
                (T2, "test2"),
                (T3, "test3")
            ))
        >> TestEnum.get_choices()
        => (("t1", "test1"), ("t2", "test2"), ("t3", "test3"))
    """

    @classmethod
    def get_choices(cls):
        if not hasattr(cls, "_choices_labels"):
            return tuple((member.value, member.value) for member in cls.__members__.values())

        choices_labels = []
        for member, label in cls._choices_labels:
            # when use `auto`, member type is auto, not value
            value = member.value if isinstance(member, auto) else member
            choices_labels.append((value, label))
        return tuple(choices_labels)

    @classmethod
    def get_choice_label(cls, value=None):
        if isinstance(value, Enum):
            value = value.value
        return dict(cls.get_choices()).get(value, value)

    @property
    def label(self):
        return dict(self.get_choices()).get(self.value, str(self.value))
