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
from datetime import datetime
from typing import Dict, List, Optional

from django.conf import settings
from django.db import connection, transaction
from django.db.models import Count
from django.utils.timezone import make_aware, utc
from django.utils.translation import gettext as _
from pydantic import BaseModel

from backend.apps.organization.models import Department, User
from backend.apps.role.models import Role, RoleGroupMember, RoleRelatedObject
from backend.apps.subject_template.models import SubjectTemplate, SubjectTemplateGroup, SubjectTemplateRelation
from backend.biz.subject import SubjectInfoList
from backend.common.error_codes import error_codes
from backend.common.time import expired_at_display
from backend.service.constants import RoleRelatedObjectType, RoleType, SubjectType
from backend.service.models.subject import Subject
from backend.service.role import RoleService
from backend.service.subject_template import SubjectTemplateService


class SubjectTemplateMemberBean(BaseModel):
    type: str
    id: str
    name: str = ""
    full_name: str = ""
    member_count: int = 0
    user_departments: Optional[List[str]] = None
    created_time: datetime


class SubjectTemplateGroupBean(BaseModel):
    id: int
    name: str
    description: str

    expired_at: int
    expired_at_display: str
    created_time: datetime

    template_id: int

    # 从部门继承的信息
    department_id: int = 0
    department_name: str = ""

    user_count: int = 0
    department_count: int = 0


class SubjectTemplateCheckBiz:
    def check_member_count(self, subject_template_id: int, new_member_count: int):
        """
        检查人员模版成员数量未超限
        """
        exists_count = SubjectTemplateRelation.objects.filter(template_id=subject_template_id).count()
        member_limit = settings.SUBJECT_AUTHORIZATION_LIMIT.get("subject_template_member_limit", 1000)
        if exists_count + new_member_count > member_limit:
            raise error_codes.VALIDATE_ERROR.format(
                _("超过人员模版最大可添加成员数{}").format(member_limit),
                True,
            )

    def check_role_subject_template_name_unique(self, role_id: int, name: str, template_id: int = 0):
        """
        检查人员模版的名字是否已存在
        """
        role_template_ids = RoleRelatedObject.objects.list_role_object_ids(
            role_id, RoleRelatedObjectType.SUBJECT_TEMPLATE.value
        )
        if template_id in role_template_ids:
            role_template_ids.remove(template_id)
        if SubjectTemplate.objects.filter(name=name, id__in=role_template_ids).exists():
            raise error_codes.CONFLICT_ERROR.format(_("存在同名人员模版"))

    def check_role_subject_template_limit(self, role: Role, new_subject_template_count: int):
        """
        检查角色下的人员模版数量是否超限
        """
        # 只针对普通分级管理，对于超级管理员和系统管理员则无限制
        if role.type in [RoleType.SUPER_MANAGER.value, RoleType.SYSTEM_MANAGER.value]:
            return

        limit = settings.SUBJECT_AUTHORIZATION_LIMIT["grade_manager_subject_template_limit"]
        role_group_ids = RoleRelatedObject.objects.list_role_object_ids(
            role.id, RoleRelatedObjectType.SUBJECT_TEMPLATE.value
        )
        if len(role_group_ids) + new_subject_template_count > limit:
            raise error_codes.VALIDATE_ERROR.format(
                _("超过分级管理员最大可创建人员模版数{}").format(limit),
                True,
            )


