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
from typing import Dict, List, Tuple

from django.conf import settings

from backend.common.error_codes import error_codes
from backend.common.local import local
from backend.publisher import shortcut as publisher_shortcut
from backend.util.cache import region
from backend.util.json import json_dumps
from backend.util.url import url_join

from .http import http_delete, http_get, http_post, http_put, logger
from .util import execute_all_data_by_paging, list_all_data_by_paging

DEFAULT_SYSTEM_FIELDS = "id,name,name_en,description,description_en"
DEFAULT_ACTION_FIELDS = "id,name,name_en,description,description_en"
DEFAULT_RESOURCE_TYPE_FIELDS = "id,name,name_en"

permission_logger = logging.getLogger("permission")


def _call_iam_api(http_func, url_path, data, timeout=30):
    # 默认请求头
    headers = {
        "Content-Type": "application/json",
        "X-Request-Id": local.request_id,
    }
    if settings.BK_IAM_HOST_TYPE == "apigateway":
        headers["x-bkapi-authorization"] = json_dumps(
            {"bk_app_code": settings.APP_ID, "bk_app_secret": settings.APP_TOKEN}
        )
    elif settings.BK_IAM_HOST_TYPE == "direct":
        headers.update({"X-Bk-App-Code": settings.APP_ID, "X-Bk-App-Secret": settings.APP_TOKEN})

    url = url_join(settings.BK_IAM_HOST, url_path)
    kwargs = {"url": url, "data": data, "headers": headers, "timeout": timeout}

    ok, data = http_func(**kwargs)
    # remove sensitive info
    kwargs["headers"] = {}

    # process result
    if not ok:
        message = "iam api failed, method: %s, info: %s" % (http_func.__name__, kwargs)
        logger.error(message)
        raise error_codes.REMOTE_REQUEST_ERROR.format(f'request iam api error: {data["error"]}')

    code = data["code"]
    message = data["message"]

    if code == 0:
        return data["data"]

    logger.warning(
        "iam api warning, request_id: %s, method: %s, info: %s, code: %d message: %s",
        local.request_id,
        http_func.__name__,
        kwargs,
        code,
        message,
    )

    error_message = (
        f"Request=[{http_func.__name__} {url_path} request_id={local.request_id}],"
        f"Response[code={code}, message={message}]"
    )
    raise error_codes.IAM_REQUEST_ERROR.format(error_message)


def list_system(fields: str = DEFAULT_SYSTEM_FIELDS) -> List[Dict]:
    """
    获取系统列表
    """
    url_path = "/api/v1/web/systems"
    return _call_iam_api(http_get, url_path, data={"fields": fields})


def get_system(system_id: str, fields: str = DEFAULT_SYSTEM_FIELDS) -> Dict:
    """
    获取单个系统信息
    """
    url_path = f"/api/v1/web/systems/{system_id}"
    return _call_iam_api(http_get, url_path, data={"fields": fields})


@region.cache_on_arguments(expiration_time=60)  # 缓存1分钟
def list_resource_type(systems: List[str], fields: str = DEFAULT_RESOURCE_TYPE_FIELDS) -> Dict[str, List[Dict]]:
    """
    查询系统的资源类型
    """
    url_path = "/api/v1/web/resource-types"
    params = {"systems": ",".join(systems), "fields": fields}
    return _call_iam_api(http_get, url_path, data=params)


@region.cache_on_arguments(expiration_time=60)  # 缓存1分钟
def list_action(system_id: str, fields: str = DEFAULT_ACTION_FIELDS) -> List[Dict]:
    """
    获取系统的所有action列表
    """
    url_path = f"/api/v1/web/systems/{system_id}/actions"
    return _call_iam_api(http_get, url_path, data={"fields": fields})


def get_action(system_id: str, action_id: str) -> Dict:
    """
    获取操作的详细信息
    """
    url_path = f"/api/v1/web/systems/{system_id}/actions/{action_id}"
    return _call_iam_api(http_get, url_path, data={})


