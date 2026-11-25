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
from typing import Iterable, Set

from backend.apps.role.models import Role, RoleRelatedObject, RoleRelation
from backend.service.constants import RoleRelatedObjectType


class PersonalPermissionBiz:
    """个人权限判定：实时读取 Role 标记与 RoleRelatedObject 归属关系

    注意：GroupTransferView / GradeManagerGroupTransferView 会改写 RoleRelatedObject.role_id，
    组与管理空间的归属可能变化，因此不做跨请求缓存，每次调用都查当前关系。
    """

    @staticmethod
    def filter_personal_group_by_ids(group_ids: Iterable[int]) -> Set[int]:
        """返回属于个人权限管理空间的用户组 ID 集合"""
        ids = {int(gid) for gid in group_ids if gid is not None}
        if not ids:
            return set()

        relations = list(
            RoleRelatedObject.objects.filter(
                object_type=RoleRelatedObjectType.GROUP.value, object_id__in=ids
            ).values_list("object_id", "role_id")
        )
        if not relations:
            return set()

        role_ids = {rid for _, rid in relations}
        # 子集管理空间继承父级标记：父级被标记时，子集下的组同样视为个人权限组
        role_relation = {r.role_id: r.parent_id for r in RoleRelation.objects.filter(role_id__in=role_ids)}
        role_ids.update(role_relation.values())

        personal_role_ids = set(Role.objects.filter(id__in=role_ids, is_personal=True).values_list("id", flat=True))
        return {
            int(gid)
            for gid, rid in relations
            if rid in personal_role_ids or (rid in role_relation and role_relation[rid] in personal_role_ids)
        }

    def is_personal_group(self, group_id: int) -> bool:
        return bool(self.filter_personal_group_by_ids([group_id]))
