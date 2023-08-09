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
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from backend.biz.resource import ResourceBiz

from .serializers import BaseInfoSLZ, ResourceAttributeQuerySLZ, ResourceAttributeValueQuerySLZ, ResourceQuerySLZ


class ResourceViewSet(ViewSet):

    biz = ResourceBiz()

    @swagger_auto_schema(
        operation_description="资源实例列表",
        request_body=ResourceQuerySLZ(label="资源查询参数"),
        responses={status.HTTP_200_OK: BaseInfoSLZ(many=True)},
        force_page_response=True,
        tags=["resource"],
    )
    def list(self, request, *args, **kwargs):
        slz = ResourceQuerySLZ(data=request.data)
        slz.is_valid(raise_exception=True)

        system_id = slz.validated_data["system_id"]
        resource_type_id = slz.validated_data["type"]
        ancestors = slz.validated_data["ancestors"]
        keyword = slz.validated_data.get("keyword") or ""
        action_system_id = slz.validated_data.get("action_system_id") or ""
        action_id = slz.validated_data.get("action_id") or ""
        # 分页
        limit = slz.validated_data["limit"]
        offset = slz.validated_data["offset"]

        # TODO：通过这个接口这样就把所有接入系统的资源拉取到？那么相当于用户访问iam saas就可以访问到接入系统所有资源，是否合理？如何鉴权？
        # 是否有keyword，如果有，则是搜索
        if keyword:
            count, results = self.biz.search_instance_for_topology(
                system_id,
                resource_type_id,
                keyword,
                ancestors,
                limit,
                offset,
                action_system_id,
                action_id,
            )
        else:
            count, results = self.biz.list_instance_for_topology(
                system_id, resource_type_id, ancestors, limit, offset, action_system_id, action_id
            )

        return Response({"count": count, "results": [i.dict() for i in results]})

    @swagger_auto_schema(
        operation_description="资源属性列表",
        query_serializer=ResourceAttributeQuerySLZ(),
        responses={status.HTTP_200_OK: BaseInfoSLZ(many=True)},
        force_page_response=True,
        tags=["resource"],
    )
    def list_resource_attribute(self, request, *args, **kwargs):
        slz = ResourceAttributeQuerySLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)

        system_id = slz.validated_data["system_id"]
        resource_type_id = slz.validated_data["type"]
        # 分页
        limit = slz.validated_data["limit"]
        offset = slz.validated_data["offset"]

        attrs = self.biz.list_attr(system_id, resource_type_id)

        count, results = len(attrs), attrs[offset : offset + limit]

        return Response({"count": count, "results": [i.dict() for i in results]})

    @swagger_auto_schema(
        operation_description="资源属性Value列表",
        query_serializer=ResourceAttributeValueQuerySLZ(),
        responses={status.HTTP_200_OK: BaseInfoSLZ(many=True)},
        force_page_response=True,
        tags=["resource"],
    )
    def list_resource_attribute_value(self, request, *args, **kwargs):
        slz = ResourceAttributeValueQuerySLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)

        system_id = slz.validated_data["system_id"]
        resource_type_id = slz.validated_data["type"]
        attr = slz.validated_data["attribute"]
        keyword = slz.validated_data.get("keyword", "")
        # 分页
        limit = slz.validated_data["limit"]
        offset = slz.validated_data["offset"]

        count, results = self.biz.list_attr_value(system_id, resource_type_id, attr, keyword, limit, offset)

        return Response({"count": count, "results": [i.dict() for i in results]})
