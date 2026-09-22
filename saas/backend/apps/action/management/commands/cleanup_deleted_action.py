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
from typing import Iterable, List, Set, Tuple

from django.core.management.base import BaseCommand, CommandError
from django.core.paginator import Paginator

from backend.api.authorization.constants import AuthorizationAPIEnum
from backend.api.authorization.models import AuthAPIAllowListConfig
from backend.apps.approval.models import ActionProcessRelation
from backend.apps.policy.models import Policy as PolicyModel
from backend.apps.role.models import Role, RoleCommonAction, RoleScope
from backend.apps.template.models import PermTemplate, PermTemplatePolicyAuthorized
from backend.apps.temporary_policy.models import TemporaryPolicy
from backend.service.action import ActionService
from backend.service.constants import RoleScopeType
from backend.util.json import json_dumps

BATCH_SIZE = 500
UPDATE_BATCH_SIZE = 50
DRY_RUN_MESSAGE_PREFIX = "[dry-run]"


def format_list(data: Iterable) -> str:
    return ",".join(str(i) for i in data)


def json_loads(content):
    if isinstance(content, bytes):
        content = content.decode("utf-8")
    return json.loads(content)


def compute_to_remove(present: List[str], action_ids: Set[str], current_action_ids: Set[str]) -> Set[str]:
    """计算某一行数据里需要清理的 action"""
    if action_ids:
        return {i for i in present if i in action_ids}
    return {i for i in present if i and i not in current_action_ids}


