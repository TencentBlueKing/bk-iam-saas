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

from iam.resource.provider import ListResult, ResourceProvider, SchemaResult

from backend.api.admin.models import AdminAPIAllowListConfig
from backend.api.authorization.models import AuthAPIAllowListConfig
from backend.api.management.models import ManagementAPIAllowListConfig
from backend.apps.group.models import Group
from backend.apps.policy.models import Policy
from backend.apps.role.models import Role
from backend.apps.template.models import PermTemplate
from backend.apps.temporary_policy.models import TemporaryPolicy


class BaseResourceProvider(ResourceProvider):
    def list_attr(self, **options):
        return ListResult(results=[], count=0)

    def list_attr_value(self, filter, page, **options):
        return ListResult(results=[], count=0)

    def list_instance(self, filter, page, **options):
        return ListResult(results=[], count=0)

    def fetch_instance_info(self, filter, **options):
        return ListResult(results=[], count=0)

    def list_instance_by_policy(self, filter, page, **options):
        return ListResult(results=[], count=0)

    def search_instance(self, filter, page, **options):
        return ListResult(results=[], count=0)

    def _millisecond_to_second(self, ms: int):
        return ms // 1000


class PolicyResourceProvider(BaseResourceProvider):
    """
    权限策略
    """

    def fetch_instance_list(self, filter, page, **options):
        queryset = Policy.objects.filter(
            updated_time__gte=datetime.fromtimestamp(self._millisecond_to_second(filter.start_time))
        ).filter(updated_time__lte=datetime.fromtimestamp(self._millisecond_to_second(filter.end_time)))
        results = []

        data_keys = list(self.fetch_resource_type_schema().properties.keys())
        for policy in queryset[page.slice_from : page.slice_to]:
            results.append(
                {
                    "id": str(policy.id),
                    "display_name": policy.display_name,
                    "creator": policy.creator,
                    "created_at": policy.created_timestamp,
                    "updater": policy.updater,
                    "updated_at": policy.updated_timestamp,
                    "data": {key: getattr(policy, key) for key in data_keys},
                }
            )
        return ListResult(results=results, count=queryset.count())

    def fetch_resource_type_schema(self, **options):
        """获取资源类型 schema 定义
        schema定义
        """
        return SchemaResult(
            properties={
                "id": {
                    "type": "number",
                    "description": "ID",
                    "description_en": "ID",
                },
                "subject_type": {
                    "type": "string",
                    "description": "subject type",
                    "description_en": "subject type",
                },
                "subject_id": {
                    "type": "string",
                    "description": "subject id",
                    "description_en": "subject id",
                },
                "system_id": {
                    "type": "string",
                    "description": "system id",
                    "description_en": "system id",
                },
                "action_id": {
                    "type": "string",
                    "description": "action id",
                    "description_en": "action id",
                },
            }
        )


class TemporaryPolicyResourceProvider(BaseResourceProvider):
    """
    临时权限策略
    """

    def fetch_instance_list(self, filter, page, **options):
        queryset = TemporaryPolicy.objects.filter(
            updated_time__gte=datetime.fromtimestamp(self._millisecond_to_second(filter.start_time))
        ).filter(updated_time__lte=datetime.fromtimestamp(self._millisecond_to_second(filter.end_time)))
        results = []

        data_keys = list(self.fetch_resource_type_schema().properties.keys())
        for policy in queryset[page.slice_from : page.slice_to]:
            results.append(
                {
                    "id": str(policy.id),
                    "display_name": policy.display_name,
                    "creator": policy.creator,
                    "created_at": policy.created_timestamp,
                    "updater": policy.updater,
                    "updated_at": policy.updated_timestamp,
                    "data": {key: getattr(policy, key) for key in data_keys},
                }
            )
        return ListResult(results=results, count=queryset.count())

    def fetch_resource_type_schema(self, **options):
        """获取资源类型 schema 定义
        schema定义
        """
        return SchemaResult(
            properties={
                "id": {
                    "type": "number",
                    "description": "ID",
                    "description_en": "ID",
                },
                "subject_type": {
                    "type": "string",
                    "description": "subject type",
                    "description_en": "subject type",
                },
                "subject_id": {
                    "type": "string",
                    "description": "subject id",
                    "description_en": "subject id",
                },
                "system_id": {
                    "type": "string",
                    "description": "system id",
                    "description_en": "system id",
                },
                "action_id": {
                    "type": "string",
                    "description": "action id",
                    "description_en": "action id",
                },
            }
        )


