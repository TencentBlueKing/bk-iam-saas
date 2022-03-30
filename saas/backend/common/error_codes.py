# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-权限中心(BlueKing-IAM) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

Customized error handling for restapi framework
"""
import copy
from typing import Optional, Type

from django.utils.translation import gettext_lazy as _
from rest_framework import status


class CodeException(Exception):
    """A common error with code_name and description"""

    delimiter = ": "

    def __init__(self, code: int, message: str, status_code: int = status.HTTP_200_OK):
        self.code = code
        self.message = message
        self.status_code = status_code
        # Default Error code
        self.code_name = "UNKNOWN_ERROR_CODE"

        super().__init__(code, message, status_code)

    def _format_message(self, message: Optional[str] = None, replace: bool = False, **kwargs):
        """Using a customized message for this ErrorCode

        :param str message: if not given, default message will be used
        :param bool replace: replace default message if true
        """
        new_obj = copy.deepcopy(self)
        if message:
            if replace:
                new_obj.message = message
            else:
                new_obj.message += "%s%s" % (new_obj.delimiter, message)

        # Render message string
        if kwargs:
            new_obj.message = new_obj.message.format(**kwargs)
        return new_obj

    def as_json(self):
        # append the code_name
        message = "%s (%s)" % (self.message, self.code_name)
        return {"result": False, "code": self.code, "message": message, "data": None}

    def __str__(self):
        return "<ErrorCode %s:(%s)>" % (self.code, self.message)


class APIException(CodeException):
    """API Error"""

    def format(self, message: Optional[str] = None, replace: bool = False, **kwargs):
        """Using a customized message for this ErrorCode

        :param str message: if not given, default message will be used
        :param bool replace: replace default message if true
        """
        return super()._format_message(message, replace, **kwargs)


class RemoteAPIException(CodeException):
    """Remote API Request Error"""

    def format(self, message: Optional[str] = None, replace: bool = False, **kwargs):
        return super()._format_message(message, replace, **kwargs)


def auto_configure_codenames(cls: Type):
    """Auto replace code_name fields"""
    for key, value in cls.__dict__.items():
        if isinstance(value, APIException) or isinstance(value, RemoteAPIException):
            # Set code_name attribute
            value.code_name = key
    return cls


@auto_configure_codenames
class ErrorCodes:
    """Error codes collection"""

    # esb错误 19020xx  component的公共错误(网络错误等等)
    # iam后台错误 19021xx  直接给到提示信息request id 后台code
    # 第三方接入系统 19022xx
    # 用户管理错误 19023xx
    # ITSM错误 19025xx
    # IAM SaaS 用户请求错误 19024xx

    # [IAM SaaS 用户请求错误：19024xx]
    # 未登录/无权限/不存在
    UNAUTHORIZED = APIException(1902401, _("用户未登录或登录态失效，请使用登录链接重新登录"), status_code=status.HTTP_401_UNAUTHORIZED)
    FORBIDDEN = APIException(1902403, _("没有访问权限"), status_code=status.HTTP_403_FORBIDDEN)
    NOT_FOUND_ERROR = APIException(1902404, _("数据不存在"), status_code=status.HTTP_404_NOT_FOUND)
    # 通用错误
    COMMON_ERROR = APIException(1902400, _("请求失败"), status_code=status.HTTP_400_BAD_REQUEST)
    CONFLICT_ERROR = APIException(1902409, _("与已有资源冲突(重名等)"), status_code=status.HTTP_409_CONFLICT)
    VALIDATE_ERROR = APIException(1902412, _("参数校验失败"), status_code=status.HTTP_400_BAD_REQUEST)
    COMPONENT_ERROR = APIException(1902413, _("请求第三方接口失败"))
    JSON_FORMAT_ERROR = APIException(1902414, _("Json格式错误"), status_code=status.HTTP_400_BAD_REQUEST)
    METHOD_NOT_ALLOWED = APIException(1902415, _("不支持当前的请求方法"), status_code=status.HTTP_405_METHOD_NOT_ALLOWED)
    INVALID_ARGS = APIException(1902416, _("参数错误"), status_code=status.HTTP_400_BAD_REQUEST)
    ACTION_VALIDATE_ERROR = APIException(1902417, _("操作检查错误"), status_code=status.HTTP_400_BAD_REQUEST)
    GROUP_TRANSFER_ERROR = APIException(1902418, _("用户组转出错误"), status_code=status.HTTP_400_BAD_REQUEST)
    VALUE_ERROR = APIException(1902419, _("数值错误"), status_code=status.HTTP_400_BAD_REQUEST)
    # 任务重复错误
    TASK_EXIST = APIException(1902420, _("存在重复任务"), status_code=status.HTTP_409_CONFLICT)
    # [ESB错误/component的公共错误(网络错误等等): 19020xx]
    REMOTE_REQUEST_ERROR = RemoteAPIException(1902000, _("请求第三方API错误"))

    # [IAM后台错误: 19021xx]
    ENGINE_REQUEST_ERROR = APIException(1902102, _("请求ENGINE错误"))

    # [第三方接入系统: 19022xx]
    RESOURCE_PROVIDER_ERROR = APIException(1902200, _("接入系统资源接口请求失败"))
    RESOURCE_PROVIDER_AUTH_INFO_VALID = APIException(1902200, _("接入系统注册的API认证信息不合法"))
    RESOURCE_PROVIDER_VALIDATE_ERROR = APIException(1902200, _("API参数校验失败"))
    RESOURCE_PROVIDER_UNAUTHORIZED = APIException(1902201, _("接入系统资源接口请求API认证失败"))
    RESOURCE_PROVIDER_NOT_FOUND = APIException(1902204, _("接入系统不存在请求的资源类型或未实现该资源的查询方法"))
    RESOURCE_PROVIDER_SEARCH_VALIDATE_ERROR = APIException(1902206, _("搜索Keyword参数校验失败"))
    RESOURCE_PROVIDER_DATA_TOO_LARGE = APIException(1902222, _("接入系统需返回的资源内容过多，拒绝返回数据"))
    RESOURCE_PROVIDER_API_REQUEST_FREQUENCY_EXCEEDED = APIException(1902229, _("请求频率超出接入系统API频率限制"))
    RESOURCE_PROVIDER_INTERNAL_SERVER_ERROR = APIException(1902250, _("接入系统自身接口异常"))
    RESOURCE_PROVIDER_JSON_LOAD_ERROR = APIException(1902250, _("接入系统自身接口返回数据进行JSON解析出错"))
    RESOURCE_PROVIDER_DATA_INVALID = APIException(1902250, _("接入系统自身接口返回数据不符合要求"))

    # 通用系统错误
    SYSTEM_ERROR = APIException(1902500, _("系统错误"), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # [ITSM请求或处理等错误 19026xx]
    # ITSM_REQUEST_ERROR = RemoteAPIException(1902501, _("ITSM请求返回码非0"))
    ITSM_PROCESSOR_NOT_SUPPORT = RemoteAPIException(1902602, _("ITSM流程里存在IAM不支持的流程处理者"))


error_codes = ErrorCodes()
