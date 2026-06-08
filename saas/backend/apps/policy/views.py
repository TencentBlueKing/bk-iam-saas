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

from itertools import chain, groupby
from typing import List

from django.utils.translation import gettext as _
from drf_yasg.utils import swagger_auto_schema
from pydantic.tools import parse_obj_as
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from backend.apps.subject.audit import SubjectPolicyDeleteAuditProvider
from backend.audit.audit import audit_context_setter, view_audit_decorator
from backend.biz.action import ActionBean, ActionBeanList
from backend.biz.constants import PolicyTag
from backend.biz.policy import (
    ConditionBean,
    PolicyBean,
    PolicyBeanList,
    PolicyEmptyException,
    RelatedResourceBean,
)
from backend.biz.policy_tag import PolicyTagBean, PolicyTagBeanList
from backend.common.error_codes import error_codes
from backend.common.serializers import ActionQuerySLZ
from backend.common.time import get_soon_expire_ts
from backend.mixins import BizMixin, ServiceMixin
from backend.service.models import Subject as SvcSubject

from .serializers import (
    PolicyDeleteSLZ,
    PolicyExpireSoonSLZ,
    PolicyPartDeleteSLZ,
    PolicyResourceCopySLZ,
    PolicySLZ,
    PolicySystemSLZ,
    RecommendActionPolicy,
    RelatedPolicySLZ,
)


class PolicyViewSet(BizMixin, GenericViewSet):
    pagination_class = None  # 去掉 swagger 中的 limit offset 参数

    @swagger_auto_schema(
        operation_description="用户的所有权限列表",
        query_serializer=ActionQuerySLZ(),
        responses={status.HTTP_200_OK: PolicySLZ(label="策略", many=True)},
        tags=["policy"],
    )
    def list(self, request, *args, **kwargs):
        slz = ActionQuerySLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)

        system_id = slz.validated_data["system_id"]
        cache_id = slz.validated_data["cache_id"]

        if cache_id != "":
            cached_policy_list = self.application_policy_list_cache.get(cache_id)
            if cached_policy_list.system_id != system_id:
                raise error_codes.INVALID_ARGS.format(_("请求的 system 与缓存策略数据的 system 不一致"))

            apply_policy_list = PolicyTagBeanList(
                self.tenant_id, system_id, parse_obj_as(List[PolicyTagBean], cached_policy_list.policies)
            )
            apply_policy_list.set_tag(PolicyTag.ADD.value)

            return Response([p.dict() for p in apply_policy_list.policies])

        subject = SvcSubject.from_username(request.user.username)
        policies = self.policy_query_biz.list_by_subject(system_id, subject)

        # ResourceNameAutoUpdate
        updated_policies = self.policy_operation_biz.update_due_to_renamed_resource(system_id, subject, policies)

        return Response([p.dict() for p in updated_policies])

    @swagger_auto_schema(
        operation_description="删除权限",
        query_serializer=PolicyDeleteSLZ(),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["policy"],
    )
    @view_audit_decorator(SubjectPolicyDeleteAuditProvider)
    def destroy(self, request, *args, **kwargs):
        slz = PolicyDeleteSLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)

        system_id = slz.validated_data["system_id"]
        ids = slz.validated_data["ids"]
        subject = SvcSubject.from_username(request.user.username)

        policy_list = self.policy_query_biz.query_policy_list_by_policy_ids(system_id, subject, ids)

        # 删除权限
        self.policy_operation_biz.delete_by_ids(system_id, subject, ids)

        # 写入审计上下文
        audit_context_setter(subject=subject, system_id=system_id, policies=policy_list.policies)

        return Response()

    @swagger_auto_schema(
        operation_description="权限更新",
        request_body=PolicyPartDeleteSLZ(label="条件删除"),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["policy"],
    )
    @view_audit_decorator(SubjectPolicyDeleteAuditProvider)
    def update(self, request, *args, **kwargs):
        slz = PolicyPartDeleteSLZ(data=request.data)
        slz.is_valid(raise_exception=True)

        data = slz.validated_data

        policy_id = kwargs["pk"]
        resource_group_id = data["resource_group_id"]
        resource_system_id = data["system_id"]
        resource_type = data["type"]
        condition_ids = data["ids"]
        condition = data["condition"]

        subject = SvcSubject.from_username(request.user.username)

        system_id = self.policy_query_biz.get_policy_system_by_id(subject, policy_id)
        update_policy = self.policy_operation_biz.delete_partial(
            system_id,
            subject,
            policy_id,
            resource_group_id,
            resource_system_id,
            resource_type,
            condition_ids,
            [ConditionBean(attributes=[], **c) for c in condition],
        )

        # 写入审计上下文
        audit_context_setter(subject=subject, system_id=system_id, policies=[update_policy])

        return Response({})


