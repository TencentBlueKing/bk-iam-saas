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
from urllib.parse import urlencode

from blue_krill.web.std_error import ErrorCode
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework import status


def _get_login_url():
    params = urlencode({"c_url": f"{settings.APP_URL}/login_success/", "app_code": settings.APP_CODE})
    login_plain_url = f"{settings.LOGIN_SERVICE_PLAIN_URL}?{params}"
    return {"login_url": settings.LOGIN_SERVICE_URL, "login_plain_url": login_plain_url}


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
    UNAUTHORIZED = ErrorCode(
        _("用户未登录或登录态失效，请使用登录链接重新登录"),
        code_num=1902401,
        status_code=status.HTTP_401_UNAUTHORIZED,
        data=_get_login_url(),
    )
    FORBIDDEN = ErrorCode(_("没有访问权限"), code_num=1902403, status_code=status.HTTP_403_FORBIDDEN)
    NOT_FOUND_ERROR = ErrorCode(_("数据不存在"), code_num=1902404, status_code=status.HTTP_404_NOT_FOUND)
    METHOD_NOT_ALLOWED = ErrorCode(
        _("不支持当前的请求方法"), code_num=1902405, status_code=status.HTTP_405_METHOD_NOT_ALLOWED
    )
    # 通用错误
    COMMON_ERROR = ErrorCode(_("请求失败"), code_num=1902400, status_code=status.HTTP_400_BAD_REQUEST)
    CONFLICT_ERROR = ErrorCode(_("与已有资源冲突(重名等)"), code_num=1902409, status_code=status.HTTP_409_CONFLICT)
    VALIDATE_ERROR = ErrorCode(_("参数校验失败"), code_num=1902412, status_code=status.HTTP_400_BAD_REQUEST)
    COMPONENT_ERROR = ErrorCode(_("请求第三方接口失败"), code_num=1902413, status_code=status.HTTP_200_OK)
    JSON_FORMAT_ERROR = ErrorCode(_("Json格式错误"), code_num=1902414, status_code=status.HTTP_400_BAD_REQUEST)
    UNSUPPORTED_MEDIA_TYPE = ErrorCode(
        _("不支持的media type"), code_num=1902415, status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    )
    INVALID_ARGS = ErrorCode(_("参数错误"), code_num=1902416, status_code=status.HTTP_400_BAD_REQUEST)
    ACTION_VALIDATE_ERROR = ErrorCode(_("操作检查错误"), code_num=1902417, status_code=status.HTTP_400_BAD_REQUEST)
    GROUP_TRANSFER_ERROR = ErrorCode(_("用户组转出错误"), code_num=1902418, status_code=status.HTTP_400_BAD_REQUEST)
    VALUE_ERROR = ErrorCode(_("数值错误"), code_num=1902419, status_code=status.HTTP_400_BAD_REQUEST)
    # 任务重复错误
    TASK_EXIST = ErrorCode(_("存在重复任务"), code_num=1902420, status_code=status.HTTP_409_CONFLICT)
    # 批量操作中 存在失败
    ACTIONS_PARTIAL_FAILED = ErrorCode(_("批量操作部分失败"), code_num=1902421, status_code=status.HTTP_200_OK)

    # [ESB错误/component的公共错误(网络错误等等): 19020xx]
    REMOTE_REQUEST_ERROR = ErrorCode(_("请求第三方API错误"), code_num=1902000, status_code=status.HTTP_200_OK)

    # [IAM后台错误: 19021xx]
    ENGINE_REQUEST_ERROR = ErrorCode(_("请求ENGINE错误"), code_num=1902102, status_code=status.HTTP_200_OK)

    # [第三方接入系统: 19022xx]
    RESOURCE_PROVIDER_ERROR = ErrorCode(
        _("接入系统资源接口请求失败"), code_num=1902200, status_code=status.HTTP_200_OK
    )
    RESOURCE_PROVIDER_AUTH_INFO_VALID = ErrorCode(
        _("接入系统注册的API认证信息不合法"), code_num=1902200, status_code=status.HTTP_200_OK
    )
    RESOURCE_PROVIDER_VALIDATE_ERROR = ErrorCode(
        _("API参数校验失败"), code_num=1902200, status_code=status.HTTP_200_OK
    )
    RESOURCE_PROVIDER_UNAUTHORIZED = ErrorCode(
        _("接入系统资源接口请求API认证失败"), code_num=1902201, status_code=status.HTTP_200_OK
    )
    RESOURCE_PROVIDER_NOT_FOUND = ErrorCode(
        _("接入系统不存在请求的资源类型或未实现该资源的查询方法"), code_num=1902204, status_code=status.HTTP_200_OK
    )
    RESOURCE_PROVIDER_SEARCH_VALIDATE_ERROR = ErrorCode(
        _("搜索Keyword参数校验失败"), code_num=1902206, status_code=status.HTTP_200_OK
    )
    RESOURCE_PROVIDER_DATA_TOO_LARGE = ErrorCode(
        _("接入系统需返回的资源内容过多，拒绝返回数据"), code_num=1902222, status_code=status.HTTP_200_OK
    )
    RESOURCE_PROVIDER_API_REQUEST_FREQUENCY_EXCEEDED = ErrorCode(
        _("请求频率超出接入系统API频率限制"), code_num=1902229, status_code=status.HTTP_200_OK
    )
    RESOURCE_PROVIDER_INTERNAL_SERVER_ERROR = ErrorCode(
        _("接入系统自身接口异常"), code_num=1902250, status_code=status.HTTP_200_OK
    )
    RESOURCE_PROVIDER_JSON_LOAD_ERROR = ErrorCode(
        _("接入系统自身接口返回数据进行JSON解析出错"), code_num=1902250, status_code=status.HTTP_200_OK
    )
    RESOURCE_PROVIDER_DATA_INVALID = ErrorCode(
        _("接入系统自身接口返回数据不符合要求"), code_num=1902250, status_code=status.HTTP_200_OK
    )

    # 通用系统错误
    SYSTEM_ERROR = ErrorCode(
        _("系统异常,请联系管理员处理"), code_num=1902500, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )

    # [ITSM请求或处理等错误 19026xx]
    ITSM_PROCESSOR_NOT_SUPPORT = ErrorCode(
        _("ITSM流程里存在IAM不支持的流程处理者"), code_num=1902602, status_code=status.HTTP_200_OK
    )


error_codes = ErrorCodes()
