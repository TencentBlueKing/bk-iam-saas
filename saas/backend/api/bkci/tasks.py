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
from datetime import datetime
from typing import List

from celery import Task, current_app
from django.core.paginator import Paginator
from django.db.models import Q
from pydantic import parse_obj_as

from backend.api.bkci.models import (
    MigrateData,
    MigrateLegacyTask,
    MigrateTask,
    Permissions,
    Policies,
    PolicyGroups,
    Projects,
    Resources,
    ResourceTypes,
    Roles,
    Services,
    UserRoles,
)
from backend.apps.group.models import Group
from backend.apps.organization.models import User
from backend.apps.policy.models import Policy as PolicyModel
from backend.apps.role.models import RoleRelatedObject
from backend.apps.template.models import PermTemplatePolicyAuthorized
from backend.component.iam import list_all_subject_member
from backend.service.constants import SubjectType
from backend.service.models.policy import Policy
from backend.service.models.subject import Subject
from backend.util.json import json_dumps


def get_user_set():
    user_set = set()

    queryset = User.objects.filter(staff_status="IN").only("username").order_by("id")
    paginator = Paginator(queryset, 1000)

    for i in paginator.page_range:
        for u in paginator.page(i):
            user_set.add(u.username)

    return user_set


class BKCIMigrateTask(Task):
    name = "backend.api.bkci.tasks.BKCIMigrateTask"

    def run(self):
        # delete all old migrate data
        MigrateData.objects.filter(version="v3").delete()

        task = MigrateTask.objects.first()
        if not task:
            return

        role_ids = json.loads(task.role_ids)

        user_set = get_user_set()

        # create new migrate data
        self.handle_group_api_policy(role_ids, user_set)
        self.handle_group_web_policy(role_ids, user_set)
        self.handle_user_custom_policy(user_set)

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

    def handle_user_custom_policy(self, user_set):
        project_subject_path_action = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(set))))

        qs = PolicyModel.objects.filter(system_id="bk_ci", subject_type="user").order_by("id")
        paginator = Paginator(qs, 100)

        for i in paginator.page_range:
            for p in paginator.page(i):
                if p.subject_id not in user_set:
                    continue

                pb = Policy.from_db_model(p, 0)

                subject = Subject(type=p.subject_type, id=p.subject_id)
                self._handle_policy(pb, subject, project_subject_path_action)

        self.batch_create_migrate_data(project_subject_path_action, "user_custom_policy", user_set)

    def handle_group_web_policy(self, role_ids, user_set):
        project_subject_path_action = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(set))))

        if role_ids:
            exists_group_ids = list(
                RoleRelatedObject.objects.filter(role_id__in=role_ids, object_type="group").values_list(
                    "object_id", flat=True
                )
            )
        else:
            exists_group_ids = []

        # 1. 遍历策略分析出所有实例
        qs = PolicyModel.objects.filter(system_id="bk_ci", subject_type="group").order_by("id")
        if exists_group_ids:
            qs = qs.exclude(subject_id__in=[str(_id) for _id in exists_group_ids])

        paginator = Paginator(qs, 100)

        for i in paginator.page_range:
            for p in paginator.page(i):
                pb = Policy.from_db_model(p, 0)

                subject = Subject(type=p.subject_type, id=p.subject_id)
                self._handle_policy(pb, subject, project_subject_path_action)

        # 2. 遍历用户组授权模板权限
        qs = PermTemplatePolicyAuthorized.objects.filter(system_id="bk_ci").order_by("id")
        if exists_group_ids:
            qs = qs.exclude(subject_id__in=[str(_id) for _id in exists_group_ids])

        for pa in qs:
            policies = parse_obj_as(List[Policy], pa.data["actions"])
            subject = Subject(type=pa.subject_type, id=pa.subject_id)
            for p in policies:
                self._handle_policy(p, subject, project_subject_path_action)

        self.batch_create_migrate_data(project_subject_path_action, "group_web_policy", user_set)

    def handle_group_api_policy(self, role_ids, user_set):
        if not role_ids:
            return

        project_subject_path_action = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(set))))

        exists_group_ids = list(
            RoleRelatedObject.objects.filter(role_id__in=role_ids, object_type="group").values_list(
                "object_id", flat=True
            )
        )

        if not exists_group_ids:
            return

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

        self.batch_create_migrate_data(project_subject_path_action, "group_api_policy", user_set)

    def batch_create_migrate_data(self, project_subject_path_action, handler_type, user_set):
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
                    members = list_all_subject_member(subject.type, subject.id)
                    members = [
                        one
                        for one in members
                        if (one["type"] == SubjectType.USER.value and one["id"] in user_set)
                        or one["type"] == SubjectType.DEPARTMENT.value
                    ]
                    if not members:
                        continue

                    data["members"] = members

                migrate_data = MigrateData(
                    project_id=project[1],
                    type=handler_type,
                    data=json_dumps(data),
                )
                migrate_data.save(force_insert=True)


