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

from backend.biz.action import ActionBiz, ActionCheckBiz
from backend.biz.action_group import ActionGroupBiz
from backend.biz.aggregate_action import AggregateActionsBiz
from backend.biz.application import ApplicationBiz
from backend.biz.approval import ApprovalProcessBiz
from backend.biz.group import GroupBiz, GroupCheckBiz
from backend.biz.helper import RoleWithPermGroupBiz
from backend.biz.instance_selection import InstanceSelectionBiz
from backend.biz.open import ApplicationPolicyListCache
from backend.biz.policy import PolicyOperationBiz, PolicyQueryBiz
from backend.biz.policy_tag import ConditionTagBiz
from backend.biz.related_policy import RelatedPolicyBiz
from backend.biz.resource import ResourceBiz
from backend.biz.resource_creator_action import ResourceCreatorActionBiz
from backend.biz.resource_type import ResourceTypeBiz
from backend.biz.role import RoleBiz, RoleCheckBiz
from backend.biz.subject import SubjectBiz
from backend.biz.subject_template import SubjectTemplateBiz, SubjectTemplateCheckBiz
from backend.biz.system import SystemBiz
from backend.biz.template import TemplateBiz, TemplateCheckBiz, TemplatePolicyCloneBiz

from .tenant import TenantMixin


class BizMixin(TenantMixin):
    """
    该 Mixin 用于在视图中获取 Biz 层的相关类
    这里的 Biz 层类是指在 `backend/biz` 目录下定义的业务逻辑类
    集合了所有业务逻辑相关的类，方便在视图中按需直接使用
    """

    @property
    def system_biz(self):
        return SystemBiz()

    @property
    def resource_type_biz(self):
        return ResourceTypeBiz()

    @property
    def instance_selection_biz(self):
        return InstanceSelectionBiz(self.tenant_id)

    @property
    def aggregate_action_biz(self):
        return AggregateActionsBiz(self.tenant_id)

    @property
    def action_biz(self):
        return ActionBiz(self.tenant_id)

    @property
    def action_group_biz(self):
        return ActionGroupBiz(self.tenant_id)

    @property
    def action_check_biz(self):
        return ActionCheckBiz(self.tenant_id)

    @property
    def group_biz(self):
        return GroupBiz(self.tenant_id)

    @property
    def group_check_biz(self):
        return GroupCheckBiz(self.tenant_id)

    @property
    def application_biz(self):
        return ApplicationBiz(self.tenant_id)

    @property
    def application_policy_list_cache(self):
        return ApplicationPolicyListCache(self.tenant_id)

    @property
    def approval_process_biz(self):
        return ApprovalProcessBiz(self.tenant_id)

    @property
    def policy_query_biz(self):
        return PolicyQueryBiz(self.tenant_id)

    @property
    def policy_operation_biz(self):
        return PolicyOperationBiz(self.tenant_id)

    @property
    def condition_biz(self):
        return ConditionTagBiz()

    @property
    def role_biz(self):
        return RoleBiz(self.tenant_id)

    @property
    def role_check_biz(self):
        return RoleCheckBiz(self.tenant_id)

    @property
    def role_with_perm_group_biz(self):
        return RoleWithPermGroupBiz(self.tenant_id)

    @property
    def template_biz(self):
        return TemplateBiz(self.tenant_id)

    @property
    def template_check_biz(self):
        return TemplateCheckBiz(self.tenant_id)

    @property
    def template_policy_clone_biz(self):
        return TemplatePolicyCloneBiz(self.tenant_id)

    @property
    def related_policy_biz(self):
        return RelatedPolicyBiz(self.tenant_id)

    @property
    def resource_biz(self):
        return ResourceBiz(self.tenant_id)

    @property
    def subject_template_biz(self):
        return SubjectTemplateBiz(self.tenant_id)

    @property
    def subject_template_check_biz(self):
        return SubjectTemplateCheckBiz(self.tenant_id)

    @property
    def subject_biz(self):
        return SubjectBiz(self.tenant_id)

    @property
    def resource_creator_action_biz(self):
        return ResourceCreatorActionBiz()