class RoleResourceProvider(BaseResourceProvider):
    """
    角色
    """

    def fetch_instance_list(self, filter, page, **options):
        queryset = Role.objects.filter(
            updated_time__gte=datetime.fromtimestamp(self._millisecond_to_second(filter.start_time))
        ).filter(updated_time__lte=datetime.fromtimestamp(self._millisecond_to_second(filter.end_time)))
        results = []

        data_keys = list(self.fetch_resource_type_schema().properties.keys())
        for role in queryset[page.slice_from : page.slice_to]:
            results.append(
                {
                    "id": str(role.id),
                    "display_name": role.name,
                    "creator": role.creator,
                    "created_at": role.created_timestamp,
                    "updater": role.updater,
                    "updated_at": role.updated_timestamp,
                    "data": {key: getattr(role, key) for key in data_keys},
                }
            )
        return ListResult(results=results, count=queryset.count())

    def fetch_resource_type_schema(self, **options):
        """获取资源类型 schema 定义
        schema定义
        """
        return SchemaResult(
            properties={
                "id": {
                    "type": "number",
                    "description": "ID",
                    "description_en": "ID",
                },
                "name": {
                    "type": "string",
                    "description": "name",
                    "description_en": "name",
                },
                "description": {
                    "type": "string",
                    "description": "description",
                    "description_en": "description",
                },
                "type": {
                    "type": "string",
                    "description": "type",
                    "description_en": "type",
                },
            }
        )


class GroupResourceProvider(BaseResourceProvider):
    """
    用户组
    """

    def fetch_instance_list(self, filter, page, **options):
        queryset = Group.objects.filter(
            updated_time__gte=datetime.fromtimestamp(self._millisecond_to_second(filter.start_time))
        ).filter(updated_time__lte=datetime.fromtimestamp(self._millisecond_to_second(filter.end_time)))
        results = []

        data_keys = list(self.fetch_resource_type_schema().properties.keys())
        for group in queryset[page.slice_from : page.slice_to]:
            results.append(
                {
                    "id": str(group.id),
                    "display_name": group.name,
                    "creator": group.creator,
                    "created_at": group.created_timestamp,
                    "updater": group.updater,
                    "updated_at": group.updated_timestamp,
                    "data": {key: getattr(group, key) for key in data_keys},
                }
            )
        return ListResult(results=results, count=queryset.count())

    def fetch_resource_type_schema(self, **options):
        """获取资源类型 schema 定义
        schema定义
        """
        return SchemaResult(
            properties={
                "id": {
                    "type": "number",
                    "description": "ID",
                    "description_en": "ID",
                },
                "name": {
                    "type": "string",
                    "description": "name",
                    "description_en": "name",
                },
                "description": {
                    "type": "string",
                    "description": "description",
                    "description_en": "description",
                },
            }
        )


class TemplateResourceProvider(BaseResourceProvider):
    """
    权限模板
    """

    def fetch_instance_list(self, filter, page, **options):
        queryset = PermTemplate.objects.filter(
            updated_time__gte=datetime.fromtimestamp(self._millisecond_to_second(filter.start_time))
        ).filter(updated_time__lte=datetime.fromtimestamp(self._millisecond_to_second(filter.end_time)))
        results = []

        data_keys = list(self.fetch_resource_type_schema().properties.keys())
        for template in queryset[page.slice_from : page.slice_to]:
            results.append(
                {
                    "id": str(template.id),
                    "display_name": template.name,
                    "creator": template.creator,
                    "created_at": template.created_timestamp,
                    "updater": template.updater,
                    "updated_at": template.updated_timestamp,
                    "data": {key: getattr(template, key) for key in data_keys},
                }
            )
        return ListResult(results=results, count=queryset.count())

    def fetch_resource_type_schema(self, **options):
        """获取资源类型 schema 定义
        schema定义
        """
        return SchemaResult(
            properties={
                "id": {
                    "type": "number",
                    "description": "ID",
                    "description_en": "ID",
                },
                "name": {
                    "type": "string",
                    "description": "name",
                    "description_en": "name",
                },
                "description": {
                    "type": "string",
                    "description": "description",
                    "description_en": "description",
                },
                "system_id": {
                    "type": "string",
                    "description": "system id",
                    "description_en": "system id",
                },
                "action_ids": {
                    "type": "array",
                    "description": "action id list",
                    "description_en": "action id list",
                },
            }
        )


