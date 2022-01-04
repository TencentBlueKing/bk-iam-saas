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
from backend.api.admin.models import AdminAPIAllowListConfig
from backend.api.authorization.models import AuthAPIAllowListConfig
from backend.api.management.models import ManagementAPIAllowListConfig


def list_api_msg_by_api_type(api_type: str):
    """
    根据api类型获取相关api信息
    """
    api_model_map = {
        "management_api": ManagementAPIAllowListConfig,
        "admin_api": AdminAPIAllowListConfig,
        "authorization_api": AuthAPIAllowListConfig,
    }
    api_msg = api_model_map[api_type].objects.list_api_msg()
    return api_msg
