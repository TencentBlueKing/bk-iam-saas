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
from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from backend.biz.action import ActionBiz
from backend.biz.action_group import ActionGroupBiz
from backend.biz.open import ApplicationPolicyListCache
from backend.service.models import Subject

from ..serializers import ActionSLZ, GroupActionQuerySLZ


class ActionViewSet(GenericViewSet):
    pagination_class = None  # 去掉swagger中的limit offset参数

    biz = ActionBiz()
    action_group_biz = ActionGroupBiz()

    application_policy_list_cache = ApplicationPolicyListCache()

    @swagger_auto_schema(
        operation_description="用户的操作列表",
        query_serializer=GroupActionQuerySLZ(),
        responses={status.HTTP_200_OK: ActionSLZ(label="操作", many=True)},
        tags=["action"],
    )
    def list(self, request, *args, **kwargs):
        slz = GroupActionQuerySLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)

        system_id = slz.validated_data["system_id"]
        cache_id = slz.validated_data["cache_id"]
        group_id = slz.validated_data["group_id"]
        user_id = slz.validated_data["user_id"]
        all = slz.validated_data["all"]
        hidden = slz.validated_data["hidden"]

        # 1. 获取用户的权限列表
        if user_id != "" and user_id == request.user.username:
            actions = self.biz.list_by_subject(system_id, request.role, Subject.from_username(user_id), hidden=hidden)
        elif user_id != "" and user_id != request.user.username:
            raise exceptions.PermissionDenied
        elif group_id != -1:
            actions = self.biz.list_by_subject(system_id, request.role, Subject.from_group_id(group_id), hidden=hidden)
        # 3. 获取的预申请的权限列表
        elif cache_id != "":
            # 从缓存里获取预申请的操作ID列表
            policy_list = self.application_policy_list_cache.get(cache_id)
            # 根据预申请的操作ID列表，获取对应的操作列表
            actions = self.biz.list_pre_application_actions(
                system_id, request.role, request.user.username, [p.action_id for p in policy_list.policies]
            )
        # 4. 查询所有的操作
        elif all:
            actions = self.biz.list(system_id).actions
        else:
            actions = self.biz.list_by_role(system_id, request.role, hidden=hidden)

        # 对操作分组, 填入到分组的数据中
        action_groups = self.action_group_biz.list_by_actions(system_id, actions)

        return Response([one.dict() for one in action_groups])
