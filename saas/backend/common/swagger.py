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
from rest_framework import serializers as drf_serializers


class CustomFieldsSerializer(drf_serializers.Serializer):
    """
    支持添加`自定义字段`的serializer
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'add_fields' arg up to the superclass
        add_fields = kwargs.pop("add_fields", None)

        # Instantiate the superclass normally
        super().__init__(*args, **kwargs)

        if add_fields is not None:
            # Add 'add_fields' to fields
            self.fields.update(add_fields)


class ResponseSerializer(CustomFieldsSerializer):
    code = drf_serializers.IntegerField()
    result = drf_serializers.BooleanField()
    message = drf_serializers.CharField()


class PaginatedDataSerializer(CustomFieldsSerializer):
    count = drf_serializers.IntegerField()
    has_next = drf_serializers.BooleanField()
    has_previous = drf_serializers.BooleanField()


def get_response_serializer(data_field=None):
    """
    用于 drf-yasg swagger_auto_schema 获取标准的 response serializer
    """
    add_fields = {"data": data_field} if data_field else {}
    return ResponseSerializer(add_fields=add_fields)


def get_paginated_response_serializer(results_field=None):

    """
    用于 drf-yasg swagger_auto_schema 获取标准翻页的 response serializer
    """
    add_fields = {"results": results_field} if results_field else {}
    paginated_data_slz = PaginatedDataSerializer(add_fields=add_fields)
    return ResponseSerializer(add_fields={"data": paginated_data_slz})


class ResponseSwaggerAutoSchema(SwaggerAutoSchema):
    def get_response_schemas(self, response_serializers):
        responses = super().get_response_schemas(response_serializers)
        new_responses = OrderedDict()
        for sc, response in responses.items():
            new_responses[sc] = openapi.Response(
                description=response.get("description", ""),
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties=OrderedDict(
                        (
                            ("code", openapi.Schema(type=openapi.TYPE_INTEGER)),
                            ("result", openapi.Schema(type=openapi.TYPE_BOOLEAN)),
                            ("message", openapi.Schema(type=openapi.TYPE_STRING)),
                            ("data", response.get("schema")),
                        )
                    ),
                ),
            )
        return new_responses


class PaginatedResponseSwaggerAutoSchema(SwaggerAutoSchema):
    def get_response_schemas(self, response_serializers):
        responses = super().get_response_schemas(response_serializers)
        new_responses = OrderedDict()
        for sc, response in responses.items():
            new_responses[sc] = openapi.Response(
                description="",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties=OrderedDict(
                        (
                            ("code", openapi.Schema(type=openapi.TYPE_INTEGER)),
                            ("result", openapi.Schema(type=openapi.TYPE_BOOLEAN)),
                            ("message", openapi.Schema(type=openapi.TYPE_STRING)),
                            (
                                "data",
                                openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties=OrderedDict(
                                        (
                                            ("count", openapi.Schema(type=openapi.TYPE_INTEGER)),
                                            ("results", response["schema"]),
                                        )
                                    ),
                                ),
                            ),
                        )
                    ),
                ),
            )
        return new_responses
