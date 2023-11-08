import json
from copy import deepcopy
from typing import List

from django.core.paginator import Paginator
from pydantic import parse_obj_as

from backend.apps.policy.models import Policy as PolicyModel
from backend.apps.role.models import Role, RoleScope
from backend.apps.template.models import PermTemplate, PermTemplatePolicyAuthorized
from backend.biz.policy import PolicyBean, PolicyBeanList, PolicyOperationBiz, PolicyQueryBiz
from backend.service.constants import RoleScopeType
from backend.service.models import Policy
from backend.service.models.subject import Subject
from backend.service.role import AuthScopeAction
from backend.service.template import TemplateService
from backend.util.json import json_dumps

system_id = "bk_monitorv3"

policy_query_biz = PolicyQueryBiz()
policy_operation_biz = PolicyOperationBiz()

template_svc = TemplateService()


def gen_new_policies(policy_list: PolicyBeanList):
    """
    manage_dashboard_v2 space -> view_single_dashboard grafana_dashboard

    view_dashboard_v2 space -> new_dashboard space

    view_dashboard_v2 space -> edit_single_dashboard grafana_dashboard
    """

    new_policies = []
    for p in policy_list.policies:
        if p.action_id == "view_dashboard_v2":
            if not policy_list.get("new_dashboard"):
                new_dashboard = deepcopy(p)
                new_dashboard.action_id = "new_dashboard"

                new_policies.append(new_dashboard)

            if not policy_list.get("edit_single_dashboard"):
                edit_single_dashboard = deepcopy(p)
                edit_single_dashboard.action_id = "edit_single_dashboard"
                edit_single_dashboard.resource_groups.__root__[0].related_resource_types[0].type = "grafana_dashboard"

                new_policies.append(edit_single_dashboard)

        elif p.action_id == "manage_dashboard_v2":
            if not policy_list.get("view_single_dashboard"):
                view_single_dashboard = deepcopy(p)
                view_single_dashboard.action_id = "view_single_dashboard"
                view_single_dashboard.resource_groups.__root__[0].related_resource_types[0].type = "grafana_dashboard"

                new_policies.append(view_single_dashboard)

    return new_policies


def migrate():
    # 1. 遍历自定义权限, 迁移数据, 如果是用户组需要记录用户组关联的角色
    subjects = (
        PolicyModel.objects.filter(system_id=system_id, action_id__in=["view_dashboard_v2", "manage_dashboard_v2"])
        .values("subject_type", "subject_id")
        .distinct()
    )

    for _subject in subjects:
        subject = Subject(type=_subject["subject_type"], id=_subject["subject_id"])

        policy_list = policy_query_biz.new_policy_list(
            system_id,
            subject,
        )

        new_policies = gen_new_policies(policy_list)
        if not new_policies:
            continue

        new_policy_list = PolicyBeanList(system_id, new_policies, need_fill_empty_fields=True)
        policy_operation_biz.alter(system_id=system_id, subject=subject, policies=new_policy_list.policies)

    # 2. 遍历角色列表, 判断是否有对应的授权范围, 如果有, 需要变更授权范围
    queryset = Role.objects.only("id").exclude(source_system_id="bk_ci_rbac")
    paginator = Paginator(queryset, 100)

    should_updated_role_scopes = []

    for i in paginator.page_range:
        for role in paginator.page(i):
            role_scope = RoleScope.objects.filter(type=RoleScopeType.AUTHORIZATION.value, role_id=role.id).first()
            if not role_scope:
                continue

            content = json.loads(role_scope.content)
            should_updated = False
            # 遍历授权范围里每个系统
            for scope in content:
                if scope["system_id"] != system_id:
                    continue
                # 判断Action是否存在，不存在则忽略
                actions = {action["id"]: action for action in scope["actions"]}
                if not ("view_dashboard_v2" in actions or "manage_dashboard_v2" in actions):
                    continue

                new_scope_actions = []
                # 生成需要加入的新增的操作
                if "manage_dashboard_v2" in actions and "view_single_dashboard" not in actions:
                    view_single_dashboard = parse_obj_as(AuthScopeAction, actions["manage_dashboard_v2"])
                    view_single_dashboard.id = "view_single_dashboard"
                    view_single_dashboard.resource_groups.__root__[0].related_resource_types[
                        0
                    ].type = "grafana_dashboard"

                    new_scope_actions.append(view_single_dashboard)

                if "view_dashboard_v2" in actions:
                    if "new_dashboard" not in actions:
                        new_dashboard = parse_obj_as(AuthScopeAction, actions["view_dashboard_v2"])
                        new_dashboard.id = "new_dashboard"

                        new_scope_actions.append(new_dashboard)

                    if "edit_single_dashboard" not in actions:
                        edit_single_dashboard = parse_obj_as(AuthScopeAction, actions["view_dashboard_v2"])
                        edit_single_dashboard.id = "edit_single_dashboard"
                        edit_single_dashboard.resource_groups.__root__[0].related_resource_types[
                            0
                        ].type = "grafana_dashboard"

                        new_scope_actions.append(edit_single_dashboard)

                if not new_scope_actions:
                    continue

                scope["actions"].extend([one.dict() for one in new_scope_actions])
                should_updated = True
                break

            if should_updated:
                role_scope.content = json_dumps(content)
                should_updated_role_scopes.append(role_scope)

    # 批量更新分级管理员授权范围
    if len(should_updated_role_scopes) > 0:
        RoleScope.objects.bulk_update(should_updated_role_scopes, fields=["content"], batch_size=20)

    # 3. 遍历权限模版, 判断是否有对应的权限, 如果有对应的权限需要更新模版, 并变更用户组的权限
    for template in PermTemplate.objects.filter(system_id=system_id):
        action_ids = template.action_ids
        if not ("view_dashboard_v2" in action_ids or "manage_dashboard_v2" in action_ids):
            continue

        length = len(action_ids)
        if "view_dashboard_v2" in action_ids:
            if "new_dashboard" not in action_ids:
                action_ids.append("new_dashboard")

            if "edit_single_dashboard" not in action_ids:
                action_ids.append("edit_single_dashboard")

        if "manage_dashboard_v2" in action_ids and "view_single_dashboard" not in action_ids:
            action_ids.append("view_single_dashboard")

        if length == len(action_ids):
            continue

        # 遍历所有授权模版的用户组
        for auth in PermTemplatePolicyAuthorized.objects.filter(template_id=template.id, system_id=system_id):
            subject = Subject(type=auth.subject_type, id=auth.subject_id)
            policy_list = PolicyBeanList(
                system_id, parse_obj_as(List[PolicyBean], auth.data["actions"]), need_fill_empty_fields=False
            )

            new_policies = gen_new_policies(policy_list)
            if not new_policies:
                continue

            template_svc.alter_template_auth(subject, template.id, parse_obj_as(List[Policy], new_policies), [])

        template.action_ids = action_ids
        template.save()


