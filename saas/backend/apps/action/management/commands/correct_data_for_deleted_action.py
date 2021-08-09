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

from backend.apps.group.models import Group

from ..util import ActionViewService


class Command(BaseCommand):
    help = "modify policy template and delete user policy for deleted action"

    def add_arguments(self, parser):
        parser.add_argument(
            "-s", action="store", dest="system_id", help="system which action will be deleted", required=True
        )
        parser.add_argument("-a", action="store", dest="action_id", help="action which will be deleted", required=True)
        parser.add_argument(
            "-e", action="store", dest="cmd_id", help="[list / delete] list or delete data", required=False
        )

    def handle(self, *args, **options):
        system_id = options["system_id"]
        action_id = options["action_id"]
        cmd_id = options.get("cmd_id")

        action_view_service = ActionViewService()

        # 查询所有涉及该action的Policy Template
        templates = action_view_service.filter_perm_template_by_action(system_id, action_id)
        # 查询模板涉及的Subjects
        template_authorized_subjects = action_view_service.get_authorized_subjects_by_template_id(
            [t.id for t in templates]
        )
        # 查询所有涉及该action的User Policy
        policies = action_view_service.filter_user_policy_by_action(system_id, action_id)

        # 打印需要处理的权限模板及其涉及的Subject
        self.print_effect_templates(templates, template_authorized_subjects)
        # 答应需要处理的策略的用户
        self.print_effect_policies(policies)

        # 用户不明确要执行变更，则无需再执行
        if cmd_id != "delete":
            return

        # 再次确认是否删除
        self.double_check_for_delete_action()

        # 执行变更
        # 1. 【执行】个人权限变更，即删除策略
        self.log_success(f"Start Delete User Policy, the length of policies is {len(policies)}")
        action_view_service.execute_delete_policy(policies)
        self.log_success("Delete User Policy For Action Success")
        # 2. 【执行】更新或删除权限模板，关联的Subject同步更新
        self.log_success(f"Start Modify Template, the length of templates is {len(templates)}")
        action_view_service.execute_modify_template(action_id, templates, template_authorized_subjects)
        self.log_success("Modify Template Success")

    def log_success(self, message):
        """打印成功信息"""
        self.stdout.write(self.style.SUCCESS(message))

    def log_common(self, message):
        """打印正常信息"""
        self.stdout.write(message)

    def double_check_for_delete_action(self):
        """
        二次确认
        """
        print("Please enter `delete`, to execute delete user policies and policy templates")
        result = input("Input: ")
        while True:
            try:
                input_info = result.lower()
            except ValueError:
                pass
            else:
                if input_info == "delete":
                    return
            result = input("Please input `delete` or Quit")

    def print_effect_templates(self, templates, template_authorized_subjects):
        """
        打印影响的权限模板及其关联的Subjects
        """
        # 查询涉及的所有用户组名称
        group_ids = [
            int(i.subject_id) for v in template_authorized_subjects.values() for i in v if i.subject_type == "group"
        ]
        groups = Group.objects.filter(id__in=group_ids)
        group_id_name_map = {str(g.id): g.name for g in groups}

        self.log_common(f"[Effect Template](the length of templates is {len(templates)})")
        for t in templates:
            self.log_common(f"Template: {t.name}")
            effect_groups = []
            effect_users = []
            for authorized_subject in template_authorized_subjects[t.id]:
                if authorized_subject.subject_type == "group":
                    effect_groups.append(
                        group_id_name_map.get(authorized_subject.subject_id, authorized_subject.subject_id)
                    )
                if authorized_subject.subject_type == "user":
                    effect_users.append(authorized_subject.subject_id)
            self.log_common(f"effect group: {', '.join(effect_groups)}")
            self.log_common(f"effect user: {', '.join(effect_users)}")

    def print_effect_policies(self, policies):
        """
        打印影响的用户策略
        """
        self.log_common(f"[Effect Policy](the length of policies is {len(policies)})")
        effect_users = [p.subject_id for p in policies]
        self.log_common(f"effect user: {', '.join(effect_users)}")