class Command(BaseCommand):
    help = "清理指定系统下已删除 Action 的 SaaS 侧关联数据"

    action_svc = ActionService()

    def add_arguments(self, parser):
        parser.add_argument("--system_id", "-s", type=str, required=True, help="系统 ID")
        parser.add_argument("--action_ids", "-a", type=str, required=False, default="", help="操作 ID")
        parser.add_argument("--dry-run", "-d", action="store_true", help="预运行")

    def handle(self, *args, **options):
        system_id: str = options["system_id"]
        dry_run: bool = options["dry_run"]
        input_action_ids: str = options["action_ids"]

        try:
            current_action_ids = {a.id for a in self.action_svc.list(system_id)}
        except Exception as e:
            raise CommandError(f"get action list from iam failed, abort to avoid accidental deletion: {e}")

        # 指定的 action 必须已被删除，仍存在则报错，避免清理存在的 action
        action_ids = [a.strip() for a in input_action_ids.split(",") if a.strip()]
        if action_ids:
            invalid_ids = [a for a in action_ids if a in current_action_ids]
            if invalid_ids:
                raise CommandError(f"actions {format_list(invalid_ids)} still exist in iam, failed to cleanup")

        self.cleanup_policy(system_id, action_ids, current_action_ids, dry_run)
        self.cleanup_temporary_policy(system_id, action_ids, current_action_ids, dry_run)
        self.cleanup_approval_process(system_id, action_ids, current_action_ids, dry_run)
        self.cleanup_api_allow_list(system_id, action_ids, current_action_ids, dry_run)
        self.cleanup_template(system_id, action_ids, current_action_ids, dry_run)
        self.cleanup_template_policy_authorized(system_id, action_ids, current_action_ids, dry_run)
        self.cleanup_role_common_action(system_id, action_ids, current_action_ids, dry_run)
        self.cleanup_role_scope(system_id, action_ids, current_action_ids, dry_run)

    def info(self, message: str, dry_run: bool):
        if dry_run:
            message = DRY_RUN_MESSAGE_PREFIX + message
        self.stdout.write(message)

    def success(self, message: str, dry_run: bool):
        if dry_run:
            message = DRY_RUN_MESSAGE_PREFIX + message
        self.stdout.write(self.style.SUCCESS(message))

    def warning(self, message: str, dry_run: bool):
        if dry_run:
            message = DRY_RUN_MESSAGE_PREFIX + message
        self.stdout.write(self.style.WARNING(message))

    def cleanup_policy(
        self, system_id: str, action_ids: List[str], current_action_ids: Set[str], dry_run: bool
    ) -> None:
        """清理策略"""
        queryset = PolicyModel.objects.filter(system_id=system_id)
        if action_ids:
            queryset = queryset.filter(action_id__in=action_ids)

        # 查询策略中是否存在已被删除的操作
        policy_action_ids: List[str] = list(queryset.values_list("action_id", flat=True).distinct())
        if not policy_action_ids:
            self.success("no found policies with deleted actions", dry_run)
            return
        found_action_ids: Set[str] = {a for a in policy_action_ids if a not in current_action_ids}
        self.info(f"found deleted actions in PolicyModel: id={format_list(found_action_ids)}", dry_run)
        if not found_action_ids:
            return

        # 执行清理
        policy_count = PolicyModel.objects.filter(system_id=system_id, action_id__in=found_action_ids).count()
        if not dry_run:
            PolicyModel.objects.filter(system_id=system_id, action_id__in=found_action_ids).delete()
        self.success(f"deleted PolicyModel: count={policy_count}", dry_run)

    def cleanup_temporary_policy(
        self, system_id: str, action_ids: List[str], current_action_ids: Set[str], dry_run: bool
    ) -> None:
        """清理临时权限"""
        queryset = TemporaryPolicy.objects.filter(system_id=system_id)
        if action_ids:
            queryset = queryset.filter(action_id__in=action_ids)

        # 查询临时权限中是否存在已被删除的操作
        policy_action_ids: List[str] = list(queryset.values_list("action_id", flat=True).distinct())
        if not policy_action_ids:
            self.success("no found temporary policies with deleted actions", dry_run)
            return
        found_action_ids: Set[str] = {a for a in policy_action_ids if a not in current_action_ids}
        self.info(f"found deleted actions in TemporaryPolicy: id={format_list(found_action_ids)}", dry_run)
        if not found_action_ids:
            return

        # 执行清理
        policy_count = TemporaryPolicy.objects.filter(system_id=system_id, action_id__in=found_action_ids).count()
        if not dry_run:
            TemporaryPolicy.objects.filter(system_id=system_id, action_id__in=found_action_ids).delete()
        self.success(f"deleted TemporaryPolicy: count={policy_count}", dry_run)

    def cleanup_template(
        self, system_id: str, action_ids: List[str], current_action_ids: Set[str], dry_run: bool
    ) -> None:
        """清理权限模板"""
        should_updated_templates: List[PermTemplate] = []
        should_deleted_action_ids = set(action_ids)
        deleted_action_ids: Set[str] = set()

        # 检查包含已删除操作的权限模板
        templates = PermTemplate.objects.filter(system_id=system_id).only("id", "_action_ids")
        for t in templates:
            ids = t.action_ids
            to_remove = compute_to_remove(ids, should_deleted_action_ids, current_action_ids)
            if not to_remove:
                continue
            t.action_ids = [i for i in ids if i not in to_remove]
            deleted_action_ids.update(to_remove)
            should_updated_templates.append(t)
        self.info(
            f"found deleted actions in PermTemplate: id={format_list(deleted_action_ids)}",
            dry_run,
        )
        if not should_updated_templates:
            return

        # 执行清理
        if not dry_run:
            PermTemplate.objects.bulk_update(
                should_updated_templates, fields=["_action_ids"], batch_size=UPDATE_BATCH_SIZE
            )
        self.success(
            f"updated PermTemplate: count={len(should_updated_templates)} , "
            f"id={format_list(t.id for t in should_updated_templates)}",
            dry_run,
        )

    def cleanup_template_policy_authorized(
        self, system_id: str, action_ids: List[str], current_action_ids: Set[str], dry_run: bool
    ) -> None:
        """清理权限模板授权"""
        should_updated_policies: List[PermTemplatePolicyAuthorized] = []
        should_deleted_action_ids = set(action_ids)
        deleted_action_ids: Set[str] = set()

        # 检查包含已删除操作的权限模板的授权
        authorized_policies = PermTemplatePolicyAuthorized.objects.filter(system_id=system_id).only(
            "id", "_data", "_auth_types"
        )
        for a in authorized_policies:
            data = a.data
            actions = data.get("actions", [])
            auth = a.auth_types

            present = [k for k in auth if k]
            for action in actions:
                aid = action.get("id", action.get("action_id"))
                if aid:
                    present.append(aid)
            to_remove = compute_to_remove(present, should_deleted_action_ids, current_action_ids)
            if not to_remove:
                continue
            deleted_action_ids.update(to_remove)
            data["actions"] = [act for act in actions if act.get("id", act.get("action_id")) not in to_remove]

            a.data = data
            a.auth_types = {k: v for k, v in auth.items() if k not in to_remove}
            should_updated_policies.append(a)
        self.info(
            f"found deleted actions in PermTemplatePolicyAuthorized: id={format_list(deleted_action_ids)}",
            dry_run,
        )
        if not should_updated_policies:
            return

        # 执行清理
        if not dry_run:
            PermTemplatePolicyAuthorized.objects.bulk_update(
                should_updated_policies, fields=["_data", "_auth_types"], batch_size=UPDATE_BATCH_SIZE
            )
        self.success(
            f"updated PermTemplatePolicyAuthorized: count={len(should_updated_policies)} , "
            f"id={format_list(a.id for a in should_updated_policies)}",
            dry_run,
        )

    def cleanup_approval_process(
        self, system_id: str, action_ids: List[str], current_action_ids: Set[str], dry_run: bool
    ) -> None:
        """清理操作审批流程"""
        queryset = ActionProcessRelation.objects.filter(system_id=system_id)
        if action_ids:
            queryset = queryset.filter(action_id__in=action_ids)
        relations: List[Tuple[int, str]] = list(queryset.values_list("id", "action_id"))
        if not relations:
            self.success("no approval processes found in ActionProcessRelation", dry_run)
            return

        # 检查包含已删除操作的审批流程
        found_action_ids: Set[str] = set()
        found_ids: List[int] = []
        for relation_id, action_id in relations:
            if action_id in current_action_ids:
                continue
            found_action_ids.add(action_id)
            found_ids.append(relation_id)
        self.info(f"found deleted actions in ActionProcessRelation: id={format_list(found_action_ids)}", dry_run)
        if not found_ids:
            return

        # 执行清理
        if not dry_run:
            ActionProcessRelation.objects.filter(id__in=found_ids).delete()
        self.success(
            f"deleted ActionProcessRelation: count={len(found_ids)} , id={format_list(found_ids)}",
            dry_run,
        )

    def cleanup_api_allow_list(
        self, system_id: str, action_ids: List[str], current_action_ids: Set[str], dry_run: bool
    ) -> None:
        """清理授权 API 白名单"""
        queryset = AuthAPIAllowListConfig.objects.filter(
            system_id=system_id, type=AuthorizationAPIEnum.AUTHORIZATION_INSTANCE.value
        )
        if action_ids:
            queryset = queryset.filter(object_id__in=action_ids)
        configs: List[Tuple[int, str]] = list(queryset.values_list("id", "object_id"))
        if not configs:
            self.success("no api allow list configs found in AuthAPIAllowListConfig", dry_run)
            return

        # 检查包含已删除操作的 API 白名单配置
        found_action_ids: Set[str] = set()
        found_ids: List[int] = []
        for config_id, object_id in configs:
            if object_id == "*" or object_id in current_action_ids:
                continue
            found_action_ids.add(object_id)
            found_ids.append(config_id)
        self.info(f"found deleted actions in AuthAPIAllowListConfig: id={format_list(found_action_ids)}", dry_run)
        if not found_ids:
            return

        # 执行清理
        if not dry_run:
            AuthAPIAllowListConfig.objects.filter(id__in=found_ids).delete()
        self.success(
            f"deleted AuthAPIAllowListConfig: count={len(found_ids)} , id={format_list(found_ids)}",
            dry_run,
        )

    def cleanup_role_common_action(
        self, system_id: str, action_ids: List[str], current_action_ids: Set[str], dry_run: bool
    ) -> None:
        """清理管理空间常用操作"""
        role_common_actions: List[RoleCommonAction] = []
        deleted_action_ids: Set[str] = set()
        should_deleted_action_ids = set(action_ids)

        # 检查包含已删除操作的管理空间常用操作
        for c in RoleCommonAction.objects.filter(system_id=system_id).only("id", "_action_ids").iterator():
            ids = c.action_ids
            to_remove = compute_to_remove(ids, should_deleted_action_ids, current_action_ids)
            if not to_remove:
                continue
            deleted_action_ids.update(to_remove)
            c.action_ids = [x for x in ids if x not in to_remove]
            role_common_actions.append(c)
        self.info(f"found deleted actions in RoleCommonAction: id={format_list(deleted_action_ids)}", dry_run)
        if not role_common_actions:
            return

        # 执行清理
        if not dry_run:
            RoleCommonAction.objects.bulk_update(
                role_common_actions, fields=["_action_ids"], batch_size=UPDATE_BATCH_SIZE
            )
        self.success(
            f"updated RoleCommonAction: count={len(role_common_actions)}, "
            f"id={format_list(c.id for c in role_common_actions)}",
            dry_run,
        )

    def cleanup_role_scope(
        self, system_id: str, action_ids: List[str], current_action_ids: Set[str], dry_run: bool
    ) -> None:
        """清理管理空间授权范围"""
        role_scopes: List[RoleScope] = []
        deleted_action_ids: Set[str] = set()
        should_deleted_action_ids = set(action_ids)

        # 检查包含已删除操作的管理空间授权范围
        roles = Role.objects.only("id")
        if system_id != "bk_ci_rbac":
            roles = roles.exclude(source_system_id="bk_ci_rbac")

        paginator = Paginator(roles, BATCH_SIZE)
        for page_num in paginator.page_range:
            for role in paginator.page(page_num).object_list:
                role_scope = RoleScope.objects.filter(type=RoleScopeType.AUTHORIZATION.value, role_id=role.id).first()
                if not role_scope:
                    continue

                try:
                    content = json_loads(role_scope.content)
                except Exception as e:
                    self.warning(
                        f"parse content from role scope, role_id={role.id}, role_scope_id={role_scope.id}, "
                        f"exception={e}",
                        dry_run,
                    )
                    continue

                # 收集本系统段里出现的 action
                present: List[str] = []
                for scope in content:
                    if isinstance(scope, dict) and scope.get("system_id") == system_id:
                        for act in scope.get("actions", []):
                            aid = act.get("id")
                            if aid:
                                present.append(aid)

                # 计算需要删除的操作
                to_remove = compute_to_remove(present, should_deleted_action_ids, current_action_ids)
                if not to_remove:
                    continue
                deleted_action_ids.update(to_remove)

                # 移除 action
                for scope in content:
                    if isinstance(scope, dict) and scope.get("system_id") == system_id:
                        scope["actions"] = [a for a in scope.get("actions", []) if a.get("id") not in to_remove]
                role_scope.content = json_dumps(content)
                role_scopes.append(role_scope)

        self.info(f"found deleted actions in RoleScope: id={format_list(deleted_action_ids)}", dry_run)
        if not role_scopes:
            return

        # 执行清理
        if not dry_run:
            RoleScope.objects.bulk_update(role_scopes, fields=["content"], batch_size=UPDATE_BATCH_SIZE)
        self.success(
            f"updated RoleScope: count={len(role_scopes)} , id={format_list(r.id for r in role_scopes)}",
            dry_run,
        )
