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

from typing import Any, Dict, List, Optional

from django.db import transaction
from django.http import Http404
from django.utils.translation import gettext as _
from pydantic import BaseModel, parse_obj_as
from pydantic.fields import Field

from backend.apps.group.models import GroupAuthorizeLock
from backend.apps.role.models import RoleRelatedObject
from backend.apps.template.models import (
    PermTemplate,
    PermTemplatePolicyAuthorized,
    PermTemplatePreGroupSync,
    PermTemplatePreUpdateLock,
)
from backend.biz.policy import (
    ConditionBean,
    PathNodeBean,
    PathNodeBeanList,
    PolicyBean,
    PolicyBeanList,
    RelatedResourceBean,
    ResourceGroupBean,
    ThinAction,
    group_paths,
)
from backend.biz.role import RoleAuthorizationScopeChecker
from backend.common.error_codes import error_codes
from backend.common.time import PERMANENT_SECONDS
from backend.service.action import ActionList, ActionService
from backend.service.constants import RoleRelatedObjectType, SubjectType, TemplatePreUpdateStatus
from backend.service.models import Action, ChainNode, Policy, Subject
from backend.service.template import TemplateGroupPreCommit, TemplateService
from backend.util.uuid import gen_uuid


class TemplateCreateBean(BaseModel):
    name: str
    system_id: str
    description: str
    action_ids: List[str]


class TemplateNameDict(BaseModel):
    data: Dict[int, str]

    def get(self, template_id: int, default=""):
        return self.data.get(template_id, default)


class TemplateGroupPreCommitBean(BaseModel):
    group_id: int = Field(alias="id")
    policies: List[PolicyBean] = Field(alias="actions")

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        for policy in self.policies:
            policy.set_expired_at(PERMANENT_SECONDS)  # 用户组默认过期时间为 永久

    class Config:
        allow_population_by_field_name = True  # 支持alias字段同时传

    @property
    def action_ids(self):
        return [one.action_id for one in self.policies]


class TemplateNameDictBean(BaseModel):
    data: Dict[int, str]

    def get(self, template_id):
        return self.data.get(template_id, template_id)


