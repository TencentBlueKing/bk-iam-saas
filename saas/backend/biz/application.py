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
import time
from collections import defaultdict
from copy import deepcopy
from itertools import groupby
from typing import Any, Dict, List, Optional, Tuple, Type

from django.db import transaction
from django.utils.translation import gettext as _
from pydantic import BaseModel
from pydantic.tools import parse_obj_as
from rest_framework.request import Request

from backend.apps.application.models import Application
from backend.apps.approval.models import ActionProcessRelation
from backend.apps.group.models import Group
from backend.apps.handover.constants import HandoverObjectType, HandoverStatus
from backend.apps.handover.models import HandoverRecord
from backend.apps.handover.tasks import execute_handover_task
from backend.apps.organization.models import User as UserModel
from backend.apps.policy.models import Policy
from backend.apps.role.models import Role, RoleRelatedObject, RoleSource, RoleUser
from backend.apps.role.tasks import sync_subset_manager_subject_scope
from backend.apps.subject_template.models import SubjectTemplate
from backend.apps.template.models import PermTemplatePolicyAuthorized
from backend.audit.audit import log_group_event, log_role_event, log_user_event
from backend.audit.constants import AuditSourceType, AuditType
from backend.biz.constants import StaffStatus
from backend.common.cache import cachedmethod
from backend.common.error_codes import error_codes
from backend.common.lock import gen_permission_handover_lock
from backend.common.time import expired_at_display
from backend.plugins.application_ticket.itsm.ticket_content import HandoverForm
from backend.plugins.application_ticket.itsm.ticket_content_tpl import FORM_SCHEMES
from backend.service.application import ApplicationService
from backend.service.approval import ApprovalProcessService
from backend.service.constants import (
    ApplicationStatus,
    ApplicationType,
    GroupSaaSAttributeEnum,
    RoleRelatedObjectType,
    RoleSourceType,
    RoleType,
    SensitivityLevel,
    SubjectType,
)
from backend.service.models import (
    Applicant,
    ApplicantDepartment,
    ApplicantInfo,
    ApplicationAuthorizationScope,
    ApplicationGroupInfo,
    ApplicationGroupPermTemplate,
    ApplicationPolicyInfo,
    ApplicationSubject,
    ApplicationSystem,
    ApprovalProcess,
    ApprovalProcessNodeWithProcessor,
    ApprovalProcessWithNodeProcessor,
    GradeManagerApplicationContent,
    GradeManagerApplicationData,
    GrantActionApplicationContent,
    GrantActionApplicationData,
    GroupApplicationContent,
    GroupApplicationData,
    HandoverApplicationContent,
    HandoverApplicationData,
    Subject,
)
from backend.service.role import RoleService
from backend.service.system import SystemService

from .application_process import (
    GradeManagerApproverHandler,
    InstanceApproverHandler,
    InstanceApproverMergeHandler,
    PolicyProcess,
    PolicyProcessHandler,
)
from .group import GroupBiz, GroupMemberExpiredAtBean
from .handover import HandoverBiz
from .policy import PolicyBean, PolicyBeanList, PolicyOperationBiz, PolicyQueryBiz
from .role import RoleBiz, RoleInfo, RoleInfoBean
from .subject import SubjectInfoList
from .system import SystemBiz
from .template import TemplateBiz

logger = logging.getLogger("app")


class BaseApplicationDataBean(BaseModel):
    """申请的基本数据"""

    applicant: str
    reason: str


class ActionApplicationDataBean(BaseApplicationDataBean):
    """自定义权限申请或续期"""

    policy_list: PolicyBeanList
    applicants: List[Applicant]

    class Config:
        # 由于PolicyBeanList并非继承于BaseModel，而是普通的类，所以需要声明允许"随意"类型
        arbitrary_types_allowed = True


class ApplicationRenewPolicyInfoBean(BaseModel):
    """自定义权限续期的策略信息"""

    id: int
    expired_at: int


class ApplicationGroupInfoBean(BaseModel):
    """申请用户组的信息"""

    id: int
    # 申请加入用户组的有效期或续期有效期
    expired_at: int


class GroupApplicationDataBean(BaseApplicationDataBean):
    """用户组申请或续期"""

    groups: List[ApplicationGroupInfoBean]
    applicants: List[Applicant]


class GradeManagerApplicationDataBean(BaseApplicationDataBean):
    """分级管理员创建或更新"""

    role_id: int = 0
    role_info: RoleInfo
    group_name: str = ""


class HandoverApplicationDataBean(BaseApplicationDataBean):
    """权限交接审批"""

    handover_to: str
    handover_info: Dict[str, Any]
    # 存储交接详情快照，用于详情页和 ITSM 审批单展示
    handover_detail: Optional[Dict[str, Any]]


class ApplicationIDStatusDict(BaseModel):
    data: Dict[int, ApplicationStatus]

    def get(self, _id: int) -> Optional[ApplicationStatus]:
        return self.data.get(_id)


class ApprovalProcessorBiz:
    """审批流程具体处理人查询
    当前只能查询IAM本身角色，后续需要扩展支持其他的再重新抽象该类
    """

    svc = RoleService()

    @cachedmethod(timeout=60)  # 缓存1分钟
    def get_super_manager_members(self) -> str:
        """获取超级管理员成员员"""
        return Role.objects.get(type=RoleType.SUPER_MANAGER.value).members

    @cachedmethod(timeout=60)  # 缓存1分钟
    def get_system_manager_members(self, system_id: str) -> str:
        """获取系统管理员成员"""
        return Role.objects.get(type=RoleType.SYSTEM_MANAGER.value, code=system_id).members

    @cachedmethod(timeout=60)  # 缓存1分钟
    def get_grade_manager_members_by_group_id(
        self, group_id: int, fallback_to_parent_if_empty: bool = True
    ) -> List[str]:
        """获取分级管理员，如果为空，获取父级管理员"""
        current_role = self.svc.get_role_by_group_id(group_id)

        if fallback_to_parent_if_empty and not current_role.members:
            parent_id = self.svc.get_parent_id(current_role.id)
            return self.svc.list_members_by_role_id(parent_id)

        return current_role.members


