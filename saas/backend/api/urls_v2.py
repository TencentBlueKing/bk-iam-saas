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
from django.conf.urls import include, url

urlpatterns = [
    # 管理类API - 对于V2 API，所有管理类API都默认在系统下
    url(r"^management/systems/(?P<system_id>[\w|-]+)/", include("backend.api.management.v2.urls")),
    # NOTE 临时api, 用于bkci迁移数据
    url(r"^migration/bkci/", include("backend.api.bkci.urls")),
]
