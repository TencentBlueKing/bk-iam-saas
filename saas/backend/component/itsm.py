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
from typing import Dict, List, Optional

from .esb import _call_esb_api
from .http import http_get, http_post


def list_process() -> List[Dict]:
    """获取审批流程列表"""
    url_path = "/api/c/compapi/v2/itsm/get_services/"
    params = {"display_type": "API", "display_role": "BK_IAM"}
    return _call_esb_api(http_get, url_path, data=params)


def get_process_nodes(process_id: int, ticket_creator: str = "") -> List[Dict]:
    """获取审批流程，并根据单据创建者判断是否实例化审批节点"""
    url_path = "/api/c/compapi/v2/itsm/get_service_roles/"
    params: Dict = {"service_id": process_id}
    if ticket_creator:
        params["ticket_creator"] = ticket_creator
    return _call_esb_api(http_get, url_path, data=params)


def create_ticket(
    process_id: int,
    creator: str,
    callback_url: str,
    node_processors: Dict[int, str],
    title: str,
    application_type_display: str,
    organization_names: str,
    reason: str,
    content: Dict,
    tag: str = "",
    dynamic_fields: Optional[List] = None,
    **kwargs,
) -> Dict:
    """获取审批流程，并根据单据创建者判断是否实例化审批节点"""
    url_path = "/api/c/compapi/v2/itsm/create_ticket/"
    data = {
        "service_id": process_id,
        "creator": creator,
        "meta": {"callback_url": callback_url, "state_processors": node_processors},
        "fields": [
            {"key": "title", "value": title, "meta": {"language": {"en": "title"}}},
            {
                "key": "application_type",
                "value": application_type_display,
                "meta": {"language": {"en": "application type"}},
            },
            {"key": "organization", "value": organization_names, "meta": {"language": {"en": "organization"}}},
            {"key": "reason", "value": reason, "meta": {"language": {"en": "reason"}}},
            {"key": "content", "value": content, "meta": {"language": {"en": "content"}}},
        ],
    }

    if dynamic_fields:
        data["dynamic_fields"] = dynamic_fields

    if tag:
        data["tag"] = tag  # NOTE: 用于ITSM审批单列表api筛选过滤字段

    # 填充额外的fields
    for k, v in kwargs.items():
        data["fields"].append({"key": k, "value": v})  # type: ignore
    return _call_esb_api(http_post, url_path, data=data)


def batch_query_ticket_result(sns: List[str]) -> List[Dict]:
    """
    批量查询单据结果
    """
    url_path = "/api/c/compapi/v2/itsm/ticket_approval_result/"
    data = {"sn": sns}
    return _call_esb_api(http_post, url_path, data=data)


def withdraw_ticket(sn: str, operator: str):
    """撤销单据"""
    url_path = "/api/c/compapi/v2/itsm/operate_ticket/"
    data = {"sn": sn, "operator": operator, "action_type": "WITHDRAW", "action_message": "applicant withdraw ticket"}
    return _call_esb_api(http_post, url_path, data=data)
