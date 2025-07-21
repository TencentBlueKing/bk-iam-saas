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

import logging
from typing import Callable, Dict, List, Tuple
from urllib.parse import urlparse

from django.conf import settings

from backend.common.error_codes import error_codes
from backend.component.util import list_all_data_by_paging
from backend.util.url import url_join

from .apigw import BkApigwBaseClient
from .http import http_get_20x

logger = logging.getLogger("component")


class BkUserClient(BkApigwBaseClient):
    """蓝鲸用户管理通过 API 网关提供的接口"""

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.api_url = url_join(
            settings.BK_API_TMPL.format(api_name=settings.BK_USER_APIGW_NAME), settings.BK_USER_APIGW_STAGE
        )
        self.headers = {
            **self.request_id_headers,
            # 只使用应用态接口
            **self.app_authorization_header,
            # 支持多租户
            "X-Bk-Tenant-Id": self.tenant_id,
        }

    def _call(self, http_func_only_20x, url_path, **kwargs):
        url = url_join(self.api_url, url_path)
        # TODO: 如何使用 requests retries 重试机制，需自定义 requests.Session; 如何传入呢？
        ok, resp_data = http_func_only_20x(url, **kwargs)

        if not ok:
            logger.error(
                "bk-user api failed! %s %s, kwargs: %s, request_id: %s, error: %s",
                http_func_only_20x.__name__,
                url,
                kwargs,
                self.request_id,
                resp_data["error"],
            )
            raise error_codes.REMOTE_REQUEST_ERROR.format(
                f"request bk-user api fail! "
                f"Request=[{http_func_only_20x.__name__} {urlparse(url).path} request_id={self.request_id}]"
                f"error={resp_data['error']}"
            )

        return resp_data["data"]

    def _new_paging_func(self, url_path: str) -> Callable[[int, int], Tuple[int, List[Dict]]]:
        """创建分页函数"""

        def list_paging(page: int, page_size: int) -> Tuple[int, List[Dict]]:
            params = {"page": page, "page_size": page_size}
            data = self._call(http_get_20x, url_path, params=params)
            return data["count"], data["results"]

        return list_paging

    def list_tenant(self) -> List[Dict]:
        """获取全量租户

        :return: [
            {
                "id": "default",
                "name": "租户 A",
                "status": "enabled",
            },
            ...
        ]
        """
        url_path = "/api/v3/open/tenants/"
        return self._call(http_get_20x, url_path)

    def list_user(self) -> List[Dict]:
        """获取全量用户

        :return: [
            {
                "bk_username": "q9k6bhqks0ckl5ew"
                "full_name": "张三",
                "display_name": "zhangsan(张三)",
                "status": "enabled",
            },
            ...
        ]
        """
        url_path = "/api/v3/open/tenant/users/"
        return list_all_data_by_paging(self._new_paging_func(url_path), page_size=1000)

    def list_virtual_user(self) -> List[Dict]:
        """获取全量虚拟用户

        :return: [
            {
                "bk_username": "klzwge6k69ly0rjt",
                "login_name": "virtual_user_1",
                "full_name": "虚拟用户 1",
                "display_name": "virtual_user_1(虚拟用户 1)",
                "status": "enabled",
            },
            ...
        ]
        """
        url_path = "/api/v3/open/tenant/virtual-users/"
        return list_all_data_by_paging(self._new_paging_func(url_path), page_size=500)

    def list_department(self) -> List[Dict]:
        """获取全量部门

        :return: [
            {
                "id": 3,
                "name": "部门 B",
                "parent_id": 1
            },
            ...
        ]
        """
        url_path = "/api/v3/open/tenant/departments/"
        return list_all_data_by_paging(self._new_paging_func(url_path), page_size=500)

    def list_department_user_relation(self) -> List[Dict]:
        """获取全量部门用户关系

        :return: [
            {
                "department_id": 1,
                "bk_username": "q9k6bhqks0ckl5ew",
            }
            ...
        ]
        """
        url_path = "/api/v3/open/tenant/department-user-relations/"
        return list_all_data_by_paging(self._new_paging_func(url_path), page_size=500)

    def retrieve_user(self, bk_username: str) -> Dict:
        """获取单个用户信息

        :param bk_username: 用户名
        :return: {
            "bk_username": "7idwx3b7nzk6xigs",
            "display_name": "zhangsan(张三)",
            "time_zone": "Asia/Shanghai",
            "language": "zh-cn",
            "status": "enabled"
        }
        """
        url_path = f"/api/v3/open/tenant/users/{bk_username}/"
        return self._call(http_get_20x, url_path)

    def batch_lookup_virtual_user(self, bk_usernames: List[str]) -> List[Dict]:
        """获取虚拟用户信息

        :param bk_usernames: 虚拟用户名
        :return: {
            "bk_username": "klzwge6k69ly0rjt",
            "login_name": "virtual_user_1",
            "display_name": "virtual_user_1(虚拟用户 1)",
        }
        """
        url_path = "/api/v3/open/tenant/virtual-users/-/lookup/"
        # FIXME(nan): bk_usernames 最多支持 100 个，后面这里需要改成分组查询
        assert len(bk_usernames) <= 100  # noqa: PLR2004

        params = {
            "lookups": ",".join(bk_usernames),
            "lookup_field": "bk_username",
        }
        return self._call(http_get_20x, url_path, params=params)

    def retrieve_user_or_virtual_user(self, bk_username: str) -> Dict:
        """获取单个用户或虚拟用户信息

        Note: 由于 IAM 并不区分用户和虚拟用户，但用户管理接口是区分的，所以需要查询两次确定
        :param bk_username: 用户名
        :return: {
            "bk_username": "q9k6bhqks0ckl5ew",
            "full_name": "张三",
            "display_name": "zhangsan(张三)",
            "status": "enabled",
        }
        """
        # 由于虚拟账号数量较少且支持批量查询，即性能高且容易判断是否存在，所以先查询虚拟用户
        virtual_users = self.batch_lookup_virtual_user([bk_username])
        if virtual_users:
            virtual_user = virtual_users[0]
            # FIXME(nan): 由于用户管理提供的 batch_lookup_virtual_user 接口，返回没有 full_name 和 status 字段
            #  所有这里暂时使用 display_name 代替 full_name; status 字段默认设置为 enabled
            virtual_user["full_name"] = virtual_user["display_name"]
            virtual_user["status"] = "enabled"
            return virtual_user

        # 如果没有查询到虚拟用户，则查询普通用户
        user = self.retrieve_user(bk_username)
        # FIXME(nan): 由于用户管理提供的 retrieve_user 接口，返回没有 full_name 字段
        #  暂时使用 display_name 代替 full_name
        user["full_name"] = user["display_name"]

        return user

    def list_user_department(self, bk_username: str, with_ancestors: bool = False) -> List[Dict]:
        """获取用户所在的部门

        :param bk_username: 用户名
        :param with_ancestors: 是否包含祖先部门
        :return: [
            {
                "id": 1,
                "name": "部门 A",
                "ancestors": [
                    {
                        "id": 1,
                        "name": "部门 A"
                    },
                    {
                        "id": 2,
                        "name": "部门 B"
                    }
                ]
            },
            ...
        ]
        """
        url_path = f"/api/v3/open/tenant/users/{bk_username}/departments/"
        params = {"with_ancestors": with_ancestors}
        return self._call(http_get_20x, url_path, params=params)
