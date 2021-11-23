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
from collections import defaultdict

from django.core.paginator import Paginator
from django.db import transaction

from backend.apps.policy.models import Policy as PolicyModel
from backend.apps.template.models import PermTemplate, PermTemplatePolicyAuthorized
from backend.biz.template import TemplateBiz
from backend.component import iam
from backend.service.constants import SubjectType
from backend.service.models import Subject
from backend.service.policy.operation import PolicyOperationService

logger = logging.getLogger("app")


# TODO: 待提供了权限模型变更功能后，可去除
class ActionViewService:
    """
    这里的所有函数都是因为要使用
    """

    def filter_perm_template_by_action(self, system_id, action_id):
        """
        通过System和Action过滤出涉及的权限模板
        """
        templates = PermTemplate.objects.filter(system_id=system_id)
        return [template for template in templates if action_id in set(template.action_ids)]

    def get_authorized_subjects_by_template_id(self, template_ids):
        """
        通过权限模板ID获取其授权关联的Subjects
        """
        authorized_subjects = PermTemplatePolicyAuthorized.objects.filter(template_id__in=template_ids)
        template_authorized_subjects = defaultdict(list)
        for ts in authorized_subjects:
            template_authorized_subjects[ts.template_id].append(ts)

        return template_authorized_subjects

    def filter_user_policy_by_action(self, system_id, action_id):
        """
        通过System和Action过滤用户策略
        """
        policies = PolicyModel.objects.filter(
            system_id=system_id, action_id=action_id, subject_type=SubjectType.USER.value
        )
        return policies

    def execute_delete_policy(self, policies):
        """
        执行删除用户策略
        """
        policy_svc = PolicyOperationService()
        logger.info(f"Start Delete User Policy, the length of policies is {len(policies)}")
        for policy in policies:
            subject = Subject(type=policy.subject_type, id=policy.subject_id)
            # 删除权限
            policy_svc.delete_by_ids(policy.system_id, subject, [policy.policy_id])
        logger.info("Delete User Policy For Action Success")

    def execute_modify_template(self, action_id, templates, template_authorized_subjects):
        """
        执行变更模板
        """
        logger.info(f"Start Modify Template, the length of templates is {len(templates)}")

        template_biz = TemplateBiz()

        # 1. 产生新的权限模板策略或删除权限模板
        updated_policy_templates = []
        deleted_policy_templates = []
        for template in templates:
            action_ids = [_id for _id in template.action_ids if _id != action_id]

            # actions 没有了，说明之前只有一个Action且是要被删除的
            if len(action_ids) == 0:
                deleted_policy_templates.append(template)
                continue

            # 更新Template
            new_template = self.update_template(action_ids, template)
            updated_policy_templates.append(new_template)

        logger.info(f"the length of templates which need to update is {len(updated_policy_templates)}")
        logger.info(f"the length of templates which need to delete is {len(deleted_policy_templates)}")

        # 2. [删除] 权限模板
        logger.info("Start Delete Template")
        for t in deleted_policy_templates:
            # 删除所有的授权对象
            authorized_templates = PermTemplatePolicyAuthorized.objects.filter(template_id=t.id).only(
                "subject_type", "subject_id"
            )
            paginator = Paginator(authorized_templates, 100)
            if paginator.count:
                for i in paginator.page_range:
                    page = paginator.page(i)
                    members = [
                        Subject(type=authorized_template.subject_type, id=authorized_template.subject_id)
                        for authorized_template in page
                    ]
                    template_biz.revoke_subjects(t.system_id, t.id, members)
            template_biz.delete(t.id)

        logger.info("Delete Template Success")

        # 3. [更新] 权限模板
        logger.info("Start Modify Template")
        for t in updated_policy_templates:
            logger.info(f"modify template[{t.name}], subjects[{len(template_authorized_subjects[t.id])}]")
            for s in template_authorized_subjects[t.id]:
                # 删除对应的action_id的后台权限, 修改授权的信息
                with transaction.atomic():
                    # 删除SaaS授权的数据
                    template_policies = [action for action in s.data["actions"] if action["id"] != action_id]
                    s.data = {"actions": template_policies}
                    s.save(update_fields=["_data"])

                    # 删除后端对应的策略
                    backend_policies = iam.list_system_policy(s.system_id, s.subject_type, s.subject_id, s.template_id)
                    for p in backend_policies:
                        if p["action_id"] == action_id:
                            iam.create_and_delete_template_policies(
                                s.system_id, s.subject_type, s.subject_id, s.template_id, [], [p["id"]]
                            )
                            break

        logger.info("Modify Template Success")

    def update_template(self, action_ids, old_template):
        """
        更新权限模板
        """
        old_template.action_ids = action_ids
        old_template.save(update_fields=["_action_ids"])
        return old_template
