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
from aenum import LowerStrEnum, auto

DELETE_POLICY_PUB_SUB_KEY = "bk_iam:deleted_policy"
DELETE_POLICY_REDIS_LIST_MAX_LENGTH = 10000


# 枚举策略删除时的方式：用策略ID删除、直接删除Subject导致策略删除
class DeletePolicyTypeEnum(LowerStrEnum):
    # 删除策略
    POLICY = auto()
    # 删除Subject
    SUBJECT = auto()
    # 删除Subject的权限模板
    SUBJECT_TEMPLATE = auto()
