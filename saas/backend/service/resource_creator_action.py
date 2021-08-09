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
from typing import Dict, List

from backend.common.error_codes import error_codes
from backend.component import iam

from .models import ResourceCreatorAction, ResourceCreatorSingleAction


class ResourceCreatorActionService:
    def get(self, system_id) -> ResourceCreatorAction:
        """获取系统的新建关联配置"""
        rca = iam.get_resource_creator_actions(system_id)
        # 空的话，说明接入系统未配置，必须报错
        if not rca:
            raise error_codes.VALIDATE_ERROR.format(
                "system[{}] do not register resource_creator_actions".format(system_id)
            )
        return ResourceCreatorAction(**rca)

    def _get_resource_type_actions_map(self, system_id: str) -> Dict[str, List[ResourceCreatorSingleAction]]:
        """展开打平resource_type 与actions映射"""
        resource_creator_action = self.get(system_id)
        rta_map = {}
        for c in resource_creator_action.config:
            rta_map.update(c.get_resource_type_actions_map())
        return rta_map

    def get_actions(self, system_id: str, resource_type_id: str) -> List[str]:
        """
        根据资源类型，获取该类型需要授权的Action
        目前暂时直接返回系统默认配置，后续可以根据user配置等生成（需要subject参数）
        """
        resource_type_actions_map = self._get_resource_type_actions_map(system_id)
        # 判断是否存在，不存在直接提示
        if resource_type_id not in resource_type_actions_map:
            raise error_codes.VALIDATE_ERROR.format(
                "system[{}]-action[{}] do not register actions for authorization of creator".format(
                    system_id, resource_type_id
                )
            )
        return [action.id for action in resource_type_actions_map[resource_type_id]]
