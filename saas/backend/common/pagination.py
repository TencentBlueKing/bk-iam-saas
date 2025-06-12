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

# 目标是统一使用page_size/page参数
# WebAPI: 使用config/default.py里DEFAULT_PAGINATION_CLASS默认配置的CompatiblePagination，
# 后续需要前端配合一起调整为page_size/page参数
# OpenAPI:
# 对于已开放接口 admin.list_groups/admin.list_group_member/mgmt.list_group/mgmt.list_group_member
# 使用CompatiblePagination兼容limit/offset和page_size/page
# 对于 OpenAPI 新接口，需要 ViewSet 需要显示配置 pagination_class=CustomPageNumberPagination
from collections import OrderedDict

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from backend.common.error_codes import error_codes


class CustomPageNumberPagination(PageNumberPagination):
    """该分页器继承 PageNumberPagination 后只对用于 Open API 返回的数据里去除 previous 和 next 参数"""

    page_size_query_param = "page_size"

    def _positive_int(self, integer_string, strict=False, cutoff=None):
        """
        Cast a string to a strictly positive integer.
        copied from https://github.com/encode/django-rest-framework/blob/master/rest_framework/pagination.py#L22
        """
        try:
            ret = int(integer_string)
        except ValueError:
            raise error_codes.VALIDATE_ERROR.format("wrong page {}".format(integer_string))

        if ret < 0 or (ret == 0 and strict):
            raise error_codes.VALIDATE_ERROR.format("wrong page {}".format(ret))
        if cutoff:
            return min(ret, cutoff)
        return ret

    def get_page_number(self, request, paginator=None):
        """重载：去除支持 page_number='last'等用于模板渲染的表达，仅仅支持数字"""
        page_number = request.query_params.get(self.page_query_param, 1)
        return self._positive_int(page_number, strict=True)

    def get_limit_offset_pair(self, request):
        """
        将 page_size/page 转换为 limit/offset，
        虽然对外 OpenAPI 是 page_size/page，但内部处理时直接获取分页时需要用到 limit/offset
        """
        limit = self.get_page_size(request)
        offset = (self.get_page_number(request) - 1) * limit
        return limit, offset

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


class CompatiblePagination(CustomPageNumberPagination):
    """默认 page_size/page 分页参数，兼容 limit/offset"""

    limit_query_param = "limit"
    offset_query_param = "offset"

    def get_page_size(self, request):
        page_size_query_param = self.page_size_query_param
        # 优先使用 page_size 参数，如果不存在而 limit 参数存在，则使用 limit 代替 page_size
        if self.page_size_query_param not in request.query_params and self.limit_query_param in request.query_params:
            page_size_query_param = self.limit_query_param

        try:
            return self._positive_int(
                request.query_params[page_size_query_param], strict=True, cutoff=self.max_page_size
            )
        except (KeyError, ValueError):
            pass

        return self.page_size

    def get_page_number(self, request, paginator=None):
        """
        重载：去除支持 page_number='last'等用于模板渲染的表达，仅仅支持数字
        支持从 offset 计算出 page_number
        @parma paginator，默认 None，其他值也无效
        """
        page_number = request.query_params.get(self.page_query_param, 1)
        # 优先使用 page 参数，如果不存在而 offset 参数存在，则使用 offset 推算出 page
        if self.page_query_param not in request.query_params and self.offset_query_param in request.query_params:
            page_size = self.get_page_size(request)
            offset = self._get_offset(request)
            # Note: 这里默认 offset 可整除 page_size，对于无法整除，说明之前 offset/limit 没有被正确用于分页
            page_number = (offset // page_size) + 1

        return self._positive_int(page_number, strict=True)

    def _get_offset(self, request):
        try:
            return self._positive_int(
                request.query_params[self.offset_query_param],
            )
        except (KeyError, ValueError):
            return 0
