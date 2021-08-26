# -*- coding: utf-8 -*-
from __future__ import absolute_import

"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-权限中心(BlueKing-IAM) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
__all__ = ["celery_app", "RUN_VER", "APP_CODE", "SECRET_KEY", "BK_URL", "BASE_DIR"]

import os

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from blueapps.core.celery import celery_app

# app 基本信息

# SaaS运行版本，如非必要请勿修改
RUN_VER = "open"
# SaaS应用ID
APP_CODE = "bk_iam"  # 假的, 待修改
# SaaS安全密钥，注意请勿泄露该密钥
SECRET_KEY = "af76be9c-2b24-4006-a68e-e66abcfd67af"  # 待修改
# 蓝鲸SaaS平台URL，例如 http://paas.bking.com
BK_URL = None

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
