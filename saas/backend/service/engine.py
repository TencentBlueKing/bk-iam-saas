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

from typing import Any, Dict, List

from pydantic import BaseModel

from backend.common.error_codes import error_codes
from backend.component.engine import batch_query_subjects, query_subjects

from .models import Condition, PathNode, Policy, RelatedResource
from .utils.translate import translate_path

MAX_ENGINE_SEARCH_RESOURCE_COUNT = 20


class PolicyResource(BaseModel):
    action_id: str
    resources: List[Dict[str, Any]]


class EngineService:
    def query_subjects_by_policy_resources(
        self, system_id: str, policy_resources: List[PolicyResource], subject_type: str, limit: int = 1000
    ):
        """
        使用policies查询相关有权限的subjects
        """
        query_data = []
        for p in policy_resources:
            if len(p.resources) == 0:
                query_data.append(
                    {
                        "system": system_id,
                        "action": {"id": p.action_id},
                        "resource": [],
                        "subject_type": subject_type,
                        "limit": limit,
                    }
                )
                continue

            for resource in p.resources:
                query_data.append(
                    {
                        "system": system_id,
                        "action": {"id": p.action_id},
                        "resource": [resource],
                        "subject_type": subject_type,
                        "limit": limit,
                    }
                )

        if not query_data:
            return []

        if len(query_data) > MAX_ENGINE_SEARCH_RESOURCE_COUNT:
            raise error_codes.ENGINE_REQUEST_ERROR.format(
                "查询的资源实例不能超过{}个".format(MAX_ENGINE_SEARCH_RESOURCE_COUNT)
            )

        resp_data = batch_query_subjects(query_data)
        return resp_data["results"]

    def query_subjects_by_resource_instance(self, query_data):
        """
        使用资源实例信息查询相关有权限的subjects
        """
        return query_subjects(query_data)

    def gen_search_policy_resources(self, policies: List[Policy]) -> List[PolicyResource]:
        """
        生成用于搜索的PolicyResource
        """
        policy_resources = []
        for p in policies:
            policy_resources.append(self._gen_query_by_policy(p))

        return policy_resources

    def _gen_query_by_policy(self, policy: Policy) -> PolicyResource:
        """
        使用policy生成查询数据
        NOTE: 这里默认关联一种资源类型的操作, 只有一个resource_group
        """
        if len(policy.resource_groups) == 0:
            # 生成无关联操作的查询条件
            return PolicyResource(action_id=policy.action_id, resources=[])

        if len(policy.list_thin_resource_type()) != 1:
            raise error_codes.ENGINE_REQUEST_ERROR.format("不支持关联多个资源类型的查询")

        rrt = policy.resource_groups[0].related_resource_types[0]
        if len(rrt.condition) == 0:
            return PolicyResource(action_id=policy.action_id, resources=[])
        resources = []
        for condition in rrt.condition:
            resources.extend(self._gen_resources_by_condition(rrt, condition))

        return PolicyResource(action_id=policy.action_id, resources=resources)

    def _gen_resources_by_condition(self, rrt: RelatedResource, condition: Condition):
        """
        使用policy condition生成用于查询的资源列表

        result:

        [
            {
                "system": "bk_job",
                "type": "script",
                "id": "fce008bbebf04a49950d59538e8a89bb",
                "attribute": {
                    "_bk_iam_path_": "/biz,2005000002/"
                }
            }
        ]
        """
        attrs = {}
        # 遍历资源实例, 生成查询条件
        for attr in condition.attributes:
            attrs[attr.id] = [v.id for v in attr.values]

        resources = []
        for instance in condition.instances:
            for path in instance.path:
                resource = self._gen_resource_by_path(rrt, attrs, path)
                resources.append(resource)

        if len(resources) == 0 and attrs:
            resources.append({"system": rrt.system_id, "type": rrt.type, "id": "*", "attribute": attrs})

        return resources

    def _gen_resource_by_path(self, rrt: RelatedResource, attrs: Dict[str, Any], path: List[PathNode]):
        """
        使用资源实例的path生成用于查询的resource

        1. 如果path是叶子节点, 资源的id为叶子点的id, 否则资源id为*
        2. 叶子节点的path为path的前缀

        result:

        {
            "system": "bk_job",
            "type": "script",
            "id": "fce008bbebf04a49950d59538e8a89bb",
            "attribute": {
                "_bk_iam_path_": "/biz,2005000002/"
            }
        }
        """
        resource: Dict[str, Any] = {
            "system": rrt.system_id,
            "type": rrt.type,
            "id": "*",
            "attribute": {},
        }
        resource["attribute"].update(attrs)
        last_node = path[-1]
        if last_node.type == rrt.type and last_node.system_id == rrt.system_id:
            resource["id"] = last_node.id
            if path[:-1]:
                resource["attribute"]["_bk_iam_path_"] = translate_path([n.dict() for n in path[:-1]])
        else:
            resource["attribute"]["_bk_iam_path_"] = translate_path([n.dict() for n in path])
        return resource
