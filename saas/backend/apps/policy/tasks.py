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
import json
import logging

from aenum import LowerStrEnum, auto
from celery import task

from backend.api.authorization.constants import AuthorizationAPIEnum
from backend.api.authorization.models import AuthAPIAllowListConfig
from backend.apps.approval.models import ActionProcessRelation
from backend.apps.policy.models import Policy
from backend.apps.role.models import RoleScope
from backend.apps.template.models import PermTemplate, PermTemplatePolicyAuthorized
from backend.component import iam
from backend.service.constants import RoleScopeType
from backend.util.enum import ChoicesEnum
from backend.util.json import json_dumps

logger = logging.getLogger("celery")


# TODO: [重构]单独的ModelChangeEvent的Service和Biz模块
class ModelChangeEventTypeEnum(ChoicesEnum, LowerStrEnum):
    ActionPolicyDeleted = "action_policy_deleted"
    ActionDeleted = "action_deleted"


class ModelChangeEventStatusEnum(ChoicesEnum, LowerStrEnum):
    Pending = auto()
    Finished = auto()


# TODO: [重构]目前还没有统一的Service和Biz，同时还要调用的Policy删除接口，待Policy重构完后再重构
@task(ignore_result=True)
def execute_model_change_event():
    """作为后台模型事件的异步任务消费者，目前包括删除Action的相关策略，删除Action权限模型"""
    # 1. 查询模型变更事件
    events = iam.list_model_change_event(ModelChangeEventStatusEnum.Pending.value)
    if len(events) == 0:
        return

    # 2. 遍历每个事件，执行对应任务
    # 记录失败事件
    failed_events = set()
    for event in events:
        event_type, system_id, action_id = event["type"], event["system_id"], event["model_id"]

        if event_type not in [
            ModelChangeEventTypeEnum.ActionPolicyDeleted.value,
            ModelChangeEventTypeEnum.ActionDeleted.value,
        ]:
            logger.info(f"The model change event of type({event_type}) not supported yet")
            continue

        # 记录执行过的事件，以防需要排查
        logger.info(f"execute model change event: f{event}")
        try:
            # 删除Action相关的所有策略
            if event_type == ModelChangeEventTypeEnum.ActionPolicyDeleted.value:
                delete_action_policies(system_id, action_id)
            elif event_type == ModelChangeEventTypeEnum.ActionDeleted.value:
                # 若依赖事件失败了，则当前事件不可执行
                # Note: 这里只处理关于Action删除和Action相关Policy删除的顺序问题
                if (ModelChangeEventTypeEnum.ActionPolicyDeleted.value, system_id, action_id) in failed_events:
                    continue

                # 删除Action模型
                delete_action(system_id, action_id)
            # 执行完事件后，更新事件状态
            iam.update_model_change_event(event["pk"], ModelChangeEventStatusEnum.Finished.value)
        except Exception as error:
            logger.exception(error)
            # 记录失败事件
            failed_events.add((event_type, system_id, action_id))


def delete_action_policies(system_id: str, action_id: str):
    """删除某个操作的所有策略"""
    # 1. 用户或用户组自定义权限删除
    Policy.objects.filter(system_id=system_id, action_id=action_id).delete()

    # 2. 权限模板：变更权限模板里的action_ids及其授权的数据
    _delete_action_from_perm_template(system_id, action_id)

    # 3. 调用后台根据action_id删除Policy的API, 实际测试在150万策略里删除10万+策略，大概需要3秒多
    iam.delete_action_policies(system_id, action_id)

    # 4. 分级管理员授权范围：role_rolescope
    _delete_action_from_role_scope(system_id, action_id)

    # 5. Action的审批流程配置：approval_actionprocessrelation
    ActionProcessRelation.objects.filter(system_id=system_id, action_id=action_id).delete()

    # 6. API白名单授权：authorization_authapiallowlistconfig
    AuthAPIAllowListConfig.objects.filter(
        type=AuthorizationAPIEnum.AUTHORIZATION_INSTANCE.value, system_id=system_id, object_id=action_id
    ).delete()


def delete_action(system_id: str, action_id: str):
    """删除Action权限模型"""
    iam.delete_action(system_id, action_id)


# TODO: [重构]_delete_action_from_perm_template/_delete_action_from_role_scope逻辑应该放到对应对象的biz里
def _delete_action_from_perm_template(system_id: str, action_id: str):
    """从权限模板里移除Action，同时包括权限模板的授权"""
    # 1 变更权限模板
    perm_templates = PermTemplate.objects.filter(system_id=system_id)
    modified_perm_template_ids = []
    updated_perm_templates = []
    for pt in perm_templates:
        action_ids = pt.action_ids
        # 要删除的Action不在权限模板里，则忽略
        if action_id not in action_ids:
            continue
        # 移除要删除Action，然后更新
        action_ids.remove(action_id)
        pt.action_ids = action_ids
        # 添加到将更新的队列
        updated_perm_templates.append(pt)
        modified_perm_template_ids.append(pt.id)
    # 批量更新权限模板
    if len(updated_perm_templates) > 0:
        PermTemplate.objects.bulk_update(updated_perm_templates, fields=["_action_ids"], batch_size=100)

    # 2 变更权限模板授权数据
    if len(modified_perm_template_ids) > 0:
        perm_template_policy_authorizeds = PermTemplatePolicyAuthorized.objects.filter(
            template_id__in=modified_perm_template_ids, system_id=system_id
        )
        updated_perm_template_policy_authorizeds = []
        for ptpa in perm_template_policy_authorizeds:
            data = ptpa.data
            actions = [a for a in data["actions"] if a["id"] != action_id]
            data["actions"] = actions
            ptpa.data = data
            updated_perm_template_policy_authorizeds.append(ptpa)
        if len(updated_perm_template_policy_authorizeds) > 0:
            PermTemplatePolicyAuthorized.objects.bulk_update(
                updated_perm_template_policy_authorizeds, fields=["_data"], batch_size=20
            )


def _delete_action_from_role_scope(system_id: str, action_id: str):
    """从分级管理员的授权范围里删除操作"""
    role_scopes = RoleScope.objects.filter(type=RoleScopeType.AUTHORIZATION.value)
    updated_role_scopes = []
    for role_scope in role_scopes:
        content = json.loads(role_scope.content)
        is_updated = False
        for scope in content:
            if scope["system_id"] != system_id:
                continue
            # 判断Action是否存在，不存在则忽略
            action_ids = {action["id"] for action in scope["actions"]}
            if action_id not in action_ids:
                continue
            # 如果包含要删除的Action，则进行更新数据
            scope["actions"] = [action for action in scope["actions"] if action["id"] != action_id]
            is_updated = True
            break
        if is_updated:
            role_scope.content = json_dumps(content)
            updated_role_scopes.append(role_scope)

    # 批量更新分级管理员授权范围
    if len(updated_role_scopes) > 0:
        RoleScope.objects.bulk_update(updated_role_scopes, fields=["content"], batch_size=10)


@task(ignore_result=True)
def delete_unquoted_expressions():
    """删除未被引用的expression"""
    iam.delete_unquoted_expressions()