current_app.tasks.register(BKCIMigrateTask())


class BKCILegacyMigrateTask(Task):
    name = "backend.api.bkci.tasks.BKCILegacyMigrateTask"

    def run(self, id: int):
        task = MigrateLegacyTask.objects.filter(id=id).first()
        if not task or task.status != "PENDING":
            return

        project_ids = json.loads(task.project_ids)
        user_set = get_user_set()
        for project_id in project_ids:
            self.handle_project(project_id, user_set)

        # update status
        task.status = "SUCCESS"
        task.save(update_fields=["status"])

    def handle_project(self, project_id: str, user_set):
        MigrateData.objects.filter(version="v0", project_id=project_id).delete()

        # 1. 从project表查询项目id
        project = (
            Projects.objects.using("bkci").filter(project_code=project_id, deleted_at__isnull=True).only("id").first()
        )
        if not project:
            return

        project_uuid = project.id

        # 2. 从services表查询出需要排除的service_id
        exclude_service_ids = list(
            Services.objects.using("bkci")
            .filter(
                service_code__in=["artifactory", "bcs", "gs-apk", "job", "vs", "wetest", "xinghai"],
                deleted_at__isnull=True,
            )
            .values_list("id", flat=True)
        )

        # 3. 从policies表中查询出所有的操作id与操作名生成map
        policies = (
            Policies.objects.using("bkci")
            .exclude(service_id__in=exclude_service_ids)
            .filter(deleted_at__isnull=True)
            .only("id", "policy_code")
            .all()
        )
        policy_map = {one.id: one.policy_code for one in policies}

        # 4. 从policies_groups表中查询出所有的操作group_id与操作的关系, 生成map
        policy_groups = (
            PolicyGroups.objects.using("bkci").filter(deleted_at__isnull=True).only("group_id", "policy_id").all()
        )

        policy_group_map = defaultdict(list)
        for one in policy_groups:
            if one.policy_id in policy_map:
                policy_group_map[one.group_id].append(policy_map[one.policy_id])

        # 5. 从resource_type表中查询出所有的资源id与资源名生成map
        resource_types = (
            ResourceTypes.objects.using("bkci")
            .exclude(service_id__in=exclude_service_ids)
            .filter(deleted_at__isnull=True)
            .only("id", "resource_type_code", "resource_type_name", "service_id")
            .all()
        )
        resource_type_map = {}
        for one in resource_types:
            resource_type_map[one.id] = {
                "id": one.resource_type_code,
                "name": one.resource_type_name,
                "service_id": one.service_id,
            }

        # 6. 从resources表中查询出所有的资源id与资源名生成map
        resources = (
            Resources.objects.using("bkci")
            .exclude(service_id__in=exclude_service_ids)
            .filter(deleted_at__isnull=True, project_id=project_uuid)
            .only("id", "resource_code", "resource_name")
            .all()
        )
        resource_map = {}
        for one in resources:
            resource_map[one.id] = {"id": one.resource_code, "name": one.resource_name}

        # 7. 从roles表中查询出所有的用户组id与用户组名生成map
        roles = (
            Roles.objects.using("bkci")
            .filter(deleted_at__isnull=True)
            .filter(Q(project_id=project_uuid) | Q(project_id=""))
            .only("id", "display_name")
            .all()
        )
        role_map = {}
        for one in roles:
            role_map[one.id] = {"id": one.id, "name": one.display_name, "members": []}

        # 8. 从user_roles表中查询出role_id与user_id填充role_map
        user_roles = (
            UserRoles.objects.using("bkci")
            .filter(deleted_at__isnull=True, project_id=project_uuid)
            .only("role_id", "user_id")
            .all()
        )
        role_user_map = defaultdict(list)
        for one in user_roles:
            if one.user_id not in user_set:
                continue
            role_user_map[one.role_id].append(one.user_id)

        for role_id, users in role_user_map.items():
            if role_id not in role_map:
                continue
            role_map[role_id]["members"] = users

        # 9. 查询特色资源group重名的service
        service_ids = []
        for resource_type in resource_type_map.values():
            if resource_type["id"] == "group" or resource_type["id"] == "task":
                service_ids.append(resource_type["service_id"])
        services = Services.objects.using("bkci").filter(id__in=service_ids).only("id", "service_code")
        service_map = {one.id: one.service_code for one in services}

        # 10. 执行转换
        self.handle_user_custom_policy(
            project_id,
            project_uuid,
            exclude_service_ids,
            policy_group_map,
            policy_map,
            resource_type_map,
            resource_map,
            service_map,
            user_set,
        )

        self.handle_group_web_policy(
            project_id,
            project_uuid,
            exclude_service_ids,
            policy_group_map,
            policy_map,
            resource_type_map,
            resource_map,
            service_map,
            role_map,
        )

    def handle_user_custom_policy(
        self,
        project_id,
        project_uuid,
        exclude_service_ids,
        policy_group_map,
        policy_map,
        resource_type_map,
        resource_map,
        service_map,
        user_set,
    ):
        user_resource_action = defaultdict(lambda: defaultdict(lambda: defaultdict(set)))

        queryset = (
            Permissions.objects.using("bkci")
            .filter(deleted_at__isnull=True, project_id=project_uuid, expire_at__gt=datetime.now())
            .exclude(service_id__in=exclude_service_ids)
            .exclude(Q(user_id__isnull=True) | Q(user_id=""))
            .order_by("id")
        )

        paginator = Paginator(queryset, 100)

        for i in paginator.page_range:
            for p in paginator.page(i):
                if p.user_id not in user_set:
                    continue

                if p.group_id and p.group_id in policy_group_map:
                    action_ids = policy_group_map[p.group_id]
                elif p.policy_id and p.policy_id in policy_map:
                    action_ids = [policy_map[p.policy_id]]
                else:
                    continue

                if not (p.resource_type_id and p.resource_type_id in resource_type_map):
                    continue

                if p.resource_id and p.resource_id in resource_map:
                    resource_id = p.resource_id
                elif p.resource_id == 0:
                    resource_id = "*"
                else:
                    continue

                for action_id in action_ids:
                    user_resource_action[p.user_id][p.resource_type_id][resource_id].add(action_id)

        for user_id, resource_type_action in user_resource_action.items():
            permissions = []
            for resource_type_id, resource_action in resource_type_action.items():
                for resource_id, action_ids in resource_action.items():
                    # 对于资源类型为group的特殊处理, 需要在action_ids中添加service
                    if (
                        resource_type_map[resource_type_id]["id"] in ["group", "task"]
                        and resource_type_map[resource_type_id]["service_id"] in service_map
                    ):
                        full_resource_type_id = (
                            service_map[resource_type_map[resource_type_id]["service_id"]]
                            + "_"
                            + resource_type_map[resource_type_id]["id"]
                        )
                    else:
                        full_resource_type_id = resource_type_map[resource_type_id]["id"]

                    if resource_id == "*":
                        paths = []
                    else:
                        paths = [
                            [
                                {
                                    "id": resource_map[resource_id]["id"],
                                    "name": resource_map[resource_id]["name"],
                                    "system_id": "bk_ci",
                                    "type": full_resource_type_id,
                                }
                            ]
                        ]

                    permissions.append(
                        {
                            "actions": [{"id": full_resource_type_id + "_" + _id} for _id in list(action_ids)],
                            "resources": [{"type": full_resource_type_id, "paths": paths}],
                        }
                    )

            data = {
                "type": "user_custom_policy",
                "project_id": project_id,
                "subject": {"type": "user", "id": user_id},
                "permissions": permissions,
            }

            migrate_data = MigrateData(
                project_id=project_id,
                type="user_custom_policy",
                data=json_dumps(data),
                version="v0",
            )
            migrate_data.save(force_insert=True)

    def handle_group_web_policy(
        self,
        project_id,
        project_uuid,
        exclude_service_ids,
        policy_group_map,
        policy_map,
        resource_type_map,
        resource_map,
        service_map,
        role_map,
    ):
        group_resource_action = defaultdict(lambda: defaultdict(lambda: defaultdict(set)))

        queryset = (
            Permissions.objects.using("bkci")
            .filter(deleted_at__isnull=True, project_id=project_uuid, expire_at__gt=datetime.now())
            .exclude(service_id__in=exclude_service_ids)
            .exclude(Q(role_id__isnull=True) | Q(role_id=0))
            .order_by("id")
        )

        paginator = Paginator(queryset, 100)

        for i in paginator.page_range:
            for p in paginator.page(i):
                if p.role_id not in role_map or not role_map[p.role_id]["members"]:
                    continue

                if p.group_id and p.group_id in policy_group_map:
                    action_ids = policy_group_map[p.group_id]
                elif p.policy_id and p.policy_id in policy_map:
                    action_ids = [policy_map[p.policy_id]]
                else:
                    continue

                if not (p.resource_type_id and p.resource_type_id in resource_type_map):
                    continue

                if p.resource_id and p.resource_id in resource_map:
                    resource_id = p.resource_id
                elif p.resource_id == 0:
                    resource_id = "*"
                else:
                    continue

                for action_id in action_ids:
                    group_resource_action[p.role_id][p.resource_type_id][resource_id].add(action_id)

        for role_id, resource_type_action in group_resource_action.items():
            permissions = []
            for resource_type_id, resource_action in resource_type_action.items():
                for resource_id, action_ids in resource_action.items():
                    # 对于资源类型为group的特殊处理, 需要在action_ids中添加service
                    if (
                        resource_type_map[resource_type_id]["id"] in ["group", "task"]
                        and resource_type_map[resource_type_id]["service_id"] in service_map
                    ):
                        full_resource_type_id = (
                            service_map[resource_type_map[resource_type_id]["service_id"]]
                            + "_"
                            + resource_type_map[resource_type_id]["id"]
                        )
                    else:
                        full_resource_type_id = resource_type_map[resource_type_id]["id"]

                    if resource_id == "*":
                        paths = []
                    else:
                        paths = [
                            [
                                {
                                    "id": resource_map[resource_id]["id"],
                                    "name": resource_map[resource_id]["name"],
                                    "system_id": "bk_ci",
                                    "type": full_resource_type_id,
                                }
                            ]
                        ]

                    permissions.append(
                        {
                            "actions": [{"id": full_resource_type_id + "_" + _id} for _id in list(action_ids)],
                            "resources": [{"type": full_resource_type_id, "paths": paths}],
                        }
                    )

            data = {
                "type": "group_web_policy",
                "project_id": project_id,
                "subject": {
                    "type": "group",
                    "id": role_map[role_id]["id"],
                    "name": role_map[role_id]["name"],
                },
                "permissions": permissions,
                "members": [{"type": "user", "id": user_id} for user_id in role_map[role_id]["members"]],
            }

            migrate_data = MigrateData(
                project_id=project_id,
                type="group_web_policy",
                data=json_dumps(data),
                version="v0",
            )
            migrate_data.save(force_insert=True)


current_app.tasks.register(BKCILegacyMigrateTask())
