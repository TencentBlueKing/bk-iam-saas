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
from io import BytesIO

import openpyxl
from openpyxl.styles import Font, colors

from backend.apps.policy.models import Policy
from backend.apps.role.constants import PermissionTypeEnum, SUBJECT_TYPE_DISPLAY_NAME
from backend.apps.template.models import PermTemplate, PermTemplatePolicyAuthorized
from backend.biz.subject import SubjectInfoList
from backend.common.resources_attribute_handler import fill_resources_attribute
from backend.component.iam import get_action, get_system
from backend.service.engine import EngineService
from backend.service.models import Subject


class SubjectsWithPermissionBiz(object):
    """
    权限管理-审计权限成员
    """

    engine_svc = EngineService()

    def __init__(self, data):
        self.system_id = data["system_id"]
        self.action_id = data["action_id"]
        self.resource_instance = data.get("resource_instance")
        self.permission_type = data["permission_type"]
        self.limit = data["limit"]

    def query_subjects_by_resource(self):
        """
        查询资源的权限成员
        @return subjects: [{
            "id": "admin",
            "type": "user",
            "name": "admin"
        }]
        """
        # 系统+操作+资源实例
        if self.resource_instance:
            return self.query_subjects_by_resource_instance()
        # 系统+操作+模板权限
        if self.permission_type == PermissionTypeEnum.TEMPLATE.value:
            return self.query_subjects_by_template()
        # 系统+操作+自定义权限
        if self.permission_type == PermissionTypeEnum.CUSTOM.value:
            return self.query_subjects_by_custom()

    def query_subjects_by_custom(self):
        """
        根据系统和操作查询有自定义权限的成员
        """
        policies = Policy.objects.filter(system_id=self.system_id, action_id=self.action_id)[0 : self.limit]
        return self._trans_subjects(policies)

    def query_subjects_by_template(self):
        """
        根据系统和操作查询模板关联的成员
        """
        template_ids = PermTemplate.objects.query_template_ids(system_id=self.system_id, action_id=self.action_id)
        policies = PermTemplatePolicyAuthorized.objects.filter(template_id__in=template_ids)[0:self.limit]
        return self._trans_subjects(policies)

    @staticmethod
    def _trans_subjects(policies):
        subject_list = [Subject(type=policy.subject_type, id=policy.subject_id) for policy in policies]
        subject_info_list = SubjectInfoList(subject_list)._to_subject_infos(subject_list)  # noqa
        return [
            {"name": subject_info.name, "type": subject_info.type, "id": subject_info.id}
            for subject_info in subject_info_list
        ]

    def query_subjects_by_resource_instance(self):
        """
        根据系统和操作和资源实例查询有权限的成员
        实现思路: 1. 调用Engine后台，根据实例搜索有权限的成员
                2. 可以使用GroupBiz()._fill_resources_attribute填充实例的attribute参数
        """
        resource_instance_type = self.resource_instance["type"]
        resource_instance_id = self.resource_instance["id"]
        # 填充attribute
        resources = [
            {"system": self.system_id, "type": resource_instance_type, "id": resource_instance_id, "attribute": {}}
        ]
        fill_resources_attribute(resources=resources)  # noqa
        # 调用Engine后台API搜索
        query_data = [
            {
                "system": self.system_id,
                "subject_type": "all",
                "action": {"id": self.action_id},
                "resource": resources,
                "limit": self.limit,
            }
        ]

        data = self.engine_svc.query_subjects_by_resource_instance(query_data=query_data)
        return data

    def _gen_export_data(self):
        """
        生成导出数据
        """
        system_name = get_system(self.system_id)["name"]
        action_name = get_action(self.system_id, self.action_id)["name"]
        subjects = self.query_subjects_by_resource()
        column_title = ["系统名", "操作名", "资源实例名称", "有权限成员", "成员类型"]
        export_data = [column_title]

        if self.resource_instance:  # 带资源实例信息查询
            for subject in subjects:
                export_msg = [
                    system_name,
                    action_name,
                    self.resource_instance["name"],
                    subject["name"],
                    SUBJECT_TYPE_DISPLAY_NAME[subject["type"]],
                ]
                export_data.append(export_msg)

        else:
            for subject in subjects:
                export_msg = [
                    system_name,
                    action_name,
                    "-",
                    subject["name"],
                    SUBJECT_TYPE_DISPLAY_NAME[subject["type"]],
                ]
                export_data.append(export_msg)

        return export_data

    def export(self):
        """
        将权限成员列表导出成excel
        """
        export_data = self._gen_export_data()

        work_book = openpyxl.Workbook()
        work_shell = work_book.active
        for row in export_data:
            work_shell.append(row)

        first_row_style = Font(bold=True, color=colors.COLOR_INDEX[2])

        for cell in work_shell["A1:E1"][0]:
            cell.font = first_row_style

        # 保存
        output = BytesIO()
        work_book.save(output)
        output.seek(0)

        return output
