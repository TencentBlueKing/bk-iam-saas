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

import random

DEF_RANDOM_CHARACTER_SET = "abcdefghijklmnopqrstuvwxyz0123456789"


def generate_random_string(length=30, chars=DEF_RANDOM_CHARACTER_SET):
    """Generates a non-guessable random string

    Random string should be strings of random characters. It should not be guessable
    and entropy when generating the random characters is important. Which is
    why SystemRandom is used instead of the default random.choice method.
    """
    rand = random.SystemRandom()
    return "".join(rand.choice(chars) for x in range(length))


def generate_random_number(min_num=0, max_num=100):
    """生成随机数"""
    rand = random.SystemRandom()
    return rand.randint(min_num, max_num)
