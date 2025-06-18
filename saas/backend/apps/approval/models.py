#!/usr/bin/env python3
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

from backend.common.models import BaseModel
from backend.service.constants import ApplicationType, SensitivityLevel


class ApprovalProcessGlobalConfig(BaseModel):
    """审批流程的全局配置：默认流程配置"""

    application_type = models.CharField("申请类型", max_length=32, choices=ApplicationType.get_choices(), unique=True)
    process_id = models.CharField("审批流程ID", max_length=32)

    class Meta:
        verbose_name = "审批流程全局配置"
        verbose_name_plural = "审批流程全局配置"
        # unique_together = ["application_type"]  # 每一种申请类型只能配置一个默认流程


class ActionProcessRelation(BaseModel):
    """操作与审批流程的关系"""

    system_id = models.CharField("系统ID", max_length=32)
    action_id = models.CharField("操作ID", max_length=32)
    process_id = models.CharField("审批流程ID", max_length=32)
    sensitivity_level = models.CharField(
        "敏感等级", max_length=32, choices=SensitivityLevel.get_choices(), default=SensitivityLevel.L1.value
    )

    class Meta:
        verbose_name = "操作与审批流程关联"
        verbose_name_plural = "操作与审批流程关联"
        # unique_together = ["system_id", "action_id"]  # 任何一个系统的操作只能配置一个审批流程

    @classmethod
    def delete_by_action(cls, system_id: str, action_id: str):
        """删除某个系统某个操作的审批流程"""
        cls.objects.filter(system_id=system_id, action_id=action_id).delete()


class GroupProcessRelation(BaseModel):
    """用户组与审批流程的关系"""

    group_id = models.IntegerField("用户组ID")
    process_id = models.CharField("审批流程ID", max_length=32)

    class Meta:
        verbose_name = "用户组与审批流程关联"
        verbose_name_plural = "用户组与审批流程关联"
        unique_together = ["group_id"]  # 任何一个用户组只能配置一个审批流程
