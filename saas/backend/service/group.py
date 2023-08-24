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
from typing import Dict, Generator, List, Tuple

from django.db import transaction
from django.db.models import F
from pydantic import BaseModel, parse_obj_as

from backend.apps.group.models import Group
from backend.apps.organization.models import Department, DepartmentMember, User
from backend.component import iam

from .constants import SubjectType
from .models import Subject


class SubjectGroup(BaseModel):
    """
    后端返回的Subject的Group
    """

    type: str
    id: str
    expired_at: int
    created_at: str  # 后端json返回的格式化时间

    # 从部门继承的信息
    department_id: int = 0
    department_name: str = ""


class GroupSubject(BaseModel):
    """
    后端返回的GroupSubject关系
    """

    subject: Subject
    group: Subject
    expired_at: int


class GroupCreation(BaseModel):
    name: str
    description: str
    readonly: bool = False

    # NOTE: 只在group创建时有用
    source_system_id: str = ""
    hidden: bool = False
    apply_disable: bool = False


class GroupMemberExpiredAt(Subject):
    expired_at: int


class GroupService:
    def create(self, info: GroupCreation, creator: str) -> Group:
        """
        创建用户组
        """
        group = Group(
            name=info.name,
            description=info.description,
            readonly=info.readonly,
            creator=creator,
            source_system_id=info.source_system_id,
            hidden=info.hidden,
            apply_disable=info.apply_disable,
        )
        group.save(force_insert=True)

        # 创建后端的用户组
        iam.create_subjects([{"type": SubjectType.GROUP.value, "id": str(group.id), "name": info.name}])

        return group

    def batch_create(self, infos: List[GroupCreation], creator: str) -> List[Group]:
        """
        批量创建用户组
        """
        groups = [
            Group(
                name=one.name,
                description=one.description,
                readonly=one.readonly,
                creator=creator,
                source_system_id=one.source_system_id,
                hidden=one.hidden,
            )
            for one in infos
        ]
        with transaction.atomic():
            # 为了获取返回的insert id, 不能使用bulk_create
            for group in groups:
                group.save()
            iam.create_subjects([{"type": SubjectType.GROUP.value, "id": str(g.id), "name": g.name} for g in groups])

        return groups

    def update(self, group: Group, name: str, description: str, apply_disable: bool, updater: str) -> Group:
        """
        更新用户组信息
        """
        group.name = name
        group.description = description
        group.updater = updater
        group.apply_disable = apply_disable

        with transaction.atomic():
            group.save()
            iam.update_subjects([{"type": SubjectType.GROUP.value, "id": str(group.id), "name": name}])

        return group

    def delete(self, group_id: int):
        """
        删除用户组
        """
        Group.objects.filter(id=group_id).delete()
        iam.delete_subjects([{"type": SubjectType.GROUP.value, "id": str(group_id)}])

    def add_members(self, group_id: int, members: List[Subject], expired_at: int):
        """
        用户组添加成员
        """
        # 如果用户只传了admin, 这里会为空报错, 兼容下
        if not members:
            return

        type_count = iam.add_subject_members(
            SubjectType.GROUP.value, str(group_id), expired_at, [m.dict() for m in members]
        )
        Group.objects.filter(id=group_id).update(
            user_count=F("user_count") + type_count[SubjectType.USER.value],
            department_count=F("department_count") + type_count[SubjectType.DEPARTMENT.value],
        )

    def remove_members(self, group_id: str, subjects: List[Subject]):
        """
        用户组删除成员
        """
        type_count = iam.delete_subject_members(SubjectType.GROUP.value, group_id, [one.dict() for one in subjects])
        Group.objects.filter(id=group_id).update(
            user_count=F("user_count") - type_count[SubjectType.USER.value],
            department_count=F("department_count") - type_count[SubjectType.DEPARTMENT.value],
        )

    def check_subject_groups_belong(self, subject: Subject, group_ids: List[int]) -> Dict[int, bool]:
        """
        校验Subject与用户组是否存在关系
        """
        group_belongs = iam.check_subject_groups_belong(subject.type, subject.id, group_ids)

        # 将group_id从str转为int
        return {int(k): v for k, v in group_belongs.items()}

    def check_subject_groups_quota(self, subject: Subject, group_ids: List[int]) -> None:
        """
        校验Subject与用户组是否数量超限
        """
        iam.check_subject_groups_quota(subject.type, subject.id, group_ids)

    def list_subject_group(self, subject: Subject, limit: int = 10, offset: int = 0) -> Tuple[int, List[SubjectGroup]]:
        """
        查询Subject的Group关系列表
        """
        iam_data = iam.get_subject_groups(subject.type, subject.id, limit=limit, offset=offset)
        count = iam_data["count"]

        relations = parse_obj_as(List[SubjectGroup], iam_data["results"])

        return count, relations

    def list_system_subject_group(
        self, system_id: str, subject: Subject, limit: int = 10, offset: int = 0
    ) -> Tuple[int, List[SubjectGroup]]:
        """
        查询有系统权限Subject的Group关系列表
        """
        iam_data = iam.get_system_subject_groups(system_id, subject.type, subject.id, limit=limit, offset=offset)
        count = iam_data["count"]

        relations = parse_obj_as(List[SubjectGroup], iam_data["results"])

        return count, relations

    def list_user_department_group(self, subject: Subject) -> List[SubjectGroup]:
        """
        查询user的部门递归的Group
        """
        if subject.type != SubjectType.USER.value:
            return []

        relations = []
        user = User.objects.get(username=subject.id)
        # 查询用户直接加入的部门
        department_ids = DepartmentMember.objects.filter(user_id=user.id).values_list("department_id", flat=True)
        department_set = set()
        group_id_set = set()
        for department in Department.objects.filter(id__in=department_ids):
            # 查询部门继承的所有部门
            for ancestor in department.get_ancestors(include_self=True):
                if ancestor.id in department_set:
                    continue
                department_set.add(ancestor.id)

                # NOTE: 获取部门加入的所有组列表, 注意可能会有性能问题(分页查询)
                all_subject_groups = iam.list_all_subject_groups(SubjectType.DEPARTMENT.value, str(ancestor.id))
                for sg in all_subject_groups:
                    if sg["id"] in group_id_set:
                        continue
                    group_id_set.add(sg["id"])

                    relations.append(SubjectGroup(department_id=ancestor.id, department_name=ancestor.name, **sg))

        return relations

    def list_subject_group_before_expired_at(
        self, subject: Subject, expired_at: int, limit: int, offset: int
    ) -> Tuple[int, List[SubjectGroup]]:
        """
        查询subject在指定过期时间之前的相关Group
        """
        iam_data = iam.get_subject_groups(subject.type, subject.id, expired_at=expired_at, limit=limit, offset=offset)

        count = iam_data["count"]
        relations = parse_obj_as(List[SubjectGroup], iam_data["results"])
        return count, relations

    def list_system_subject_group_before_expired_at(
        self, system_id: str, subject: Subject, expired_at: int, limit: int, offset: int
    ) -> Tuple[int, List[SubjectGroup]]:
        """
        查询有系统权限subject在指定过期时间之前的相关Group
        """
        iam_data = iam.get_system_subject_groups(
            system_id, subject.type, subject.id, expired_at=expired_at, limit=limit, offset=offset
        )

        count = iam_data["count"]
        relations = parse_obj_as(List[SubjectGroup], iam_data["results"])
        return count, relations

    def list_all_subject_group_before_expired_at(self, subject: Subject, expired_at: int) -> List[SubjectGroup]:
        """
        查询所有subject在指定过期时间之前的相关Group
        """
        all_subject_groups = iam.list_all_subject_groups(subject.type, subject.id, expired_at=expired_at)
        relations = parse_obj_as(List[SubjectGroup], all_subject_groups)
        return relations

    def get_member_count_before_expired_at(self, group_id: int, expired_at: int) -> int:
        """
        获取过期的成员数量
        """
        data = iam.list_subject_member_before_expired_at(SubjectType.GROUP.value, str(group_id), expired_at, 0, 0)
        return data["count"]

    def list_paging_members_before_expired_at(
        self, group_id: int, expired_at: int, limit: int = 10, offset: int = 0
    ) -> Tuple[int, List[SubjectGroup]]:
        """
        分页查询用户组过期的成员
        """
        data = iam.list_subject_member_before_expired_at(
            SubjectType.GROUP.value, str(group_id), expired_at, limit, offset
        )
        return data["count"], parse_obj_as(List[SubjectGroup], data["results"])

    def list_exist_groups_before_expired_at(self, group_ids: List[int], expired_at: int) -> List[int]:
        """
        筛选出存在的即将过期的用户组id
        """
        subjects = [{"type": SubjectType.GROUP.value, "id": str(_id)} for _id in group_ids]

        exist_group_ids = []
        for i in range(0, len(subjects), 500):
            part_subjects = subjects[i : i + 500]
            data = iam.list_exist_subjects_before_expired_at(part_subjects, expired_at)
            exist_group_ids.extend([int(m["id"]) for m in data])

        return exist_group_ids

    def update_subject_groups_expired_at(self, subject_expired_at: GroupMemberExpiredAt, group_ids: List[int]):
        """
        subject group 续期
        """
        for group_id in group_ids:
            iam.update_subject_members_expired_at(
                SubjectType.GROUP.value,
                str(group_id),
                [subject_expired_at.dict()],
            )

    def update_members_expired_at(self, group_id: int, members: List[GroupMemberExpiredAt]):
        """
        更新用户组成员的过期时间
        """
        iam.update_subject_members_expired_at(
            SubjectType.GROUP.value,
            str(group_id),
            [one.dict() for one in members],
        )

    def list_paging_group_member(self, group_id: int, limit: int, offset: int) -> Tuple[int, List[SubjectGroup]]:
        """分页查询用户组成员"""
        data = iam.list_subject_member(SubjectType.GROUP.value, str(group_id), limit, offset)
        return data["count"], parse_obj_as(List[SubjectGroup], data["results"])

    def list_all_group_member(self, group_id: int) -> List[SubjectGroup]:
        """
        分页查询用户组所有成员

        NOTE: 谨慎使用, 性能问题
        """
        data = iam.list_all_subject_member(SubjectType.GROUP.value, str(group_id))
        return parse_obj_as(List[SubjectGroup], data)

    def list_group_subject_before_expired_at(self, expired_at: int) -> Generator[GroupSubject, None, None]:
        """
        查询在指定过期时间之前的相关GroupSubject关系
        """
        limit, offset = 1000, 0
        while True:
            iam_data = iam.list_group_subject_before_expired_at(expired_at=expired_at, limit=limit, offset=offset)
            if len(iam_data["results"]) == 0:
                break

            relations = parse_obj_as(List[GroupSubject], iam_data["results"])
            for relation in relations:
                yield relation

            offset += limit

    def list_rbac_group_by_resource(
        self,
        system_id: str,
        action_id: str,
        resource_type_system_id: int,
        resource_type_id: str,
        resource_id: str,
        bk_iam_path: str = "",
    ) -> List[Subject]:
        """
        查询rbac资源权限的用户组
        """
        attribute = {}
        if bk_iam_path:
            attribute["_bk_iam_path_"] = [bk_iam_path]

        data = iam.query_rbac_group_by_resource(
            system_id, action_id, resource_type_system_id, resource_type_id, resource_id, attribute=attribute
        )
        return parse_obj_as(List[Subject], data)
