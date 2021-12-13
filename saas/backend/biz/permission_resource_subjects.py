from backend.apps.template.models import PermTemplate, PermTemplatePolicyAuthorized
from backend.biz.group import GroupBiz
from backend.biz.subject import SubjectInfoList
from backend.service.engine import EngineService
from backend.service.models import Subject
from backend.apps.policy.models import Policy


class PermissionResourceSubjects(object):
    max_limit = 1000

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
        if self.limit > self.max_limit:
            raise Exception(f'最大查询数量不能超过{self.max_limit}条')
        # 系统+操作+资源实例
        if self.resource_instance:
            return self.query_subjects_by_resource_instance()
        # 系统+操作+模板权限
        if self.permission_type == "template":  # TODO 常量
            return self.query_subjects_by_template()
        # 系统+操作+自定义权限
        if self.permission_type == "custom":  # TODO 常量
            return self.query_subjects_by_custom()

    def query_subjects_by_custom(self):
        """
        根据系统和操作查询有自定义权限的成员
        实现思路：1. 根据系统和操作去Policy表中，查询关联的所有成员列表
        """
        policies = Policy.objects.filter(system_id=self.system_id, action_id=self.action_id)[0:self.limit]
        return self.__trans_subjects(policies)

    def query_subjects_by_template(self):
        """
        根据系统和操作查询模板关联的成员
        实现思路：1. 根据系统和操作去PermTemplate表中，查询关联的所有权限模板id
                2. 根据查询出来的权限模板id，去PermTemplatePolicyAuthorized表查询关联的用户组列表
        """
        query_action_id = f'"{self.action_id}"'
        template_ids = PermTemplate.objects.filter(
            system_id=self.system_id, _action_ids__contains=query_action_id
        ).values_list("id")
        policies = PermTemplatePolicyAuthorized.objects.filter(
            template_id__in=template_ids
        )[0:self.limit]
        return self.__trans_subjects(policies)

    @staticmethod
    def __trans_subjects(policies):
        subject_list = [
            Subject(type=policy.subject_type, id=policy.subject_id)
            for policy in policies
        ]
        subject_info_list = SubjectInfoList(subject_list)._to_subject_infos(subject_list)  # noqa
        return [{
            "name": subject_info.name,
            "type": subject_info.type,
            "id": subject_info.id
        } for subject_info in subject_info_list]

    def query_subjects_by_resource_instance(self):
        """
        根据系统和操作和资源实例查询有权限的成员
        实现思路: 1. 调用Engine后台，根据实例搜索有权限的成员
                2. 可以使用GroupBiz()._fill_resources_attribute填充实例的attribute参数
        """
        resource_instance_type = self.resource_instance["type"]
        resource_instance_id = self.resource_instance["id"]
        # 填充attribute
        resources = [{
            "system": self.system_id,
            "type": resource_instance_type,
            "id": resource_instance_id,
            "attribute": {}
        }]
        GroupBiz()._fill_resources_attribute(resources)  # noqa
        # 调用Engine后台API搜索
        query = [
            {
                "system": self.system_id,
                "subject_type": "all",  # TODO 常量
                "action": {
                    "id": self.action_id
                },
                "resources": resources,
                "limit": self.limit
            }
        ]
        return EngineService().query_subjects_by_resource_instance(query=query)
