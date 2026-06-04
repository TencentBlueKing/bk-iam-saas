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
import json
import zlib
from typing import Any, Dict


def compress_json(data: Dict[str, Any]) -> str:
    """将字典压缩为十六进制编码的字符串"""
    json_str = json.dumps(data, ensure_ascii=False)
    compressed = zlib.compress(json_str.encode("utf-8"))
    return compressed.hex()


def decompress_json(compressed_str: str) -> Dict[str, Any]:
    """将压缩字符串解压为字典"""
    if not compressed_str:
        return {}
    compressed_bytes = bytes.fromhex(compressed_str)
    json_str = zlib.decompress(compressed_bytes).decode("utf-8")
    return json.loads(json_str)
