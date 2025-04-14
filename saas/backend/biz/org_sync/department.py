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
import logging
from collections import defaultdict
from typing import Dict, List, Set, Tuple

from backend.apps.organization.models import Department, DepartmentMember, SubjectToDelete
from backend.component import usermgr
from backend.service.constants import SubjectType

from .base import BaseSyncDBService
from .util import convert_list_for_mptt

logger = logging.getLogger("organization")


class DBDepartmentSyncService(BaseSyncDBService):
    """部门同步服务"""

    def __init__(self):
        """初始数据"""
        self.new_departments = usermgr.list_department()
        self.old_departments = list(Department.objects.all())

    def created_handler(self):
        """关于新建部门，DB的处理"""
        # 新老数据对比 => 需要新增的部门
        old_department_id_set = {i.id for i in self.old_departments}
        created_departments = [
            Department(
                id=dept["id"],
                parent_id=dept["parent"],
                name=dept["name"],
                category_id=dept["category_id"],
                order=dept["order"],
            )
            for dept in self.new_departments
            if dept["id"] not in old_department_id_set
        ]

        if not created_departments:
            return

        # 1. 使用BFS转换出可顺序插入的列表，使用mptt进行插入
        id_parent_ids = [(i.id, i.parent_id) for i in created_departments]
        sorted_departments = convert_list_for_mptt(id_parent_ids)  # 把父级部门排到前面, 保证父级部门会被先创建

        # 2. 以mptt方式添加部门，不可批量添加，因为存在依赖，添加时parent可能未存在
        created_department_dict = {i.id: i for i in created_departments}
        for dept_id in sorted_departments:
            dept = created_department_dict[dept_id]
            parent_department = None
            if dept.parent_id:
                try:
                    parent_department = Department.objects.get(id=dept.parent_id)
                except Exception:  # pylint: disable=broad-except
                    # 记录错误信息，然后将异常往上抛，因为Django QuerySet get异常并不会输出具体ID是什么，不利于问题排查
                    logger.exception(f"parent department(id:{dept.parent_id}) not found")
                    raise
            # 对于mptt，必须是parent实例对象，无法使用parent_id代替
            dept.parent = parent_department
            dept.save()

        # 移除待删除的部门
        SubjectToDelete.objects.filter(
            subject_type=SubjectType.DEPARTMENT.value, subject_id__in=[str(i.id) for i in created_departments]
        ).delete()

    def deleted_handler(self):
        """关于删除部门，DB的处理"""
        # 新老数据对比 => 需要删除的部门
        new_department_id_set = {i["id"] for i in self.new_departments}
        deleted_departments = [dept for dept in self.old_departments if dept.id not in new_department_id_set]

        if not deleted_departments:
            return

        # 1. 使用BFS转换出可顺序删除的列表，使用mptt进行删除
        id_parent_ids = [(i.id, i.parent_id) for i in deleted_departments]
        sorted_departments = convert_list_for_mptt(
            id_parent_ids, reverse=True
        )  # 把子级部门排到前面, 保证先删除的是子级部门

        # 2. 以mptt方式删除部门，不可批量删除，因为存在依赖，删除时可能前一个parent也在删除中，树无法变更
        created_department_dict = {i.id: i for i in deleted_departments}
        for dept_id in sorted_departments:
            created_department_dict[dept_id].delete()

        # TODO: DB里其他表存在了被删的记录如何处理？不处理可能展示有些问题，比如权限模板授权表等等

        # 记录待删除的部门
        subject_to_delete = [
            SubjectToDelete(subject_id=str(dept_id), subject_type=SubjectType.DEPARTMENT.value)
            for dept_id in sorted_departments
        ]
        SubjectToDelete.objects.bulk_create(subject_to_delete, batch_size=100, ignore_conflicts=True)

    def updated_parent_handler(self):
        """关于更新部门拓扑，DB的处理"""
        # 只更新变更了的parent的部门
        new_department_parent_dict = {i["id"]: i["parent"] for i in self.new_departments}
        new_department_id_set = set(new_department_parent_dict.keys())
        updated_parent_departments = []
        for dept in self.old_departments:
            # 新部门里不存则表示将被删除，不需要处理
            if dept.id not in new_department_id_set:
                continue
            if dept.parent_id != new_department_parent_dict[dept.id]:
                updated_parent_departments.append({"id": dept.id, "parent_id": new_department_parent_dict[dept.id]})

        if not updated_parent_departments:
            return

        # SaaS使用mptt进行更新parent
        for d in updated_parent_departments:
            # Note: 这里必须重新获取部门对象，否则会是旧的数据，这样会导致更新时lft\rght\level错误
            dept = Department.objects.get(id=d["id"])
            dept.parent = Department.objects.get(id=d["parent_id"]) if d["parent_id"] else None
            dept.save()

    def updated_handler(self):
        """关于更新部门基本信息，DB的处理"""
        # 只更新变更了的name,category_id,order的部门
        new_department_dict = {i["id"]: i for i in self.new_departments}
        updated_departments = []
        for dept in self.old_departments:
            new_dept = new_department_dict.get(dept.id)
            # 新部门里不存则表示将被删除，不需要处理
            if not new_dept:
                continue
            if (dept.name, dept.category_id, dept.order) != (
                new_dept["name"],
                new_dept["category_id"],
                new_dept["order"],
            ):
                dept.name = new_dept["name"]
                dept.category_id = new_dept["category_id"]
                dept.order = new_dept["order"]
                updated_departments.append(dept)

        if not updated_departments:
            return

        Department.objects.bulk_update(updated_departments, ["name", "order", "category_id"], batch_size=1000)

    def sync_to_db(self):
        """SaaS DB 相关变更"""
        # 新增部门
        self.created_handler()
        # 更新部门拓扑
        self.updated_parent_handler()
        # 删除部门
        self.deleted_handler()
        # 更新部门基本信息
        self.updated_handler()


