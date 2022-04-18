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
# 目标是统一使用page_size/page参数
# WebAPI: 使用config/default.py里DEFAULT_PAGINATION_CLASS默认配置的CustomLimitOffsetPagination，后续需要前端配合一起调整为page_size/page参数
# OpenAPI:
# 已开放接口admin.list_groups/admin.list_group_member/mgmt.list_group_member使用CompatiblePageNumberPagination兼容limit/offset和page_size/page
# 对于OpenAPI新接口，需要ViewSet需要显示配置pagination_class=CustomPageNumberPagination
from collections import OrderedDict

from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from rest_framework.response import Response


class CustomLimitOffsetPagination(LimitOffsetPagination):
    """该分页器继承LimitOffsetPagination后只对用于Web API返回的数据里去除previous和next参数"""

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


class CustomPageNumberPagination(PageNumberPagination):
    """该分页器继承PageNumberPagination后只对用于Open API返回的数据里去除previous和next参数"""

    page_size_query_param = "page_size"

    def get_paginated_response(self, data):
        return Response(OrderedDict([("count", self.page.paginator.count), ("results", data)]))

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


class CompatiblePageNumberPagination(CustomPageNumberPagination):
    """默认page_size/page分页参数，兼容limit/offset"""

    limit_query_param = "limit"
    offset_query_param = "offset"

    def get_page_size(self, request):
        # 优先使用page_size参数，如果不存在而limit参数存在，则使用limit代替page_size
        if self.page_size_query_param not in request.query_params and self.limit_query_param in request.query_params:
            request.query_params[self.page_size_query_param] = request.query_params[self.limit_query_param]

        return super().get_page_size(request)

    def get_page_number(self, request, paginator):
        # 优先使用page参数，如果不存在而offset参数存在，则使用offset推算出page
        if self.page_query_param not in request.query_params and self.offset_query_param in request.query_params:
            page_size = paginator.per_page
            offset = self._get_offset(request)
            # Note: 这里默认offset可整除page_size，对于无法整除，说明之前offset/limit没有被正确用于分页
            request.query_params[self.page_query_param] = (offset // page_size) + 1

        return super().get_page_number(request, paginator)

    def _get_offset(self, request):
        try:
            offset = int(request.query_params[self.offset_query_param])
        except (KeyError, ValueError):
            offset = 0

        if offset < 0:
            return 0
        return offset
