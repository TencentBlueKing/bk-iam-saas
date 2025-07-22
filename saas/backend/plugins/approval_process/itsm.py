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

import json
from typing import Dict, List

from django.conf import settings
from django.utils.translation import gettext as _

from backend.common.cache import cachedmethod
from backend.common.error_codes import error_codes
from backend.component.client.bk_itsm import BkITSMClient
from backend.service.constants import IAM_SUPPORT_PROCESSOR_TYPES, ApplicationType, ProcessorSource
from backend.service.models import ApprovalProcess, ApprovalProcessNode, ApprovalProcessWithNode
from backend.util.enum import ChoicesEnum

from .base import ApprovalProcessProvider


class DefaultProcessNameEnum(ChoicesEnum):
    """默认流程名称枚举"""

    DEFAULT = "超级管理员审批"
    GROUP = "超级管理员审批"


APPLICATION_TYPE_DEFAULT_PROCESS_DICT = {
    ApplicationType.GRANT_ACTION.value: DefaultProcessNameEnum.DEFAULT.value,  # type: ignore[attr-defined]
    ApplicationType.JOIN_GROUP.value: DefaultProcessNameEnum.GROUP.value,  # type: ignore[attr-defined]
}


class ITSMApprovalProcessProvider(ApprovalProcessProvider):
    """ITSM 提供审批流程"""

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.client = BkITSMClient(tenant_id=tenant_id)

    @cachedmethod(timeout=60)  # 缓存 1 分钟
    def _list(self, tenant_id: str) -> List[ApprovalProcess]:
        """查询审批流程列表，所有流程"""
        processes = self.client.list_process()
        return [ApprovalProcess(id=p["key"], name=p["name"]) for p in processes]

    def list(self) -> List[ApprovalProcess]:
        return self._list(tenant_id=self.tenant_id)

    @cachedmethod(timeout=60)  # 缓存 1 分钟
    def _list_with_nodes(self, tenant_id: str, application_type: ApplicationType) -> List[ApprovalProcessWithNode]:
        """审批流程列表，查询指定申请类型的流程列表，并附带流程节点
        1. 对于 ITSM, 不支持通过条件过滤出指定申请类型的，只能手动匹配
        2. 对于 ITSM，不支持查询流程时附带节点名称，所有都需要单独查询
        """
        processes = self.client.list_process()

        process_list = []
        # 遍历，并查询流程节点
        for p in processes:
            nodes = self.get_process_nodes(p["key"])
            process_list.append(ApprovalProcessWithNode(id=p["key"], name=p["name"], nodes=nodes))

        # 过滤出满足对应申请类型的流程
        return [p for p in process_list if p.is_match_application_type(application_type)]

    def list_with_nodes(self, application_type: ApplicationType) -> List[ApprovalProcessWithNode]:
        return self._list_with_nodes(tenant_id=self.tenant_id, application_type=application_type)

    def get_default_process(self, application_type: ApplicationType) -> ApprovalProcess:
        """获取某种申请类型的默认流程
        application_type 只需要实现两种，（1）加入用户组（2）申请自定义权限
        """
        processes = self.list()

        # 每种申请类型的默认流程名称
        default_process_name = APPLICATION_TYPE_DEFAULT_PROCESS_DICT.get(
            application_type,
            DefaultProcessNameEnum.DEFAULT.value,  # type: ignore[attr-defined]
        )

        # 遍历所有流程，找到对应默认流程
        for p in processes:
            if p.name == default_process_name:
                return p

        raise error_codes.INVALID_ARGS.format(_("ITSM 未内置 [{}]").format(default_process_name), True)

    def get_process_nodes(self, workflow_keys: str) -> List[ApprovalProcessNode]:
        """查询流程节点
        ITSM 将自动将除 IAM 角色以外的归为其他审批人类型，同时检查来源 IAM 的角色是否真的是 IAM 支持的
        """
        process_nodes = []
        nodes = self.client.get_process_nodes(workflow_keys)
        for node in nodes.values():
            # 转换为 IAM 规定的结构所需要流程处理者来源和类型
            if node["type"] != "APPROVE_TASK":
                continue
            source, _type = (
                ProcessorSource.OTHER.value,
                node["meta"]["processors"][0]["path"],
            )  # NOTE: other 的节点 iam 无需处理
            # activities 中的 type 判断是否为审批节点，类型为"APPROVE_TASK"可设置 source = ProcessorSource.IAM.value
            # meta 中的 processors 中的 path 可以对应 IAM_SUPPORT_PROCESSOR_TYPES 中的审批类型
            if node["type"] == "APPROVE_TASK":
                source = ProcessorSource.IAM.value
                # 对于来源于 IAM，需要检查角色是否满足
                if _type not in IAM_SUPPORT_PROCESSOR_TYPES:
                    raise error_codes.ITSM_PROCESSOR_NOT_SUPPORT.format(f"workflow_keys: {workflow_keys}, node:{node}")

            process_nodes.append(
                ApprovalProcessNode(id=node["key"], name=node["name"], processor_source=source, processor_type=_type)
            )

        return process_nodes

    def _load_workflow_template(self) -> Dict:
        system_id = settings.ITSM_SYSTEM_ID
        tenant_id = self.tenant_id

        # 读取工作流模板 JSON 文件内容
        with open(settings.ITSM_WORKERFLOW_TEMPLATE_FILE, "r") as f:
            workflow_template = json.load(f)

        # 替换系统 ID 和租户 ID
        workflow_template["system"]["name"] = system_id
        workflow_template["system"]["code"] = system_id
        # 必须保证表单模型是全局唯一的，这里使用 tenant_id 和 system_id 作为前缀
        workflow_template["key_mapping"]["form_models"] = {
            f"{tenant_id}__{system_id}__{k}": v for k, v in workflow_template["key_mapping"]["form_models"].items()
        }
        # 必须保证流程类型是全局唯一的，这里使用 tenant_id 和 system_id 作为前缀
        workflow_template["key_mapping"]["workflow_categories"] = {
            f"{tenant_id}__{system_id}__{k}": v
            for k, v in workflow_template["key_mapping"]["workflow_categories"].items()
        }
        # 必须保证流程是全局唯一的，这里使用 tenant_id 和 system_id 作为前缀
        workflow_template["key_mapping"]["workflows"] = {
            f"{tenant_id}__{system_id}__{k}": v for k, v in workflow_template["key_mapping"]["workflows"].items()
        }

        return workflow_template

    def create_workflow(self):
        """创建工作流程"""
        workflow_template = self._load_workflow_template()
        # 注册默认流程
        self.client.migrate_system(workflow_template)

    def get_default_workflow_key(self) -> List[str]:
        workflow_template = self._load_workflow_template()
        # 获取默认流程的 key
        return list(workflow_template["key_mapping"]["workflows"].keys())
