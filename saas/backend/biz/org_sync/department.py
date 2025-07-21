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
from typing import Dict, List, Set, Tuple

from django.db import transaction

from backend.apps.organization.models import Department, DepartmentMember, DepartmentRelationMPTTTree, SubjectToDelete
from backend.component.client.bk_user import BkUserClient
from backend.service.constants import SubjectType
from backend.util.tree import bfs_traversal_tree, build_forest_with_parent_relations

from .base import BaseSyncDBService


class DBDepartmentSyncService(BaseSyncDBService):
    """部门同步服务"""

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.new_departments = BkUserClient(self.tenant_id).list_department()
        self.old_departments = list(Department.objects.filter(tenant_id=self.tenant_id))

    def sync(self):
        """ "同步部门

        Note: 非增量方式同步，而是全删除后全添加再重建的方式
        Q: 为什么不是增量模式时候，一通对比之后，直接往现有的 MPTT 森林里面塞节点？
        A: MPTT 树结构复杂，变更操作可能存在风险，且后台任务对性能要求不高，先用简单的删除重建方案
        """
        # {dept_id: dept}
        dept_id_map = {d["id"]: d for d in self.new_departments}

        dept_id_to_db_dept_map: Dict[int, Department] = {}
        mptt_tree_ids: Set[int] = set()

        # 父子部门关系 [(id, parent_id), ...]
        parent_relations = [(d["id"], d["parent_id"] or None) for d in self.new_departments]
        # 根据部门父子关系，构建森林
        forest_roots = build_forest_with_parent_relations(parent_relations)
        # 逐棵树进行遍历，因为需要保证一棵树的节点拥有相同的 tree_id
        for root in forest_roots:
            tree_id = self._generate_tree_id()
            mptt_tree_ids.add(tree_id)

            # 通过 bfs 遍历的方式，确保父节点会先被创建
            for node in bfs_traversal_tree(root):
                dept = dept_id_map[node.id]
                db_parent = dept_id_to_db_dept_map.get(dept["parent_id"]) if dept["parent_id"] else None
                # 生成部门对象
                dept_id_to_db_dept_map[node.id] = Department(
                    tenant_id=self.tenant_id,
                    id=node.id,
                    name=dept["name"],
                    parent=db_parent,
                    tree_id=tree_id,
                    # NOTE：初始化时 lft, rght, level 均不能为空，
                    # 因此先赋零值，后面 partial_rebuild 会修改
                    lft=0,
                    rght=0,
                    level=0,
                )

        with Department.objects.disable_mptt_updates(), transaction.atomic():
            # 删除所有旧部门
            Department.objects.filter(tenant_id=self.tenant_id).delete()
            # 批量创建新部门
            Department.objects.bulk_create(list(dept_id_to_db_dept_map.values()), batch_size=1000)
            # 逐棵对当前数据源的树进行重建
            for tree_id in mptt_tree_ids:
                Department.objects.partial_rebuild(tree_id=tree_id, tenant_id=self.tenant_id)

    def _generate_tree_id(self) -> int:
        """
        在 MPTT 中，单个 tree_id 只能用于一棵树，因此需要为不同的树分配不同的 ID

        分配实现：利用 MySQL 自增 ID 分配 tree_id（不需要包含到事务中，虽然可能造成浪费）
        """
        return DepartmentRelationMPTTTree.objects.create(tenant_id=self.tenant_id).id

    def handle_subject_to_delete(self):
        """处理 SubjectToDelete 中的部门数据"""
        new_ids = {d["id"] for d in self.new_departments}
        old_ids = {d.id for d in self.old_departments}

        # 新部门，需要从待删除里移除
        SubjectToDelete.objects.filter(
            tenant_id=self.tenant_id,
            subject_type=SubjectType.DEPARTMENT.value,
            subject_id__in=[str(i) for i in new_ids - old_ids],
        ).delete()

        # 旧部门，需要添加到待删除列表
        SubjectToDelete.objects.bulk_create(
            [
                SubjectToDelete(
                    tenant_id=self.tenant_id,
                    subject_type=SubjectType.DEPARTMENT.value,
                    subject_id=str(dept_id),
                )
                for dept_id in old_ids
            ],
            batch_size=100,
            ignore_conflicts=True,
        )

    def sync_to_db(self):
        """SaaS DB 相关变更"""
        with transaction.atomic():
            # 同步部门
            self.sync()
            self.handle_subject_to_delete()