class PolicyResourceGroupDeleteViewSet(BizMixin, GenericViewSet):
    @swagger_auto_schema(
        operation_description="Policy 删除资源组",
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["policy"],
    )
    @view_audit_decorator(SubjectPolicyDeleteAuditProvider)
    def destroy(self, request, *args, **kwargs):
        policy_id = kwargs["pk"]
        resource_group_id = kwargs["resource_group_id"]
        subject = SvcSubject.from_username(request.user.username)

        system_id = self.policy_query_biz.get_policy_system_by_id(subject, policy_id)
        # 删除权限
        update_policy = self.policy_operation_biz.delete_by_resource_group_id(
            system_id, subject, policy_id, resource_group_id
        )

        # 写入审计上下文
        audit_context_setter(subject=subject, system_id=system_id, policies=[update_policy])

        return Response()


class PolicySystemViewSet(BizMixin, GenericViewSet):
    pagination_class = None  # 去掉 swagger 中的 limit offset 参数

    @swagger_auto_schema(
        operation_description="用户的有权限的所有系统列表",
        responses={status.HTTP_200_OK: PolicySystemSLZ(label="系统", many=True)},
        tags=["policy"],
    )
    def list(self, request, *args, **kwargs):
        subject = SvcSubject.from_username(request.user.username)

        data = self.policy_query_biz.list_system_counter_by_subject(subject)

        return Response([one.dict() for one in data])


class PolicyExpireSoonViewSet(BizMixin, GenericViewSet):
    pagination_class = None  # 去掉 swagger 中的 limit offset 参数

    @swagger_auto_schema(
        operation_description="用户即将过期的权限列表",
        responses={status.HTTP_200_OK: PolicyExpireSoonSLZ(label="系统", many=True)},
        tags=["policy"],
    )
    def list(self, request, *args, **kwargs):
        subject = SvcSubject.from_username(request.user.username)

        data = self.policy_query_biz.list_expired(subject, get_soon_expire_ts())

        return Response([one.dict() for one in data])


class RelatedPolicyViewSet(BizMixin, GenericViewSet):
    """
    生成依赖操作
    """

    @swagger_auto_schema(
        operation_description="生成依赖操作",
        request_body=RelatedPolicySLZ(label="策略"),
        responses={status.HTTP_200_OK: PolicySLZ(label="策略", many=True)},
        tags=["policy"],
    )
    def create(self, request, *args, **kwargs):
        slz = RelatedPolicySLZ(data=request.data)
        slz.is_valid(raise_exception=True)

        data = slz.validated_data
        system_id = data["system_id"]
        source_policy = PolicyBean.parse_obj(data["source_policy"])

        # 移除用户已有的权限，只需要生成新增数据的依赖操作权限
        subject = SvcSubject.from_username(request.user.username)
        old_policy_list = self.policy_query_biz.new_policy_list(system_id, subject)
        old_policy = old_policy_list.get(source_policy.action_id)
        if old_policy:
            try:
                # 移除用户已有的资源实例
                source_policy = source_policy.remove_resource_group_list(old_policy.resource_groups)
            except PolicyEmptyException:
                # 如果来源 policy 与用户已有的策略完全一致，不需要生成依赖操作
                return Response([])

        # 关联操作
        related_policies = self.related_policy_biz.create_related_policies(system_id, source_policy)
        # 目标策略
        target_policies = parse_obj_as(List[PolicyTagBean], data["target_policies"])
        target_policy_list = PolicyTagBeanList(self.tenant_id, system_id, target_policies)

        # 新增的操作
        related_policy_list = PolicyTagBeanList(
            self.tenant_id, system_id, parse_obj_as(List[PolicyTagBean], related_policies)
        )
        add_policy_list = related_policy_list.sub(target_policy_list)
        if add_policy_list.policies:
            tag_add_policy_list = PolicyTagBeanList(
                self.tenant_id, system_id, parse_obj_as(List[PolicyTagBean], add_policy_list.policies)
            )
            tag_add_policy_list.set_tag(PolicyTag.ADD.value)  # 对于新增的部分打 tag, 方便前端处理

            # 对已有策略中会增加部分实例的策略打 update 标签
            for p in target_policy_list.policies:
                add_policy = add_policy_list.get(p.action_id)
                if (
                    add_policy
                    and not p.has_resource_group_list(add_policy.resource_groups)
                    and p.tag != PolicyTag.ADD.value
                ):
                    p.tag = PolicyTag.UPDATE.value

            target_policy_list.add(tag_add_policy_list)  # 合并

        target_policy_list.fill_empty_fields()

        return Response([p.dict() for p in target_policy_list.policies])


