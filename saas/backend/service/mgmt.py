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
from backend.api.management.constants import ManagementAPIEnum
from backend.api.management.models import ManagementAPIAllowListConfig


class WhiteListService:
    def list_management_api(self):
        """
        管理类API列表
        """
        management_api = dict(ManagementAPIEnum.get_choices())
        data = [{"api": api, "name": management_api[api]} for api in management_api]
        return data

    def add_management_api(self, username: str, system_id: str, api: str):
        """
        新增管理类API白名单
        """
        ManagementAPIAllowListConfig.objects.update_or_create(
            defaults={"updater": username}, creator=username, system_id=system_id, api=api
        )

    def delete_management_api_by_id(self, id: int):
        """
        删除管理类API白名单
        """
        ManagementAPIAllowListConfig.objects.filter(id=id).delete()
