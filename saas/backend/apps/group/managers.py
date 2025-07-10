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

from typing import List

from django.db import models
from django.db.models import Q


class GroupAuthorizeLockManager(models.Manager):
    def is_authorizing(self, group_id: int, template_ids: List[int], custom_action_system_ids: List[str]) -> bool:
        """
        用户组是否正在授权

        group_id: 用户组ID
        template_ids: 被授权的模板ID集
        custom_action_system_ids: 被授权的自定义权限系统ID集
        """
        return (
            self.filter(group_id=group_id)
            .filter(Q(template_id__in=template_ids) | (Q(template_id=0) & Q(system_id__in=custom_action_system_ids)))
            .exists()
        )