class TemplateBiz:
    svc = TemplateService()
    action_svc = ActionService()

    def create(self, role_id: int, info: TemplateCreateBean, creator: str) -> PermTemplate:
        """
        创建权限模板
        """
        with transaction.atomic():
            template = PermTemplate(creator=creator, updater=creator, **info.dict(exclude={"action_ids"}))
            template.action_ids = info.action_ids
            template.save(force_insert=True)
            RoleRelatedObject.objects.create_template_relation(role_id, template.id)

        return template

    def delete_pre_update_lock(self, template_id: int):
        """
        删除模板预更新锁
        """
        lock = PermTemplatePreUpdateLock.objects.acquire_lock_not_running_or_raise(template_id=template_id)
        if not lock:
            return

        with transaction.atomic():
            lock.delete()
            PermTemplatePreGroupSync.objects.delete_by_template(template_id)

    def delete(self, template_id: int):
        """
        删除权限模板
        """
        if PermTemplatePolicyAuthorized.objects.count_by_template(template_id) != 0:
            raise error_codes.VALIDATE_ERROR.format(_("该权限模板已被用户组关联, 不能删除!"))

        with transaction.atomic():
            PermTemplate.objects.filter(id=template_id).delete()
            RoleRelatedObject.objects.delete_template_relation(template_id)

    def grant_subject(self, system_id: str, template_id: int, subject: Subject, policies: List[PolicyBean]):
        """
        权限模板增加成员
        """
        self.svc.grant_subject(
            system_id,
            template_id,
            subject,
            parse_obj_as(List[Policy], policies),
            action_list=self.action_svc.new_action_list(system_id),
        )

    def filter_not_auth_subjects(self, template_id, subjects: List[Subject]) -> List[Subject]:
        """
        筛选出还没授权的subjects
        """
        exists_subjects = PermTemplatePolicyAuthorized.objects.query_exists_subject(
            template_id, [s.id for s in subjects]
        )
        return [s for s in subjects if s not in set(exists_subjects)]

    def revoke_subjects(self, system_id: str, template_id: int, members: List[Subject]):
        """
        批量移除模板成员
        """
        for member in members:
            self.svc.revoke_subject(system_id, template_id, member)

    def delete_template_auth_by_subject(self, subject: Subject):
        """
        删除subject模板授权
        """
        template_ids = list(
            PermTemplatePolicyAuthorized.objects.filter_by_subject(subject).values_list("template_id", flat=True)
        )
        templates = PermTemplate.objects.filter(id__in=template_ids)
        for template in templates:
            self.svc.revoke_subject(template.system_id, template.id, subject)

    def create_or_update_group_pre_commit(self, template_id: int, pre_commits: List[TemplateGroupPreCommitBean]):
        """
        创建或更新用户组更新的预提交信息
        """
        self.svc.create_or_update_group_pre_commit(
            template_id, parse_obj_as(List[TemplateGroupPreCommit], pre_commits)
        )

    def list_template_update_add_action_id(self, template: PermTemplate) -> List[str]:
        """
        查询模板预更新中的新增操作
        """
        lock = PermTemplatePreUpdateLock.objects.acquire_lock_waiting_or_raise(template_id=template.id)
        return list(set(lock.action_ids) - set(template.action_ids))

    def sync_group_template_auth(self, group_id: int, template_id: int):
        """
        同步用户组模板授权
        """
        # 查询需要删除的操作
        lock = PermTemplatePreUpdateLock.objects.acquire_lock_or_raise(template_id=template_id)
        template = PermTemplate.objects.get_or_404(template_id)
        del_action_ids = list(set(template.action_ids) - set(lock.action_ids))

        # 查询需要新增的策略信息
        create_policies = []
        group_pre_commit = PermTemplatePreGroupSync.objects.get_by_group_template(group_id, template_id)
        if group_pre_commit:
            create_policies = parse_obj_as(List[Policy], group_pre_commit.data["actions"])

        # 执行策略变更
        subject = Subject.from_group_id(group_id)
        self.svc.alter_template_auth(subject, template_id, create_policies, del_action_ids)
        if group_pre_commit:
            PermTemplatePreGroupSync.objects.update_status(group_pre_commit.id, TemplatePreUpdateStatus.FINISHED.value)

    def finish_template_update_sync(self, template_id: int):
        """
        结束模板更新同步
        """
        lock = PermTemplatePreUpdateLock.objects.acquire_lock_or_raise(template_id=template_id)
        template = PermTemplate.objects.get_or_404(template_id)
        template.action_ids = lock.action_ids
        with transaction.atomic():
            template.save(update_fields=["_action_ids"])
            lock.delete()
            PermTemplatePreGroupSync.objects.delete_by_template(template_id)

    def create_template_update_lock(self, template: PermTemplate, action_ids: List[str]) -> PermTemplatePreUpdateLock:
        """
        创建模板更新锁
        """
        if GroupAuthorizeLock.objects.filter(template_id=template.id).exists():
            raise error_codes.VALIDATE_ERROR.format(_("正在授权中, 请稍后!"))

        if set(template.action_ids) == set(action_ids):
            raise error_codes.VALIDATE_ERROR.format(_("权限模板未变更, 无需更新!"))

        template_id = template.id
        lock = PermTemplatePreUpdateLock.objects.acquire_lock_not_running_or_raise(template_id=template_id)
        if lock and set(lock.action_ids) != set(action_ids):
            raise error_codes.VALIDATE_ERROR.format(_("任务正在运行中，请稍后!"))

        if not lock:
            lock = PermTemplatePreUpdateLock(template_id=template_id)
            lock.action_ids = action_ids  # type: ignore
            lock.save(force_insert=True)

        return lock

    def get_template_name_dict_by_ids(self, template_ids: List[int]) -> TemplateNameDict:
        """
        获取模板id: name的字典
        """
        queryset = PermTemplate.objects.filter(id__in=template_ids).only("name")
        return TemplateNameDict(data={one.id: one.name for one in queryset})