@region.cache_on_arguments(expiration_time=60)
def list_instance_selection(system_id: str) -> List[Dict]:
    """
    获取系统的实例视图列表
    """
    url_path = f"/api/v1/web/systems/{system_id}/instance-selections"
    return _call_iam_api(http_get, url_path, data={})


def get_action_groups(system_id: str) -> List[Dict]:
    """
    获取指定操作类型的关联拓扑
    """
    url_path = f"/api/v1/web/systems/{system_id}/system-settings/action-groups"
    return _call_iam_api(http_get, url_path, data={})


def get_resource_creator_actions(system_id: str) -> Dict:
    """
    获取新建关联配置
    """
    url_path = f"/api/v1/web/systems/{system_id}/system-settings/resource-creator-actions"
    return _call_iam_api(http_get, url_path, data={})


def get_common_actions(system_id: str) -> Dict:
    """
    获取常用操作
    """
    url_path = f"/api/v1/web/systems/{system_id}/system-settings/common-actions"
    return _call_iam_api(http_get, url_path, data={})


def create_subjects(subjects: List[Dict[str, str]]) -> None:
    """
    创建subject
    """
    url_path = "/api/v1/web/subjects"
    return _call_iam_api(http_post, url_path, data=subjects)


def update_subjects(subjects: List[Dict[str, str]]) -> None:
    """
    更新subject
    """
    url_path = "/api/v1/web/subjects"
    return _call_iam_api(http_put, url_path, data=subjects)


def create_subjects_by_auto_paging(subjects: List[Dict[str, str]]) -> None:
    """通过自动分页批量创建Subject"""

    def create_paging_subjects(paging_data):
        """[分页]创建Subject"""
        url_path = "/api/v1/web/subjects"
        _call_iam_api(http_post, url_path, data=paging_data)

    return execute_all_data_by_paging(create_paging_subjects, subjects, 3000)


def delete_subjects(subjects: List[dict]) -> None:
    """
    删除授权对象
    """
    url_path = "/api/v1/web/subjects"
    result = _call_iam_api(http_delete, url_path, data=subjects)
    # 发布订阅-删除策略
    publisher_shortcut.publish_delete_policies_by_subject(subjects)
    return result


def delete_subjects_by_auto_paging(subjects: List[Dict[str, str]]) -> None:
    """通过自动分页批量删除Subject"""

    def delete_paging_subjects(paging_data):
        """[分页]删除Subject"""
        url_path = "/api/v1/web/subjects"
        _call_iam_api(http_delete, url_path, data=paging_data)
        # 发布订阅-删除策略
        publisher_shortcut.publish_delete_policies_by_subject(paging_data)

    return execute_all_data_by_paging(delete_paging_subjects, subjects, 3000)


def list_subject(_type: str, limit: int = 10, offset: int = 0) -> Dict:
    """
    获取subject列表
    """
    url_path = "/api/v1/web/subjects"
    params = {"type": _type, "limit": limit, "offset": offset}
    return _call_iam_api(http_get, url_path, data=params)


def list_all_subject(_type: str) -> List[Dict]:
    """
    获取某个类型的所有Subject
    """

    def list_paging_subject(page: int, page_size: int) -> Tuple[int, List[Dict]]:
        """[分页]获取部门列表"""
        limit = page_size
        offset = (page - 1) * page_size
        url_path = "/api/v1/web/subjects"
        params = {"type": _type, "limit": limit, "offset": offset}
        data = _call_iam_api(http_get, url_path, data=params)
        return data["count"], data["results"]

    return list_all_data_by_paging(list_paging_subject, 1000)


def list_all_subject_department() -> List[Dict]:
    """
    所有Subject的departments
    """

    def list_paging_subject_department(page: int, page_size: int) -> Tuple[int, List[Dict]]:
        """[分页]获取部门列表"""
        limit = page_size
        offset = (page - 1) * page_size
        url_path = "/api/v1/web/subject-departments"
        params = {"limit": limit, "offset": offset}
        data = _call_iam_api(http_get, url_path, data=params)
        return data["count"], data["results"]

    return list_all_data_by_paging(list_paging_subject_department, 1000)