class DBDepartmentSyncExactInfo(BaseSyncDBService):
    """部门额外数据"""

    def __init__(self, tenant_id: str):
        """初始数据"""
        self.tenant_id = tenant_id
        self.departments = list(Department.objects.filter(tenant_id=self.tenant_id))
        self.department_members = list(DepartmentMember.objects.filter(tenant_id=self.tenant_id))
        self.id_to_new_info = self._calculate()

    def _calculate(self) -> Dict[int, Dict]:
        """ "同步部门额外数据

        计算出的数据：
        1. 部门的祖先
        2. 部门的直接子部门数量
        3. 部门的直接用户数
        4. 部门的递归用户数
        """
        # # 这里不可使用 parent，否则由于 parent 是外键关联，会引起 DB 查询
        parent_relations = [(d.id, d.parent_id) for d in self.departments]
        # 根据部门父子关系，构建森林; 时间复杂度 O(n)
        forest_roots = build_forest_with_parent_relations(parent_relations)

        # 逐棵树使用 BFS 进行遍历，记录（1）每个节点的祖先（2）每个节点的孩子数量; 时间复杂度 O(n)
        ancestors_map: Dict[int, List] = defaultdict(list)
        child_count_map: Dict[int, int] = defaultdict(int)
        for root in forest_roots:
            # 使用 BFS 遍历树，保证了父节点会先被遍历到，这样计算祖先时，直接上级的祖先已经计算好了，可以直接使用
            for node in bfs_traversal_tree(root):
                child_count_map[node.id] = len(node.children)
                # 计算祖先：父节点的祖先 + 父节点
                ancestors_map[node.id] = ancestors_map[node.parent_id] + [node.parent_id] if node.parent_id else []

        # 计算每个部门的成员数量
        member_count_map: Dict[int, int] = defaultdict(int)
        for dm in self.department_members:
            member_count_map[dm.department_id] += 1

        # 计算每个部门的递归成员数量；时间复杂度：用户数 * (用户平均所在直接部门数 * 部门平均深度)
        # 1. 记录每个用户与部门，包括祖先部门关系
        # Note: 这里的用户与部门关系记录是一个集合，避免重复
        user_dept_paris: Set[Tuple[str, int]] = set()
        for dm in self.department_members:
            # 用户所在的部门
            user_dept_paris.add((dm.username, dm.department_id))
            # 用户所在的祖先部门
            for ancestor in ancestors_map[dm.department_id]:
                user_dept_paris.add((dm.username, ancestor))
        # 2. 统计每个部门的递归成员数量
        recursive_member_count_map: Dict[int, int] = defaultdict(int)
        for _, dept_id in user_dept_paris:
            recursive_member_count_map[dept_id] += 1

        # 获取每个部门的 Name，用于部门祖先包括 Name 一起更新记录
        id_name_map = {i.id: i.name for i in self.departments}
        # 组装出新数据
        id_to_new_info: Dict[int, Dict] = defaultdict(dict)
        for dept in self.departments:
            ancestors = [{"id": i, "name": id_name_map[i]} for i in ancestors_map[dept.id]]
            id_to_new_info[dept.id] = {
                "ancestors": json.dumps(ancestors) if ancestors else "",
                "child_count": child_count_map[dept.id],
                "member_count": member_count_map[dept.id],
                "recursive_member_count": recursive_member_count_map[dept.id],
            }

        return id_to_new_info

    def update_exact_info(self):
        """更新部门的计算的冗余存储数据"""
        should_update = []
        for dept in self.departments:
            new_info = self.id_to_new_info[dept.id]
            ancestors = new_info["ancestors"]
            child_count = new_info["child_count"]
            member_count = new_info["member_count"]
            recursive_member_count = new_info["recursive_member_count"]

            if (
                dept.child_count != child_count
                or dept.member_count != member_count
                or dept.recursive_member_count != recursive_member_count
                or dept.ancestors != ancestors
            ):
                dept.child_count = child_count
                dept.member_count = member_count
                dept.recursive_member_count = recursive_member_count
                dept.ancestors = ancestors
                should_update.append(dept)

        if not should_update:
            return

        Department.objects.bulk_update(
            should_update, ["ancestors", "child_count", "member_count", "recursive_member_count"], batch_size=1000
        )

    def sync_to_db(self):
        """SaaS DB 相关变更"""
        with transaction.atomic():
            # 更新部门冗余信息
            self.update_exact_info()
