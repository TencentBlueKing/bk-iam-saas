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
from typing import Dict

from backend.common.cache import cached
from backend.component import usermgr


@cached(timeout=5 * 60)
def _get_category_dict() -> Dict[int, str]:
    """获取所有目录的ID与Name映射"""
    # TODO: 需要修改为直接读取DB数据，避免因为usermgr的及时变更引起未同步前的数据不一致问题
    categories = usermgr.list_category()
    return {i["id"]: i["display_name"] for i in categories}


def get_category_name(category_id: int):
    """获取目录名称"""
    category_dict = _get_category_dict()
    return category_dict.get(category_id) or "默认目录"


# ---------------------------------------------------------------------------------------------- #
# [重构] biz.Organization：提供组织架构相关数据组装、校验、填充后数据等给到View层调用，调用service层获取相关数据
# ---------------------------------------------------------------------------------------------- #
