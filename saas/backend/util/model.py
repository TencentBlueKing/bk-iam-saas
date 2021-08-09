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
from pydantic import BaseModel
from pydantic.main import ModelMetaclass


class ExcludeModelMetaclass(ModelMetaclass):
    def __new__(mcs, name, bases, namespace, **kwargs):  # noqa
        exclude = namespace.pop("__exclude__", [])
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)
        for field_name in exclude:
            cls.__fields__.pop(field_name)
            cls.__field_defaults__.pop(field_name, None)
        return cls


class ExcludeModel(BaseModel, metaclass=ExcludeModelMetaclass):
    """
    带 __exclude__ 参数的Pydantic BaseModel基类

    继承了该类的子类会在继承已有的Pydantic field的同时移除 __exclude__ 配置的不需要的 field
    """

    pass