class DBDepartmentSyncExactInfo(BaseSyncDBService):
    """部门额外数据"""

    def __init__(self):
        """初始数据"""
        self.new_exact_infos = self.calculate_new_data()
        self.old_exact_infos = list(Department.objects.all())

    def _calculate_children(self, departments: List[Department]) -> Tuple[Set, Dict[int, List]]:
        """根据id和parentID的相邻关系，计算出每个节点的孩子列表和根节点"""
        root = set()  # 记录每棵树的根节点，后面用于遍历树
        # 存储每个节点的孩子
        children_map = defaultdict(list)
        for dept in departments:
            parent_id = dept.parent_id  # 这里不可使用parent，否则由于parent是外键关联，会引起DB查询
            # 如果parent为None，则为单独的树root
            if not parent_id:
                root.add(dept.id)
                continue
            # 作为其他节点的孩子
            children_map[parent_id].append(dept.id)

        return root, children_map

    def _calculate_ancestors(
        self, departments: List[Department], root: Set, children_map: Dict[int, List]
    ) -> Dict[int, List]:
        """使用BFS从根节点遍历树的每个节点，计算出每个节点的祖先"""
        ancestors_map: Dict[int, List] = defaultdict(list)
        # 进行BFS遍历
        node_set = {i.id for i in departments}
        queue = list(root)  # 使用index来模拟队列即可，不使用python的deque数据结构
        left_point = 0  # 初始化出队列指针
        right_point = len(queue)  # 初始化入队列指针
        # 当出队列指针=入队列指针时，说明队列为空，没有节点可遍历了
        while left_point < right_point:
            # 遍历队列里的值
            cnt = right_point - left_point
            for i in range(cnt):
                node = queue[left_point + i]
                # 避免出现环的情况下，死循环
                if node not in node_set:
                    continue
                node_set.remove(node)
                # 检测是否有孩子，有的话则入队列
                if children_map[node]:
                    queue.extend(children_map[node])  # 入队列
                    right_point += len(children_map[node])  # 入队列指针往后移动
                    # 并且每个孩子的祖先为 上级的祖先+上级
                    ancestors = ancestors_map[node] + [node]
                    for child in children_map[node]:
                        ancestors_map[child] = ancestors
            # 出队列指针向后移动位置
            left_point += cnt

        return ancestors_map

    def _calculate_member_count(self, department_members: List[DepartmentMember]) -> Dict[int, int]:
        """计算每个部门成员数量"""
        member_count_map: Dict[int, int] = defaultdict(int)
        for dm in department_members:
            member_count_map[dm.department_id] += 1

        return member_count_map

    def _calculate_recursive_member_count(
        self, department_members: List[DepartmentMember], ancestors_map: Dict[int, list]
    ) -> Dict[int, int]:
        """计算每个部门的递归成员数量"""
        # 每个用户的所在的所有部门(包括部门的祖先)
        user_depts_dict = defaultdict(set)
        for dm in department_members:
            user_depts_dict[dm.user_id].add(dm.department_id)
            user_depts_dict[dm.user_id].update(ancestors_map[dm.department_id])

        # 遍历每个用户，对于所在的每个部门人数 + 1，得到每个部门的递归用户数
        recursive_member_count_map: Dict[int, int] = defaultdict(int)
        for dept_set in user_depts_dict.values():
            for dept in dept_set:
                recursive_member_count_map[dept] += 1

        return recursive_member_count_map

    def calculate_new_data(self) -> List[Dict]:
        """
        计算出的数据：
        1. 部门的祖先
        2. 部门的直接子部门数量
        3. 部门的直接用户数
        4. 部门的用户数(包括递归子部门)

        计算方法：
        1. 遍历所有节点，记录每个节点的孩子，最后可得到每个节点的直接子部门数量
        2. 从Root遍历到叶子节点，当前节点祖先=直接上级的祖先+直接上级
        3. 查询DepartmentMember，遍历每条记录，可得到每个部门的用户数(不包含递归子部门的)
        4. 查询DepartmentMember，遍历得到每个用户的所在的部门(包括部门的祖先)，遍历每个用户，对于所在的每个部门人数+1，得到每个部门的递归用户数
        """
        # 预先查询需要用于计算数据：部门、部门成员
        depts = list(Department.objects.all())
        dept_members = list(DepartmentMember.objects.all())

        # NOTE: 以下计算是使用树等方式计算需要的数据，不可用直接查询DB计算，否则DB查询量将会非常大

        # 1. 遍历所有节点，记录每个节点的孩子，最后可得到每个节点的直接子部门数量
        root, children_map = self._calculate_children(depts)
        child_count_map = {dept_id: len(children) for dept_id, children in children_map.items()}

        # 2. 从Root遍历到叶子节点，当前节点祖先=直接上级的祖先+直接上级
        ancestors_map = self._calculate_ancestors(depts, root, children_map)

        # 3. 查询DepartmentMember，遍历每条记录，可得到每个部门的用户数(不包含递归子部门的)
        member_count_map = self._calculate_member_count(dept_members)

        # 4. 查询DepartmentMember，遍历得到每个用户的所在的部门(包括部门的祖先)，遍历每个用户，对于所在的每个部门人数+1，得到每个部门的递归用户数
        recursive_member_count_map = self._calculate_recursive_member_count(dept_members, ancestors_map)

        # 组装出新数据
        new_exact_infos = []
        # 获取每个部门的Name，用于部门祖先包括Name一起更新记录
        id_name_map = {i.id: i.name for i in depts}
        for dept in depts:
            ancestor_list = [{"id": i, "name": id_name_map[i]} for i in ancestors_map[dept.id]]
            ancestors = json.dumps(ancestor_list) if ancestor_list else ""
            new_exact_infos.append(
                {
                    "id": dept.id,
                    "ancestors": ancestors,
                    "child_count": child_count_map.get(dept.id, 0),
                    "member_count": member_count_map[dept.id],
                    "recursive_member_count": recursive_member_count_map[dept.id],
                }
            )
        return new_exact_infos

    def updated_exact_info_handle(self):
        """更新部门的计算的冗余存储数据"""
        new_exact_info_dict = {i["id"]: i for i in self.new_exact_infos}
        updated = []
        for dept in self.old_exact_infos:
            ancestors = new_exact_info_dict[dept.id]["ancestors"]
            child_count = new_exact_info_dict[dept.id]["child_count"]
            member_count = new_exact_info_dict[dept.id]["member_count"]
            recursive_member_count = new_exact_info_dict[dept.id]["recursive_member_count"]

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
                updated.append(dept)

        if not updated:
            return

        Department.objects.bulk_update(
            updated, ["ancestors", "child_count", "member_count", "recursive_member_count"], batch_size=1000
        )

    def sync_to_db(self):
        """SaaS DB 相关变更"""
        # 更新部门
        self.updated_exact_info_handle()