def migrate_ci():
    # 2. 遍历角色列表, 判断是否有对应的授权范围, 如果有, 需要变更授权范围
    queryset = Role.objects.only("id").filter(source_system_id="bk_ci_rbac")
    paginator = Paginator(queryset, 100)

    for i in paginator.page_range:
        should_updated_role_scopes = []
        for role in paginator.page(i):
            role_scope = RoleScope.objects.filter(type=RoleScopeType.AUTHORIZATION.value, role_id=role.id).first()
            if not role_scope:
                continue

            content = json.loads(role_scope.content)
            should_updated = False
            # 遍历授权范围里每个系统
            for scope in content:
                if scope["system_id"] != system_id:
                    continue
                # 判断Action是否存在，不存在则忽略
                actions = {action["id"]: action for action in scope["actions"]}
                if not ("view_dashboard_v2" in actions or "manage_dashboard_v2" in actions):
                    continue

                new_scope_actions = []
                # 生成需要加入的新增的操作
                if "manage_dashboard_v2" in actions and "view_single_dashboard" not in actions:
                    view_single_dashboard = parse_obj_as(AuthScopeAction, actions["manage_dashboard_v2"])
                    view_single_dashboard.id = "view_single_dashboard"
                    view_single_dashboard.resource_groups.__root__[0].related_resource_types[
                        0
                    ].type = "grafana_dashboard"

                    new_scope_actions.append(view_single_dashboard)

                if "view_dashboard_v2" in actions:
                    if "new_dashboard" not in actions:
                        new_dashboard = parse_obj_as(AuthScopeAction, actions["view_dashboard_v2"])
                        new_dashboard.id = "new_dashboard"

                        new_scope_actions.append(new_dashboard)

                    if "edit_single_dashboard" not in actions:
                        edit_single_dashboard = parse_obj_as(AuthScopeAction, actions["view_dashboard_v2"])
                        edit_single_dashboard.id = "edit_single_dashboard"
                        edit_single_dashboard.resource_groups.__root__[0].related_resource_types[
                            0
                        ].type = "grafana_dashboard"

                        new_scope_actions.append(edit_single_dashboard)

                if not new_scope_actions:
                    continue

                scope["actions"].extend([one.dict() for one in new_scope_actions])
                should_updated = True
                break

            if should_updated:
                role_scope.content = json_dumps(content)
                should_updated_role_scopes.append(role_scope)

        # 批量更新分级管理员授权范围
        if len(should_updated_role_scopes) > 0:
            RoleScope.objects.bulk_update(should_updated_role_scopes, fields=["content"], batch_size=20)