def create_subject_departments_by_auto_paging(subject_departments: List[Dict]) -> None:
    """通过自动分页批量添加subject的所有部门记录"""

    def create_paging_subject_departments(paging_data):
        """[分页]添加subject的所有部门记录"""
        url_path = "/api/v1/web/subject-departments"
        params = paging_data
        _call_iam_api(http_post, url_path, data=params)

    return execute_all_data_by_paging(create_paging_subject_departments, subject_departments, 1000)


def update_subject_departments_by_auto_paging(subject_departments: List[Dict]) -> None:
    """通过自动分页批量更新subject的所有部门记录"""

    def update_paging_subject_departments(paging_data):
        """[分页]更新subject的所有部门记录"""
        url_path = "/api/v1/web/subject-departments"
        params = paging_data
        _call_iam_api(http_put, url_path, data=params)

    return execute_all_data_by_paging(update_paging_subject_departments, subject_departments, 1000)


def delete_subject_departments_by_auto_paging(subjects: List[str]) -> None:
    """通过自动分页批量删除subject的所有部门记录"""

    def add_paging_subject_departments(paging_data):
        """[分页]删除subject的所有部门记录"""
        url_path = "/api/v1/web/subject-departments"
        params = paging_data
        _call_iam_api(http_delete, url_path, data=params)

    return execute_all_data_by_paging(add_paging_subject_departments, subjects, 1000)


def list_subject_member(_type: str, id: str, limit: int = 10, offset: int = 0) -> Dict:
    """
    获取subject的成员列表
    """
    url_path = "/api/v1/web/subject-members"
    params = {"type": _type, "id": id, "limit": limit, "offset": offset}
    return _call_iam_api(http_get, url_path, data=params)


def get_subject_relation(_type: str, id: str, expired_at: int = 0) -> List[Dict]:
    """
    获取subject的关系列表
    """
    url_path = "/api/v1/web/subject-relations"
    params = {"type": _type, "id": id, "before_expired_at": expired_at}
    return _call_iam_api(http_get, url_path, data=params)


def delete_subject_members(_type: str, id: str, members: List[dict]) -> Dict[str, int]:
    """
    批量删除subject的成员
    """
    url_path = "/api/v1/web/subject-members"
    params = {"type": _type, "id": id, "members": members}
    permission_logger.info("iam subject delete member url: %s, data: %s", url_path, params)
    return _call_iam_api(http_delete, url_path, data=params)


def delete_subject_members_by_auto_paging(_type: str, id: str, members: List[dict]) -> None:
    """通过自动分页批量删除subject的成员"""

    def delete_paging_subject_members(paging_data):
        """[分页]添加subject的成员"""
        url_path = "/api/v1/web/subject-members"
        params = {
            "type": _type,
            "id": id,
            "members": paging_data,
        }
        _call_iam_api(http_delete, url_path, data=params)

    return execute_all_data_by_paging(delete_paging_subject_members, members, 1000)


def add_subject_members(_type: str, id: str, policy_expired_at: int, members: List[dict]) -> Dict[str, int]:
    """
    批量添加subject的成员
    """
    url_path = "/api/v1/web/subject-members"
    params = {
        "type": _type,
        "id": id,
        "members": members,
        "policy_expired_at": policy_expired_at,
    }
    permission_logger.info("iam subject add member url: %s, data: %s", url_path, params)
    return _call_iam_api(http_post, url_path, data=params)


def add_subject_members_by_auto_paging(_type: str, id: str, policy_expired_at: int, members: List[dict]) -> None:
    """通过自动分页批量添加subject的成员"""

    def add_paging_subject_members(paging_data):
        """[分页]添加subject的成员"""
        url_path = "/api/v1/web/subject-members"
        params = {
            "type": _type,
            "id": id,
            "members": paging_data,
            "policy_expired_at": policy_expired_at,
        }
        _call_iam_api(http_post, url_path, data=params)

    return execute_all_data_by_paging(add_paging_subject_members, members, 1000)


