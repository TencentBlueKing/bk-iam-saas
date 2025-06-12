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

import datetime
from typing import Dict, List, Tuple

import requests
from django.conf import settings
from urllib3.util.retry import Retry

from .esb import _call_esb_api
from .http import http_get
from .util import list_all_data_by_paging

retries = Retry(total=settings.REQUESTS_MAX_RETRIES, backoff_factor=0.1, status_forcelist=[500])
session = requests.Session()
adapter = requests.adapters.HTTPAdapter(
    pool_connections=settings.REQUESTS_POOL_CONNECTIONS,
    pool_maxsize=settings.REQUESTS_POOL_MAXSIZE,
    max_retries=retries,
)
session.mount("https://", adapter)
session.mount("http://", adapter)

# 用户管理，分页的默认数量为1000（实际最大可支持2000）
USERMGR_DEFAULT_PAGE_SIZE = 1000

# 超时时间
USERMGR_DEFAULT_TIMEOUT = 60


def list_category() -> List[Dict]:
    """获取目录列表"""

    def list_paging_category(page: int, page_size: int) -> Tuple[int, List[Dict]]:
        """[分页]获取目录列表"""
        url_path = "/api/c/compapi/v2/usermanage/list_categories/"
        params = {
            "fields": "id,display_name",
            "ordering": "id",
            "page": page,
            "page_size": page_size,
        }
        data = _call_esb_api(http_get, url_path, data=params, timeout=USERMGR_DEFAULT_TIMEOUT, request_session=session)
        return data["count"], data["results"]

    return list_all_data_by_paging(list_paging_category, USERMGR_DEFAULT_PAGE_SIZE)


def retrieve_user(username, fields: str = "id,username,display_name,staff_status,category_id") -> Dict:
    """获取单一用户信息"""
    url_path = "/api/c/compapi/v2/usermanage/retrieve_user/"
    params = {"id": username, "fields": fields}
    return _call_esb_api(http_get, url_path, data=params, timeout=USERMGR_DEFAULT_TIMEOUT, request_session=session)


def list_new_user(end_utc_time: datetime.datetime, minute_delta: int = 0) -> List[Dict]:
    """查询新增用户，条件是时间"""
    # 生成要查询的条件
    create_times = [end_utc_time]
    for i in range(minute_delta):
        create_times.append(end_utc_time - datetime.timedelta(minutes=i + 1))
    create_time_fuzzy_lookups = [t.strftime("%Y-%m-%d %H:%M") for t in create_times]
    fuzzy_lookups = ",".join(create_time_fuzzy_lookups)

    def list_paging_new_user(page: int, page_size: int) -> Tuple[int, List[Dict]]:
        """[分页]获取新增用户列表"""
        url_path = "/api/c/compapi/v2/usermanage/list_users/"
        params = {
            "fields": "id,username,display_name,staff_status,category_id",
            "ordering": "id",
            "page": page,
            "page_size": page_size,
            "lookup_field": "create_time",
            "fuzzy_lookups": fuzzy_lookups,
        }
        data = _call_esb_api(http_get, url_path, data=params, timeout=USERMGR_DEFAULT_TIMEOUT, request_session=session)
        return data["count"], data["results"]

    return list_all_data_by_paging(list_paging_new_user, USERMGR_DEFAULT_PAGE_SIZE)


def list_profile() -> List[Dict]:
    """获取用户列表"""

    def list_paging_profile(page: int, page_size: int) -> Tuple[int, List[Dict]]:
        """[分页]获取用户列表"""
        url_path = "/api/c/compapi/v2/usermanage/list_users/"
        params = {
            "fields": "id,username,display_name,staff_status,category_id",
            "ordering": "id",
            "page": page,
            "page_size": page_size,
        }
        data = _call_esb_api(http_get, url_path, data=params, timeout=USERMGR_DEFAULT_TIMEOUT, request_session=session)
        return data["count"], data["results"]

    return list_all_data_by_paging(list_paging_profile, USERMGR_DEFAULT_PAGE_SIZE)


def list_department() -> List[Dict]:
    """获取部门列表"""

    def list_paging_department(page: int, page_size: int) -> Tuple[int, List[Dict]]:
        """[分页]获取部门列表"""
        url_path = "/api/c/compapi/v2/usermanage/list_departments/"
        params = {"fields": "id,name,category_id,parent,order", "ordering": "id", "page": page, "page_size": page_size}
        data = _call_esb_api(http_get, url_path, data=params, timeout=USERMGR_DEFAULT_TIMEOUT, request_session=session)
        return data["count"], data["results"]

    return list_all_data_by_paging(list_paging_department, USERMGR_DEFAULT_PAGE_SIZE)


def list_department_profile() -> List[Dict]:
    """获取部门与用户关系列表"""

    def _list_paging_department_profile(page: int, page_size: int) -> Tuple[int, List[Dict]]:
        """[分页]获取部门与用户关系列表"""
        url_path = "/api/c/compapi/v2/usermanage/list_edges_department_profile/"
        params = {"ordering": "id", "page": page, "page_size": page_size}
        data = _call_esb_api(http_get, url_path, data=params, timeout=USERMGR_DEFAULT_TIMEOUT, request_session=session)
        return data["count"], data["results"]

    return list_all_data_by_paging(_list_paging_department_profile, USERMGR_DEFAULT_PAGE_SIZE)


def list_profile_leader() -> List[Dict]:
    """获取用户Leader列表"""

    def _list_paging_profile_leader(page: int, page_size: int) -> Tuple[int, List[Dict]]:
        """[分页]获取用户Leader列表"""
        url_path = "/api/c/compapi/v2/usermanage/list_edges_leader_profile/"
        params = {"ordering": "id", "page": page, "page_size": page_size}
        data = _call_esb_api(http_get, url_path, data=params, timeout=USERMGR_DEFAULT_TIMEOUT, request_session=session)
        return data["count"], data["results"]

    return list_all_data_by_paging(_list_paging_profile_leader, USERMGR_DEFAULT_PAGE_SIZE)
