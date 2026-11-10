# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云 - 权限中心 (BlueKing-IAM) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import json
from collections import defaultdict
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
from backend.component import iam
from backend.service.constants import ACTION_ALL, RoleScopeType
from backend.service.models.subject import Subject
from backend.service.policy.operation import PolicyOperationService
from backend.util.json import json_dumps

BATCH_SIZE = 500
UPDATE_BATCH_SIZE = 50
DELETE_BATCH_SIZE = 200
DRY_RUN_MESSAGE_PREFIX = "[dry-run]"
ID_LIST_LIMIT = 50


def format_list(data: Iterable, limit: int = ID_LIST_LIMIT) -> str:
    """格式化 id 列表为字符串；数量过多时截断，避免日志撑爆。"""
    items = list(data)
    if len(items) <= limit:
        return ",".join(str(i) for i in items)
    return f"total={len(items)}, first {limit}=" + ",".join(str(i) for i in items[:limit])


def chunked(iterable, size):
    """把可迭代对象切成定长列表。"""
    buf = []
    for item in iterable:
        buf.append(item)
        if len(buf) >= size:
            yield buf
            buf = []
    if buf:
        yield buf


def flush_bulk_update(model_cls, objs: list, fields: List[str], batch_size: int, dry_run: bool) -> None:
    """分批 bulk_update 并清空缓冲；dry-run 时只清空缓冲不写库"""
    if not objs:
        return
    if not dry_run:
        model_cls.objects.bulk_update(objs, fields=fields, batch_size=batch_size)
    objs.clear()


def compute_to_remove(present: List[str], action_ids: Set[str], current_action_ids: Set[str]) -> Set[str]:
    """计算某一行数据里需要清理的 action"""
    # Note: ACTION_ALL("*") 表示"该系统任意操作"，是授权范围/模板中的合法值，且不会出现在 Action 列表中，不能被清理
    if action_ids:
        return {i for i in present if i in action_ids and i != ACTION_ALL}
    return {i for i in present if i and i != ACTION_ALL and i not in current_action_ids}


def list_action_ids_in_system(system_id: str) -> Set[str]:
    """获取系统当前 action id 集合。"""
    # 空列表/残缺列表一旦被缓存，作为删除判据会误删，以此这里通过 __wrapped__ 直接访问底层函数，绕过缓存
    actions = iam.list_action.__wrapped__(system_id, fields="id")
    return {a["id"] for a in actions}


