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
import logging
import time
import traceback
from functools import partial
from typing import Any, Dict, List, Tuple, Union
from urllib.parse import urlparse

import requests
from aenum import LowerStrEnum, auto
from django.utils import translation
from django.utils.functional import SimpleLazyObject
from requests import auth

from backend.common.cache import cachedmethod
from backend.common.debug import http_trace
from backend.common.error_codes import error_codes
from backend.common.i18n import get_bk_language
from backend.common.local import local
from backend.metrics import callback_request_duration

request_pool = requests.Session()
logger = logging.getLogger("component")


ResponseCodeToErrorDict = {
    401: {"error": error_codes.RESOURCE_PROVIDER_UNAUTHORIZED, "replace_message": False},
    404: {"error": error_codes.RESOURCE_PROVIDER_NOT_FOUND, "replace_message": False},
    406: {"error": error_codes.RESOURCE_PROVIDER_SEARCH_VALIDATE_ERROR, "replace_message": True},
    422: {"error": error_codes.RESOURCE_PROVIDER_DATA_TOO_LARGE, "replace_message": False},
    429: {"error": error_codes.RESOURCE_PROVIDER_API_REQUEST_FREQUENCY_EXCEEDED, "replace_message": False},
    500: {"error": error_codes.RESOURCE_PROVIDER_INTERNAL_SERVER_ERROR, "replace_message": False},
}


class AuthTypeEnum(LowerStrEnum):
    NONE = auto()
    BASIC = auto()
    DIGEST = auto()


class ResourceAPIEnum(LowerStrEnum):
    """资源回调的API"""

    LIST_ATTR = auto()
    LIST_ATTR_VALUE = auto()
    LIST_INSTANCE = auto()
    FETCH_INSTANCE_INFO = auto()
    LIST_INSTANCE_BY_POLICY = auto()
    SEARCH_INSTANCE = auto()


def _generate_http_auth(auth_info: Dict[str, str]) -> Union[None, auth.HTTPBasicAuth, auth.HTTPDigestAuth]:
    # 无需认证
    if not auth_info:
        return None

    auth_type = auth_info["auth"]
    username = "bk_iam"
    password = auth_info["token"]

    # 不鉴权，一般测试联调时可能使用
    if auth_type == AuthTypeEnum.NONE.value:
        return None

    # http basic auth
    if auth_type == AuthTypeEnum.BASIC.value:
        return auth.HTTPBasicAuth(username, password)

    # http digest auth
    if auth_type == AuthTypeEnum.DIGEST.value:
        return auth.HTTPDigestAuth(username, password)

    # 后续可能支持Signature，可以继承auth.AuthBase类自定义相关子类
    # 可参考：https://requests.readthedocs.io/en/master/user/authentication/#new-forms-of-authentication

    raise error_codes.RESOURCE_PROVIDER_AUTH_INFO_VALID