class TemplateCheckBiz:
    svc = TemplateService()

    def check_role_template_name_exists(self, role_id: int, name: str, template_id: int = 0):
        """
        检查名字是否被使用
        """
        role_template_ids = RoleRelatedObject.objects.list_role_object_ids(
            role_id, RoleRelatedObjectType.TEMPLATE.value
        )
        if template_id in role_template_ids:
            role_template_ids.remove(template_id)
        if PermTemplate.objects.filter(id__in=role_template_ids, name=name).exists():
            raise error_codes.VALIDATE_ERROR.format(_("存在同名权限模板"))

    def check_add_member(self, template_id: int, subject: Subject, action_ids: List[str]):
        """
        检查增加成员的数据
        """
        try:
            template = PermTemplate.objects.get_or_404(template_id)
        except Http404:
            raise error_codes.VALIDATE_ERROR.format(_("模板: {} 不存在").format(template_id))

        try:
            PermTemplatePolicyAuthorized.objects.get_by_subject_template(subject, template_id)
            raise error_codes.VALIDATE_ERROR.format(
                _("用户组: {} 不能授权已授权的模板: {}").format(subject.id, template.name)
            )
        except Http404:
            pass

        if set(template.action_ids) != set(action_ids):
            raise error_codes.VALIDATE_ERROR.format(_("提交的操作列表与模板: {} 实际的不一致").format(template.name))

    def check_group_update_pre_commit(
        self, template_id: int, pre_commits: List[TemplateGroupPreCommitBean], add_action_ids: List[str]
    ):
        """
        检查用户组更新模板授权的预提交信息

        action_ids: 模板与提交中新增的操作
        """
        # 检查用户组是否都是已授权过的用户组
        queryset = PermTemplatePolicyAuthorized.objects.filter_by_template(template_id).values_list(
            "subject_type", "subject_id"
        )
        exists_members = [Subject(type=one[0], id=one[1]) for one in queryset]
        subjects = [Subject.from_group_id(one.group_id) for one in pre_commits]
        if not set(subjects).issubset(set(exists_members)):
            raise error_codes.VALIDATE_ERROR.format(_("提交数据中存在模板未授权的用户组!"))

        # 检查用户组提交的新增操作与模板与提交的新增操作是否一致
        action_id_set = set(add_action_ids)
        for pre_commit in pre_commits:
            if set(pre_commit.action_ids) != action_id_set:
                raise error_codes.VALIDATE_ERROR.format(
                    _("提交操作数据{}与模板预更新的数据{}不一致!").format(pre_commit.action_ids, add_action_ids)
                )

    def check_group_pre_commit_complete(self, template_id: int):
        """
        检查用户组的与提交信息是否完整
        """
        exists_group_ids = (
            PermTemplatePolicyAuthorized.objects.filter_by_template(template_id)
            .filter(subject_type=SubjectType.GROUP.value)
            .values_list("subject_id", flat=True)
        )
        pre_commit_group_ids = PermTemplatePreGroupSync.objects.filter_by_template(template_id).values_list(
            "group_id", flat=True
        )

        if set(map(str, pre_commit_group_ids)) != set(exists_group_ids):
            raise error_codes.VALIDATE_ERROR.format(
                _("权限模板授权的用户组更新信息不完整! 缺少以下action: {}").format(
                    set(exists_group_ids) - set(map(str, pre_commit_group_ids))
                )
            )


class ActionCloneConfig(BaseModel):
    action_id: str
    from_actions: List[ThinAction] = Field(alias="copy_from_actions")

    class Config:
        allow_population_by_field_name = True


class GroupClonePolicy(BaseModel):
    group_id: int
    policy: PolicyBean


class ChainNodeList:
    def __init__(self, nodes: List[ChainNode]) -> None:
        self.nodes = nodes

    def match_prefix(self, node_list: "ChainNodeList") -> Optional["ChainNodeList"]:
        """
        匹配视图的前缀
        """
        for self_node, node in zip(self.nodes, node_list.nodes, strict=False):
            if not self_node.match_chain_node(node):
                return None

        # 取长度小的，视图的前缀
        if len(self.nodes) > len(node_list.nodes):
            return node_list

        return self

    @property
    def length(self) -> int:
        return len(self.nodes)

    def is_match_path(self, path: List[PathNodeBean]) -> bool:
        if len(path) > self.length:
            return False

        for path_node, chain_node in zip(path, self.nodes, strict=False):
            if not chain_node.match_resource_type(path_node.to_path_resource_type()):
                return False

        return True


