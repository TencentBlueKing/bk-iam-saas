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
from collections import defaultdict
from typing import List

from celery import Task, current_app
from django.core.paginator import Paginator
from pydantic import parse_obj_as

from backend.api.bkci.models import MigrateData, MigrateTask
from backend.apps.group.models import Group
from backend.apps.policy.models import Policy as PolicyModel
from backend.apps.role.models import RoleRelatedObject
from backend.apps.template.models import PermTemplatePolicyAuthorized
from backend.component.iam import list_all_subject_member
from backend.service.models.policy import Policy
from backend.service.models.subject import Subject
from backend.util.json import json_dumps


class BKCIMigrateTask(Task):
    name = "backend.api.bkci.tasks.BKCIMigrateTask"

    def run(self):
        # delete all old migrate data
        MigrateData.objects.all().delete()

        task = MigrateTask.objects.first()
        if not task:
            return

        role_ids = json.loads(task.role_ids)

        # create new migrate data
        self.handle_group_api_policy(role_ids)
        self.handle_group_web_policy(role_ids)
        self.handle_user_custom_policy()

        # update status
        task.status = "SUCCESS"
        task.save(update_fields=["status"])

    def _handle_policy(self, policy: Policy, subject: Subject, project_subject_path_action):
        if not policy.resource_groups.__root__:
            return

        if not policy.resource_groups[0].related_resource_types:
            return

        if not policy.resource_groups[0].related_resource_types[0].condition:
            return

        for rg in policy.resource_groups:
            for rtt in rg.related_resource_types:
                for condition in rtt.condition:
                    for instance in condition.instances:
                        for path in instance.path:
                            first_node = path.__root__[0]
                            if first_node.type != "project":
                                continue

                            project_subject_path_action[(first_node.type, first_node.id)][subject][path][rtt.type].add(
                                policy.action_id
                            )

    def handle_user_custom_policy(self):
        project_subject_path_action = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(set))))

        qs = PolicyModel.objects.filter(system_id="bk_ci", subject_type="user").order_by("id")
        paginator = Paginator(qs, 100)

        for i in paginator.page_range:
            for p in paginator.page(i):
                pb = Policy.from_db_model(p, 0)

                subject = Subject(type=p.subject_type, id=p.subject_id)
                self._handle_policy(pb, subject, project_subject_path_action)

        self.batch_create_migrate_data(project_subject_path_action, "user_custom_policy")

    def handle_group_web_policy(self, role_ids):
        project_subject_path_action = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(set))))

        exists_group_ids = list(
            RoleRelatedObject.objects.filter(role_id__in=role_ids, object_type="group").values_list(
                "object_id", flat=True
            )
        )

        # 1. 遍历策略分析出所有实例
        qs = (
            PolicyModel.objects.filter(system_id="bk_ci", subject_type="group")
            .exclude(subject_id__in=[str(_id) for _id in exists_group_ids])
            .order_by("id")
        )
        paginator = Paginator(qs, 100)

        for i in paginator.page_range:
            for p in paginator.page(i):
                pb = Policy.from_db_model(p, 0)

                subject = Subject(type=p.subject_type, id=p.subject_id)
                self._handle_policy(pb, subject, project_subject_path_action)

        # 2. 遍历用户组授权模板权限
        qs = (
            PermTemplatePolicyAuthorized.objects.filter(system_id="bk_ci")
            .exclude(subject_id__in=[str(_id) for _id in exists_group_ids])
            .order_by("id")
        )
        for pa in qs:
            policies = parse_obj_as(List[Policy], pa.data["actions"])
            subject = Subject(type=pa.subject_type, id=pa.subject_id)
            for p in policies:
                self._handle_policy(p, subject, project_subject_path_action)

        self.batch_create_migrate_data(project_subject_path_action, "group_web_policy")

    def handle_group_api_policy(self, role_ids):
        project_subject_path_action = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(set))))

        exists_group_ids = list(
            RoleRelatedObject.objects.filter(role_id__in=role_ids, object_type="group").values_list(
                "object_id", flat=True
            )
        )

        # 1. 遍历策略分析出所有实例
        qs = (
            PolicyModel.objects.filter(system_id="bk_ci", subject_type="group")
            .filter(subject_id__in=[str(_id) for _id in exists_group_ids])
            .order_by("id")
        )
        paginator = Paginator(qs, 100)

        for i in paginator.page_range:
            for p in paginator.page(i):
                pb = Policy.from_db_model(p, 0)

                subject = Subject(type=p.subject_type, id=p.subject_id)
                self._handle_policy(pb, subject, project_subject_path_action)

        # 2. 遍历用户组授权模板权限
        qs = (
            PermTemplatePolicyAuthorized.objects.filter(system_id="bk_ci")
            .filter(subject_id__in=[str(_id) for _id in exists_group_ids])
            .order_by("id")
        )
        for pa in qs:
            policies = parse_obj_as(List[Policy], pa.data["actions"])
            subject = Subject(type=pa.subject_type, id=pa.subject_id)
            for p in policies:
                self._handle_policy(p, subject, project_subject_path_action)

        self.batch_create_migrate_data(project_subject_path_action, "group_api_policy")

    def batch_create_migrate_data(self, project_subject_path_action, handler_type):
        for project, subject_path_action in project_subject_path_action.items():
            for subject, path_type_action in subject_path_action.items():
                subject_dict = subject.dict()
                if subject.type == "group":
                    group = Group.objects.filter(id=subject.id).first()
                    if not group:
                        continue

                    subject_dict["name"] = group.name

                permissions = []
                for path, type_actions in path_type_action.items():
                    for _type, actions in type_actions.items():
                        permissions.append(
                            {
                                "actions": [{"id": _id} for _id in list(actions)],
                                "resources": [{"type": _type, "paths": [[one.dict() for one in path.__root__]]}],
                            }
                        )

                data = {
                    "type": handler_type,
                    "project_id": project[1],
                    "subject": subject_dict,
                    "permissions": permissions,
                }

                if subject.type == "group":
                    data["members"] = list_all_subject_member(subject.type, subject.id)

                migrate_data = MigrateData(
                    project_id=project[1],
                    type=handler_type,
                    data=json_dumps(data),
                )
                migrate_data.save(force_insert=True)


current_app.tasks.register(BKCIMigrateTask())
