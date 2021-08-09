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
from typing import Any, Callable, Dict, List, Tuple


# TODO: 后续抽象成通用的公共函数，比如paging_func支持可变参数等，同时改成一个通用装饰器
def list_all_data_by_paging(
    paging_func: Callable[[int, int], Tuple[int, List[Dict]]], page_size: int = 1000
) -> List[Dict]:
    """获取所有数据通过循环分页"""
    page = 1
    # 先第一次调用
    total, results = paging_func(page, page_size)
    # 返回的数据数量
    result_count = len(results)
    # 已获取的数据总数
    count = result_count
    # 已获得的数据
    data = results
    # 最大循环次数，避免死循环
    maximum = int(total / page_size + 1)
    # 返回数据数量等于page_size且已获取的总数小于total
    while result_count == page_size and count < total and page <= maximum:
        page += 1
        _, results = paging_func(page, page_size)
        result_count = len(results)
        count += result_count
        data.extend(results)
    return data


def execute_all_data_by_paging(
    paging_func: Callable[[List[Any]], None], data: List[Any], page_size: int = 1000
) -> None:
    """通过分页数据的方式循环执行调用"""
    for i in range(0, len(data), page_size):
        paging_func(data[i : i + page_size])
