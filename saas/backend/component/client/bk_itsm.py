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

import io
import json
import logging
from typing import Any, Dict, List, Tuple
from urllib.parse import urlparse

from django.conf import settings

from backend.common.error_codes import error_codes
from backend.component.util import list_all_data_by_paging
from backend.util.url import url_join

from .apigw import BkApigwBaseClient
from .http import http_get_20x, http_post_20x

logger = logging.getLogger("component")


class BkITSMClient(BkApigwBaseClient):
    """ITSM 通过网关提供的 API"""

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.api_url = url_join(
            settings.BK_API_URL_TMPL.format(api_name=settings.ITSM_APIGW_NAME), settings.ITSM_APIGW_STAGE
        )
        self.headers = {
            **self.request_id_headers,
            # 只使用应用认证相关的 ITSM 接口
            **self.app_authorization_header,
            # ITSM 定义的 与 接入系统之间的认证
            "SYSTEM-TOKEN": settings.ITSM_SYSTEM_TOKEN,
            # 支持多租户
            "X-Bk-Tenant-Id": self.tenant_id,
        }

    def _call(self, http_func_only_20x, url_path, **kwargs):
        url = url_join(self.api_url, url_path)
        kwargs.setdefault("headers", {}).update(self.headers)
        ok, resp_data = http_func_only_20x(url, **kwargs)

        if not ok:
            logger.error(
                "itsm api failed! %s %s, kwargs: %s, request_id: %s, error: %s",
                http_func_only_20x.__name__,
                url,
                kwargs,
                self.request_id,
                resp_data["error"],
            )
            raise error_codes.REMOTE_REQUEST_ERROR.format(
                f"request itsm api fail! "
                f"Request=[{http_func_only_20x.__name__} {urlparse(url).path} request_id={self.request_id}]"
                f"error={resp_data['error']}"
            )

        code = resp_data.get("code", -1)
        if str(code) in ["0", "20000"]:
            return resp_data["data"]

        message = resp_data.get("message", "unknown")
        logger.error(
            "itsm api error! %s %s, kwargs: %s, request_id: %s, code: %s, message: %s",
            http_func_only_20x.__name__,
            url,
            kwargs,
            self.request_id,
            code,
            message,
        )

        raise error_codes.REMOTE_REQUEST_ERROR.format(
            f"request itsm api error! "
            f"Request=[{http_func_only_20x.__name__} {urlparse(url).path} request_id={self.request_id}] "
            f"Response[code={code}, message={message}]"
        )

    def list_process(self) -> List[Dict]:
        """获取审批流程列表"""
        url_path = "/api/v1/system_workflow/list/"

        def list_paging_process(page: int, page_size: int) -> Tuple[int, List[Dict]]:
            params = {"system_id": settings.ITSM_SYSTEM_ID, "page": page, "page_size": page_size}
            data = self._call(http_get_20x, url_path, params=params)
            return data["count"], data["results"]

        return list_all_data_by_paging(list_paging_process, page_size=20)

    def get_process_nodes(self, workflow_keys: str) -> Dict[Any, Any]:
        """获取审批流程，并根据单据创建者判断是否实例化审批节点"""
        # workflow_keys 可以通过","分割传递多个
        url_path = "/api/v1/workflows/"
        params = {"workflow_keys": workflow_keys}

        data = self._call(http_get_20x, url_path, params=params)
        return data["items"][0]["activities"]

    def create_ticket(
        self, workflow_key: str, form_data: Dict, operator: str, callback_url: str, callback_token: str
    ) -> Dict:
        """获取审批流程，并根据单据创建者判断是否实例化审批节点"""
        url_path = "/api/v1/ticket/create/"
        data = {
            "workflow_key": workflow_key,
            "form_data": form_data,
            "callback_url": callback_url,
            "callback_token": callback_token,
            "operator": operator,
            "system_id": settings.ITSM_SYSTEM_ID,
        }

        return self._call(http_post_20x, url_path, json=data)

    def batch_query_ticket_result(self, ids: List[str]) -> List[Dict]:
        """
        批量查询单据结果
        """
        url_path = "/api/v1/system_ticket/list/"

        def list_paging_ticket(page: int, page_size: int) -> Tuple[int, List[Dict]]:
            params = {
                "system_id": settings.ITSM_SYSTEM_ID,
                "id__in": ",".join(ids),
                "page": page,
                "page_size": page_size,
            }
            data = self._call(http_get_20x, url_path, params=params)
            return data["count"], data["results"]

        return list_all_data_by_paging(list_paging_ticket, page_size=50)

    def withdraw_ticket(self, ticket_id: str):
        """撤销单据"""
        url_path = "/api/v1/tickets/revoked/"
        data = {"system_id": settings.ITSM_SYSTEM_ID, "ticket_id": ticket_id}
        return self._call(http_post_20x, url_path, json=data)

    def create_system(self, name: str, code: str, token: str, desc: str):
        """创建系统"""
        url_path = "/api/v1/system/create/"
        data = {"name": name, "code": code, "token": token, "desc": desc}
        return self._call(http_post_20x, url_path, json=data)

    def migrate_system(self, workflow_template: Dict):
        """迁移系统工作流程"""
        url_path = "/api/v1/system/migrate/"

        # 将 workflow_template 转换为 JSON 字符串，并编码为 UTF-8
        json_data = json.dumps(workflow_template, indent=2)
        # 以 BytesIO 的形式创建文件对象并以上传文件方式发送请求
        with io.BytesIO(json_data.encode("utf-8")) as f:
            # Note: 设置更长的超时时间，避免导入过多工作流时超时
            return self._call(http_post_20x, url_path, files={"file": f.getvalue()}, timeout=180)
