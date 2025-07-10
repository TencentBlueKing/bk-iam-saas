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

from backend.apps.action.models import AggregateAction as AggregateActionModel

from .models import AggregateActions


class AggregateActionsService:
    def list(self, system_ids: List[str]) -> List[AggregateActions]:
        """
        获取聚合操作列表
        """
        models = AggregateActionModel.objects.filter(system_id__in=system_ids)
        return [self._gen_aggregate_action_by_model(model) for model in models]

    def _gen_aggregate_action_by_model(self, model: AggregateActionModel) -> AggregateActions:
        return AggregateActions(
            system_id=model.system_id,
            actions=[{"system_id": model.system_id, "id": _id} for _id in model.action_ids],
            aggregate_resource_types=model.aggregate_resource_type,
        )
