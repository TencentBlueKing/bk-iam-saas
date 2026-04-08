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
from textwrap import dedent
from typing import Dict, List, Union

from django.core.paginator import Paginator
from django.db import connection, models
from django.utils.functional import cached_property

from backend.common.constants import DEFAULT_TENANT_ID
from backend.common.models import BaseModel, BaseSystemHiddenModel
from backend.service.constants import (
    RoleConfigType,
    RoleRelatedObjectType,
    RoleScopeType,
    RoleSourceType,
    RoleType,
    SubjectType,
)
from backend.util.json import json_dumps

from .constants import DEFAULT_ROLE_PERMISSIONS
from .managers import RoleRelatedObjectManager, RoleRelationManager, RoleUserManager


class Role(BaseModel, BaseSystemHiddenModel):
    """
    角色
    """

    tenant_id = models.CharField("租户 ID", max_length=64, default=DEFAULT_TENANT_ID)

    name = models.CharField("名称", max_length=512)
    name_en = models.CharField("英文名", max_length=512, default="")
    description = models.CharField("描述", max_length=255, default="")
    type = models.CharField("类型", max_length=32, choices=RoleType.get_choices(), db_index=True)
    code = models.CharField("标志", max_length=64, default="")
    inherit_subject_scope = models.BooleanField("继承人员管理范围", default=False)
    sync_perm = models.BooleanField("同步角色权限", default=False)

    class Meta:
        verbose_name = "角色"
        verbose_name_plural = "角色"
        ordering = ["-id"]

    @property
    def system_permission_enabled_content(self):
        enabled_content, _ = RoleUserSystemPermission.objects.get_or_create(role_id=self.id, tenant_id=self.tenant_id)
        return enabled_content

    @property
    def members(self):
        return list(RoleUser.objects.filter(role_id=self.id).values_list("username", flat=True))

    @property
    def permissions(self):
        return DEFAULT_ROLE_PERMISSIONS[self.type]


class RoleUser(BaseModel):
    """
    角色的用户
    """

    tenant_id = models.CharField("租户 ID", max_length=64, default=DEFAULT_TENANT_ID)

    role_id = models.IntegerField("角色 ID")
    username = models.CharField("用户 id", max_length=64, db_index=True)
    readonly = models.BooleanField("只读标识", default=False)  # 增加可读标识

    objects = RoleUserManager()

    class Meta:
        verbose_name = "角色的用户"
        verbose_name_plural = "角色的用户"
        ordering = ["id"]
        indexes = [
            models.Index(fields=["role_id", "username"]),  # 创建复合索引
        ]


class RoleUserSystemPermission(BaseModel):
    """
    角色里的用户是否拥有对应接入系统的超级权限
    """

    tenant_id = models.CharField("租户 ID", max_length=64, default=DEFAULT_TENANT_ID)

    role_id = models.IntegerField("角色 ID", db_index=True)
    content = models.TextField("限制内容", default='{"enabled_users": [], "global_enabled": false}')

    @cached_property
    def enabled_detail(self) -> Dict[str, Union[List[str], bool]]:
        return json.loads(self.content)

    @property
    def enabled_users(self) -> List[str]:
        return self.enabled_detail["enabled_users"]

    @property
    def global_enabled(self) -> bool:
        return self.enabled_detail["global_enabled"]

    @classmethod
    def get_enabled_detail(cls, role_id: int, tenant_id: str):
        enabled_content, _ = cls.objects.get_or_create(role_id=role_id, tenant_id=tenant_id)
        return enabled_content.enabled_detail

    @classmethod
    def update_global_enabled(cls, role_id: int, global_enabled: bool, tenant_id: str):
        enabled_detail = cls.get_enabled_detail(role_id, tenant_id)
        enabled_detail["global_enabled"] = global_enabled
        cls.objects.filter(role_id=role_id, tenant_id=tenant_id).update(content=json_dumps(enabled_detail))

    @classmethod
    def add_enabled_users(cls, role_id: int, username: str, tenant_id: str):
        enabled_detail = cls.get_enabled_detail(role_id, tenant_id)
        enabled_detail["enabled_users"].append(username)
        cls.objects.filter(role_id=role_id, tenant_id=tenant_id).update(content=json_dumps(enabled_detail))

    @classmethod
    def delete_enabled_users(cls, role_id: int, username: str, tenant_id: str):
        enabled_detail = cls.get_enabled_detail(role_id, tenant_id)
        enabled_detail["enabled_users"].remove(username)
        cls.objects.filter(role_id=role_id, tenant_id=tenant_id).update(content=json_dumps(enabled_detail))


class Permission(models.Model):
    """
    权限
    """

    tenant_id = models.CharField("租户 ID", max_length=64, default=DEFAULT_TENANT_ID)

    name = models.CharField("名称", max_length=64)
    name_en = models.CharField("英文名", max_length=64, default="")
    code = models.CharField("标志", max_length=64)

    class Meta:
        verbose_name = "权限"
        verbose_name_plural = "权限"