class ResourceProviderClient:
    """资源提供者请求客户端"""

    def __init__(self, system_id: str, resource_type_id: str, url: str, auth_info: Dict[str, str]):
        """初始化请求需要的HTTP鉴权和其他HEADER"""
        self.system_id = system_id
        self.resource_type_id = resource_type_id
        self.url = url
        self.request_id = local.request_id
        self.request_username = local.request_username
        self.headers = {
            "Content-Type": "application/json",
            "Request-Id": self.request_id,
            "Blueking-Language": get_bk_language(translation.get_language()),
        }
        self.http_auth = _generate_http_auth(auth_info)
        self.timeout = 30

    def _call_api(self, data):
        """调用请求API"""
        trace_func = partial(http_trace, method="post", url=self.url, data=data)

        # 特殊场景下，给到请求时的用户名
        headers = self.headers.copy()
        if data["method"] in [ResourceAPIEnum.LIST_INSTANCE.value, ResourceAPIEnum.SEARCH_INSTANCE.value]:
            # 值有可能未空，因为并非所有请求都是来自页面
            headers["Request-Username"] = self.request_username

        kwargs = {
            "url": self.url,
            "json": data,
            "headers": headers,
            "auth": self.http_auth,
            "timeout": self.timeout,
            "verify": False,
        }

        # 由于request_id可能在请求返回header被更新，所以需要lazyObject
        # 该信息用于日志
        base_log_msg = SimpleLazyObject(
            lambda: (
                "resource_provider [system={}, resource={}]; "
                "API [request_id={}, request_username={}, url={}, data.method={}]; "
                "Detail[{}]"
            ).format(
                self.system_id,
                self.resource_type_id,
                self.request_id,
                self.request_username,
                self.url,
                data["method"],
                kwargs,
            )
        )

        # 回调请求的详细信息
        request_detail_info = (
            f"call {self.system_id}'s API fail! "
            f"you should check: "
            f"1.the network is ok 2.{self.system_id} is available 3.get details from {self.system_id}'s log. "
            f"[POST {urlparse(self.url).path} body.data.method={data['method']}]"
            f"(system_id={self.system_id}, resource_type_id={self.resource_type_id}) request_id={self.request_id}"
        )

        try:
            st = time.time()
            resp = request_pool.request("post", **kwargs)
            # 接入系统可返回request_id便于排查，避免接入系统未使用权限中心请求头里的request_id而自行生成，所以需要再获取赋值
            self.request_id = resp.headers.get("X-Request-Id") or self.request_id
            latency = int((time.time() - st) * 1000)
            # 打印DEBUG日志，用于调试时使用
            logger.debug(
                f"Response [status_code={resp.status_code}, content={resp.text}, Latency={latency}ms]."
                f"{base_log_msg}"
            )

            callback_request_duration.labels(
                system=self.system_id,
                resource_type=self.resource_type_id,
                function=data["method"],
                method="post",
                path=urlparse(self.url).path,
                status=resp.status_code,
            ).observe(latency)
        except requests.exceptions.RequestException as e:
            logger.exception(f"RequestException! {base_log_msg}")
            trace_func(exc=traceback.format_exc())
            # 接口不可达
            raise error_codes.RESOURCE_PROVIDER_ERROR.format(
                f"{self.system_id}'s API unreachable! {request_detail_info}. Exception {e}"
            )

        try:
            # 非2xx类都会异常
            resp.raise_for_status()
            # 返回可能非JSON
            resp = resp.json()
        except requests.exceptions.HTTPError:
            logger.exception(f"StatusCodeException! {base_log_msg}")
            trace_func(exc=traceback.format_exc())
            # 接口状态码异常
            raise error_codes.RESOURCE_PROVIDER_ERROR.format(
                f"{self.system_id}'s API response status code is `{resp.status_code}`, should be `200`! "
                f"{request_detail_info}"
            )
        except Exception as error:  # pylint: disable=broad-except
            logger.exception(f"ResponseDataException! response_content: {resp.text}， error: {error}. {base_log_msg}")
            trace_func(exc=traceback.format_exc())
            # 数据异常，JSON解析出错
            raise error_codes.RESOURCE_PROVIDER_JSON_LOAD_ERROR.format(
                f"{self.system_id}'s API error: {error}! " f"{request_detail_info}"
            )

        if "code" not in resp:
            raise error_codes.RESOURCE_PROVIDER_ERROR.format(
                f"{self.system_id}'s API response body.code missing! response_content: {resp}. {request_detail_info}"
            )

        code = resp["code"]
        if code == 0:
            # TODO: 验证Data数据的schema是否正确，可能得放到每个具体method去定义并校验
            return resp["data"]

        logger.error(f"Return Code Not Zero! response_content: {resp}. {base_log_msg}")

        # code不同值代表不同意思，401: 认证失败，404: 资源类型不存在，500: 接入系统异常，422: 资源内容过多，拒绝返回数据 等等
        if code not in ResponseCodeToErrorDict:
            trace_func(code=code)
            raise error_codes.RESOURCE_PROVIDER_ERROR.format(
                f"{self.system_id}'s API response body.code != 0, code is {code}! " f"{request_detail_info}"
            )

        raise ResponseCodeToErrorDict[code]["error"].format(
            message=(
                f"{self.system_id}'s API response body.code is {code}, body.message={resp.get('message', '')}! "
                f"{request_detail_info}"
            ),
            replace=ResponseCodeToErrorDict[code]["replace_message"],
        )

    def _handle_empty_data(self, data, default: Union[List, Dict]) -> Any:
        """处理兼容对方返回空数据为None、[]、{}、字符串"""
        if not data:
            return default

        # 校验类型是否一致
        if not isinstance(data, type(default)):
            raise error_codes.RESOURCE_PROVIDER_DATA_INVALID.format(
                f"{self.system_id}'s API response data wrong! "
                f"the type of data must be {type(default)}, but got {type(data)}! [data={data}]."
                f"you should check the response of {self.system_id}'s API "
                f"[POST {urlparse(self.url).path} request_id={self.request_id}]"
            )
        return data

    def _validate_paginated_data(self, resp_data: Dict) -> None:
        if "count" not in resp_data or "results" not in resp_data:
            raise error_codes.RESOURCE_PROVIDER_DATA_INVALID.format(
                f"{self.system_id}'s API response data wrong! "
                f"it's a paginated API, so the response.body.data should contain key `count` and `result`!"
                f"[response.body.data={resp_data}]"
                f"you should check the response of {self.system_id}'s API "
                f"[POST {urlparse(self.url).path} request_id={self.request_id}]."
            )

        count, results = resp_data["count"], resp_data["results"]
        if len(results) > count:
            logger.error(
                "resource_provider data invalid, "
                "the count of data must be greater than or equal to the length of results, "
                "count=%d, len(results)=%d",
                count,
                len(results),
            )
            raise error_codes.RESOURCE_PROVIDER_DATA_INVALID.format(
                f"{self.system_id}'s API response data wrong! "
                f"the count of data must be greater than or equal to the length of results, "
                f"[count={count}, len(results)={len(results)}]."
                f"you should check the response of {self.system_id}'s API "
                f"[POST {urlparse(self.url).path} request_id={self.request_id}]."
            )

    def list_attr(self) -> List[Dict[str, str]]:
        """查询某个资源类型可用于配置权限的属性列表"""
        data = {"type": self.resource_type_id, "method": ResourceAPIEnum.LIST_ATTR.value}
        resp_data = self._handle_empty_data(self._call_api(data), default=[])

        # {"id": "id", "display_name":""} should not be displayed in frontend for making policy
        removed_attr_id_data = [d for d in resp_data if d.get("id") != "id"]
        return removed_attr_id_data

    def list_attr_value(
        self, attr: str, filter_condition: Dict, page: Dict[str, int]
    ) -> Tuple[int, List[Dict[str, str]]]:
        """获取一个资源类型某个属性的值列表"""
        filter_condition["attr"] = attr
        data = {
            "type": self.resource_type_id,
            "method": ResourceAPIEnum.LIST_ATTR_VALUE.value,
            "filter": filter_condition,
            "page": page,
        }
        resp_data = self._handle_empty_data(self._call_api(data), default={"count": 0, "results": []})

        self._validate_paginated_data(resp_data)
        return resp_data["count"], resp_data["results"]

    def list_instance(self, filter_condition: Dict, page: Dict[str, int]) -> Tuple[int, List[Dict[str, str]]]:
        """根据过滤条件查询实例"""
        data = {
            "type": self.resource_type_id,
            "method": ResourceAPIEnum.LIST_INSTANCE.value,
            "filter": filter_condition,
            "page": page,
        }
        resp_data = self._handle_empty_data(self._call_api(data), default={"count": 0, "results": []})

        self._validate_paginated_data(resp_data)
        return resp_data["count"], resp_data["results"]

    def fetch_instance_info(self, filter_condition: Dict) -> List[Dict]:
        """批量获取资源实例详情"""
        data = {
            "type": self.resource_type_id,
            "method": ResourceAPIEnum.FETCH_INSTANCE_INFO.value,
            "filter": filter_condition,
        }
        return self._handle_empty_data(self._call_api(data), default=[])

    def list_instance_by_policy(
        self, filter_condition: Dict, page: Dict[str, int]
    ) -> Tuple[int, List[Dict[str, str]]]:
        """根据策略表达式查询资源实例"""
        data = {
            "type": self.resource_type_id,
            "method": ResourceAPIEnum.LIST_INSTANCE_BY_POLICY.value,
            "filter": filter_condition,
            "page": page,
        }
        resp_data = self._handle_empty_data(self._call_api(data), default={"count": 0, "results": []})

        self._validate_paginated_data(resp_data)
        return resp_data["count"], resp_data["results"]

    def search_instance(self, filter_condition: Dict, page: Dict[str, int]) -> Tuple[int, List[Dict[str, str]]]:
        """根据过滤条件且必须保证keyword不为空查询实例"""
        return self._search_instance(self.system_id, self.resource_type_id, filter_condition, page)

    @cachedmethod(timeout=60)  # 缓存1分钟
    def _search_instance(
        self, system_id: str, resource_type_id: str, filter_condition: Dict, page: Dict[str, int]
    ) -> Tuple[int, List[Dict[str, str]]]:
        """根据过滤条件且必须保证keyword不为空查询实例"""
        if not filter_condition["keyword"]:
            raise error_codes.RESOURCE_PROVIDER_VALIDATE_ERROR.format(
                f"search_instance[system:{system_id}] param keyword should not be empty"
            )
        data = {
            "type": resource_type_id,
            "method": ResourceAPIEnum.SEARCH_INSTANCE.value,
            "filter": filter_condition,
            "page": page,
        }
        resp_data = self._handle_empty_data(self._call_api(data), default={"count": 0, "results": []})

        self._validate_paginated_data(resp_data)
        return resp_data["count"], resp_data["results"]
