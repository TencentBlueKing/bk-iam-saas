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
from collections import OrderedDict

from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response


class CustomLimitOffsetPagination(LimitOffsetPagination):
    """自定义分页器
    该分页器继承LimitOffsetPagination后只对用于API返回的数据里去除previous和next参数
    """

    def get_paginated_response(self, data):
        return Response(OrderedDict([("count", self.count), ("results", data)]))

    def get_paginated_response_schema(self, schema):
        return {
            "type": "object",
            "properties": {
                "count": {
                    "type": "integer",
                    "example": 123,
                },
                "results": schema,
            },
        }