class ChainList:
    def __init__(self, chains: List[ChainNodeList]) -> None:
        self.chains = chains

    def append(self, chain: ChainNodeList):
        """
        新增新的chain到容器中

        如果新增的链与已有的链中前缀没有重复, 增加到链中
        如果已有的链比新增的链短， 则替换为新的
        """
        for i in range(len(self.chains)):
            old_chain = self.chains[i]
            prefix = old_chain.match_prefix(chain)
            if not prefix:
                continue

            # 前缀与已有的chain一样并且新的链长度大于已有的则替换
            if (prefix.length == old_chain.length) and (chain.length > old_chain.length):
                self.chains[i] = chain
                return

            # 如果已有的链能完整的覆盖新增的链则不用替换
            if (prefix.length == chain.length) and chain.length <= old_chain.length:
                return

        # 以上没有匹配的情况下，直接新增
        self.chains.append(chain)

    def match_prefix(self, chain_list: "ChainList") -> Optional["ChainList"]:
        """
        匹配chain的前缀，返回所有结果的集合，并去重
        """
        new_chain_list = ChainList([])
        for target_chain in self.chains:
            for source_chain in chain_list.chains:
                prefix = target_chain.match_prefix(source_chain)
                if not prefix:
                    continue
                new_chain_list.append(prefix)

        return new_chain_list if new_chain_list.length != 0 else None

    @property
    def length(self) -> int:
        return len(self.chains)