class RolePerm(models.Model):
    """
    角色的权限
    """

    tenant_id = models.CharField("租户 ID", max_length=64, default=DEFAULT_TENANT_ID)

    role_id = models.IntegerField("角色 ID")
    perm_id = models.IntegerField("权限 ID")

    class Meta:
        verbose_name = "角色的权限"
        verbose_name_plural = "角色的权限"
        indexes = [models.Index(fields=["role_id"])]


class RoleScope(models.Model):
    """
    角色的限制范围
    """

    tenant_id = models.CharField("租户 ID", max_length=64, default=DEFAULT_TENANT_ID)

    role_id = models.IntegerField("角色 ID")
    type = models.CharField("限制类型", max_length=32, choices=RoleScopeType.get_choices())
    content = models.TextField("限制内容")

    class Meta:
        verbose_name = "角色的限制范围"
        verbose_name_plural = "角色的限制范围"
        indexes = [models.Index(fields=["role_id"])]

    @classmethod
    def delete_action_from_scope(cls, system_id: str, action_id: str):
        """
        从可授权范围里删除某个操作，由于 json 存储了所有授权信息，所以无法直接索引，只能遍历所有
        """
        qs = Role.objects.only("id")
        if system_id != "bk_ci_rbac":
            qs = qs.exclude(source_system_id="bk_ci_rbac")

        paginator = Paginator(qs, 100)
        should_updated_role_scopes = []
        for i in paginator.page_range:
            for role in paginator.page(i):
                role_scope = cls.objects.filter(type=RoleScopeType.AUTHORIZATION.value, role_id=role.id).first()
                if not role_scope:
                    continue

                content = json.loads(role_scope.content)
                should_updated = False
                # 遍历授权范围里每个系统
                for scope in content:
                    if scope["system_id"] != system_id:
                        continue
                    # 判断 Action 是否存在，不存在则忽略
                    action_ids = {action["id"] for action in scope["actions"]}
                    if action_id not in action_ids:
                        continue
                    # 如果包含要删除的 Action，则进行更新数据
                    scope["actions"] = [action for action in scope["actions"] if action["id"] != action_id]
                    should_updated = True
                    break
                if should_updated:
                    role_scope.content = json_dumps(content)
                    should_updated_role_scopes.append(role_scope)

        # 批量更新分级管理员授权范围
        if len(should_updated_role_scopes) > 0:
            cls.objects.bulk_update(should_updated_role_scopes, fields=["content"], batch_size=20)


class ScopeSubject(models.Model):
    """
    subject 的限制冗余
    """

    tenant_id = models.CharField("租户 ID", max_length=64, default=DEFAULT_TENANT_ID)

    role_scope_id = models.IntegerField("角色限制 ID")
    role_id = models.IntegerField("角色 ID")
    subject_type = models.CharField("授权对象类型", max_length=32, choices=SubjectType.get_choices())
    subject_id = models.CharField("授权对象 ID", max_length=64)

    class Meta:
        verbose_name = "subject 限制"
        verbose_name_plural = "subject 限制"
        indexes = [
            models.Index(fields=["subject_id", "subject_type", "role_id"]),
            models.Index(fields=["role_id", "role_scope_id"]),
        ]


class RoleRelatedObject(BaseModel):
    """
    角色关联资源
    """

    tenant_id = models.CharField("租户 ID", max_length=64, default=DEFAULT_TENANT_ID)

    role_id = models.IntegerField("角色 ID")
    object_type = models.CharField("对象类型", max_length=32, choices=RoleRelatedObjectType.get_choices())
    object_id = models.IntegerField("对象 ID")
    sync_perm = models.BooleanField("跟随角色同步", default=False)

    objects = RoleRelatedObjectManager()

    class Meta:
        verbose_name = "角色关联资源"
        verbose_name_plural = "角色关联资源"
        unique_together = ["role_id", "object_type", "object_id"]
        indexes = [
            models.Index(fields=["object_id", "object_type"]),
        ]


class RoleRelation(BaseModel):
    """
    角色关系

    当前只有 分级管理员 -- 子集管理员 的 1 对多关系
    """

    tenant_id = models.CharField("租户 ID", max_length=64, default=DEFAULT_TENANT_ID)

    parent_id = models.IntegerField("父级角色 ID")
    role_id = models.IntegerField("角色 ID", db_index=True)

    objects = RoleRelationManager()

    class Meta:
        verbose_name = "角色关系"
        verbose_name_plural = "角色关系"
        unique_together = ["parent_id", "role_id"]


class RoleCommonAction(BaseModel):
    """
    角色常用操作
    """

    tenant_id = models.CharField("租户 ID", max_length=64, default=DEFAULT_TENANT_ID)

    role_id = models.IntegerField("角色 ID")
    system_id = models.CharField("系统 ID", max_length=32)
    name = models.CharField("名称", max_length=128)
    name_en = models.CharField("名称 EN", max_length=128, default="")
    _action_ids = models.TextField("操作列表", db_column="action_ids")

    class Meta:
        verbose_name = "角色常用操作"
        verbose_name_plural = "角色常用操作"
        ordering = ["id"]
        indexes = [models.Index(fields=["role_id", "system_id"])]

    @property
    def action_ids(self):
        return json.loads(self._action_ids)

    @action_ids.setter
    def action_ids(self, action_ids):
        self._action_ids = json_dumps(action_ids)


