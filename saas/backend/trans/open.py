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
from typing import Any, List

from pydantic import ConfigDict, BaseModel, Field
from pydantic.tools import parse_obj_as

from backend.biz.action import ActionCheckBiz, ActionForCheck
from backend.biz.instance_selection import InstanceSelectionBean, InstanceSelectionBiz, PathResourceTypeBean
from backend.biz.policy import PolicyBean, PolicyBeanList, group_paths
from backend.biz.resource import ResourceBiz, ResourceNodeBean
from backend.common.error_codes import error_codes
from backend.util.uuid import gen_uuid


class OpenResourcePathNode(BaseModel):
    system_id: str = Field(alias="system", default="")  # 默认值为空，兼容早期API都允许不传system
    type: str
    id: str
    name: str = ""
    model_config = ConfigDict(populate_by_name=True)


class OpenRelatedResource(BaseModel):
    system_id: str = Field(alias="system")
    type: str
    paths: List[List[OpenResourcePathNode]] = []
    attributes: List[Any] = []  # 一般情况下，若支持属性，其API协议与PolicyBean等都一致的，所以不需要额外定义，Any表示即可
    model_config = ConfigDict(populate_by_name=True)

    def _raise_match_selection_fail_exception(self, path: List[OpenResourcePathNode]):
        raise error_codes.VALIDATE_ERROR.format(f"resource({path}) not satisfy instance selection")

    def fill_instance_system(self, selections: List[InstanceSelectionBean]):
        """使用实例视图，对所有资源实例路径进行system填充"""
        for path in self.paths:
            # 遍历每个实例视图，查询哪些实例视图与path是匹配
            path_resource_types = [PathResourceTypeBean(system_id=node.system_id, id=node.type) for node in path]
            match_selections = [selection for selection in selections if selection.match_path(path_resource_types)]

            # 若没有任何一个实例视图匹配，说明数据有问题，直接异常
            if not match_selections:
                self._raise_match_selection_fail_exception(path)

            # 判断是否路径上每个节点都有system，有的话不需要使用实例视图填充
            if all([node.system_id != "" for node in path]):
                continue

            # 取匹配的实例视图的第一个来做填充
            first_match_selection = match_selections[0]

            # 获取到实例视图提供的系统列表, 填充到现有的path中
            system_ids = first_match_selection.list_match_path_system_id(path_resource_types)
            for node, system_id in zip(path, system_ids):
                node.system_id = system_id

            # 如果有多个实例视图可以匹配, 所有实例视图返回的system_ids必须一致
            for selection in match_selections[1:]:
                if system_ids != selection.list_match_path_system_id(path_resource_types):
                    self._raise_match_selection_fail_exception(path)

    def fill_instance_name(self):
        """填充资源实例名称
        Note: 这里的填充名字只会对缺名称的进行填充，因为对于授权API是说，是可以完全信任接入系统传的名称
        """
        # 必须保证所有资源实例的system_id都存在
        assert all([node.system_id != "" for path in self.paths for node in path])

        # 查询资源Name
        resource_biz = ResourceBiz()
        resource_nodes = [ResourceNodeBean.parse_obj(node) for path in self.paths for node in path if node.name == ""]
        name_provider = resource_biz.fetch_resource_name(resource_nodes, raise_not_found_exception=True)

        # 填充实例名称
        for path in self.paths:
            for node in path:
                if node.name == "":
                    node.name = name_provider.get_attribute(ResourceNodeBean.parse_obj(node))


class OpenPolicy(BaseModel):
    """
    这是Open API 对于 授权等涉及到策略相关的对外统一数据结构
    """

    system_id: str = Field(alias="system")
    action_id: str = Field(alias="id")
    related_resource_types: List[OpenRelatedResource]
    model_config = ConfigDict(populate_by_name=True)

    def fill_instance_system(self):
        """填充system，由于申请数据里的资源实例可能只有type和id，不知道该资源是哪个系统的，所以需要根据权限模型的进行填充"""
        # 使用模型里的实例视图进行填充
        instance_selection_biz = InstanceSelectionBiz()
        for rrt in self.related_resource_types:
            # 查询实例视图
            selections = instance_selection_biz.list_by_action_resource_type(
                self.system_id,
                self.action_id,
                rrt.system_id,
                rrt.type,
            )

            # 对于只支持属性配置的操作，不需要填充
            if not selections:
                # 没有实例视图，但是在授权时配置里实例，则不允许
                if len(rrt.paths) > 0:
                    raise error_codes.VALIDATE_ERROR.format(f"action({self.action_id}) not support to grant instance")
                continue

            # 填充path的system_id
            rrt.fill_instance_system(selections)

    def fill_instance_name(self):
        """填充资源实例名称"""
        for rrt in self.related_resource_types:
            rrt.fill_instance_name()


class OpenCommonTrans:
    """主要是处理open api的通用处理，因为所有open api都会保持相同的概念协议，所有很多转换逻辑都是通用"""

    action_check_biz = ActionCheckBiz()

    @staticmethod
    def _to_policies(open_policies: List[OpenPolicy]) -> List[PolicyBean]:
        """批量将OpenPolicy转换为PolicyBean"""
        policies = []
        for open_policy in open_policies:
            related_resource_types = []
            for rrt in open_policy.related_resource_types:
                rrt_dict = rrt.dict()
                # 将多个以path方式表示的实例进行分组
                instances = group_paths(rrt_dict["paths"])

                # 若instances和attributes都为空，则为无限制
                condition = (
                    [{"instances": instances, "attributes": rrt_dict["attributes"]}]
                    if instances or rrt_dict["attributes"]
                    else []
                )

                related_resource_types.append(
                    {
                        "system_id": rrt.system_id,
                        "type": rrt.type,
                        "condition": condition,
                    }
                )

            policy = PolicyBean.parse_obj(
                {
                    "action_id": open_policy.action_id,
                    "resource_groups": [{"id": gen_uuid(), "related_resource_types": related_resource_types}]
                    if related_resource_types
                    else [],
                }
            )
            policies.append(policy)

        return policies

    def _to_policy_list(self, system_id: str, open_policies: List[OpenPolicy], expired_at=0) -> PolicyBeanList:
        """授权数据转换的公共逻辑：(1) 校验与权限模型是否一致（2）转换为策略数据，并校验实例视图和填充相关字段"""
        # 1. 初步检查是否合法数据，与权限模型是否一致
        self.action_check_biz.check(system_id, parse_obj_as(List[ActionForCheck], open_policies))

        # 2. 转换为策略数据结构
        policies = self._to_policies(open_policies)
        # 设置有效期
        if expired_at > 0:
            for p in policies:
                p.set_expired_at(expired_at)

        policy_list = PolicyBeanList(
            system_id=system_id,
            policies=policies,
            need_fill_empty_fields=True,  # 填充相关字段
            need_check_instance_selection=True,  # 校验实例视图
        )

        return policy_list