def list_system_policy(system_id: str, subject_type: str, subject_id: str, template_id: int = 0) -> List[Dict]:
    """
    获取subject有权限的policy
    """
    url_path = f"/api/v1/web/systems/{system_id}/policies"
    params = {
        "subject_type": subject_type,
        "subject_id": subject_id,
        "template_id": template_id,
    }
    return _call_iam_api(http_get, url_path, data=params)


def alter_policies(
    system_id: str,
    subject_type: str,
    subject_id: str,
    create_policies: List[Dict],
    update_policies: List[Dict],
    delete_policy_ids: List[int],
) -> Dict:
    """
    变更权限

    create_policies: [{
        "action_id": "view_host",
        "resource_expression": "",
        "environment": "",
        "expired_at": 4102444800
    }]

    update_policies: [{
        "id": 1,
        "action_id": "edit_host",
        "resource_expression": "",
        "environment": "",
        "expired_at": 4102444800
    }]

    delete_policy_ids: [2, 3, 4]
    """
    url_path = f"/api/v1/web/systems/{system_id}/policies"
    data = {
        "subject": {"type": subject_type, "id": subject_id},
        "create_policies": create_policies,
        "update_policies": update_policies,
        "delete_policy_ids": delete_policy_ids,
    }
    permission_logger.info("iam alter policies url: %s, data: %s", url_path, data)
    result = _call_iam_api(http_post, url_path, data=data)
    # 发布订阅-删除策略
    publisher_shortcut.publish_delete_policies_by_id(delete_policy_ids)
    return result


def delete_policies(system_id: str, subject_type: str, subject_id: str, policy_ids: List[int]) -> None:
    """
    删除权限
    """
    url_path = "/api/v1/web/policies"
    data = {"system_id": system_id, "subject_type": subject_type, "subject_id": subject_id, "ids": policy_ids}
    permission_logger.info("iam delete policies url: %s, data: %s", url_path, data)
    result = _call_iam_api(http_delete, url_path, data=data)
    # 发布订阅-删除策略
    publisher_shortcut.publish_delete_policies_by_id(policy_ids)
    return result


def create_and_delete_template_policies(
    system_id: str,
    subject_type: str,
    subject_id: str,
    template_id: int,
    create_policies: List[Dict],
    delete_policy_ids: List[int],
) -> None:
    """
    创建/删除权限模板授权信息
    """
    url_path = "/api/v1/web/perm-templates/policies"
    data = {
        "subject": {"type": subject_type, "id": subject_id},
        "system_id": system_id,
        "template_id": template_id,
        "create_policies": create_policies,
        "delete_policy_ids": delete_policy_ids,
    }
    permission_logger.info("iam create and delete template policies url: %s, data: %s", url_path, data)
    result = _call_iam_api(http_post, url_path, data=data)
    # 发布订阅-删除策略
    publisher_shortcut.publish_delete_policies_by_id(delete_policy_ids)
    return result


def update_template_policies(
    system_id: str, subject_type: str, subject_id: str, template_id: int, update_policies: List[Dict]
) -> None:
    """
    更新权限模板授权信息
    """
    url_path = "/api/v1/web/perm-templates/policies"
    data = {
        "subject": {"type": subject_type, "id": subject_id},
        "system_id": system_id,
        "template_id": template_id,
        "update_policies": update_policies,
    }
    permission_logger.info("iam update template policies url: %s, data: %s", url_path, data)
    return _call_iam_api(http_put, url_path, data=data)


def delete_template_policies(system_id: str, subject_type: str, subject_id: str, template_id: int) -> None:
    """
    删除权限模板授权信息
    """
    url_path = "/api/v1/web/perm-templates/policies"
    data = {"system_id": system_id, "subject_type": subject_type, "subject_id": subject_id, "template_id": template_id}
    permission_logger.info("iam delete template policies url: %s, data: %s", url_path, data)
    result = _call_iam_api(http_delete, url_path, data=data)
    # 发布订阅-删除策略
    publisher_shortcut.publish_delete_policies_by_template_subject(template_id, subject_type, subject_id)
    return result


