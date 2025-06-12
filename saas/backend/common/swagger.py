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

from drf_yasg import openapi
from drf_yasg.inspectors import SwaggerAutoSchema


class ResponseSwaggerAutoSchema(SwaggerAutoSchema):
    def get_response_schemas(self, response_serializers):
        responses = super().get_response_schemas(response_serializers)
        new_responses = OrderedDict()
        for sc, response in responses.items():
            data = response.get("schema") or openapi.Schema(type=openapi.TYPE_OBJECT)
            if self.should_page() or self.overrides.get("force_page_response", False):
                data = openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties=OrderedDict(
                        (
                            ("count", openapi.Schema(type=openapi.TYPE_INTEGER)),
                            ("results", response.get("schema")),
                        )
                    ),
                    required=["count", "results"],
                )
            new_responses[sc] = openapi.Response(
                description=response.get("description", ""),
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties=OrderedDict(
                        (
                            ("code", openapi.Schema(type=openapi.TYPE_INTEGER)),
                            ("result", openapi.Schema(type=openapi.TYPE_BOOLEAN)),
                            ("message", openapi.Schema(type=openapi.TYPE_STRING)),
                            ("data", data),
                        )
                    ),
                ),
            )
        return new_responses