class SubjectTemplateBiz:
    svc = SubjectTemplateService()

    role_svc = RoleService()

    def create(
        self,
        role: Role,
        name: str,
        description: str,
        creator: str,
        subjects: List[Subject],
        readonly: bool = False,
        source_group_id: int = 0,
    ) -> SubjectTemplate:
        with transaction.atomic():
            # 创建template
            subject_template = self.svc.create(
                name=name,
                description=description,
                creator=creator,
                subjects=subjects,
                readonly=readonly,
                source_group_id=source_group_id,
            )

            # 关联角色
            RoleRelatedObject.objects.create_subject_template_relation(role.id, subject_template.id)

        return subject_template

    def get_group_count_dict(self, template_ids: List[int]) -> Dict[int, int]:
        q = (
            SubjectTemplateGroup.objects.order_by()
            .filter(template_id__in=template_ids)
            .values("template_id")
            .annotate(count=Count("*"))
        )
        return {item["template_id"]: item["count"] for item in q}

    def delete(self, template_id: int):
        return self.svc.delete(template_id)

    def delete_group(self, template_id: int, group_id: int):
        self.svc.delete_group(template_id, group_id)

        # 同步删除role group member
        RoleGroupMember.objects.filter(group_id=group_id, subject_template_id=template_id).delete()

    def add_members(self, template_id: int, members: List[Subject]):
        group_ids = self.svc.add_members(template_id, members)

        # 同步添加role group member
        role_group_members = []
        for group_id in group_ids:
            # 添加role group member
            role = self.role_svc.get_role_by_group_id(group_id)
            if role.type == RoleType.SUBSET_MANAGER.value:
                role_id = self.role_svc.get_parent_id(role.id)
                subset_id = role.id
            else:
                role_id = role.id
                subset_id = 0

            role_group_members.extend(
                [
                    RoleGroupMember(
                        role_id=role_id,
                        group_id=group_id,
                        subset_id=subset_id,
                        subject_template_id=template_id,
                        subject_id=one.id,
                        subject_type=one.type,
                    )
                    for one in members
                ]
            )

        if role_group_members:
            RoleGroupMember.objects.bulk_create(role_group_members, batch_size=100, ignore_conflicts=True)

    def delete_members(self, template_id: int, members: List[Subject]):
        self.svc.delete_members(template_id, members)

        # 同步删除role group member
        user_ids = [one.id for one in members if one.type == SubjectType.USER.value]
        if user_ids:
            RoleGroupMember.objects.filter(
                subject_template_id=template_id, subject_type=SubjectType.USER.value, subject_id__in=user_ids
            ).delete()

        department_ids = [one.id for one in members if one.type == SubjectType.DEPARTMENT.value]
        if department_ids:
            RoleGroupMember.objects.filter(
                subject_template_id=template_id,
                subject_type=SubjectType.DEPARTMENT.value,
                subject_id__in=department_ids,
            ).delete()

    def convert_to_subject_template_members(
        self, relations: List[SubjectTemplateRelation]
    ) -> List[SubjectTemplateMemberBean]:
        subjects = [Subject(type=relation.subject_type, id=relation.subject_id) for relation in relations]
        subject_info_list = SubjectInfoList(subjects)

        # 查询用户的部门
        usernames = [one.id for one in subjects if one.type == SubjectType.USER.value]
        user_dict = {u.username: u for u in User.objects.filter(username__in=usernames)} if usernames else {}

        # 组合数据结构
        subject_template_member_beans = []
        for subject, relation in zip(subjects, relations):
            subject_info = subject_info_list.get(subject)
            if not subject_info:
                continue

            # 填充用户所属的部门
            user_departments = None
            if subject.type == SubjectType.USER.value:
                user = user_dict.get(subject.id, None)
                if user:
                    user_departments = [d.full_name for d in user.departments]

            subject_template_member_bean = SubjectTemplateMemberBean(
                created_time=relation.created_time,
                user_departments=user_departments,
                **subject_info.dict(),
            )
            subject_template_member_beans.append(subject_template_member_bean)

        return subject_template_member_beans

    def search_member_by_keyword(self, template_id: int, keyword: str) -> List[SubjectTemplateMemberBean]:
        """根据关键词 获取指定人员模版成员列表"""
        queryset = SubjectTemplateRelation.objects.filter(template_id=template_id)
        subject_template_members = self.convert_to_subject_template_members(queryset)
        hit_members = list(
            filter(lambda m: keyword in m.id.lower() or keyword in m.name.lower(), subject_template_members)
        )

        return hit_members

    def get_group_template_count_dict(self, group_ids: List[int]) -> Dict[int, int]:
        q = (
            SubjectTemplateGroup.objects.order_by()
            .filter(group_id__in=group_ids)
            .values("group_id")
            .annotate(count=Count("*"))
        )
        return {item["group_id"]: item["count"] for item in q}

    def get_subject_template_group_count(
        self,
        subject: Subject,
        id: int = 0,
        name: str = "",
        description: str = "",
        hidden: bool = True,
        group_ids: Optional[List[int]] = None,
        system_id: str = "",
    ) -> int:
        if group_ids is not None and len(group_ids) == 0:
            return 0

        # 构建动态的 WHERE 子句
        where_conditions = []
        params = [subject.type, subject.id]
        if id:
            where_conditions.append("a.id = %s")
            params.append(id)
        if name:
            where_conditions.append("a.name LIKE %s")
            params.append("%" + name + "%")
        if description:
            where_conditions.append("a.description LIKE %s")
            params.append("%" + description + "%")
        if hidden:
            where_conditions.append("a.hidden = 0")
        if group_ids:
            where_conditions.append("a.id IN %s")
            params.append(tuple(group_ids))
        if system_id:
            where_conditions.append("a.source_system_id = %s")
            params.append(system_id)

        sql_query = """
            SELECT
                COUNT(*)
            FROM
                group_group AS a
            LEFT JOIN
                subject_template_subjecttemplategroup AS b ON a.id = b.group_id
            LEFT JOIN
                subject_template_subjecttemplaterelation AS c ON b.template_id = c.template_id
            WHERE
                c.subject_type = %s AND c.subject_id = %s
        """

        if where_conditions:
            sql_query += " AND " + " AND ".join(where_conditions)

        with connection.cursor() as cursor:
            cursor.execute(sql_query, params)
            result = cursor.fetchone()

        count = result[0] if result else 0
        return count

    def get_subject_department_template_group_count(
        self,
        subject: Subject,
        id: int = 0,
        name: str = "",
        description: str = "",
        hidden: bool = True,
        group_ids: Optional[List[int]] = None,
        system_id: str = "",
    ) -> int:
        if subject.type != SubjectType.USER.value:
            return 0

        if group_ids is not None and len(group_ids) == 0:
            return 0

        departments = self.get_user_departments(subject.id)
        if not departments:
            return 0

        department_ids = [str(department.id) for department in departments]

        # 构建动态的 WHERE 子句
        where_conditions = []
        params = [SubjectType.DEPARTMENT.value, tuple(department_ids)]
        if id:
            where_conditions.append("a.id = %s")
            params.append(id)
        if name:
            where_conditions.append("a.name LIKE %s")
            params.append("%" + name + "%")
        if description:
            where_conditions.append("a.description LIKE %s")
            params.append("%" + description + "%")
        if hidden:
            where_conditions.append("a.hidden = 0")
        if group_ids:
            where_conditions.append("a.id IN %s")
            params.append(tuple(group_ids))
        if system_id:
            where_conditions.append("a.source_system_id = %s")
            params.append(system_id)

        sql_query = """
            SELECT
                COUNT(*)
            FROM
                group_group AS a
            LEFT JOIN
                subject_template_subjecttemplategroup AS b ON a.id = b.group_id
            LEFT JOIN
                subject_template_subjecttemplaterelation AS c ON b.template_id = c.template_id
            WHERE
                c.subject_type = %s AND c.subject_id IN %s
        """

        if where_conditions:
            sql_query += " AND " + " AND ".join(where_conditions)

        with connection.cursor() as cursor:
            cursor.execute(sql_query, params)
            result = cursor.fetchone()

        count = result[0] if result else 0
        return count

    def list_paging_subject_template_group(
        self,
        subject: Subject,
        id: int = 0,
        name: str = "",
        description: str = "",
        hidden: bool = True,
        group_ids: Optional[List[int]] = None,
        system_id: str = "",
        limit: int = 10,
        offset: int = 0,
    ) -> List[SubjectTemplateGroupBean]:
        if group_ids is not None and len(group_ids) == 0:
            return []

        # 构建动态的 WHERE 子句
        where_conditions = []
        params = [subject.type, subject.id]
        if id:
            where_conditions.append("a.id = %s")
            params.append(id)
        if name:
            where_conditions.append("a.name LIKE %s")
            params.append("%" + name + "%")
        if description:
            where_conditions.append("a.description LIKE %s")
            params.append("%" + description + "%")
        if hidden:
            where_conditions.append("a.hidden = 0")
        if group_ids:
            where_conditions.append("a.id IN %s")
            params.append(tuple(group_ids))
        if system_id:
            where_conditions.append("a.source_system_id = %s")
            params.append(system_id)

        params.extend([limit, offset])

        sql_query = """
            SELECT
                a.id,
                a.name,
                a.description,
                a.user_count,
                a.department_count,
                b.template_id,
                b.expired_at,
                b.created_time
            FROM
                group_group AS a
            LEFT JOIN
                subject_template_subjecttemplategroup AS b ON a.id = b.group_id
            LEFT JOIN
                subject_template_subjecttemplaterelation AS c ON b.template_id = c.template_id
            WHERE
                c.subject_type = %s AND c.subject_id = %s
        """

        if where_conditions:
            sql_query += " AND " + " AND ".join(where_conditions)

        sql_query += " ORDER BY c.id DESC LIMIT %s OFFSET %s;"

        with connection.cursor() as cursor:
            cursor.execute(sql_query, params)

            # 获取结果
            result = cursor.fetchall()

        beans = [
            SubjectTemplateGroupBean(
                id=one[0],
                name=one[1],
                description=one[2],
                user_count=one[3],
                department_count=one[4],
                template_id=one[5],
                expired_at=one[6],
                expired_at_display=expired_at_display(one[6]),
                created_time=make_aware(one[7], timezone=utc),
            )
            for one in result
        ]

        return beans

    def list_paging_subject_department_template_group(
        self,
        subject: Subject,
        id: int = 0,
        name: str = "",
        description: str = "",
        hidden: bool = True,
        group_ids: Optional[List[int]] = None,
        system_id: str = "",
        limit: int = 10,
        offset: int = 0,
    ) -> List[SubjectTemplateGroupBean]:
        if subject.type != SubjectType.USER.value:
            return []

        if group_ids is not None and len(group_ids) == 0:
            return []

        departments = self.get_user_departments(subject.id)
        if not departments:
            return []

        department_dict = {str(department.id): department.name for department in departments}

        # 构建动态的 WHERE 子句
        params = [SubjectType.DEPARTMENT.value, tuple(department_dict.keys())]
        where_conditions = []
        if id:
            where_conditions.append("a.id = %s")
            params.append(id)
        if name:
            where_conditions.append("a.name LIKE %s")
            params.append("%" + name + "%")
        if description:
            where_conditions.append("a.description LIKE %s")
            params.append("%" + description + "%")
        if hidden:
            where_conditions.append("a.hidden = 0")
        if group_ids:
            where_conditions.append("a.id IN %s")
            params.append(tuple(group_ids))
        if system_id:
            where_conditions.append("a.source_system_id = %s")
            params.append(system_id)

        params.extend([limit, offset])

        sql_query = """
            SELECT
                a.id,
                a.name,
                a.description,
                a.user_count,
                a.department_count,
                b.template_id,
                b.expired_at,
                b.created_time,
                c.subject_id
            FROM
                group_group AS a
            LEFT JOIN
                subject_template_subjecttemplategroup AS b ON a.id = b.group_id
            LEFT JOIN
                subject_template_subjecttemplaterelation AS c ON b.template_id = c.template_id
            WHERE
                c.subject_type = %s AND c.subject_id IN %s
        """

        if where_conditions:
            sql_query += " AND " + " AND ".join(where_conditions)

        sql_query += " ORDER BY c.id DESC LIMIT %s OFFSET %s;"

        with connection.cursor() as cursor:
            cursor.execute(sql_query, params)

            # 获取结果
            result = cursor.fetchall()

        beans = []
        for one in result:
            bean = SubjectTemplateGroupBean(
                id=one[0],
                name=one[1],
                description=one[2],
                user_count=one[3],
                department_count=one[4],
                template_id=one[5],
                expired_at=one[6],
                expired_at_display=expired_at_display(one[6]),
                created_time=make_aware(one[7], timezone=utc),
                department_id=int(one[8]),
                department_name=department_dict.get(one[8], ""),
            )

            beans.append(bean)

        return beans

    def get_user_departments(self, username: str) -> List[Department]:
        u = User.objects.filter(username=username).first()
        if not u:
            return []

        department_ids = u.ancestor_department_ids
        if not department_ids:
            return []

        return list(Department.objects.filter(id__in=department_ids))
