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

from typing import List

from django.db import transaction
from pydantic import parse_obj_as

from backend.api.authorization.models import AuthAPIAllowListConfig
from backend.apps.approval.models import ActionProcessRelation
from backend.apps.policy.models import Policy as PolicyModel
from backend.apps.role.models import RoleScope
from backend.apps.template.models import PermTemplate, PermTemplatePolicyAuthorized
from backend.service.action import ActionService
from backend.service.constants import ModelChangeEventStatus, ModelChangeEventType
from backend.service.model_event import ModelEventService
from backend.service.models import ModelEvent
from backend.service.policy.operation import PolicyOperationService


class ModelEventBean(ModelEvent):
    """继承ModelEvent的数据属性"""


class BaseEventExecutor:
    def __init__(self, event: ModelEventBean):
        self.event = event

    def run(self):
        self.execute()
        self.finish()

    def execute(self):
        """每个子类事件需要实现各自的执行逻辑"""
        raise NotImplementedError("subclasses of BaseEventExecutor must provide an execute() method")

    def finish(self):
        """事件执行结束后执行-更新状态"""
        ModelEventService().update_status(self.event.id, ModelChangeEventStatus.Finished.value)


class DeleteActionPolicyEventExecutor(BaseEventExecutor):
    """删除操作的策略"""

    def execute(self):
        """删除某个操作的所有策略"""
        system_id, action_id = self.event.system_id, self.event.model_id

        # 策略删除，包括自定义和模板权限
        with transaction.atomic():
            # 1. 用户或用户组自定义权限删除
            PolicyModel.delete_by_action(system_id=system_id, action_id=action_id)

            # 2. 权限模板：变更权限模板里的action_ids及其授权的数据
            template_ids = PermTemplate.delete_action(system_id, action_id)
            PermTemplatePolicyAuthorized.delete_action(system_id, action_id, template_ids)

            # 3. 调用后台根据action_id删除Policy的API, 实际测试在150万策略里删除10万+策略，大概需要3秒多
            PolicyOperationService().delete_backend_policy_by_action(system_id, action_id)

        # 4. 分级管理员授权范围
        RoleScope.delete_action_from_scope(system_id, action_id)

        # 5. Action的审批流程配置
        ActionProcessRelation.delete_by_action(system_id=system_id, action_id=action_id)

        # 6. API白名单授权撤销
        AuthAPIAllowListConfig.delete_by_action(system_id, action_id)


class DeleteActionEventExecutor(BaseEventExecutor):
    """删除操作"""

    def execute(self):
        """删除Action权限模型"""
        ActionService().delete(self.event.system_id, self.event.model_id)


class ModelEventBiz:
    svc = ModelEventService()

    def list(self, status: str, limit: int = 1000) -> List[ModelEventBean]:
        """有限制条数的查询"""
        events = self.svc.list(status, limit)
        return parse_obj_as(List[ModelEventBean], events)

    def get_executor(self, event: ModelEventBean) -> BaseEventExecutor:
        """
        获取事件执行者，用于执行事件
        """
        # Note: 目前只能处理某个操作的策略删除和操作本身的删除
        if event.type == ModelChangeEventType.ActionPolicyDeleted.value:
            return DeleteActionPolicyEventExecutor(event=event)

        if event.type == ModelChangeEventType.ActionDeleted.value:
            return DeleteActionEventExecutor(event=event)

        raise NotImplementedError(f"{event.type} executor not implement")

    def delete_finished_event(self, before_updated_at: int, limit: int = 1000):
        """有限制条数和时间的删除事件"""
        self.svc.delete_finished_event(before_updated_at, limit)