class RoleSource(BaseModel):
    """
    角色创建来源
    """

    tenant_id = models.CharField("租户 ID", max_length=64, default=DEFAULT_TENANT_ID)

    role_id = models.IntegerField("角色 ID", unique=True)
    source_type = models.CharField("来源类型", max_length=32, choices=RoleSourceType.get_choices())
    source_system_id = models.CharField("来源系统", max_length=32, default="")

    class Meta:
        verbose_name = "角色创建来源"
        verbose_name_plural = "角色创建来源"
        indexes = [models.Index(fields=["source_system_id", "source_type"])]

    @classmethod
    def get_role_count(cls, role_type: str, system_id: str, source_type: str = RoleSourceType.API.value):
        with connection.cursor() as cursor:
            cursor.execute(
                dedent(
                    """SELECT
                    COUNT(*)
                    FROM
                    role_rolesource a
                    left join role_role b ON a.role_id = b.id
                    WHERE
                    a.source_type = %s
                    AND a.source_system_id = %s
                    AND b.type = %s"""
                ),
                [source_type, system_id, role_type],
            )
            row = cursor.fetchone()
            return row[0]


class RoleResourceRelation(BaseModel):
    """
    角色资源标签

    用于自定义申请权限查询管理员审批人
    """

    tenant_id = models.CharField("租户 ID", max_length=64, default=DEFAULT_TENANT_ID)

    role_id = models.IntegerField("角色 ID")
    system_id = models.CharField("资源系统", max_length=32)
    resource_type_id = models.CharField("资源类型", max_length=32)
    resource_id = models.CharField("资源 ID", max_length=36)

    class Meta:
        verbose_name = "角色资源关系"
        verbose_name_plural = "角色资源关系"
        unique_together = ["resource_id", "resource_type_id", "system_id", "role_id"]


class RoleConfig(BaseModel):
    """
    角色配置
    """

    tenant_id = models.CharField("租户 ID", max_length=64, default=DEFAULT_TENANT_ID)

    role_id = models.IntegerField("角色 ID")
    type = models.CharField("限制类型", max_length=32, choices=RoleConfigType.get_choices())
    _config = models.TextField("配置", db_column="config", default="{}")

    class Meta:
        verbose_name = "角色配置"
        verbose_name_plural = "角色配置"
        indexes = [models.Index(fields=["role_id", "type"])]

    @property
    def config(self):
        return json.loads(self._config)

    @config.setter
    def config(self, config):
        self._config = json_dumps(config)


class AnonymousRole:
    tenant_id = ""
    id = 0
    pk = 0
    name = "STAFF"
    name_en = ""
    description = ""
    type = RoleType.STAFF.value
    code = ""

    system_permission_enabled_content = RoleUserSystemPermission(
        id=0, role_id=0, content='{"enabled_users": [], "global_enabled": false}'
    )
    members: List[str] = []

    def __str__(self):
        return "AnonymousRole"

    def __eq__(self, other):
        return isinstance(other, self.__class__)

    def __hash__(self):
        return 0  # instances always return the same hash value

    def __int__(self):
        raise TypeError("Cannot cast AnonymousRole to int. Are you trying to use it in place of Role?")

    def save(self):
        raise NotImplementedError("Django doesn't provide a DB representation for AnonymousRole.")

    def delete(self):
        raise NotImplementedError("Django doesn't provide a DB representation for AnonymousRole.")

    @property
    def permissions(self):
        return []


class RoleGroupMember(models.Model):
    """
    角色用户组成员冗余数据表
    """

    tenant_id = models.CharField("租户 ID", max_length=64, default=DEFAULT_TENANT_ID)

    role_id = models.IntegerField("角色 ID")
    subset_id = models.IntegerField("二级角色 ID", default=0)
    group_id = models.IntegerField("用户组 ID", db_index=True)
    subject_template_id = models.IntegerField("用户模板 ID", default=0, db_index=True)
    subject_type = models.CharField("用户类型", max_length=32, choices=SubjectType.get_choices())
    subject_id = models.CharField("用户 ID", max_length=32)

    class Meta:
        verbose_name = "角色用户组成员"
        verbose_name_plural = "角色用户组成员"
        unique_together = [
            ["role_id", "subject_type", "subject_id", "group_id", "subject_template_id"],
        ]


class RolePolicyExpiredNotificationConfig(BaseModel):
    """
    角色策略过期通知配置
    """

    tenant_id = models.CharField("租户 ID", max_length=64, default=DEFAULT_TENANT_ID)

    role_id = models.IntegerField("角色 ID", unique=True)
    _config = models.TextField("配置", db_column="config", default="{}")

    class Meta:
        verbose_name = "角色策略过期通知配置"
        verbose_name_plural = "角色策略过期通知配置"

    @property
    def config(self):
        return json.loads(self._config)

    @config.setter
    def config(self, config):
        self._config = json_dumps(config)
