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

from typing import List, Optional

from django.db import models

from backend.service.constants import RoleRelatedObjectType


class RoleUserManager(models.Manager):
    def user_role_exists(self, user_id: str, role_id: int) -> bool:
        return self.filter(role_id=role_id, username=user_id).exists()

    def delete_grade_manager_member(self, role_id: int, usernames: List[str]):
        """
        批量删除分级管理员成员
        特别注意：不可用于超级管理员和系统管理员
        """
        self.filter(role_id=role_id, username__in=usernames).delete()


class RoleRelatedObjectManager(models.Manager):
    def delete_object_relation(self, object_id: int, object_type: str):
        self.filter(object_type=object_type, object_id=object_id).delete()

    def list_object_relation(self, role_id: int, object_type: str):
        """获取角色关联的模板或用户组ID列表"""
        return self.filter(role_id=role_id, object_type=object_type).order_by("id")

    def create_object_relation(self, role_id: int, object_id: int, object_type: str):
        """创建：角色与其产生的模板或用户组的关联关系"""
        return self.create(role_id=role_id, object_type=object_type, object_id=object_id)

    def batch_create_object_relation(self, role_id: int, object_ids: List[int], object_type: str):
        """批量创建：角色与其产生的模板或用户组的关联关系"""
        self.bulk_create(
            [self.model(role_id=role_id, object_type=object_type, object_id=object_id) for object_id in object_ids],
            batch_size=100,
        )

    def create_template_relation(self, role_id: int, template_id: int):
        """
        创建角色与角色创建的模板关系
        """
        return self.create_object_relation(role_id, template_id, RoleRelatedObjectType.TEMPLATE.value)

    def create_subject_template_relation(self, role_id: int, template_id: int):
        """
        创建角色与角色创建的人员模板关系
        """
        return self.create_object_relation(role_id, template_id, RoleRelatedObjectType.SUBJECT_TEMPLATE.value)

    def delete_template_relation(self, template_id: int):
        """
        移除角色与角色创建的模板关系
        """
        self.delete_object_relation(template_id, RoleRelatedObjectType.TEMPLATE.value)

    def list_role_object_ids(self, role_id: int, object_type: str) -> List[int]:
        return list(self.filter(role_id=role_id, object_type=object_type).values_list("object_id", flat=True))

    def create_group_relation(self, role_id: int, group_id: int):
        """
        创建角色与角色创建的用户组关系
        """
        return self.create_object_relation(role_id, group_id, RoleRelatedObjectType.GROUP.value)

    def batch_create_group_relation(self, role_id: int, group_ids: List[int]):
        """
        批量创建角色与角色创建的用户组关系
        """
        self.batch_create_object_relation(role_id, group_ids, RoleRelatedObjectType.GROUP.value)

    def delete_group_relation(self, group_id: int):
        """
        移除角色与角色创建的用户组关系
        """
        self.delete_object_relation(group_id, RoleRelatedObjectType.GROUP.value)


class RoleRelationManager(models.Manager):
    def list_sub_id(self, role_id: int) -> List[int]:
        """
        查询分级管理员的子集管理的id
        """
        return list(self.filter(parent_id=role_id).values_list("role_id", flat=True))

    def get_parent_role_id(self, role_id: int) -> Optional[int]:
        """
        查询父级role
        """
        relation = self.filter(role_id=role_id).first()
        if not relation:
            return None

        return relation.parent_id