class ApprovedPassApplicationBiz:
    """审批通过处理"""

    policy_operation_biz = PolicyOperationBiz()
    group_biz = GroupBiz()
    role_biz = RoleBiz()
    handover_biz = HandoverBiz()

    def _check_subject_exists(self, subject: Subject) -> Tuple[bool, str]:
        """
        检查subject是否在职
        """
        assert subject.type == SubjectType.USER.value  # 只有用户类型的subject才需要检查
        user = UserModel.objects.filter(username=subject.id).first()
        if not user:
            return False, f"user [{subject.id}] not exists"

        if user.staff_status != StaffStatus.IN.value:
            return False, f"user [{subject.id}] staff status [{user.staff_status}]"

        return True, ""

    def _grant_action(
        self, subject: Subject, application: Application, audit_type: str = AuditType.USER_POLICY_CREATE.value
    ):
        """用户自定义权限授权"""
        system_id = application.data["system"]["id"]
        actions = application.data["actions"]
        applicants = (
            application.data["applicants"]
            if "applicants" in application.data
            else [{"type": subject.type, "id": subject.id}]
        )

        for applicant in applicants:
            if applicant["type"] != SubjectType.USER.value:
                logger.warn(
                    "application [%d] grant action approve fail: %s", application.id, f"{subject} type is not user"
                )
                continue

            subject = Subject.parse_obj(applicant)
            ok, msg = self._check_subject_exists(subject)
            if not ok:
                logger.warn("application [%d] grant action approve fail: %s", application.id, msg)
                continue

            policies = parse_obj_as(List[PolicyBean], actions)
            self.policy_operation_biz.alter(system_id=system_id, subject=subject, policies=policies)

            log_user_event(audit_type, subject, system_id, actions, sn=application.sn)

    def _renew_action(self, subject: Subject, application: Application):
        """用户自定义权限续期"""
        ok, msg = self._check_subject_exists(subject)
        if not ok:
            logger.warn("application [%d] renew action approve fail: %s", application.id, msg)
            return

        self._grant_action(subject, application, audit_type=AuditType.USER_POLICY_UPDATE.value)

    def _join_group(self, subject: Subject, application: Application):
        """加入用户组"""
        ok, msg = self._check_subject_exists(subject)
        if not ok:
            logger.warn("application [%d] join group approve fail: %s", application.id, msg)
            return

        applicants = (
            application.data["applicants"]
            if "applicants" in application.data
            else [{"type": subject.type, "id": subject.id}]
        )

        subjects = [Subject.parse_obj(one) for one in applicants]

        qs = Group.objects.filter(id__in=[group["id"] for group in application.data["groups"]]).values_list(
            "id", flat=True
        )
        group_id_set = set(qs)

        # 兼容，新老数据在data都存在expired_at
        default_expired_at = application.data["expired_at"]
        # 加入用户组
        for group in application.data["groups"]:
            if group["id"] not in group_id_set:
                continue

            # 新数据才有，老数据则使用data外层的expired_at
            expired_at = group.get("expired_at", default_expired_at)
            try:
                self.group_biz.add_members(group["id"], subjects, expired_at)
            except Group.DoesNotExist:
                # 若审批通过时，用户组已经被删除，则直接忽略
                logger.error(
                    f"subject {subject} join group({group['id']}) fail! "
                    "the group has been deleted before the application is approved"
                )

        log_group_event(
            AuditType.GROUP_MEMBER_CREATE.value,
            subject,
            [one["id"] for one in application.data["groups"]],
            sn=application.sn,
        )

    def _renew_group(self, subject: Subject, application: Application):
        """用户组续期"""
        groups = application.data["groups"]
        qs = Group.objects.filter(id__in=[group["id"] for group in groups]).values_list("id", flat=True)
        group_id_set = set(qs)

        applicants = (
            application.data["applicants"]
            if "applicants" in application.data
            else [{"type": subject.type, "id": subject.id}]
        )

        subjects = [Subject.parse_obj(one) for one in applicants]

        for group in groups:
            if group["id"] not in group_id_set:
                logger.error(
                    f"subject {subject} renew group({group['id']}) fail! "
                    "the group has been deleted before the application is approved"
                )
                continue

            self.group_biz.update_members_expired_at(
                group["id"],
                [
                    GroupMemberExpiredAtBean(type=subject.type, id=subject.id, expired_at=group["expired_at"])
                    for subject in subjects
                ],
            )

        log_group_event(
            AuditType.GROUP_MEMBER_RENEW.value,
            subject,
            [one["id"] for one in application.data["groups"]],
            sn=application.sn,
        )

    def _gen_role_info_bean(
        self, data: Dict[Any, Any], source_system_id: str = "", hidden: bool = False
    ) -> RoleInfoBean:
        """处理分级管理员数据"""
        # 兼容新老数据
        auth_scopes = data["authorization_scopes"]
        for scope in auth_scopes:
            # 新数据是system，没有system_id
            if "system_id" not in scope:
                scope["system_id"] = scope["system"]["id"]

        data["members"] = [{"username": username} for username in data["members"]]
        return RoleInfoBean(source_system_id=source_system_id, hidden=hidden, **data)

    def _create_rating_manager(self, subject: Subject, application: Application):
        """创建分级管理员"""
        info = self._gen_role_info_bean(
            application.data, source_system_id=application.source_system_id, hidden=application.hidden
        )
        with transaction.atomic():
            role = self.role_biz.create_grade_manager(info, subject.id)

            # 创建同步权限用户组
            if info.sync_perm:
                attrs = {
                    GroupSaaSAttributeEnum.SOURCE_FROM_ROLE.value: True,
                }
                if application.source_system_id:
                    attrs[GroupSaaSAttributeEnum.SOURCE_TYPE.value] = AuditSourceType.OPENAPI.value

                self.group_biz.create_sync_perm_group_by_role(
                    role,
                    application.applicant,
                    group_name=application.data.get("group_name", ""),
                    attrs=attrs,
                    sync_subject_template=info.sync_subject_template,
                )

            if application.source_system_id:
                # 记录role创建来源信息
                RoleSource.objects.create(
                    role_id=role.id,
                    source_type=RoleSourceType.API.value,
                    source_system_id=application.source_system_id,
                )

        log_role_event(AuditType.ROLE_CREATE.value, subject, role, sn=application.sn)

        return role

    @transaction.atomic
    def _update_rating_manager(self, subject: Subject, application: Application):
        """更新分级管理员"""
        role = Role.objects.get(type=RoleType.GRADE_MANAGER.value, id=application.data["id"])
        info = self._gen_role_info_bean(application.data)
        self.role_biz.update(role, info, subject.id)

        if role.type == RoleType.GRADE_MANAGER.value and "subject_scopes" in info.get_partial_fields():
            transaction.on_commit(lambda: sync_subset_manager_subject_scope.delay(role.id))

        role = Role.objects.get(id=role.id)
        # 更新同步权限用户组信息
        self.group_biz.update_sync_perm_group_by_role(
            role,
            application.applicant,
            sync_members=True,
            sync_prem=True,
            group_name=application.data.get("group_name", ""),
        )

        log_role_event(
            AuditType.ROLE_UPDATE.value,
            subject,
            role,
            extra={"name": info.name, "description": info.description},
            sn=application.sn,
        )

        return role

    def _grant_temporary_action(self, subject: Subject, application: Application):
        """临时权限授权"""
        ok, msg = self._check_subject_exists(subject)
        if not ok:
            logger.warn("application [%d] grant temporary action approve fail: %s", application.id, msg)
            return

        system_id = application.data["system"]["id"]
        actions = application.data["actions"]

        self.policy_operation_biz.create_temporary_policies(
            system_id=system_id, subject=subject, policies=parse_obj_as(List[PolicyBean], actions)
        )

        log_user_event(AuditType.USER_TEMPORARY_POLICY_CREATE.value, subject, system_id, actions, sn=application.sn)

    def _filter_handover_info(
        self, handover_from: str, handover_info: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], List[str]]:
        """
        审批回调时检查每种类型的交接数据是否仍然有效，移除无效数据并收集警告信息
        """
        filtered_info: Dict[str, Any] = {}
        warnings: List[str] = []
        now_ts = int(time.time())

        # 过滤 group_ids：检查用户是否仍在组中（且未过期）
        group_ids = handover_info.get("group_ids", [])
        if group_ids:
            subject = Subject.from_username(handover_from)
            subject_groups = GroupBiz().list_all_subject_group(subject)
            # 只保留未过期的组
            subject_group_id_set = {g.id: g.name for g in subject_groups if g.expired_at > now_ts}
            valid_group_ids = [gid for gid in group_ids if gid in subject_group_id_set]
            removed = set(group_ids) - set(valid_group_ids)
            if removed:
                all_group_map = {g.id: g.name for g in subject_groups}
                group_names = ", ".join([all_group_map.get(gid, f"ID:{gid}") for gid in removed])
                warnings.append(f"用户已不在用户组 {group_names} 中或已过期，已跳过")
            filtered_info["group_ids"] = valid_group_ids

        # 过滤 custom_policies：检查策略是否仍然存在（且未过期）
        custom_policies = handover_info.get("custom_policies", [])
        if custom_policies:
            filtered_policies = []
            for cp in custom_policies:
                system_id = cp["system_id"]
                policy_ids = cp["policy_ids"]
                subject = Subject.from_username(handover_from)
                policies = PolicyQueryBiz().list_by_subject(system_id, subject)
                # 只保留未过期的策略
                subject_policy_id_set = {p.policy_id: p.action_id for p in policies if not p.is_expired()}
                valid_policy_ids = [pid for pid in policy_ids if pid in subject_policy_id_set]
                removed = set(policy_ids) - set(valid_policy_ids)
                if removed:
                    all_policy_map = {p.policy_id: p.action_id for p in policies}
                    policy_names = ", ".join([all_policy_map.get(pid, f"policy_id:{pid}") for pid in removed])
                    warnings.append(f"系统 {system_id} 的策略 {policy_names} 已不存在或已过期，已跳过")
                if valid_policy_ids:
                    filtered_policies.append({"system_id": system_id, "policy_ids": valid_policy_ids})
            filtered_info["custom_policies"] = filtered_policies

        # 过滤 role_ids：检查用户是否拥有该角色
        role_ids = handover_info.get("role_ids", [])
        if role_ids:
            valid_role_ids = []
            # 一次性查询所有相关角色名称
            roles = Role.objects.filter(id__in=role_ids).values("id", "name")
            role_map = {r["id"]: r["name"] for r in roles}
            for rid in role_ids:
                if RoleUser.objects.user_role_exists(handover_from, rid):
                    valid_role_ids.append(rid)
                else:
                    role_name = role_map.get(rid, f"ID:{rid}")
                    warnings.append(f"角色 {role_name} 不在当前用户的可交接范围内，已跳过")
            filtered_info["role_ids"] = valid_role_ids

        return filtered_info, warnings

    def _handover(self, subject: Subject, application: Application):
        """权限交接审批通过处理"""

        app_data = application.data or {}
        handover_from: str = app_data.get("handover_from") or ""
        handover_to: str = app_data.get("handover_to") or ""
        handover_info: Dict[str, Any] = app_data.get("handover_info") or {}
        reason = application.reason

        if not handover_from or not handover_to:
            logger.error(
                "application [%d] handover content invalid: missing handover_from or handover_to", application.id
            )
            return

        # 检查接收人是否在职
        handover_to_subject = Subject.from_username(handover_to)
        ok, msg = self._check_subject_exists(handover_to_subject)
        if not ok:
            logger.warn("application [%d] handover approve fail: %s", application.id, msg)
            return

        # 过滤无效的交接数据，收集 warnings
        filtered_handover_info, warnings = self._filter_handover_info(handover_from, handover_info)
        if warnings:
            app_data["handover_warnings"] = warnings
            Application.objects.filter(id=application.id).update(_data=json.dumps(app_data))

        # 创建交接记录
        handover_record = self.handover_biz.create_handover_record(
            handover_from, handover_to, reason, filtered_handover_info
        )
        # 事务提交后再启动异步任务, 避免 delay 比事务提交更快导致查不到 HandoverTask
        execute_handover_task.delay(
            handover_from=handover_from,
            handover_to=handover_to,
            handover_record_id=handover_record.id,
        )

    def handle(self, application: Application):
        """审批通过处理"""
        func_name = f"_{application.type}"
        handle_func = getattr(self, func_name)

        subject = Subject.from_username(application.applicant)
        return handle_func(subject, application)