class BatchPolicyResourceCopyViewSet(BizMixin, ServiceMixin, GenericViewSet):
    """
    批量复制策略资源
    """

    @swagger_auto_schema(
        operation_description="批量复制策略资源",
        request_body=PolicyResourceCopySLZ(label="策略"),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["policy"],
    )
    def create(self, request, *args, **kwargs):
        slz = PolicyResourceCopySLZ(data=request.data)
        slz.is_valid(raise_exception=True)

        """
        1. 对 actions 做以 system 做分组
        2. 查询 system_id 对应的操作的实例视图
        3. 校验资源的类型是否满足操作对应的资源类型
        4. 通过实例视图筛选对应的实例
        5. 返回操作相关的信息与资源的数据/列表
        """
        data = slz.validated_data
        resource_type = RelatedResourceBean.parse_obj(data["resource_type"])
        actions = data["actions"]

        action_resource = []
        actions = sorted(actions, key=lambda action: action["system_id"])
        for system_id, grouping_actions in groupby(actions, key=lambda action: action["system_id"]):
            action_list = self.action_svc.new_action_list(system_id)
            for action in grouping_actions:
                sys_action = action_list.get(action["id"])
                if not sys_action:
                    continue
                rrt = sys_action.get_related_resource_type(resource_type.system_id, resource_type.type)
                if not rrt:
                    continue

                # 过滤满足实例视图的资源
                new_resource_type = resource_type.clone_and_filter_by_instance_selections(
                    rrt.instance_selections, ignore_attribute=True
                )
                if not new_resource_type:
                    continue
                action_resource.append(
                    {"system_id": action["system_id"], "id": action["id"], "resource_type": new_resource_type.dict()}
                )

        return Response(action_resource)


class RecommendPolicyViewSet(BizMixin, GenericViewSet):
    """
    生成推荐操作
    """

    pagination_class = None  # 去掉 swagger 中的 limit offset 参数

    @swagger_auto_schema(
        operation_description="生成推荐操作",
        query_serializer=ActionQuerySLZ(),
        responses={status.HTTP_200_OK: RecommendActionPolicy(label="推荐操作策略")},
        tags=["policy"],
    )
    def list(self, request, *args, **kwargs):
        slz = ActionQuerySLZ(data=request.query_params)
        slz.is_valid(raise_exception=True)

        system_id = slz.validated_data["system_id"]
        cache_id = slz.validated_data["cache_id"]

        cached_policy_list = self.application_policy_list_cache.get(cache_id)
        if cached_policy_list.system_id != system_id:
            raise error_codes.INVALID_ARGS.format(_("请求的 system 与缓存策略数据的 system 不一致"))

        # 查询推荐的操作
        recommend_action_dict = self.action_group_biz.get_action_same_group_dict(
            system_id, [one.action_id for one in cached_policy_list.policies]
        )

        action_list = self.action_biz.action_svc.new_action_list(system_id)

        # 生成推荐的策略
        policy_list = PolicyBeanList(self.tenant_id, system_id, [])
        for policy in cached_policy_list.policies:
            recommend_action_ids = recommend_action_dict.get(policy.action_id)
            if not recommend_action_ids:
                continue

            recommend_policies = self.related_policy_biz.create_recommend_policies(
                policy, action_list, recommend_action_ids
            )

            policy_list.add(PolicyBeanList(self.tenant_id, system_id, recommend_policies))  # 合并去重

        # 移除用户已有的操作
        subject = SvcSubject.from_username(request.user.username)
        own_policies = self.policy_query_biz.list_by_subject(system_id, subject)

        # 只移除用户已有的实例
        policy_list = policy_list.sub(PolicyBeanList(self.tenant_id, system_id, own_policies))

        policy_list.fill_empty_fields()

        # 生成推荐的操作，排除已生成推荐策略的操作
        own_action_id_set = {p.action_id for p in own_policies}
        actions, action_id_set = [], set()
        for action_id in chain(*list(recommend_action_dict.values())):
            if action_id in action_id_set:  # 去重
                continue
            action_id_set.add(action_id)

            # 用户已有的操作不需要推荐
            if action_id in own_action_id_set:
                continue

            action = action_list.get(action_id)
            if not action:
                continue

            actions.append(action)

        action_bean_list = ActionBeanList(parse_obj_as(List[ActionBean], actions))
        action_bean_list.fill_related_resource_type_name()
        return Response(
            {
                "actions": [a.dict() for a in action_bean_list.actions],
                "policies": [p.dict() for p in policy_list.policies],
            }
        )
