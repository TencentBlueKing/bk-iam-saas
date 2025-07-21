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


def url_join(host: str, *paths: str) -> str:
    """
    拼接 host, path 生成 url

    处理 host, path有多余/的情况
    """
    if not paths:
        return host

    # 处理头尾的斜杠
    leading_slash = "/" if paths[0].startswith("/") else ""
    trailing_slash = "/" if paths[-1].endswith("/") else ""
    # 去除每个路径的前后斜杠，并用/连接
    url_path = leading_slash + "/".join(p.strip("/") for p in paths) + trailing_slash

    # 确保 host 以斜杠结尾，path 以斜杠开头
    return "{}/{}".format(host.rstrip("/"), url_path.lstrip("/"))