class AdminAPIAllowListConfigResourceProvider(BaseResourceProvider):
    """
    超管类api白名单
    """

    def fetch_instance_list(self, filter, page, **options):
        queryset = AdminAPIAllowListConfig.objects.filter(
            updated_time__gte=datetime.fromtimestamp(self._millisecond_to_second(filter.start_time))
        ).filter(updated_time__lte=datetime.fromtimestamp(self._millisecond_to_second(filter.end_time)))
        results = []

        data_keys = list(self.fetch_resource_type_schema().properties.keys())
        for config in queryset[page.slice_from : page.slice_to]:
            results.append(
                {
                    "id": str(config.id),
                    "display_name": config.api,
                    "creator": config.creator,
                    "created_at": config.created_timestamp,
                    "updater": config.updater,
                    "updated_at": config.updated_timestamp,
                    "data": {key: getattr(config, key) for key in data_keys},
                }
            )
        return ListResult(results=results, count=queryset.count())

    def fetch_resource_type_schema(self, **options):
        """获取资源类型 schema 定义
        schema定义
        """
        return SchemaResult(
            properties={
                "id": {
                    "type": "number",
                    "description": "ID",
                    "description_en": "ID",
                },
                "api": {
                    "type": "string",
                    "description": "api",
                    "description_en": "api",
                },
                "app_code": {
                    "type": "string",
                    "description": "app_code",
                    "description_en": "app_code",
                },
            }
        )


class AuthAPIAllowListConfigResourceProvider(BaseResourceProvider):
    """
    授权类api白名单
    """

    def fetch_instance_list(self, filter, page, **options):
        queryset = AuthAPIAllowListConfig.objects.filter(
            updated_time__gte=datetime.fromtimestamp(self._millisecond_to_second(filter.start_time))
        ).filter(updated_time__lte=datetime.fromtimestamp(self._millisecond_to_second(filter.end_time)))
        results = []

        data_keys = list(self.fetch_resource_type_schema().properties.keys())
        for config in queryset[page.slice_from : page.slice_to]:
            results.append(
                {
                    "id": str(config.id),
                    "display_name": config.type,
                    "creator": config.creator,
                    "created_at": config.created_timestamp,
                    "updater": config.updater,
                    "updated_at": config.updated_timestamp,
                    "data": {key: getattr(config, key) for key in data_keys},
                }
            )
        return ListResult(results=results, count=queryset.count())

    def fetch_resource_type_schema(self, **options):
        """获取资源类型 schema 定义
        schema定义
        """
        return SchemaResult(
            properties={
                "id": {
                    "type": "number",
                    "description": "ID",
                    "description_en": "ID",
                },
                "type": {
                    "type": "string",
                    "description": "type",
                    "description_en": "type",
                },
                "system_id": {
                    "type": "string",
                    "description": "system id",
                    "description_en": "system id",
                },
                "object_id": {
                    "type": "string",
                    "description": "object id",
                    "description_en": "object id",
                },
            }
        )


class ManagementAPIAllowListConfigResourceProvider(BaseResourceProvider):
    """
    管理类api白名单
    """

    def fetch_instance_list(self, filter, page, **options):
        queryset = ManagementAPIAllowListConfig.objects.filter(
            updated_time__gte=datetime.fromtimestamp(self._millisecond_to_second(filter.start_time))
        ).filter(updated_time__lte=datetime.fromtimestamp(self._millisecond_to_second(filter.end_time)))
        results = []

        data_keys = list(self.fetch_resource_type_schema().properties.keys())
        for config in queryset[page.slice_from : page.slice_to]:
            results.append(
                {
                    "id": str(config.id),
                    "display_name": config.api,
                    "creator": config.creator,
                    "created_at": config.created_timestamp,
                    "updater": config.updater,
                    "updated_at": config.updated_timestamp,
                    "data": {key: getattr(config, key) for key in data_keys},
                }
            )
        return ListResult(results=results, count=queryset.count())

    def fetch_resource_type_schema(self, **options):
        """获取资源类型 schema 定义
        schema定义
        """
        return SchemaResult(
            properties={
                "id": {
                    "type": "number",
                    "description": "ID",
                    "description_en": "ID",
                },
                "api": {
                    "type": "string",
                    "description": "api",
                    "description_en": "api",
                },
                "system_id": {
                    "type": "string",
                    "description": "system id",
                    "description_en": "system id",
                },
            }
        )
