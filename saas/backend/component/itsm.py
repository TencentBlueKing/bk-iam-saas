#!/usr/bin/env python3
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

from typing import Any, Dict, List

from django.conf import settings

from .apigw import _call_apigw_api
from .http import http_get, http_post


def list_process() -> List[Dict]:
    """获取审批流程列表"""
    url_path = "/api/v1/system_workflow/list/"

    params = {"system_id": settings.BK_ITSM_V4_SYSTEM_ID}
    data = _call_apigw_api(http_get, url_path, data=params)
    return data["results"]


def get_process_nodes(workflow_keys: str) -> Dict[Any, Any]:
    """获取审批流程，并根据单据创建者判断是否实例化审批节点"""
    # workflow_keys可以通过","分割传递多个
    url_path = "/api/v1/workflows/"
    params: Dict = {"workflow_keys": workflow_keys}

    data = _call_apigw_api(http_get, url_path, data=params)
    return data["items"][0]["activities"]


def create_ticket(
    workflow_key: str, form_data: Dict, operator: str, callback_url: str, callback_token: str, system_id: str
) -> Dict:
    """获取审批流程，并根据单据创建者判断是否实例化审批节点"""
    url_path = "/api/v1/ticket/create/"
    data = {
        "workflow_key": workflow_key,
        "form_data": form_data,
        "callback_url": callback_url,
        "callback_token": callback_token,
        "operator": operator,
        "system_id": system_id,
    }

    return _call_apigw_api(http_post, url_path, data=data)


def batch_query_ticket_result(ids: List[str]) -> List[Dict]:
    """
    批量查询单据结果
    """
    url_path = "/api/v1/system_ticket/list/"
    params = {"system_id": settings.BK_ITSM_V4_SYSTEM_ID, "id__in": ",".join(ids)}
    data = _call_apigw_api(http_get, url_path, data=params)
    return data["results"]


def withdraw_ticket(ticket_id: str):
    """撤销单据"""
    url_path = "/api/v1/tickets/revoked/"
    data = {"system_id": settings.BK_ITSM_V4_SYSTEM_ID, "ticket_id": ticket_id}
    return _call_apigw_api(http_post, url_path, data=data)
