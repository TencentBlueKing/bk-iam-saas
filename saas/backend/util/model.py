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

from typing import Any, Dict, List, Tuple

from pydantic import BaseModel, PrivateAttr
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
    带 __exclude__ 参数的 Pydantic BaseModel 基类

    继承了该类的子类会在继承已有的 Pydantic field 的同时移除 __exclude__ 配置的不需要的 field
    """


class ListModel(BaseModel):
    """
    用于包装 typing List, 不需要额外的结构来支持 ModelList
    """

    __root__: List[Any]

    def __init__(__pydantic_self__, **data: Any) -> None:  # noqa: N805
        """
        兼容 parse_obj 的逻辑

        pydantic 中使用 parse_obj 函数时自定义__root__的类会自动增加 __root__ = Object 的构建参数
        为了兼容 ListModel 之间的转换，这里在 init 时结构 __root__ 参数指向 Object 的 __root__
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


class PartialModel(BaseModel):
    # 某些情况下，只需要用到数据类的部分字段，
    # _partial_fields 用于记录数据类对象的哪些字段是可用，配合 from_partial_data 一起使用
    _partial_fields: List[str] = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        # __fields__ 只包含 public 字段，不包含 private 字段，即不会包含_partial_fields 字段
        self._partial_fields = data["_partial_fields"] if "_partial_fields" in data else list(self.__fields__.keys())

    def get_partial_fields(self):
        return self._partial_fields

    @classmethod
    def from_partial_data(cls, partial_data: Dict):
        """
        由于做 ORM Update 时，partial_data 只包含了需要更新字段，所以需要使用该函数将不更新的字段填充空值
        否则因为该数据类存在没有默认值的字段会导致转换失败
        同时会设置私有字段_partial_fields 来明确出 partial_data 里的字段
        """
        config = cls.__config__

        # 遍历所有字段，将不存在的且必填字段设置为空值
        data = {}
        for name, field in cls.__fields__.items():
            # 查找每个字段是否存在 partial_data 里，pydantic 是支持别名的，而且优先使用别名
            alias_found = field.alias in partial_data
            name_found = config.allow_population_by_field_name and field.alt_alias and field.name in partial_data

            # 存在则不需要设置空值
            if alias_found or name_found:
                continue

            # 对于非必填的值则无需设置
            if not field.required:
                continue

            # 设置空值
            data[name] = cls._get_empty_value(field.outer_type_)

        # 将 partial_data 添加 data 里
        data.update(partial_data)
        # 可用字段列表
        data["_partial_fields"] = list(partial_data.keys())

        return cls(**data)

    @staticmethod
    def _get_empty_value(_type):
        """
        根据类型返回类型对应的空值，该函数只能判断基础类型，若需判断其他类型可以重写该函数，比如：

        class SubModel(PartialModel):
            x: Union[List[str], Dict[str, int]]

            @staticmethod
            def _get_empty_value(_type):
                if _type == Union[List[str], Dict[str, int]]:
                    return the empty value
                return super(SubModel, SubModel)._get_empty_value(_type)
        """
        try:
            if issubclass(_type, str):
                return ""
            if issubclass(_type, int):
                return 0
            if issubclass(_type, bool):
                return False
            # 类似 List[...] 均可
            if issubclass(_type, List):
                return []
            # 类似 Tuple[...] 均可
            if issubclass(_type, Tuple):
                return ()
            # 类似 Dict[...] 或 dict 均可
            if issubclass(_type, Dict):
                return {}
        except:  # noqa
            pass

        raise TypeError(f"can't get empty value for {_type}")
