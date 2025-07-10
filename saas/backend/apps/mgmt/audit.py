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

from backend.audit.audit import DataProvider, audit_context_getter
from backend.audit.constants import AuditObjectType, AuditType


class BaseMgmtWhiteListProvider(DataProvider):
    @property
    def white_list(self):
        return audit_context_getter(self.request, "white_list")

    @property
    def extra(self):
        return {}

    @property
    def object_type(self):
        return AuditObjectType.WHITE_LIST.value

    @property
    def object_id(self):
        return self.white_list.id

    @property
    def object_name(self):
        return self.white_list.api


class AdminApiWhiteListCreateAuditProvider(BaseMgmtWhiteListProvider):
    type = AuditType.ADMIN_API_ALLOW_LIST_CONFIG_CREATE.value

    @property
    def extra(self):
        return {"app_code": self.white_list.app_code}


class AdminApiWhiteListDeleteAuditProvider(BaseMgmtWhiteListProvider):
    type = AuditType.ADMIN_API_ALLOW_LIST_CONFIG_DELETE.value

    @property
    def extra(self):
        return {"app_code": self.white_list.app_code}


class AuthorizationApiWhiteListCreateAuditProvider(BaseMgmtWhiteListProvider):
    type = AuditType.AUTHORIZATION_API_ALLOW_LIST_CONFIG_CREATE.value

    @property
    def object_name(self):
        return self.white_list.type

    @property
    def system_id(self):
        return self.white_list.system_id

    @property
    def extra(self):
        return {"object_id": self.white_list.object_id}


class AuthorizationApiWhiteListDeleteAuditProvider(BaseMgmtWhiteListProvider):
    type = AuditType.AUTHORIZATION_API_ALLOW_LIST_CONFIG_DELETE.value

    @property
    def object_name(self):
        return self.white_list.type

    @property
    def system_id(self):
        return self.white_list.system_id

    @property
    def extra(self):
        return {"object_id": self.white_list.object_id}


class ManagementApiWhiteListCreateAuditProvider(BaseMgmtWhiteListProvider):
    type = AuditType.MANAGEMENT_API_ALLOW_LIST_CONFIG_CREATE.value

    @property
    def system_id(self):
        return self.white_list.system_id


class ManagementApiWhiteListDeleteAuditProvider(BaseMgmtWhiteListProvider):
    type = AuditType.MANAGEMENT_API_ALLOW_LIST_CONFIG_DELETE.value

    @property
    def system_id(self):
        return self.white_list.system_id