def create_subject_role(subjects: List[Dict[str, str]], role_type: str, system_id: str = "SUPER"):
    """
    创建后台的subject角色信息
    """
    url_path = "/api/v1/web/subject-roles"
    data = {"role_type": role_type, "system_id": system_id, "subjects": subjects}
    permission_logger.info("iam create subject role url: %s, data: %s", url_path, data)
    return _call_iam_api(http_post, url_path, data=data)


def delete_subject_role(subjects: List[Dict[str, str]], role_type: str, system_id: str = "SUPER"):
    """
    删除后台的subject角色信息
    """
    url_path = "/api/v1/web/subject-roles"
    data = {"role_type": role_type, "system_id": system_id, "subjects": subjects}
    permission_logger.info("iam delete subject role url: %s, data: %s", url_path, data)
    return _call_iam_api(http_delete, url_path, data=data)


def list_policy(subject_type: str, subject_id: str, expired_at: int) -> List[Dict]:
    """
    获取subject在指定过期时间前的policy列表
    """
    url_path = "/api/v1/web/policies"
    params = {
        "subject_type": subject_type,
        "subject_id": subject_id,
        "before_expired_at": expired_at,
    }
    return _call_iam_api(http_get, url_path, data=params)


def update_policy_expired_at(subject_type: str, subject_id: str, policies: List[Dict]) -> List[Dict]:
    """
    更新策略的过期时间
    """
    url_path = "/api/v1/web/policies/expired_at"
    data = {
        "subject_type": subject_type,
        "subject_id": subject_id,
        "policies": policies,
    }
    return _call_iam_api(http_put, url_path, data=data)


def update_subject_members_expired_at(_type: str, id: str, members: List[dict]) -> List[Dict]:
    """
    subject成员更新过期时间
    """
    url_path = "/api/v1/web/subject-members/expired_at"
    data = {
        "type": _type,
        "id": id,
        "members": members,
    }
    return _call_iam_api(http_put, url_path, data=data)


def list_subject_member_before_expired_at(
    subject_type: str, subject_id: str, expired_at: int, limit: int = 10, offset: int = 0
) -> Dict:
    """
    获取subject的成员列表
    """
    url_path = "/api/v1/web/subject-members/query"
    data = {"type": subject_type, "id": subject_id, "before_expired_at": expired_at, "limit": limit, "offset": offset}
    return _call_iam_api(http_get, url_path, data=data)


def list_exist_subjects_before_expired_at(subjects: List[Dict], expired_at: int) -> List:
    """
    查询已过期的subjects
    """
    url_path = "/api/v1/web/subjects/before_expired_at"
    data = {"subjects": subjects, "before_expired_at": expired_at}
    return _call_iam_api(http_post, url_path, data=data)


def list_model_change_event(status: str = "pending"):
    """查询模型变更事件
    status: pending/finished/空
    return: [{"pk", "type", "status", "system_id", "model_type", "model_id", "model_pk"}]
    """
    url_path = "/api/v1/web/model-change-event"
    data = {"status": status}
    return _call_iam_api(http_get, url_path, data=data)


def update_model_change_event(event_pk: int, status: str):
    """更新模型变更事件状态
    status: pending/finished/空
    """
    url_path = f"/api/v1/web/model-change-event/{event_pk}"
    data = {"status": status}
    return _call_iam_api(http_put, url_path, data=data)


def delete_action_policies(system_id: str, action_id: str):
    """删除Action的所有策略"""
    url_path = f"/api/v1/web/systems/{system_id}/actions/{action_id}/policies"
    return _call_iam_api(http_delete, url_path, data={})


def delete_action(system_id: str, action_id: str):
    """删除Action权限模型"""
    url_path = f"/api/v1/web/systems/{system_id}/actions/{action_id}"
    return _call_iam_api(http_delete, url_path, data={})


def delete_unquoted_expressions():
    """删除未被引用的expression"""
    url_path = "/api/v1/web/unquoted-expressions"
    return _call_iam_api(http_delete, url_path, data={})
