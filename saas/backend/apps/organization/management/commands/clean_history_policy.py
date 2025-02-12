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
from django.core.management.base import BaseCommand

from backend.apps.organization.models import User, SubjectToDelete
from backend.apps.organization.constants import StaffStatus
from backend.service.constants import SubjectType
from backend.apps.policy.models import Policy
from backend.apps.temporary_policy.models import TemporaryPolicy
from backend.service.models import Subject
from backend.service.policy.query import PolicyQueryService
from backend.common.error_codes import error_codes
from blue_krill.web.std_error import APIError


class Command(BaseCommand):
    help = "Clean history policy"

    def handle(self, *args, **options):

        # 清理离职用户遗留权限
        self.clean_out_user_policy()
        # 清理离职又入职用户遗留权限
        self.clean_user_policy()

    def clean_user_policy(self):
        """
        清理离职又入职用户权限
        """
        srv = PolicyQueryService()
        policy_set = set()
        users = User.objects.filter(staff_status=StaffStatus.IN.value).all()

        for user in users:
            policies = Policy.objects.filter(
                subject_type=SubjectType.USER.value,
                subject_id=user.username,
                updated_time__lt=user.updated_time).all()

            for policy in policies:
                subject = Subject.from_username(policy.subject_id)
                try:
                    srv.get_policy_by_id(policy.id, subject)
                except APIError as e:
                    if e.code == error_codes.NOT_FOUND_ERROR.code:
                        policy_set.add(policy)
        for policy in policy_set:
            policy.delete()

    def clean_out_user_policy(self):
        """
        清理离职用户权限
        """
        subject_to_delete_users = SubjectToDelete.objects.filter(
            subject_type=SubjectType.USER.value).all()
        usernames = {user.subject_id for user in subject_to_delete_users}
        users = (User.objects.filter(staff_status=StaffStatus.OUT.value)
                 .exclude(username__in=usernames).all())
        subject_ids = {user.username for user in users}

        # 清理权限
        Policy.objects.filter(subject_type=SubjectType.USER.value,
                              subject_id__in=subject_ids).delete()

        # 清理临时权限
        TemporaryPolicy.objects.filter(subject_type=SubjectType.USER.value,
                                       subject_id__in=subject_ids).delete()
