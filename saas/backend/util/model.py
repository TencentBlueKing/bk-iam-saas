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
from typing import Any, List

from pydantic import BaseModel
from pydantic.main import ModelMetaclass


class ExcludeModelMetaclass(ModelMetaclass):
    def __new__(mcs, name, bases, namespace, **kwargs):  # noqa
        exclude = namespace.pop("__exclude__", [])
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)
        for field_name in exclude:
            cls.__fields__.pop(field_name)
        return cls


class ExcludeModel(BaseModel, metaclass=ExcludeModelMetaclass):
    """
    带 __exclude__ 参数的Pydantic BaseModel基类

    继承了该类的子类会在继承已有的Pydantic field的同时移除 __exclude__ 配置的不需要的 field
    """

    pass


class ListModel(BaseModel):
    """
    用于包装typing List, 不需要额外的结构来支持ModelList
    """

    __root__: List[Any]

    def __init__(__pydantic_self__, **data: Any) -> None:
        """
        兼容parse_obj的逻辑

        pydantic 中使用parse_obj函数时自定义__root__的类会自动增加 __root__ = Object 的构建参数
        为了兼容ListModel之间的转换，这里在init时结构 __root__ 参数指向 Object 的 __root__
        """
        if "__root__" in data and isinstance(data["__root__"], ListModel):
            data["__root__"] = data["__root__"].__root__
        super().__init__(**data)

    def __iter__(self):
        return iter(self.__root__)

    def __getitem__(self, index):
        return self.__root__[index]

    def __len__(self) -> int:
        return len(self.__root__)

    def __delitem__(self, index: int):
        self.__root__.pop(index)

    def __setitem__(self, index: int, val: Any):
        self.__root__[index] = val

    def __add__(self, other: "ListModel"):
        return ListModel.parse_obj(self.__root__ + other.__root__)

    def __contains__(self, item: Any):
        return item in self.__root__

    def dict(self, *args, **kwargs):
        return super().dict(*args, **kwargs)["__root__"]

    def pop(self, index: int):
        return self.__root__.pop(index)

    def append(self, item):
        self.__root__.append(item)

    def extend(self, other: "ListModel"):
        self.__root__.extend(other.__root__)
