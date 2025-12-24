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
from rest_framework.renderers import JSONRenderer


class GetAssetsRenderer(JSONRenderer):
    """
    采用统一的结构封装返回内容
    """

    SUCCESS_CODE = 0
    SUCCESS_MESSAGE = "OK"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        print("render_response", data)
        if not isinstance(data, dict) or "assets" not in data or "code" not in data:
            data = {
                "assets": data,
                "code": self.SUCCESS_CODE,
                "msg": self.SUCCESS_MESSAGE,
            }

        response = super().render(data, accepted_media_type, renderer_context)
        return response


class HandoverRenderer(JSONRenderer):
    SUCCESS_CODE = 0
    SUCCESS_MESSAGE = "OK"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if not isinstance(data, dict) or "err_list" not in data or "code" not in data:
            data = {
                "err_list": data,
                "code": self.SUCCESS_CODE,
                "msg": self.SUCCESS_MESSAGE,
            }

        response = super().render(data, accepted_media_type, renderer_context)
        return response
