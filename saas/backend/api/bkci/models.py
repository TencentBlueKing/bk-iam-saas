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

from django.db import models


class MigrateTask(models.Model):
    """
    迁移任务
    """

    status = models.CharField("任务状态", default="", max_length=36)
    role_ids = models.TextField("role_ids", default="")

    class Meta:
        verbose_name = "迁移任务"
        verbose_name_plural = "迁移任务"


class MigrateData(models.Model):
    """
    迁移数据
    """

    project_id = models.CharField("项目ID", max_length=64)
    type = models.CharField("数据类型", max_length=32, default="")
    data = models.TextField("数据")
    version = models.CharField("版本", max_length=32, default="v3")

    class Meta:
        verbose_name = "迁移数据"
        verbose_name_plural = "迁移数据"


class MigrateLegacyTask(models.Model):
    status = models.CharField("任务状态", default="", max_length=36)
    project_ids = models.TextField("project_ids", default="")

    class Meta:
        verbose_name = "迁移任务"
        verbose_name_plural = "迁移任务"


# iam v0 models
class Permissions(models.Model):
    deleted_at = models.DateTimeField(blank=True, null=True)
    policy_id = models.PositiveIntegerField(blank=True, null=True)
    role_id = models.PositiveIntegerField(blank=True, null=True)
    project_id = models.CharField(max_length=32, blank=True, null=True)
    user_id = models.CharField(max_length=255, blank=True, null=True)
    service_id = models.PositiveIntegerField(blank=True, null=True)
    group_id = models.PositiveIntegerField(blank=True, null=True)
    resource_id = models.PositiveIntegerField(blank=True, null=True)
    resource_type_id = models.PositiveIntegerField(blank=True, null=True)
    expire_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "permissions"


class Policies(models.Model):
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    extra = models.CharField(max_length=255, blank=True, null=True)
    policy_name = models.CharField(max_length=255, blank=True, null=True)
    desc = models.CharField(max_length=255, blank=True, null=True)
    effect = models.IntegerField(blank=True, null=True)
    kind = models.CharField(max_length=255, blank=True, null=True)
    label = models.CharField(max_length=255, blank=True, null=True)
    policy_code = models.CharField(max_length=127)
    service_id = models.PositiveIntegerField(blank=True, null=True)
    level = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "policies"
        unique_together = (("service_id", "policy_code"),)


class PolicyGroups(models.Model):
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    extra = models.CharField(max_length=255, blank=True, null=True)
    group_id = models.PositiveIntegerField(blank=True, null=True)
    policy_id = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "policy_groups"
        unique_together = (("group_id", "policy_id"),)


class Projects(models.Model):
    id = models.CharField(primary_key=True, max_length=32)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    extra = models.CharField(max_length=255, blank=True, null=True)
    cc_app_id = models.PositiveIntegerField(blank=True, null=True)
    project_code = models.CharField(max_length=32, blank=True, null=True)
    env = models.CharField(max_length=16, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "projects"


class ResourceTypes(models.Model):
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    extra = models.CharField(max_length=255, blank=True, null=True)
    resource_type_code = models.CharField(max_length=16, blank=True, null=True)
    resource_type_name = models.CharField(max_length=64, blank=True, null=True)
    service_id = models.PositiveIntegerField(blank=True, null=True)
    category = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "resource_types"


class Resources(models.Model):
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    extra = models.CharField(max_length=255, blank=True, null=True)
    project_id = models.CharField(max_length=32, blank=True, null=True)
    service_id = models.PositiveIntegerField(blank=True, null=True)
    resource_code = models.CharField(max_length=255, blank=True, null=True)
    resource_name = models.CharField(max_length=255, blank=True, null=True)
    resource_type_id = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "resources"


class Roles(models.Model):
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    extra = models.CharField(max_length=255, blank=True, null=True)
    project_id = models.CharField(max_length=32, blank=True, null=True)
    display_name = models.CharField(max_length=255, blank=True, null=True)
    role_name = models.CharField(max_length=127, blank=True, null=True)
    type = models.CharField(max_length=127, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "roles"


class Services(models.Model):
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    extra = models.CharField(max_length=255, blank=True, null=True)
    service_code = models.CharField(max_length=16, blank=True, null=True)
    service_name = models.CharField(max_length=64, blank=True, null=True)
    desc = models.CharField(max_length=255, blank=True, null=True)
    enabled_envs = models.CharField(max_length=63, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "services"


class UserRoles(models.Model):
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    extra = models.CharField(max_length=255, blank=True, null=True)
    project_id = models.CharField(max_length=32, blank=True, null=True)
    role_id = models.PositiveIntegerField(blank=True, null=True)
    user_id = models.CharField(max_length=255, blank=True, null=True)
    user_type = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "user_roles"