class TemplatePolicyCloneBiz:
    """
    模板策略克隆BIZ

    用于模板更新时, 新增操作从已有操作中Clone策略

    1. 生成clone的配置, 匹配目标action与源action视图是否有相同的链路前缀, 如果有则可以从该源action Clone策略数据
    2. 生成clone的策略, 遍历源策略的每个实例路径, 是否能与上一步匹配的链路前缀匹配, 如果可以匹配则该路径Clone
    """

    svc = TemplateService()
    action_svc = ActionService()

    def generate_template_groups_clone_policy(
        self, template: PermTemplate, group_ids: List[str], action_id: str, source_action_id: str, role
    ) -> List[GroupClonePolicy]:
        """
        生成模板更新时用户组的clone Policy
        """
        old_action_ids = template.action_ids
        if source_action_id not in old_action_ids:
            return []

        action_list = self.action_svc.new_action_list(template.system_id)
        config_dict = self._gen_action_clone_config_dict(action_list, [action_id], [source_action_id])

        # 配置不存在
        if action_id not in config_dict or source_action_id not in config_dict[action_id]:
            return []
        chain_list = config_dict[action_id][source_action_id]

        new_action = action_list.get(action_id)
        if new_action is None:
            return []

        scope_check = RoleAuthorizationScopeChecker(role=role)
        authorized_templates = PermTemplatePolicyAuthorized.objects.filter_by_template(template.id).filter(
            subject_type=SubjectType.GROUP.value, subject_id__in=group_ids
        )

        group_policies = []
        for authorized_template in authorized_templates:
            policy_list = PolicyBeanList(
                template.system_id,
                [PolicyBean.parse_obj(one) for one in authorized_template.data["actions"]],
            )
            source_policy = policy_list.get(source_action_id)
            if source_policy is None:
                continue

            policy = self._gen_clone_policy(template.system_id, new_action, source_policy, chain_list, scope_check)
            if not policy:
                continue

            # 填充名称
            clone_policy_list = PolicyBeanList(template.system_id, [policy], need_fill_empty_fields=True)
            group_policies.append(
                GroupClonePolicy(group_id=int(authorized_template.subject_id), policy=clone_policy_list.policies[0])
            )

        return group_policies

    def _gen_clone_policy(
        self,
        system_id: str,
        action: Action,
        source_policy: PolicyBean,
        chain_list: ChainList,
        scope_checker: RoleAuthorizationScopeChecker,
    ) -> Optional[PolicyBean]:
        """
        生成clone的policy
        """
        if len(source_policy.list_thin_resource_type()) != 1:
            return None

        match_paths = []  # 能匹配实例视图前缀的资源路径
        match_path_hash_set = set()  # 用于去重

        for rg in source_policy.resource_groups:
            # NOTE 有环境属性的资源组不能生成
            if len(rg.environments) != 0:
                continue

            for path_list in rg.related_resource_types[0].iter_path_list():
                for chain in chain_list.chains:
                    if not chain.is_match_path(list(path_list)):
                        continue

                    _hash = path_list.to_path_string()
                    if _hash in match_path_hash_set:
                        break

                    match_path_hash_set.add(_hash)
                    match_paths.append(list(path_list))
                    break

        if not match_paths:
            return None

        # 检查role scope, 剔除不在范围的部分
        match_paths = scope_checker.remove_path_outside_scope(system_id, action.id, match_paths)
        if not match_paths:
            return None

        return self._gen_policy_by_paths(action, match_paths)

    def _gen_policy_by_paths(self, action: Action, paths: List[List[PathNodeBean]]) -> PolicyBean:
        """
        生成新的Policy
        """
        instances = group_paths([PathNodeBeanList.parse_obj(one).dict() for one in paths])
        condition = ConditionBean(instances=instances, attributes=[])
        related_resource_types = [
            RelatedResourceBean(system_id=rrt.system_id, type=rrt.id, condition=[condition])
            for rrt in action.related_resource_types
        ]
        return PolicyBean(
            action_id=action.id,
            resource_groups=[ResourceGroupBean(id=gen_uuid(), related_resource_types=related_resource_types)],
        )

    def gen_system_action_clone_config(
        self, system_id: str, new_action_ids: List[str], old_action_ids: List[str]
    ) -> List[ActionCloneConfig]:
        """
        生成系统的操作clone配置
        """
        configs: List[ActionCloneConfig] = []
        action_list = self.action_svc.new_action_list(system_id)
        config_dict = self._gen_action_clone_config_dict(action_list, new_action_ids, old_action_ids)
        for target_action_id, source_action_dict in config_dict.items():
            copy_from_actions = [ThinAction.parse_obj(action_list.get(action_id)) for action_id in source_action_dict]
            configs.append(ActionCloneConfig(action_id=target_action_id, from_actions=copy_from_actions))

        return configs

    def _gen_action_clone_config_dict(
        self, action_list: ActionList, new_action_ids: List[str], old_action_ids: List[str]
    ) -> Dict[str, Dict[str, ChainList]]:
        """
        生成操作数据clone的配置信息

        return: {
            "target_action_id": {
                "source_action_id": prefix_chain_list  # ChainList
            }
        }
        """
        target_actions = action_list.filter(new_action_ids)
        source_actions = action_list.filter(old_action_ids)

        action_config = {}
        for target_action in target_actions:
            source_action_chains = {}
            for source_action in source_actions:
                # 操作的实例视图匹配逻辑
                chian_list = self._gen_action_instance_selection_chain_prefix_list(target_action, source_action)
                if not chian_list:
                    continue

                source_action_chains[source_action.id] = chian_list

            if not source_action_chains:
                continue
            action_config[target_action.id] = source_action_chains

        return action_config

    def _gen_action_instance_selection_chain_prefix_list(
        self, target_action: Action, source_action: Action
    ) -> Optional[ChainList]:
        """
        生成操作的实例视图匹配前缀列表
        """
        # 目标与来源操作如果不关联资源类型, 不匹配
        if len(target_action.related_resource_types) == 0 or len(source_action.related_resource_types) == 0:
            return None

        # 来源操作如果关联多个资源类型, 不匹配
        if len(source_action.related_resource_types) > 1:
            return None

        # 来源操作的实例视图为空, 不匹配
        source_selections = source_action.related_resource_types[0].instance_selections
        if not source_selections:
            return None
        source_chain_list = ChainList(
            [ChainNodeList(selection.resource_type_chain) for selection in source_selections]
        )

        prefix_chain_list = None
        for rrt in target_action.related_resource_types:
            # 目标操作的实例视图为空, 不匹配
            if not rrt.instance_selections:
                return None

            target_chain_list = ChainList(
                [ChainNodeList(selection.resource_type_chain) for selection in rrt.instance_selections]
            )
            chain_list = target_chain_list.match_prefix(source_chain_list)
            if not chain_list:
                return None

            # 如果target_action关联了多个资源类型，取多个资源类型的前缀的交集
            if prefix_chain_list is None:
                prefix_chain_list = chain_list
            else:
                prefix_chain_list = prefix_chain_list.match_prefix(chain_list)

        return prefix_chain_list if prefix_chain_list and prefix_chain_list.length != 0 else None
