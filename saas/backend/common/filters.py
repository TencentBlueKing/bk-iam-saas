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

from django_filters import rest_framework as filters
from django_filters.rest_framework.backends import DjangoFilterBackend


class NoCheckModelFilterBackend(DjangoFilterBackend):
    """
    不校验model与filterset_class是否匹配的filter backend
    """

    def get_filterset_class(self, view, queryset=None):
        """
        Return the `FilterSet` class used to filter the queryset.
        """
        return getattr(view, "filterset_class", None)


class InitialFilterSet(filters.FilterSet):
    """
    给field添加initial初始值
    """

    def __init__(self, data=None, *args, **kwargs):
        # if filterset is bound, use initial values as defaults
        if data is not None:
            # get a mutable copy of the QueryDict
            data = data.copy()

            for name, f in self.base_filters.items():
                initial = f.extra.get("initial", None)

                # filter param is either missing or empty, use initial as default
                if data.get(name, None) is None and initial is not None:
                    data[name] = initial

        super().__init__(data, *args, **kwargs)
