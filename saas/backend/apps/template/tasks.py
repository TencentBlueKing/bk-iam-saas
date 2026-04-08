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

from typing import Any, List

from backend.apps.template.models import PermTemplate, PermTemplatePolicyAuthorized
from backend.biz.template import TemplateBiz
from backend.long_task.constants import TaskType
from backend.long_task.tasks import StepTask, register_handler
from backend.service.constants import SubjectType
from backend.service.models import Subject


@register_handler(TaskType.TEMPLATE_UPDATE.value)
class TemplateUpdateTask(StepTask):
    """
    权限模板更新
    """

    def __init__(self, template_id: int):
        self.template_id = template_id
        self.tenant_id = PermTemplate.objects.only("tenant_id").get(id=self.template_id).tenant_id
        self.template_biz = TemplateBiz(self.tenant_id)

    def get_params(self) -> List[Any]:
        qs = PermTemplatePolicyAuthorized.objects.filter_by_template(self.template_id).only(
            "subject_type", "subject_id"
        )
        return [{"type": one.subject_type, "id": one.subject_id} for one in qs]

    def run(self, item: Any):
        subject = Subject.parse_obj(item)
        if subject.type == SubjectType.GROUP.value:
            # 同步单个 subject 的预提交的变更信息
            self.template_biz.sync_group_template_auth(int(subject.id), self.template_id)

    def on_success(self):
        # 结束同步，完成修改模板，删除预提交的相关信息
        self.template_biz.finish_template_update_sync(self.template_id)
