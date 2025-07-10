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

from django.utils import translation
from rest_framework.renderers import JSONRenderer

from backend.common.constants import DjangoLanguageEnum


def handle_translate(data):
    """处理翻译"""
    # 判断是否Dict或List
    if not isinstance(data, dict) and not isinstance(data, list):
        return data

    # 对于List，则进行遍历，并递归查询每个数据
    if isinstance(data, list):
        return [handle_translate(i) for i in data]

    # 对于Dict，判断是否有_en结尾的
    ens = []
    for k in list(data.keys()):
        if isinstance(k, str) and k.endswith("_en"):
            ens.append(k)
    # 对于_en的，看是否需要替换
    for k_en in ens:
        k = k_en[0:-3]
        value_en = data.pop(k_en)
        if translation.get_language() == DjangoLanguageEnum.EN.value and value_en:
            data[k] = value_en
    # 对于其他字段，进行递归
    for k, v in data.items():
        data[k] = handle_translate(v)

    return data


class BKAPIRenderer(JSONRenderer):
    """
    采用统一的结构封装返回内容
    """

    SUCCESS_CODE = 0
    SUCCESS_MESSAGE = "OK"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if not isinstance(data, dict) or "result" not in data or "code" not in data:
            data = {
                "data": data,
                "result": True,
                "code": self.SUCCESS_CODE,
                "message": self.SUCCESS_MESSAGE,
            }
        # 处理翻译
        view = renderer_context.get("view")

        translate_exempt = view and getattr(view, "translate_exempt", False)
        if not translate_exempt and isinstance(data, dict) and "data" in data:
            data["data"] = handle_translate(data["data"])

        if renderer_context and "permissions" in renderer_context:
            data["permissions"] = renderer_context["permissions"]

        if renderer_context and "message" in renderer_context:
            data["message"] = renderer_context["message"]

        return super().render(data, accepted_media_type, renderer_context)
