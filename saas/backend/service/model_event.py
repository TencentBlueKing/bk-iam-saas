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

from pydantic import parse_obj_as

from backend.component import iam

from .constants import ModelChangeEventStatus
from .models import ModelEvent


class ModelEventService:
    def list(self, status: str, limit: int = 1000) -> List[ModelEvent]:
        events = iam.list_model_change_event(status, limit)
        return parse_obj_as(List[ModelEvent], events)

    def update_status(self, event_id: int, status: str):
        """更新事件状态"""
        iam.update_model_change_event(event_id, status)

    def delete_finished_event(self, before_updated_at: int, limit: int = 1000):
        """
        删除已结束的事件
        before_updated_at 表示删除多久之前的，时间戳字段，单位秒
        """
        iam.delete_model_change_event(ModelChangeEventStatus.Finished.value, before_updated_at, limit)
