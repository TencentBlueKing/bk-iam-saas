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

from collections import defaultdict
from typing import List, Tuple


def convert_list_for_mptt(data: List[Tuple[int, int]], reverse: bool = False) -> List[int]:
    """转换为按顺序变更的数据"""
    node_set = {i[0] for i in data}
    # 由于存在parent=None或parent不在新增的列表里，可能形成多棵Tree即森林
    root = set()
    children_map = defaultdict(list)
    for i, parent in data:
        # 如果parent为None或0,或者在新增列表列不存在，则为单独的树root
        if not parent or parent not in node_set:
            root.add(i)
            continue
        # 作为其他树的孩子
        children_map[parent].append(i)

    # 使用BFS遍历出可插入的数据
    # 初始化队列
    queue = list(root)  # 使用index来模拟队列即可，不使用python的deque数据结构
    left_point = 0  # 初始化出队列指针
    right_point = len(queue)  # 初始化入队列指针
    # 当出队列指针=入队列指针时，说明队列为空，没有节点可遍历了
    while left_point < right_point:
        # 遍历队列里的值
        cnt = right_point - left_point
        for i in range(cnt):
            node = queue[left_point + i]
            # 避免出现环的情况下，死循环
            if node not in node_set:
                continue
            node_set.remove(node)
            # 检测是否有孩子，有的话则入队列
            if children_map[node]:
                queue.extend(children_map[node])  # 入队列
                right_point += len(children_map[node])  # 入队列指针往后移动
        # 出队列指针向后移动位置
        left_point += cnt

    # 翻转，从叶子节点 -> 根节点
    if reverse:
        queue.reverse()
    return queue