class Command(BaseCommand):
    help = "清理指定系统下已删除 Action 的 SaaS 侧关联数据，默认仅清理 SaaS，--clean-backend 时尝试清理 IAM 后台。" "注意：若执行中途失败，修复原因后重新执行本命令即可。"

    policy_svc = PolicyOperationService()

    def add_arguments(self, parser):
        parser.add_argument("--system_id", "-s", type=str, required=True, help="系统 ID")
        parser.add_argument("--action_ids", "-a", type=str, required=False, default="", help="操作 ID 列表")
        parser.add_argument("--all-deleted", action="store_true", help="清理全部已删除操作必须显示指定")
        parser.add_argument("--dry-run", "-d", action="store_true", help="预运行")
        parser.add_argument("--yes", action="store_true", help="确认执行；非 dry-run 时必须指定，避免误删")
        parser.add_argument("--clean-backend", action="store_true", help="同步清理 IAM 后台策略")

    def handle(self, *args, **options):
        system_id: str = options["system_id"]
        dry_run: bool = options["dry_run"]
        force: bool = options["yes"]
        all_deleted: bool = options["all_deleted"]
        clean_backend: bool = options["clean_backend"]
        input_action_ids: str = options["action_ids"]

        action_ids = [a.strip() for a in input_action_ids.split(",") if a.strip()]
        # ACTION_ALL 表示全部操作，不是真实 Action，若允许指定，会把授权范围等数据中的 "*" 一并清除
        if ACTION_ALL in action_ids:
            raise CommandError(
                f'"{ACTION_ALL}" means all actions and is not a real Action, it cannot be specified in --action_ids'
            )
        if not action_ids and not all_deleted:
            raise CommandError("to cleanup all deleted actions, please use the --all-deleted flag")
        auto_mode = not action_ids

        try:
            current_action_ids = list_action_ids_in_system(system_id)
        except Exception as e:
            raise CommandError(f"get action list from iam failed, abort to avoid accidental deletion: {e}")

        # 指定的 action 必须已被删除，仍存在则报错，避免清理仍存在的 action
        if action_ids:
            invalid_ids = [a for a in action_ids if a in current_action_ids]
            if invalid_ids:
                raise CommandError(f"actions {format_list(invalid_ids)} still exist in iam, failed to cleanup")

        # 自动检测模式下，空列表说明 IAM 返回值异常，继续执行会把该系统全部关联数据清空，直接拒绝
        if auto_mode and not current_action_ids:
            raise CommandError(
                "iam reports NO action for this system; refusing to cleanup in case of empty/abnormal result. "
                "If you are sure some actions have been deleted, specify them explicitly with --action_ids."
            )

        if auto_mode:
            self.info(
                f"there are {len(current_action_ids)} actions in system [{system_id}]: "
                f"{format_list(current_action_ids)}; actions not in the list will be deleted",
                dry_run,
            )
        else:
            self.info(f"actions to be cleaned up in system [{system_id}]: {format_list(action_ids)}", dry_run)

        # 非 dry-run 时必须显式 --yes 才会执行，两者都没有则仅提示后结束，避免误删
        if not dry_run and not force:
            self.warning(
                "neither --dry-run nor --yes specified, nothing will be cleaned up; "
                "rerun with --dry-run to preview, or --yes to execute"
            )
            return

        self.cleanup_policy(system_id, action_ids, current_action_ids, dry_run, clean_backend)
        self.cleanup_temporary_policy(system_id, action_ids, current_action_ids, dry_run, clean_backend)
        self.cleanup_approval_process(system_id, action_ids, current_action_ids, dry_run)
        self.cleanup_api_allow_list(system_id, action_ids, current_action_ids, dry_run)
        self.cleanup_template(system_id, action_ids, current_action_ids, dry_run)
        self.cleanup_template_policy_authorized(system_id, action_ids, current_action_ids, dry_run)
        self.cleanup_role_common_action(system_id, action_ids, current_action_ids, dry_run)
        self.cleanup_role_scope(system_id, action_ids, current_action_ids, dry_run)

    def info(self, message: str, dry_run: bool = False):
        if dry_run:
            message = DRY_RUN_MESSAGE_PREFIX + message
        self.stdout.write(message)

    def success(self, message: str, dry_run: bool = False):
        if dry_run:
            message = DRY_RUN_MESSAGE_PREFIX + message
        self.stdout.write(self.style.SUCCESS(message))

    def warning(self, message: str, dry_run: bool = False):
        if dry_run:
            message = DRY_RUN_MESSAGE_PREFIX + message
        self.stdout.write(self.style.WARNING(message))

    def cleanup_policy(
        self,
        system_id: str,
        action_ids: List[str],
        current_action_ids: Set[str],
        dry_run: bool,
        clean_backend: bool,
    ) -> None:
        """清理策略"""
        queryset = PolicyModel.objects.filter(system_id=system_id)
        if action_ids:
            queryset = queryset.filter(action_id__in=action_ids)

        # 查询策略中是否存在已被删除的操作
        policy_action_ids: List[str] = list(queryset.values_list("action_id", flat=True).distinct())
        if not policy_action_ids:
            self.success("no policies found with deleted actions", dry_run)
            return
        found_action_ids: Set[str] = {a for a in policy_action_ids if a and a not in current_action_ids}
        self.info(f"found deleted actions in PolicyModel: id={format_list(found_action_ids)}", dry_run)
        if not found_action_ids:
            return

        policy_count = PolicyModel.objects.filter(system_id=system_id, action_id__in=found_action_ids).count()

        # 后台策略删除：action 已删时后台 DeleteByActionID 会报错，仅记录不中断
        if not dry_run:
            for a in found_action_ids:
                self._delete_policy_by_action(system_id, a, clean_backend)

        self.success(f"deleted PolicyModel: count={policy_count}", dry_run)

    def _delete_policy_by_action(self, system_id: str, action_id: str, clean_backend: bool):
        if clean_backend:
            try:
                self.policy_svc.delete_backend_policy_by_action(system_id, action_id)
            except Exception as e:
                self.warning(
                    "clean backend policy by action failed (action may be already deleted): "
                    f"system_id={system_id}, action_id={action_id}, err={e}",
                )

        PolicyModel.objects.filter(system_id=system_id, action_id=action_id).delete()

    def cleanup_temporary_policy(
        self,
        system_id: str,
        action_ids: List[str],
        current_action_ids: Set[str],
        dry_run: bool,
        clean_backend: bool,
    ) -> None:
        """清理临时权限"""
        queryset = TemporaryPolicy.objects.filter(system_id=system_id)
        if action_ids:
            queryset = queryset.filter(action_id__in=action_ids)

        # 查询临时权限中是否存在已被删除的操作
        policy_action_ids: List[str] = list(queryset.values_list("action_id", flat=True).distinct())
        if not policy_action_ids:
            self.success("no temporary policies found with deleted actions", dry_run)
            return
        found_action_ids: Set[str] = {a for a in policy_action_ids if a and a not in current_action_ids}
        self.info(f"found deleted actions in TemporaryPolicy: id={format_list(found_action_ids)}", dry_run)
        if not found_action_ids:
            return

        policy_count = TemporaryPolicy.objects.filter(system_id=system_id, action_id__in=found_action_ids).count()

        if not dry_run:
            for a in found_action_ids:
                self._delete_temporary_policies_by_action(system_id, a, clean_backend)

        self.success(f"deleted TemporaryPolicy: count={policy_count}", dry_run)

    def _delete_temporary_policies_by_action(self, system_id: str, action_id: str, clean_backend: bool) -> None:
        """按操作删除临时权限"""
        if not clean_backend:
            TemporaryPolicy.objects.filter(system_id=system_id, action_id=action_id).delete()
            return

        # 按 (subject_type, subject_id) 聚合该 action 下待删的主键，iam 会同时删除 saas 和 后台的临时权限数据
        groups = defaultdict(list)
        for tp_id, subject_type, subject_id in TemporaryPolicy.objects.filter(
            system_id=system_id, action_id=action_id
        ).values_list("id", "subject_type", "subject_id"):
            groups[(subject_type, subject_id)].append(tp_id)

        for (subject_type, subject_id), policy_ids in groups.items():
            try:
                self.policy_svc.delete_temporary_policies_by_ids(
                    system_id, Subject(type=subject_type, id=subject_id), policy_ids
                )
            except Exception as e:
                self.warning(
                    f"delete temporary policies (saas+backend) failed, "
                    f"subject={subject_type}/{subject_id}, action_id={action_id}, "
                    f"count={len(policy_ids)}, err={e}",
                )

    def cleanup_template(
        self, system_id: str, action_ids: List[str], current_action_ids: Set[str], dry_run: bool
    ) -> None:
        """清理权限模板"""
        should_deleted_action_ids = set(action_ids)
        deleted_action_ids: Set[str] = set()
        buf: List[PermTemplate] = []
        affected_count = 0

        # 用 iterator + 分批写回，避免大系统 OOM
        templates = PermTemplate.objects.filter(system_id=system_id).only("id", "_action_ids").iterator()
        for t in templates:
            ids = t.action_ids
            to_remove = compute_to_remove(ids, should_deleted_action_ids, current_action_ids)
            if not to_remove:
                continue
            deleted_action_ids.update(to_remove)
            remaining = [i for i in ids if i not in to_remove]
            t.action_ids = remaining
            if not remaining:
                # 清空后保留记录（与现有 Model 方法行为一致，删模板会级联影响授权），仅告警
                self.warning(
                    f"PermTemplate(id={t.id}) became empty after cleanup, kept as-is for manual review",
                    dry_run,
                )
            buf.append(t)
            affected_count += 1
            if len(buf) >= UPDATE_BATCH_SIZE:
                flush_bulk_update(PermTemplate, buf, ["_action_ids"], UPDATE_BATCH_SIZE, dry_run)
        flush_bulk_update(PermTemplate, buf, ["_action_ids"], UPDATE_BATCH_SIZE, dry_run)

        self.info(f"found deleted actions in PermTemplate: id={format_list(deleted_action_ids)}", dry_run)
        if affected_count:
            self.success(f"updated PermTemplate: count={affected_count}", dry_run)

    def cleanup_template_policy_authorized(
        self, system_id: str, action_ids: List[str], current_action_ids: Set[str], dry_run: bool
    ) -> None:
        """清理权限模板授权"""
        # NOTE: 现有 PermTemplatePolicyAuthorized.delete_action 只更新 _data、遗漏了 _auth_types，此处同时清理两者。
        should_deleted_action_ids = set(action_ids)
        deleted_action_ids: Set[str] = set()
        to_update: List[PermTemplatePolicyAuthorized] = []
        affected_count = 0

        # 模板授权是「模板 × 用户组」，大系统易到十万级，使用 iterator + 分批写回。
        authorized_policies = (
            PermTemplatePolicyAuthorized.objects.filter(system_id=system_id)
            .only("id", "_data", "_auth_types")
            .iterator()
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

            remaining_actions = [act for act in actions if act.get("id", act.get("action_id")) not in to_remove]
            data["actions"] = remaining_actions
            a.data = data
            a.auth_types = {k: v for k, v in auth.items() if k not in to_remove}
            if not remaining_actions and not a.auth_types:
                self.warning(
                    f"PermTemplatePolicyAuthorized(id={a.id}) became empty after cleanup, "
                    f"kept as-is for manual review",
                    dry_run,
                )
            to_update.append(a)
            affected_count += 1
            if len(to_update) >= UPDATE_BATCH_SIZE:
                flush_bulk_update(
                    PermTemplatePolicyAuthorized, to_update, ["_data", "_auth_types"], UPDATE_BATCH_SIZE, dry_run
                )

        flush_bulk_update(
            PermTemplatePolicyAuthorized, to_update, ["_data", "_auth_types"], UPDATE_BATCH_SIZE, dry_run
        )

        self.info(
            f"found deleted actions in PermTemplatePolicyAuthorized: id={format_list(deleted_action_ids)}",
            dry_run,
        )
        if affected_count:
            self.success(f"updated PermTemplatePolicyAuthorized: count={affected_count}", dry_run)

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
            if not action_id or action_id in current_action_ids:
                continue
            found_action_ids.add(action_id)
            found_ids.append(relation_id)
        self.info(f"found deleted actions in ActionProcessRelation: id={format_list(found_action_ids)}", dry_run)
        if not found_ids:
            return

        # 执行清理
        if not dry_run:
            ActionProcessRelation.objects.filter(id__in=found_ids).delete()
        self.success(f"deleted ActionProcessRelation: count={len(found_ids)}", dry_run)

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
            if not object_id or object_id == "*" or object_id in current_action_ids:
                continue
            found_action_ids.add(object_id)
            found_ids.append(config_id)
        self.info(f"found deleted actions in AuthAPIAllowListConfig: id={format_list(found_action_ids)}", dry_run)
        if not found_ids:
            return

        # 执行清理
        if not dry_run:
            AuthAPIAllowListConfig.objects.filter(id__in=found_ids).delete()
        self.success(f"deleted AuthAPIAllowListConfig: count={len(found_ids)}", dry_run)

    def cleanup_role_common_action(
        self, system_id: str, action_ids: List[str], current_action_ids: Set[str], dry_run: bool
    ) -> None:
        """清理管理空间常用操作"""

        # NOTE: 现有 RoleCommonAction 无 delete_by_action 方法、executor 也未清理。
        deleted_action_ids: Set[str] = set()
        should_deleted_action_ids = set(action_ids)
        to_update: List[RoleCommonAction] = []
        to_delete_ids: List[int] = []
        affected_count = 0
        deleted_empty_count = 0

        for c in RoleCommonAction.objects.filter(system_id=system_id).only("id", "_action_ids").iterator():
            ids = c.action_ids
            to_remove = compute_to_remove(ids, should_deleted_action_ids, current_action_ids)
            if not to_remove:
                continue
            deleted_action_ids.update(to_remove)
            remaining = [x for x in ids if x not in to_remove]
            affected_count += 1
            if remaining:
                c.action_ids = remaining
                to_update.append(c)
            else:
                # Action 全部移除后删除记录，避免留下空列表导致后续编辑/展示报错。
                to_delete_ids.append(c.id)
                deleted_empty_count += 1

            if len(to_update) >= UPDATE_BATCH_SIZE:
                flush_bulk_update(RoleCommonAction, to_update, ["_action_ids"], UPDATE_BATCH_SIZE, dry_run)

        flush_bulk_update(RoleCommonAction, to_update, ["_action_ids"], UPDATE_BATCH_SIZE, dry_run)

        if not dry_run and to_delete_ids:
            for sub in chunked(to_delete_ids, DELETE_BATCH_SIZE):
                RoleCommonAction.objects.filter(id__in=sub).delete()

        self.info(f"found deleted actions in RoleCommonAction: id={format_list(deleted_action_ids)}", dry_run)
        if affected_count:
            self.success(
                f"updated RoleCommonAction: count={affected_count} (deleted empty: count={deleted_empty_count})",
                dry_run,
            )

    def cleanup_role_scope(
        self, system_id: str, action_ids: List[str], current_action_ids: Set[str], dry_run: bool
    ) -> None:
        """清理管理空间授权范围"""
        deleted_action_ids: Set[str] = set()
        should_deleted_action_ids = set(action_ids)
        affected_count = 0

        roles = Role.objects.only("id")
        if system_id != "bk_ci_rbac":
            roles = roles.exclude(source_system_id="bk_ci_rbac")

        paginator = Paginator(roles, BATCH_SIZE)
        for page_num in paginator.page_range:
            role_ids = [role.id for role in paginator.page(page_num).object_list]
            if not role_ids:
                continue

            # 本页所有 role 的授权范围一次性查出
            scopes_by_role = {
                rs.role_id: rs
                for rs in RoleScope.objects.filter(type=RoleScopeType.AUTHORIZATION.value, role_id__in=role_ids)
            }

            buf: List[RoleScope] = []
            for role_id in role_ids:
                role_scope = scopes_by_role.get(role_id)
                if not role_scope:
                    continue

                try:
                    content = json.loads(role_scope.content)
                except Exception as e:
                    self.warning(
                        f"parse content from role scope, role_id={role_id}, role_scope_id={role_scope.id}, "
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
                buf.append(role_scope)
                affected_count += 1

                if len(buf) >= UPDATE_BATCH_SIZE:
                    flush_bulk_update(RoleScope, buf, ["content"], UPDATE_BATCH_SIZE, dry_run)
            flush_bulk_update(RoleScope, buf, ["content"], UPDATE_BATCH_SIZE, dry_run)

        self.info(f"found deleted actions in RoleScope: id={format_list(deleted_action_ids)}", dry_run)
        if affected_count:
            self.success(f"updated RoleScope: count={affected_count}", dry_run)