class ApplicationBiz:
    svc = ApplicationService()
    system_svc = SystemService()
    approval_process_svc = ApprovalProcessService()
    approval_processor_biz = ApprovalProcessorBiz()
    approved_pass_biz = ApprovedPassApplicationBiz()

    policy_biz = PolicyQueryBiz()
    template_biz = TemplateBiz()

    def _get_approval_process_with_node_processor(
        self, process: ApprovalProcess, **kwargs
    ) -> ApprovalProcessWithNodeProcessor:
        """获取审批流程并附带每个流程节点的实际处理人
        kwargs: 可能有system_id、group_id
        由于不同流程节点的查询具体处理人时是依赖申请内容的
        比如申请不同用户组，其分级管理员成员可能是不一样的，同样申请不同系统的权限，其系统管理员成员也不一样
        """
        nodes = self.approval_process_svc.get_process_nodes(process.id)
        # 1. 遍历每个节点，对IAM的角色进行查询对应的具体处理人
        nodes_with_processor = []
        for node in nodes:
            node_with_processor = parse_obj_as(ApprovalProcessNodeWithProcessor, node)
            # 非IAM来源，则不需要IAM关注
            if not node.is_iam_source():
                nodes_with_processor.append(node_with_processor)
                continue

            # 对于来着IAM的角色，则需要查询对应角色的成员
            processors = []
            if node.processor_type == RoleType.SUPER_MANAGER.value:
                processors = self.approval_processor_biz.get_super_manager_members()
            elif node.processor_type == RoleType.SYSTEM_MANAGER.value:
                processors = self.approval_processor_biz.get_system_manager_members(system_id=kwargs["system_id"])
            elif node.processor_type == RoleType.GRADE_MANAGER.value:
                # 如果是自定义权限, 需要后续流程中填充审批人
                if "group_id" in kwargs:
                    processors = self.approval_processor_biz.get_grade_manager_members_by_group_id(
                        group_id=kwargs["group_id"]
                    )
            # NOTE: 由于资源实例审批人节点的逻辑涉及到复杂的拆分, 合并逻辑, 不在这里处理

            node_with_processor.processors = processors
            nodes_with_processor.append(node_with_processor)

        # 组装出流程带节点及其节点具体处理人数据
        process_with_node_processor = parse_obj_as(ApprovalProcessWithNodeProcessor, process)
        process_with_node_processor.nodes = nodes_with_processor

        return process_with_node_processor

    def _merge_application_by_approval_process(
        self, process_dict: Dict[Any, ApprovalProcessWithNodeProcessor]
    ) -> Dict[ApprovalProcessWithNodeProcessor, List]:
        """通过审批流程，合并申请单"""
        merge_process_dict = defaultdict(list)
        for obj, process in process_dict.items():
            merge_process_dict[process].append(obj)
        return merge_process_dict

    def _get_applicant_info(self, applicant: str) -> ApplicantInfo:
        """获取申请者相关信息"""
        # 查询用户的部门信息
        user = UserModel.objects.filter(username=applicant).first()
        if not user:
            raise error_codes.INVALID_ARGS.format(f"user: {applicant} not exists")

        departments = user.departments
        applicant_departments = [
            ApplicantDepartment(id=dept.id, name=dept.name, full_name=dept.full_name) for dept in departments
        ]

        return ApplicantInfo(username=applicant, organization=applicant_departments)

    @cachedmethod(timeout=60)  # 缓存1分钟
    def _gen_application_system(self, system_id: str) -> ApplicationSystem:
        """生成申请的系统信息"""
        system = self.system_svc.get(system_id)
        return parse_obj_as(ApplicationSystem, system)

    def create_for_policy(
        self,
        application_type: ApplicationType,
        data: ActionApplicationDataBean,
        content_template: Optional[Dict[str, Any]] = None,
        policy_contents: Optional[List[Tuple[PolicyBean, Any]]] = None,
        title_prefix: str = "",
    ) -> List[Application]:
        """自定义权限"""
        # 1. 提前查询部分信息
        # (1) 对Policy里相关Name进行填充 => 调用Service层接口需要"完整"数据，用于Ticket创建和展示
        policy_list = data.policy_list
        policy_list.fill_empty_fields()
        # (2) 查询申请者信息
        applicant_info = self._get_applicant_info(data.applicant)
        # (3) 查询系统信息
        system_id = data.policy_list.system_id
        system_info = self._gen_application_system(system_id)

        # 3. 查询每个操作对应的流程
        action_ids = [p.action_id for p in policy_list.policies]
        action_processes = self.approval_process_svc.list_action_process(system_id=system_id, action_ids=action_ids)

        # 4. 生成policy - process对象列表
        policy_process_list = []
        for action_process in action_processes:
            process = self._get_approval_process_with_node_processor(action_process.process, system_id=system_id)
            policy = policy_list.get(action_process.action_id)

            policy_process_list.append(PolicyProcess(policy=policy, process=process))

        # 5. 通过管道填充可能的资源实例审批人/分级管理员审批节点的审批人
        pipeline: List[Type[PolicyProcessHandler]] = [
            InstanceApproverMergeHandler,
            InstanceApproverHandler,
            GradeManagerApproverHandler,
        ]
        for pipe in pipeline:
            policy_process_list = pipe(system_id).handle(policy_process_list)

        # 6. 依据审批流程合并策略
        policy_list_process = self._merge_policies_by_approval_process(system_id, policy_process_list)

        # 7. 根据合并的单据，组装出调用Service层创建单据所需数据
        new_data_list = []
        for policy_list, process in policy_list_process:
            # 组装申请数据
            application_data = GrantActionApplicationData(
                type=application_type,
                applicant_info=applicant_info,
                reason=data.reason,
                content=GrantActionApplicationContent(
                    system=system_info,
                    policies=parse_obj_as(List[ApplicationPolicyInfo], policy_list.policies),
                    applicants=data.applicants,
                ),
            )

            # 组装外部传入的 itsm 单据数据
            content: Optional[Dict[str, Any]] = None
            if content_template and policy_contents:
                content = deepcopy(content_template)
                policy_form_value = [c for p, c in policy_contents if policy_list.contains_policy(p)]
                for c in content["form_data"]:
                    if (
                        isinstance(c, dict)
                        and c.get("scheme") == "policy_table_scheme"
                        and isinstance(c.get("value"), list)
                    ):
                        c["value"] = policy_form_value

            new_data_list.append((application_data, process, content))

        # 8. 循环创建申请单
        applications = []
        for _data, _process, _content in new_data_list:
            application = self.svc.create_for_policy(
                _data,
                _process,
                approval_content=_content,
                approval_title_prefix=title_prefix,
            )
            applications.append(application)

        return applications

    def _merge_policies_by_approval_process(
        self, system_id, policy_process_list: List[PolicyProcess]
    ) -> List[Tuple[PolicyBeanList, ApprovalProcessWithNodeProcessor]]:
        """聚合审批流程相同的策略"""
        # 聚合相同流程所有的polices
        merge_process_dict = defaultdict(list)
        for policy_process in policy_process_list:
            merge_process_dict[policy_process.process].append(policy_process.policy)

        policy_list_process = []
        # 流程相同的策略中, 合并action_id一样的策略
        for _process, _policies in merge_process_dict.items():
            policy_list = PolicyBeanList(system_id, [])
            for p in _policies:
                policy_list.add(PolicyBeanList(system_id, [p]))

            policy_list_process.append((policy_list, _process))

        return policy_list_process

    def create_for_renew_policy(
        self, policy_infos: List[ApplicationRenewPolicyInfoBean], applicant: str, reason: str
    ) -> List[Application]:
        """自定义权限续期"""
        subject = Subject.from_username(applicant)
        policy_expired_at_dict = {p.id: p.expired_at for p in policy_infos}

        # 查询策略所属系统
        db_policies = (
            # TODO: 已存在的申请单数据如何处理？policy_id的含义已经变化了
            Policy.objects.filter(
                subject_type=subject.type, subject_id=subject.id, id__in=[p.id for p in policy_infos]
            )
            .defer("_resources")
            .order_by("system_id")
        )

        # 转换为ApplicationBiz创建申请单所需数据结构
        user = UserModel.objects.get(username=applicant)

        # 按系统分组
        data_list = []
        for system_id, policies in groupby(db_policies, lambda p: p.system_id):
            policy_list = self.policy_biz.query_policy_list_by_policy_ids(system_id, subject, [p.id for p in policies])

            # 由于是续期，所以需要修改续期时间
            for p in policy_list.policies:
                p.set_expired_at(policy_expired_at_dict[p.policy_id])

            data_list.append(
                ActionApplicationDataBean(
                    applicant=applicant,
                    policy_list=policy_list,
                    applicants=[
                        Applicant(type=SubjectType.USER.value, id=user.username, display_name=user.display_name)
                    ],
                    reason=reason,
                )
            )

        # 循环创建申请单
        applications = []
        for data in data_list:
            applications.extend(self.create_for_policy(ApplicationType.RENEW_ACTION.value, data))

        return applications

    def _gen_group_permission_data(self, group_id: int) -> List[ApplicationGroupPermTemplate]:
        """生成用户组权限数据"""
        subject = Subject.from_group_id(group_id)

        application_templates = []

        # 查询自定义权限 涉及的系统
        system_counter_list = self.policy_biz.list_system_counter_by_subject(subject, hidden=False)
        # 查询自定义权限
        for system_counter in system_counter_list:
            policies = self.policy_biz.list_by_subject(system_counter.id, subject)
            application_templates.append(
                ApplicationGroupPermTemplate(
                    id=0,
                    name="自定义权限",
                    system=parse_obj_as(ApplicationSystem, system_counter),
                    policies=parse_obj_as(List[ApplicationPolicyInfo], policies),
                )
            )

        # 查询用户组权限模板权限
        authorized_query_set = PermTemplatePolicyAuthorized.objects.filter_by_subject(subject)
        # 查询模板名称
        template_ids = list(authorized_query_set.values_list("template_id", flat=True))
        template_name_dict = self.template_biz.get_template_name_dict_by_ids(template_ids)
        # 循环组织权限模板数据
        for authorized in authorized_query_set:
            policy_list = PolicyBeanList(
                system_id=authorized.system_id,
                policies=parse_obj_as(List[PolicyBean], authorized.data["actions"]),
                need_fill_empty_fields=True,
            )
            application_templates.append(
                ApplicationGroupPermTemplate(
                    id=authorized.template_id,
                    name=template_name_dict.get(authorized.template_id),
                    system=self._gen_application_system(authorized.system_id),
                    policies=parse_obj_as(List[ApplicationPolicyInfo], policy_list.policies),
                )
            )

        return application_templates

    def _gen_group_application_content(
        self, group_infos: List[ApplicationGroupInfoBean], applicants: List[Applicant]
    ) -> GroupApplicationContent:
        """生成用户组单据所需内容"""
        # 1. 用户组基本信息
        groups = Group.objects.filter(id__in=[g.id for g in group_infos])
        group_expired_at_dict = {g.id: g.expired_at for g in group_infos}
        # 2. 查询用户组所属的管理员
        q = RoleRelatedObject.objects.filter(
            object_type=RoleRelatedObjectType.GROUP.value, object_id__in=[g.id for g in group_infos]
        ).values("role_id", "object_id")
        group_role = {one["object_id"]: one["role_id"] for one in q}
        role_name = {}

        if group_role:
            q = Role.objects.filter(id__in=group_role.values()).values("id", "name")
            role_name = {one["id"]: one["name"] for one in q}

        # 3. 组装用户组相关数据
        group_infos = [
            ApplicationGroupInfo(
                id=group.id,
                name=group.name,
                description=group.description,
                expired_at=group_expired_at_dict[group.id],
                expired_display=expired_at_display(group_expired_at_dict[group.id]),
                templates=self._gen_group_permission_data(group.id),
                role_name=role_name.get(group_role.get(group.id, 0), ""),
            )
            for group in groups
        ]

        return GroupApplicationContent(groups=group_infos, applicants=applicants)

    def create_for_group(
        self,
        application_type: ApplicationType,
        data: GroupApplicationDataBean,
        source_system_id: str = "",
        content_template: Optional[Dict[str, Any]] = None,
        group_content: Optional[Dict[str, Any]] = None,
        title_prefix: str = "",
    ) -> List[Application]:
        """申请加入用户组"""
        # 1. 查询申请者信息
        applicant_info = self._get_applicant_info(data.applicant)

        # 2. 查询每个用户组的审批流程
        group_processes = self.approval_process_svc.list_group_process([g.id for g in data.groups])

        # 3. 实例化每个流程
        group_process_dict = {}
        for group_process in group_processes:
            process = self._get_approval_process_with_node_processor(
                group_process.process, group_id=group_process.group_id
            )
            group_process_dict[group_process.group_id] = process

        # 4. 合并单据
        merge_process_dict = self._merge_application_by_approval_process(group_process_dict)

        # 5. 根据合并的单据，组装出调用Service层创建单据所需数据
        new_data_list = []
        for process, group_ids in merge_process_dict.items():
            # 组装申请数据
            application_data = GroupApplicationData(
                type=application_type,
                applicant_info=applicant_info,
                reason=data.reason,
                content=self._gen_group_application_content(
                    [g for g in data.groups if g.id in group_ids], data.applicants
                ),
            )

            # 组装外部传入的itsm单据数据
            content: Optional[Dict[str, Any]] = None
            if content_template and group_content:
                content = deepcopy(content_template)
                content["form_data"][0]["value"] = [group_content[str(_id)] for _id in group_ids]

            new_data_list.append((application_data, process, content))

        # 7. 循环创建申请单
        applications = []
        for _data, _process, _content in new_data_list:
            application = self.svc.create_for_group(
                _data,
                _process,
                source_system_id=source_system_id,
                approval_content=_content,
                approval_title_prefix=title_prefix,
            )
            applications.append(application)

        return applications

    def _gen_grade_manager_application_content(
        self, role_info: RoleInfo, role_id: int, group_name: str = ""
    ) -> GradeManagerApplicationContent:
        """生成申请单据所需内容"""
        # 成员需要显示名称
        members = SubjectInfoList(Subject.from_usernames(role_info.member_usernames))
        # 授权成员范围，查询相关信息
        subject_scopes = SubjectInfoList(role_info.subject_scopes)

        # 授权范围
        authorization_scopes = []
        for scope in role_info.authorization_scopes:
            system = self._gen_application_system(scope.system_id)
            policy_list = PolicyBeanList(
                system_id=scope.system_id,
                policies=parse_obj_as(List[PolicyBean], scope.actions),
                need_fill_empty_fields=True,
            )
            authorization_scopes.append(ApplicationAuthorizationScope(system=system, policies=policy_list.policies))

        return GradeManagerApplicationContent(
            id=role_id,
            name=role_info.name,
            description=role_info.description,
            members=parse_obj_as(List[ApplicationSubject], members.subjects),
            subject_scopes=parse_obj_as(List[ApplicationSubject], subject_scopes.subjects),
            authorization_scopes=authorization_scopes,
            sync_perm=role_info.sync_perm,
            group_name=group_name,
        )

    def create_for_grade_manager(
        self,
        application_type: ApplicationType,
        data: GradeManagerApplicationDataBean,
        source_system_id: str = "",
        callback_id: str = "",
        callback_url: str = "",
        approval_title: str = "",
        approval_content: Optional[Dict] = None,
    ) -> List[Application]:
        """分级管理员"""
        # 1. 查询申请者信息
        applicant_info = self._get_applicant_info(data.applicant)

        # 2. 查询对应的审批流程(所有分级管理员的申请都使用同一个流程)
        grade_manager_process = self.approval_process_svc.get_default_process(
            ApplicationType.CREATE_GRADE_MANAGER.value
        )

        # 3. 实例化流程
        process = self._get_approval_process_with_node_processor(grade_manager_process.process)

        # 4. 组装数据并创建单据
        application = self.svc.create_for_grade_manager(
            GradeManagerApplicationData(
                type=application_type,
                applicant_info=applicant_info,
                reason=data.reason,
                content=self._gen_grade_manager_application_content(
                    data.role_info, data.role_id, group_name=data.group_name
                ),
            ),
            process,
            source_system_id=source_system_id,
            callback_id=callback_id,
            callback_url=callback_url,
            approval_title=approval_title,
            approval_content=approval_content,
        )

        return [application]

    def get_handover_detailed_info(self, handover_from: str, handover_info: Dict[str, Any]) -> Dict[str, Any]:
        """获取权限交接审批单的详细展示数据

        供 ITSM 表单渲染、详情页展示等场景共用
        """
        detailed_info = {}

        for key, value in handover_info.items():
            if not value:
                continue

            if key == HandoverObjectType.GROUP_IDS.value:
                detailed_info[key] = self._get_group_detailed_info(handover_from, value)
            elif key == HandoverObjectType.CUSTOM_POLICIES.value:
                detailed_info[key] = self._get_custom_policies_detailed_info(handover_from, value)
            elif key == HandoverObjectType.ROLE_IDS.value:
                # value 是 role_ids 列表
                roles = Role.objects.filter(id__in=value)
                detailed_info[key] = [
                    {
                        "id": role.id,
                        "type": role.type,
                        "name": role.name,
                        "name_en": role.name_en,
                        "description": role.description,
                    }
                    for role in roles
                ]
            elif key == HandoverObjectType.SUBJECT_TEMPLATE_IDS.value:
                # value 是 subject_template_ids 列表
                templates = SubjectTemplate.objects.filter(id__in=value)
                detailed_info[key] = [{"id": t.id, "name": t.name, "description": t.description} for t in templates]

        return detailed_info

    def _get_group_detailed_info(self, handover_from: str, group_ids: List[int]) -> List[Dict[str, Any]]:
        """获取用户组的详细展示数据（含过期时间、所属管理空间、最高敏感等级）"""
        groups = Group.objects.filter(id__in=group_ids)

        # 获取用户的用户组及过期时间
        subject = Subject.from_username(handover_from)
        subject_groups = GroupBiz().list_all_subject_group(subject)
        group_expired_at = {g.id: g.expired_at for g in subject_groups}

        # 查询用户组所属的管理空间名称
        group_role_map = {
            one["object_id"]: one["role_id"]
            for one in RoleRelatedObject.objects.filter(
                object_type=RoleRelatedObjectType.GROUP.value, object_id__in=group_ids
            ).values("role_id", "object_id")
        }
        role_name_map: Dict[int, str] = {}
        if group_role_map:
            role_name_map = {
                one["id"]: one["name"]
                for one in Role.objects.filter(id__in=set(group_role_map.values())).values("id", "name")
            }

        # 查询每个用户组的最高敏感等级
        highest_sensitivity_level_map = self._get_groups_highest_sensitivity_level(group_ids)

        return [
            {
                "id": group.id,
                "name": group.name,
                "description": group.description,
                "expired_at": group_expired_at.get(group.id),
                "role_name": role_name_map.get(group_role_map.get(group.id, 0), ""),
                "highest_sensitivity_level": highest_sensitivity_level_map.get(group.id, SensitivityLevel.L1.value),
            }
            for group in groups
        ]

    def _get_custom_policies_detailed_info(
        self, handover_from: str, system_policies_list: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """获取自定义权限的详细展示数据（含系统信息、策略详情，支持回退到原始数据）"""
        system_biz = SystemBiz()
        system_list = system_biz.new_system_list()
        query_biz = PolicyQueryBiz()
        subject = Subject.from_username(handover_from)

        result = []
        for system_policy in system_policies_list:
            sys = system_list.get(system_policy["system_id"])

            # 获取策略详情
            # Note: 不过滤过期策略，因为展示详情时需要显示申请时的数据
            application_policies: List[Dict[str, Any]] = []
            if system_policy["policy_ids"]:
                policies = query_biz.list_by_subject(system_policy["system_id"], subject)
                policy_map = {p.policy_id: p for p in policies}
                hit_policies = [policy_map[pid] for pid in system_policy["policy_ids"] if pid in policy_map]
                if hit_policies:
                    application_policies = [
                        p.dict(by_alias=True) for p in parse_obj_as(List[ApplicationPolicyInfo], hit_policies)
                    ]

            # 如果重新查询失败（策略已删除或过期），回退使用原始存储的 policies
            if not application_policies and system_policy.get("policies"):
                application_policies = system_policy["policies"]

            result.append(
                {
                    "id": system_policy["system_id"],
                    "policy_ids": system_policy["policy_ids"],
                    "name": sys.name if sys else "",
                    "name_en": sys.name_en if sys else "",
                    "policies": application_policies,
                }
            )

        return result

    @staticmethod
    def _get_groups_highest_sensitivity_level(group_ids: List[int]) -> Dict[int, str]:
        """计算用户组的最高敏感等级

        取每个用户组下所有自定义权限策略的最高敏感等级
        """
        if not group_ids:
            return {}

        # 1. 查询所有用户组的 (system_id, action_id) 关系
        group_actions = list(
            Policy.objects.filter(
                subject_type=SubjectType.GROUP.value,
                subject_id__in=[str(gid) for gid in group_ids],
            ).values("subject_id", "system_id", "action_id")
        )
        if not group_actions:
            return {gid: SensitivityLevel.L1.value for gid in group_ids}

        # 2. 查询所涉及系统的 (system_id, action_id) -> sensitivity_level 映射
        involved_systems = {ga["system_id"] for ga in group_actions}
        sensitivity_map = {
            (rel["system_id"], rel["action_id"]): rel["sensitivity_level"]
            for rel in ActionProcessRelation.objects.filter(system_id__in=involved_systems).values(
                "system_id", "action_id", "sensitivity_level"
            )
        }

        # 3. 聚合每个用户组的最高敏感等级
        group_levels: Dict[int, List[str]] = defaultdict(list)
        for ga in group_actions:
            level = sensitivity_map.get((ga["system_id"], ga["action_id"]), SensitivityLevel.L1.value)
            group_levels[int(ga["subject_id"])].append(level)

        return {
            gid: (max(group_levels[gid]) if group_levels.get(gid) else SensitivityLevel.L1.value) for gid in group_ids
        }

    def create_handover_with_approval(self, data: HandoverApplicationDataBean) -> Dict:
        """开启审批开关：走 ITSM 审批

        将创建审批单的逻辑从 HandoverBiz 迁移到 ApplicationBiz，
        使审批逻辑与交接执行逻辑解耦
        """
        handover_from = data.applicant

        # 1. 用户级分布式锁
        user_lock_key = handover_from
        user_lock = gen_permission_handover_lock(user_lock_key)
        if not user_lock.acquire():
            raise error_codes.TASK_EXIST.format(message="存在正在处理的交接申请，请勿重复提交")

        try:
            # 2. 检查有无 PENDING 的审批单
            if Application.objects.filter(
                applicant=handover_from,
                type=ApplicationType.HANDOVER.value,
                status=ApplicationStatus.PENDING.value,
            ).exists():
                raise error_codes.TASK_EXIST.format(message="存在审批中的交接申请，请勿重复提交")

            # 3. 检查有无 RUNNING 的交接任务
            if HandoverRecord.objects.filter(
                handover_from=handover_from, status=HandoverStatus.RUNNING.value
            ).exists():
                raise error_codes.TASK_EXIST.format(message="存在正在执行的交接任务，请勿重复提交")

            # 4. 查询详细数据用于表单渲染和快照存储
            handover_detail = self.get_handover_detailed_info(handover_from, data.handover_info)
            data.handover_detail = handover_detail

            # 5. 创建审批单
            application = self.create_for_handover(data)
        finally:
            # 释放用户级分布式锁
            user_lock.release()

        return {
            "application_id": application.id,
            "approval_sn": application.sn,
            "status": ApplicationStatus.PENDING.value,
        }

    def _gen_handover_approval_content(self, content: HandoverApplicationContent) -> Dict[str, Any]:
        """生成权限交接审批单的展示数据

        Args:
            content: HandoverApplicationContent 实例，包含 handover_detail 用于展示
        """
        # 返回 ITSM 期望的格式
        return {
            "schemes": FORM_SCHEMES,
            "form_data": HandoverForm.from_application(content).form_data,
        }

    def create_for_handover(
        self,
        data: HandoverApplicationDataBean,
    ) -> Application:
        """创建权限交接审批单据"""
        # 1. 查询申请者信息
        applicant_info = self._get_applicant_info(data.applicant)

        # 2. 查询对应的审批流程
        handover_process = self.approval_process_svc.get_default_process(ApplicationType.HANDOVER.value)

        # 3. 实例化流程
        process = self._get_approval_process_with_node_processor(handover_process.process)

        # 4. 组装数据并创建单据
        application_data = HandoverApplicationData(
            type=ApplicationType.HANDOVER,
            applicant_info=applicant_info,
            reason=data.reason,
            content=HandoverApplicationContent(
                handover_from=data.applicant,
                handover_to=data.handover_to,
                handover_info=data.handover_info,  # 存储交接数据(纯ID)
                handover_detail=data.handover_detail,  # 存储详情快照
            ),
        )

        # 5. 生成 ITSM 表单数据
        approval_content = self._gen_handover_approval_content(application_data.content)

        application = self.svc.create_for_handover(application_data, process, approval_content=approval_content)

        return application

    def handle_application_result(self, application: Application, status: ApplicationStatus):
        """处理审批单据结果"""
        # 若还在审批中，则忽略
        if status == ApplicationStatus.PENDING.value:
            return

        # 已处理的单据不需要继续处理
        if application.status != ApplicationStatus.PENDING.value:
            return

        # 对于非审批中，都需要将单据状态更新保存
        # Note: 由于application里的data字段较大，使用save更新时相当所有字段都更新，所以需指定status字段更新
        application.status = status
        application.save(update_fields=["status", "updated_time"])

        try:
            # 审批通过，则执行相关授权等
            if status == ApplicationStatus.PASS.value:
                return self.approved_pass_biz.handle(application)
        except Exception as e:  # pylint: disable=broad-except
            # NOTE: 由于以上执行过程中会记录审计信息, 如果发生异常, 事务不能正常回滚, 所以这里手动回滚下
            application.status = ApplicationStatus.PENDING.value
            application.save(update_fields=["status", "updated_time"])
            raise e

    def handle_approval_callback_request(self, callback_id: str, request: Request):
        """处理审批回调请求"""
        # 获取审批回调处理的单据，包括单据号和单据状态
        ticket = self.svc.get_approval_ticket_from_callback_request(request)

        try:
            application = Application.objects.get(sn=ticket.sn, callback_id=callback_id)
        except Application.DoesNotExist:
            raise error_codes.NOT_FOUND_ERROR

        # 处理申请单结果
        return self.handle_application_result(application, ticket.status)

    def query_application_approval_status(self, applications: List[Application]) -> ApplicationIDStatusDict:
        """查询申请单审批状态"""
        sn_id_dict = {a.sn: a.id for a in applications}
        tickets = self.svc.query_ticket_approval_status(list(sn_id_dict.keys()))

        return ApplicationIDStatusDict(data={sn_id_dict[t.sn]: t.status for t in tickets})

    def cancel_application(self, application: Application, operator: str, need_cancel_ticket: bool = True):
        """撤销申请单"""
        if application.applicant != operator:
            raise error_codes.INVALID_ARGS.format(_("只有申请人能取消"))  # 只能取消自己的申请单

        if need_cancel_ticket:
            # 撤销单据
            self.svc.cancel_ticket(application.sn, application.applicant)

        # 更新状态
        self.handle_application_result(application, ApplicationStatus.CANCELLED.value)

    def get_approval_url(self, application: Application) -> str:
        """查询审批URL"""
        ticket = self.svc.get_ticket(application.sn)
        return ticket.url
