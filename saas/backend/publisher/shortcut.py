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
from typing import Dict, List

from .constants import DeletePolicyTypeEnum
from .tasks import publish_delete_policies


def publish_delete_policies_by_id(policy_ids: List[int]):
    if len(policy_ids) > 0:
        publish_delete_policies(DeletePolicyTypeEnum.POLICY.value, {"policy_ids": policy_ids})


def publish_delete_policies_by_subject(subjects: List[Dict]):
    """
    subjects: [{"type", "id"}, ...]
    """
    if len(subjects) > 0:
        publish_delete_policies(DeletePolicyTypeEnum.SUBJECT.value, {"subjects": subjects})


def publish_delete_policies_by_template_subject(template_id: int, subject_type: str, subject_id: str):
    publish_delete_policies(
        DeletePolicyTypeEnum.SUBJECT_TEMPLATE.value,
        {"subject_templates": [{"template_id": template_id, "subject": {"type": subject_type, "id": subject_id}}]},
    )
