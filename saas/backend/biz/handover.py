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
import logging
import abc

from backend.biz.group import GroupBiz
from backend.biz.policy import PolicyOperationBiz, PolicyBean, PolicyQueryBiz
from backend.biz.role import RoleBiz
from backend.service.models import Subject
from backend.service.constants import SubjectType
from backend.apps.role.models import RoleUser
from backend.apps.handover.constants import HandoverTaskStatus
from backend.apps.handover.models import HandOverTask

logger = logging.getLogger(__name__)


def create_handover_task(handover_record_id, handover_info):

    # 批量创建交接明细记录
    handover_task_details = []
    for object_type in handover_info:
        for obj in handover_info[object_type]:
            handover_task_details.append(
                HandOverTask(
                    handover_record_id=handover_record_id,
                    object_type=object_type,
                    object_id=obj["id"],
                    object_detail=json.dumps(obj),
                )
            )
    HandOverTask.objects.bulk_create(handover_task_details, batch_size=500)


def verify_group_permission(subject, group_id):
    subject_groups = GroupBiz().list_subject_group(subject=subject)

    for subject_group in subject_groups:
        if (subject_group.id == group_id) and (subject_group.department_id == 0) and (subject_group.expired_at != 0):
            return True


def verify_custom_permission(subject, system_id, policy_id):
    subject_polices = PolicyQueryBiz().list_by_subject(system_id=system_id, subject=subject)
    for subject_police in subject_polices:
        if subject_police.action_id == policy_id and subject_police.expired_at != 0:
            return True


def verify_role_permission(username, role_id):
    return RoleUser.objects.user_role_exists(username, role_id)


class BaseHandover(object):

    @abc.abstractmethod
    def handler(self):
        try:
            self.grant_permission()

        except Exception as e:
            error_info = "授权失败"
            self.set_status(status=HandoverTaskStatus.Failed.value, error_info=error_info)
            return False

        try:
            self.revoke_permission()

        except Exception as e:
            error_info = "权限移除失败"
            self.set_status(status=HandoverTaskStatus.Failed.value, error_info=error_info)
            return False

        self.set_status(status=HandoverTaskStatus.Succeed.value)
        return True

    def set_status(self, status, error_info=""):
        HandOverTask.objects.filter(id=self.handover_task_id).update(
            status=status, error_info=error_info)


class GroupHandover(BaseHandover):
    def __init__(self, handover_task_id, handover_from, handover_to, object_detail):
        self.handover_task_id= handover_task_id

        self.grant_subject = Subject(type=SubjectType.USER.value, id=handover_to)
        self.remove_subject = Subject(type=SubjectType.USER.value, id=handover_from)

        self.group_id = object_detail["id"]
        self.expired_at = object_detail["expired_at"]


    def verify_permission(self):
        is_pass = verify_group_permission(subject=self.remove_subject, group_id=self.group_id)
        if not is_pass:
            error_info = "所交接的用户组权限校验失败"
            self.set_status(status=HandoverTaskStatus.Failed.value, error_info=error_info)
            return False
        return True

    def grant_permission(self):
        # TODO 需不需要校验？
        # GroupCheckBiz().check_member_count(group_id, len(grant_subject))    # 检查用户组成员数量未超限
        # GroupCheckBiz().check_subject_group_limit()   # 检查subject授权的group数量是否超限
        expired_at = self.object_detail["expired_at"]
        GroupBiz().add_members(group_id=int(self.group_id), members=[self.grant_subject], expired_at=self.expired_at)

    def revoke_permission(self):
        GroupBiz().remove_members(group_id=str(self.group_id), subjects=[self.remove_subject])


class CustomHandover(BaseHandover):
    def __init__(self, handover_task_id, handover_from, handover_to, object_detail):
        self.handover_task_id = handover_task_id

        self.grant_subject = Subject(type=SubjectType.USER.value, id=handover_to)
        self.remove_subject = Subject(type=SubjectType.USER.value, id=handover_from)

        self.system_id = object_detail["id"]
        self.policy_info = object_detail["policy_info"]
        self.policy_id = self.policy_info["id"]
        self.policies = [PolicyBean(**self.policy_info)]

    def verify_permission(self):

        is_pass = verify_custom_permission(
            system_id=self.system_id, subject=self.remove_subject, policy_id=self.policy_id)
        if not is_pass:
            error_info = "所交接的自定义权限权校验失败"
            self.set_status(status=HandoverTaskStatus.Failed.value, error_info=error_info)
            return False
        return True

    def grant_permission(self):
        PolicyOperationBiz().alter(system_id=self.system_id, subject=self.grant_subject, policies=self.policies)

    def revoke_permission(self):
        PolicyOperationBiz().revoke(system_id=self.system_id, subject=self.remove_subject, delete_policies=self.policies)


class SuperManHandover(BaseHandover):
    def __init__(self, handover_task_id, handover_from, handover_to, object_detail):
        self.handover_task_id = handover_task_id
        self.handover_from = handover_from
        self.handover_to = handover_to

        self.role_id = object_detail["id"]

    def verify_permission(self):
        is_pass = verify_role_permission(username=self.handover_from, role_id=self.role_id)
        if not is_pass:
            error_info = "所交接的超级管理员权限权校验失败"
            self.set_status(status=HandoverTaskStatus.Failed.value, error_info=error_info)
            return False
        return True


    def grant_permission(self):
        RoleBiz().add_super_manager_member(username=self.handover_to, need_sync_backend_role=True)

    def revoke_permission(self):
        RoleBiz().delete_super_manager_member(username=self.handover_from)


class SystemManHandover(BaseHandover):
    def __init__(self, handover_task_id, handover_from, handover_to, object_detail):
        self.handover_task_id = handover_task_id
        self.handover_from = handover_from
        self.handover_to = handover_to

        self.grant_subject = Subject(type=SubjectType.USER.value, id=handover_to)
        self.remove_subject = Subject(type=SubjectType.USER.value, id=handover_from)

        self.role_id = object_detail["id"]
        self.members = RoleBiz().list_members_by_role_id(self.role_id)  # 获取指定角色的成员列表

    def verify_permission(self):
        is_pass = verify_role_permission(username=self.handover_from, role_id=self.role_id)
        if not is_pass:
            error_info = "所交接的系统管理员权限权校验失败"
            self.set_status(status=HandoverTaskStatus.Failed.value, error_info=error_info)
            return False
        return True

    def grant_permission(self):
        self.members.append(self.handover_to)
        RoleBiz().modify_system_manager_members(role_id=self.role_id, members=self.members)  # 修改系统管理员成员

    def revoke_permission(self):
        self.members.remove(self.handover_from)
        RoleBiz().modify_system_manager_members(role_id=self.role_id, members=self.members)  # 修改系统管理员成员


class GradeManHandover(BaseHandover):
    def __init__(self, handover_task_id, handover_from, handover_to, object_detail):
        self.handover_task_id = handover_task_id
        self.handover_from = handover_from
        self.handover_to = handover_to

        self.role_id = object_detail["id"]


    def verify_permission(self):
        is_pass = verify_role_permission(username=self.handover_from, role_id=self.role_id)
        if not is_pass:
            error_info = "所交接的分级管理员权限权校验失败"
            self.set_status(status=HandoverTaskStatus.Failed.value, error_info=error_info)
            return False
        return True

    def grant_permission(self):
        RoleBiz().add_grade_manager_members(self.role_id, [self.handover_to])

    def revoke_permission(self):
        RoleBiz().delete_member(self.role_id, self.handover_from)
