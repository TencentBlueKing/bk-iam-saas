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
from django.http import StreamingHttpResponse
from openpyxl.styles import Font, colors

from backend.apps.policy.models import Policy
from backend.apps.role.constants import PermissionTypeEnum
from backend.apps.template.models import PermTemplate, PermTemplatePolicyAuthorized
from backend.biz.subject import SubjectInfoList
from backend.biz.utils import fill_resources_attribute
from backend.service.action import ActionService
from backend.service.constants import SubjectType
from backend.service.engine import EngineService
from backend.service.models import Subject
from backend.service.system import SystemService
from backend.service.utils.translate import translate_path


class QueryAuthorizedSubjects(object):
    """
    权限管理-审计权限成员
    """

    engine_svc = EngineService()

    def __init__(self, data):
        self.system_id = data["system_id"]
        self.action_id = data["action_id"]
        self.resource_instances = data.get("resource_instances")
        self.permission_type = data["permission_type"]
        self.limit = data["limit"]

    def query_by_permission_type(self):
        """
        查询资源的权限成员
        @return subjects: [{
            "id": "admin",
            "type": "user",
            "name": "admin"
        }]
        """
        # 系统+操作+资源实例
        if self.permission_type == PermissionTypeEnum.RESOURCE_INSTANCE.value:
            return self.query_by_resource_instance()
        # 系统+操作+模板权限
        if self.permission_type == PermissionTypeEnum.TEMPLATE.value:
            return self._query_subjects_by_template()
        # 系统+操作+自定义权限
        if self.permission_type == PermissionTypeEnum.CUSTOM.value:
            return self._query_by_custom()

    def _query_by_custom(self):
        """
        根据系统和操作查询有自定义权限的成员
        """
        policies = (
            Policy.objects.filter(system_id=self.system_id, action_id=self.action_id)
            .values("subject_id", "subject_type")
            .distinct()[0 : self.limit]
        )
        return self._trans_subjects(policies)

    def _query_subjects_by_template(self):
        """
        根据系统和操作查询模板关联的成员
        """
        template_ids = PermTemplate.objects.query_template_ids(system_id=self.system_id, action_id=self.action_id)
        policies = (
            PermTemplatePolicyAuthorized.objects.filter(template_id__in=template_ids)
            .values("subject_id", "subject_type")
            .distinct()[0 : self.limit]
        )

        return self._trans_subjects(policies)

    @staticmethod
    def _trans_subjects(policies):
        subject_list = [Subject(type=policy["subject_type"], id=policy["subject_id"]) for policy in policies]
        subject_info_list = SubjectInfoList(subject_list)._to_subject_infos(subject_list)
        return [
            {"name": subject_info.name, "type": subject_info.type, "id": subject_info.id}
            for subject_info in subject_info_list
        ]

    def query_by_resource_instance(self, subject_type: str = "all"):
        """
        根据系统和操作和资源实例查询有权限的成员
        """
        if self.resource_instances:
            resources = [
                {
                    "system": resource_instance["system_id"],
                    "type": resource_instance["type"],
                    "id": resource_instance["id"],
                    "attribute": {"_bk_iam_path_": translate_path(resource_instance["path"])}
                    if resource_instance.get("path")
                    else {},
                }
                for resource_instance in self.resource_instances
            ]
            # 填充attribute
            fill_resources_attribute(resources=resources)

        else:
            resources = []

        # 调用Engine后台API搜索
        query_data = {
            "system": self.system_id,
            "subject_type": subject_type,
            "action": {"id": self.action_id},
            "resource": resources,
            "limit": self.limit,
        }

        data = self.engine_svc.query_subjects_by_resource_instance(query_data=query_data)
        return data

    def _gen_resource_instance_info(self, resource_instances):
        """
        根据用户资源实例信息生成导出文件中资源实例列所需显示的数据：类型:名称(路径A/路径B/路径C)
        """
        resource_info_list = []
        for resource_instance in self.resource_instances:
            path_info = ""
            if resource_instance.get("path"):
                path_info = f"({'/'.join([path_info['name'] for path_info in resource_instance['path']])})"
            resource_info_list.append(f"{resource_instance['type']}：{resource_instance['name']}{path_info}")
        return "\n".join(resource_info_list)

    def _gen_export_data(self):
        """
        生成导出数据
        """
        system_name = SystemService().get(self.system_id).name
        action_name = ActionService().get(self.system_id, self.action_id).name
        subjects = self.query_by_permission_type()
        export_data = [["系统名", "系统ID", "操作名", "操作ID", "资源实例", "有权限成员", "成员ID", "成员类型"]]

        resource_instance_info = (
            self._gen_resource_instance_info(self.resource_instances) if self.resource_instances else "-"
        )
        export_data.extend(
            [
                [
                    system_name,
                    self.system_id,
                    action_name,
                    self.action_id,
                    resource_instance_info,
                    subject["name"],
                    subject["id"],
                    SubjectType.get_choice_label(subject["type"]),
                ]
                for subject in subjects
            ]
        )
        return export_data

    @staticmethod
    def _fill_export_data_style(work_shell):
        first_row_style = Font(bold=True, color=colors.COLOR_INDEX[2])
        for cell in work_shell["A1:H1"][0]:
            cell.font = first_row_style

    def export(self, filename: str):
        """
        将权限成员列表导出成excel
        """
        export_data = self._gen_export_data()
        work_book, work_shell = ExcelHandler().fill_work_shell(export_data)
        self._fill_export_data_style(work_shell)
        output = ExcelHandler().save_handled_work_book(work_book, filename)
        return output


class ExcelHandler(object):
    """
    excel处理
    """

    def fill_work_shell(self, export_data: list):
        """
        新建work_book，完成work_shell填充
        """
        work_book = openpyxl.Workbook()
        work_shell = work_book.active
        for row in export_data:
            work_shell.append(row)

        return work_book, work_shell

    def save_handled_work_book(self, work_book, filename):
        """
        处理完毕的work_book保存
        """
        output = BytesIO()
        work_book.save(output)
        output.seek(0)
        data = StreamingHttpResponse(output)
        data["Content-Type"] = "application/octet-stream"
        data["Content-Disposition"] = f'attachment;filename="{filename}.xlsx"'

        return data
