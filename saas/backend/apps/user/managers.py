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

from typing import Dict, List

from django.db import models

from backend.apps.user.constants import NewbieSceneEnum


class UserProfileManager(models.Manager):
    def update_newbie(self, tenant_id, username: str, scene: str, status: bool):
        profile, _ = self.get_or_create(
            tenant_id=tenant_id, username=username, defaults={"_newbie": "{}", "_favorite_systems": "[]"}
        )
        # 存在则修改数据后再保存
        newbie_dict = profile.newbie
        newbie_dict[scene] = status
        profile.newbie = newbie_dict
        profile.save()

    def list_newbie(self, username: str) -> List[Dict]:
        """列出某个用户的所有场景的新手指引状态"""
        # DB 查询，由于未读过任何一个新手指引，所以可能不存在记录
        profile = self.filter(username=username).first()
        newbie_dict = profile.newbie if profile else {}

        # 遍历所有新手指引的场景返回
        return [{"scene": scene.value, "status": newbie_dict.get(scene.value, False)} for scene in NewbieSceneEnum]

    def list_favorite_systems(self, username: str) -> List[str]:
        """列出某个用户收藏的系统"""
        profile = self.filter(username=username).first()
        if not profile:
            return []
        return profile.favorite_systems

    def add_favorite_systems(self, tenant_id: str, username: str, systems: List[str]):
        profile, _ = self.get_or_create(
            tenant_id=tenant_id, username=username, defaults={"_newbie": "{}", "_favorite_systems": "[]"}
        )
        favorite_systems = profile.favorite_systems
        for system in systems:
            if system not in favorite_systems:
                favorite_systems.append(system)
        profile.favorite_systems = favorite_systems
        profile.save()

    def remove_favorite_systems(self, username: str, systems: List[str]):
        profile, _ = self.get_or_create(username=username, defaults={"_newbie": "{}", "_favorite_systems": "[]"})
        favorite_systems = profile.favorite_systems
        for system in systems:
            if system in favorite_systems:
                favorite_systems.remove(system)
        profile.favorite_systems = favorite_systems
        profile.save()
