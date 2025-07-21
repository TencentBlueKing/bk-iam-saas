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

from typing import List

from pydantic import BaseModel

from backend.common.error_codes import error_codes
from backend.service.models import ResourceCreatorActionConfigItem
from backend.service.resource_creator_action import ResourceCreatorActionService


class ResourceCreatorActionBean(BaseModel):
    id: str  # 资源类型 ID
    action_ids: List[str]  # 该资源类型的实例被创建时，对应创建者需要的该资源实例的操作权限


class ResourceCreatorActionBiz:
    svc = ResourceCreatorActionService()

    def list_action_id(self, system_id: str, resource_type_id: str) -> List[str]:
        """查询某个资源类型当其实例被创建时，创建者需要的操作权限"""
        resource_creator_action_config = self.svc.get(system_id)
        # 空的话，说明接入系统未配置，必须报错
        if resource_creator_action_config is None:
            raise error_codes.VALIDATE_ERROR.format(
                "system[{}] do not register resource_creator_actions config".format(system_id)
            )

        # 由于配置是按照资源类型层级存储的，所以需要将其平铺便于后续查询
        rac_beans = self._tiled_resource_creator_action(resource_creator_action_config.config)
        resource_type_actions_dict = {i.id: i.action_ids for i in rac_beans}

        # 判断是否存在，不存在直接提示
        if resource_type_id not in resource_type_actions_dict:
            raise error_codes.VALIDATE_ERROR.format(
                "system[{}]-action[{}] do not register actions for authorization of creator".format(
                    system_id, resource_type_id
                )
            )

        return resource_type_actions_dict[resource_type_id]

    def _tiled_resource_creator_action(
        self, rca_config: List[ResourceCreatorActionConfigItem]
    ) -> List[ResourceCreatorActionBean]:
        """将新建关联配置按照资源类型平铺"""
        rac_beans = []

        for config_item in rca_config:
            rac_beans.append(
                ResourceCreatorActionBean(id=config_item.id, action_ids=[a.id for a in config_item.actions])
            )
            if config_item.sub_resource_types is None:
                continue
            # 处理子资源类型的
            sub_rac_beans = self._tiled_resource_creator_action(config_item.sub_resource_types)
            rac_beans.extend(sub_rac_beans)

        return rac_beans
