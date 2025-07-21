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

from backend.trans.application import ApplicationDataTrans
from backend.trans.group import GroupTrans
from backend.trans.open_application import AccessSystemApplicationTrans
from backend.trans.open_authorization import AuthorizationTrans
from backend.trans.open_management import GradeManagerTrans, ManagementCommonTrans
from backend.trans.role import RoleAuthScopeTrans, RoleTrans

from .tenant import TenantMixin


class TransMixin(TenantMixin):
    @property
    def application_data_trans(self):
        return ApplicationDataTrans(self.tenant_id)

    @property
    def role_trans(self):
        return RoleTrans(self.tenant_id)

    @property
    def group_trans(self):
        return GroupTrans(self.tenant_id)

    @property
    def role_auth_scope_trans(self):
        return RoleAuthScopeTrans()

    @property
    def access_system_application_trans(self):
        return AccessSystemApplicationTrans(self.tenant_id)

    @property
    def authorization_trans(self):
        return AuthorizationTrans(self.tenant_id)

    @property
    def grade_manager_trans(self):
        return GradeManagerTrans(self.tenant_id)

    @property
    def management_common_trans(self):
        return ManagementCommonTrans(self.tenant_id)
