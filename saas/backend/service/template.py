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

from django.db import transaction
from django.db.models import Count, F
from django.utils.translation import gettext as _
from pydantic import BaseModel

from backend.apps.template.models import PermTemplate, PermTemplatePolicyAuthorized, PermTemplatePreGroupSync
from backend.common.error_codes import error_codes
from backend.common.time import PERMANENT_SECONDS
from backend.component import iam

from .models import Policy, Subject, SystemCounter
from .policy.query import PolicyList, new_backend_policy_list_by_subject


class TemplateGroupPreCommit(BaseModel):
    group_id: str
    policies: List[Policy]

    def convert_policies_to_dict(self) -> List[Dict[str, Any]]:
        return [one.dict() for one in self.policies]


class TemplateService:
    # Template Auth
    def revoke_subject(self, system_id: str, template_id: int, subject: Subject):
        """
        移除模板成员
        """
        with transaction.atomic():
            count, _ = PermTemplatePolicyAuthorized.objects.filter(
                template_id=template_id, subject_type=subject.type, subject_id=subject.id
            ).delete()

            if count != 0:
                # 更新冗余count
                PermTemplate.objects.filter(id=template_id).update(subject_count=F("subject_count") - count)

                # 调用后端删除权限
                iam.delete_template_policies(system_id, subject.type, subject.id, template_id)

    def grant_subject(self, system_id: str, template_id: int, subject: Subject, policies: List[Policy]):
        """
        模板增加成员
        """
        authorized_template = PermTemplatePolicyAuthorized(
            template_id=template_id, subject_type=subject.type, subject_id=subject.id, system_id=system_id
        )
        authorized_template.data = {"actions": [p.dict() for p in policies]}

        with transaction.atomic():
            authorized_template.save(force_insert=True)
            PermTemplate.objects.filter(id=template_id).update(subject_count=F("subject_count") + 1)
            iam.create_and_delete_template_policies(
                system_id, subject.type, subject.id, template_id, [p.to_backend_dict(system_id) for p in policies], []
            )

    def alter_template_auth(
        self, subject: Subject, template_id: int, create_policies: List[Policy], delete_action_ids: List[str]
    ):
        """
        变更subject的模板授权信息
        """
        # 获取已有的授权信息
        authorized_template = PermTemplatePolicyAuthorized.objects.get_by_subject_template(subject, template_id)
        system_id = authorized_template.system_id
        policy_list = self._convert_template_actions_to_policy_list(authorized_template.data["actions"])

        # 查询subject的后端权限信息
        backend_policy_list = new_backend_policy_list_by_subject(system_id, subject, template_id)

        # 获取需要删除后端policy ids
        delete_policy_ids = [
            backend_policy_list.get(_id).id  # type: ignore
            for _id in delete_action_ids
            if backend_policy_list.get(_id)
        ]
        policy_list.remove_by_action_ids(delete_action_ids)

        if create_policies:
            # 合并, 如果列表中已存在对应的操作id, 则不能创建
            policy_list.extend_without_repeated(create_policies)

        create_backend_policies = [
            p.to_backend_dict(system_id) for p in create_policies if not backend_policy_list.get(p.action_id)
        ]

        with transaction.atomic():
            # 修改模板授权信息
            authorized_template = PermTemplatePolicyAuthorized.objects.select_for_update().get(
                id=authorized_template.id
            )
            authorized_template.data = {"actions": [p.dict() for p in policy_list.policies]}
            authorized_template.save(update_fields=["_data"])

            if not create_backend_policies and not delete_policy_ids:
                return

            # 变更后端policy
            iam.create_and_delete_template_policies(
                system_id, subject.type, subject.id, template_id, create_backend_policies, delete_policy_ids
            )

    def update_template_auth(self, subject: Subject, template_id: int, policies: List[Policy]):
        """
        跟新subject的模板授权信息
        """
        authorized_template = PermTemplatePolicyAuthorized.objects.get_by_subject_template(subject, template_id)
        system_id = authorized_template.system_id
        policy_list = self._convert_template_actions_to_policy_list(authorized_template.data["actions"])

        # 查询subject的后端权限信息
        backend_policy_list = new_backend_policy_list_by_subject(system_id, subject, template_id)

        # 填充policy_id, 更新policy
        for p in policies:
            if not backend_policy_list.get(p.action_id):
                raise error_codes.VALIDATE_ERROR.format(_("模板{}没有{}操作的权限").format(template_id, p.id))

            p.policy_id = backend_policy_list.get(p.action_id).id  # type: ignore
            policy_list.update(p)

        with transaction.atomic():
            authorized_template = PermTemplatePolicyAuthorized.objects.select_for_update().get(
                id=authorized_template.id
            )
            authorized_template.data = {"actions": [p.dict() for p in policy_list.policies]}
            authorized_template.save(update_fields=["_data"])
            iam.update_template_policies(
                system_id, subject.type, subject.id, template_id, [p.to_backend_dict(system_id) for p in policies]
            )

    def direct_update_db_template_auth(self, subject: Subject, template_id: int, policies: List[Policy]):
        """
        直接更新Subject的模板授权信息，这里只更新DB，不更新后台
        一般用于更新name等，与鉴权无关的信息
        """
        authorized_template = PermTemplatePolicyAuthorized.objects.get_by_subject_template(subject, template_id)
        with transaction.atomic():
            authorized_template = PermTemplatePolicyAuthorized.objects.select_for_update().get(
                id=authorized_template.id
            )
            authorized_template.data = {"actions": [p.dict() for p in policies]}
            authorized_template.save(update_fields=["_data"])

    def _convert_template_actions_to_policy_list(self, actions: List[Dict]) -> PolicyList:
        """转换模板的授权的actions到PolicyList, 兼容过期时间为空的情况"""
        policies = []
        for action in actions:
            if "expired_at" not in action or not action["expired_at"]:
                action["expired_at"] = PERMANENT_SECONDS
            policies.append(Policy.parse_obj(action))
        return PolicyList(policies)

    def list_system_counter_by_subject(self, subject: Subject) -> List[SystemCounter]:
        """
        查询subject有权限的系统-模板数量信息
        """
        qs = (
            PermTemplatePolicyAuthorized.objects.filter_by_subject(subject)
            .values("system_id")
            .annotate(count=Count("system_id"))
            .order_by()
        )

        return [SystemCounter(id=one["system_id"], count=one["count"]) for one in qs]

    def create_or_update_group_pre_commit(self, template_id: int, pre_commits: List[TemplateGroupPreCommit]):
        """
        创建或更新用户组预更新信息
        """
        group_ids = [one.group_id for one in pre_commits]
        exists_db_per_commits = PermTemplatePreGroupSync.objects.filter(
            template_id=template_id, group_id__in=group_ids
        ).defer("data")
        exists_db_per_commit_dict = {one.group_id: one for one in exists_db_per_commits}

        create_pre_commits, update_pre_commits = [], []
        for pre_commit in pre_commits:
            group_id = pre_commit.group_id

            if group_id in exists_db_per_commit_dict:
                db_pre_commit = exists_db_per_commit_dict[group_id]
                db_pre_commit.data = {"actions": pre_commit.convert_policies_to_dict()}
                update_pre_commits.append(db_pre_commit)
            else:
                db_pre_commit = PermTemplatePreGroupSync(template_id=template_id, group_id=group_id)
                db_pre_commit.data = {"actions": pre_commit.convert_policies_to_dict()}
                create_pre_commits.append(db_pre_commit)

        with transaction.atomic():
            if create_pre_commits:
                PermTemplatePreGroupSync.objects.bulk_create(create_pre_commits, batch_size=100)

            if update_pre_commits:
                PermTemplatePreGroupSync.objects.bulk_update(update_pre_commits, ["data"], batch_size=100)
