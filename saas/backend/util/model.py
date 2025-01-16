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
from typing import Any, Dict, List, Tuple, TypeVar, Generic

from pydantic import BaseModel, PrivateAttr, RootModel
from pydantic._internal._model_construction import ModelMetaclass

T = TypeVar("T")


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


class ListModel(RootModel[List[T]], Generic[T]):  # 这里显式继承 Generic[T]
    """
    用于包装 List，不需要额外的结构来支持 ModelList
    """

    def __init__(self, root: List[T] = None) -> None:
        """
        兼容 Pydantic 1 旧逻辑：
        - Pydantic 2 中不再支持 `__root__`，需要使用 `RootModel`
        - 兼容 `ListModel` 之间的转换
        """
        if isinstance(root, ListModel):
            root = root.root
        super().__init__(root=root or [])

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, index):
        return self.root[index]

    def __len__(self) -> int:
        return len(self.root)

    def __delitem__(self, index: int):
        self.root.pop(index)

    def __setitem__(self, index: int, val: Any):
        self.root[index] = val

    def __add__(self, other: "ListModel[T]"):
        return ListModel(self.root + other.root)

    def __contains__(self, item: Any):
        return item in self.root

    def model_dump(self, *args, **kwargs):  # Pydantic 2: dict() → model_dump()
        return super().model_dump(*args, **kwargs)["root"]

    def pop(self, index: int):
        return self.root.pop(index)

    def append(self, item):
        self.root.append(item)

    def extend(self, other: "ListModel[T]"):
        self.root.extend(other.root)


class PartialModel(BaseModel):
    # 某些情况下，只需要用到数据类的部分字段，_partial_fields用于记录数据类对象的哪些字段是可用，配合from_partial_data一起使用
    _partial_fields: List[str] = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        # __fields__ 只包含public字段，不包含private字段，即不会包含_partial_fields字段
        self._partial_fields = data["_partial_fields"] if "_partial_fields" in data else list(self.__fields__.keys())

    def get_partial_fields(self):
        return self._partial_fields

    @classmethod
    def from_partial_data(cls, partial_data: Dict):
        """
        由于做ORM Update时，partial_data只包含了需要更新字段，所以需要使用该函数将不更新的字段填充空值
        否则因为该数据类存在没有默认值的字段会导致转换失败
        同时会设置私有字段_partial_fields来明确出partial_data里的字段
        """
        config = cls.__config__

        # 遍历所有字段，将不存在的且必填字段设置为空值
        data = {}
        for name, field in cls.__fields__.items():
            # 查找每个字段是否存在partial_data里，pydantic是支持别名的，而且优先使用别名
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

        # 将partial_data添加data里
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
            # 类似List[...]均可
            if issubclass(_type, List):
                return []
            # 类似Tuple[...]均可
            if issubclass(_type, Tuple):
                return ()
            # 类似 Dict[...] 或 dict均可
            if issubclass(_type, Dict):
                return {}
        except:  # noqa
            pass

        raise TypeError(f"can't get empty value for {_type}")
