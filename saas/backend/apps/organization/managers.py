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

from django.db import models


class SyncErrorLogManager(models.Manager):
    def create_error_log(self, tenant_id: str, sync_record_id: int, exception_msg: str, traceback_msg: str):
        """创建：同步用户管理组织架构异常记录的日志详情"""
        sync_error_log = {"exception_msg": exception_msg, "traceback_msg": traceback_msg}
        return self.create(tenant_id=tenant_id, sync_record_id=sync_record_id, log=sync_error_log)
