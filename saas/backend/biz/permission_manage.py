from backend.apps.template.models import PermTemplate, PermTemplatePolicyAuthorized
from backend.biz.group import GroupBiz
from backend.biz.resource import ResourceBiz
from backend.biz.subject import SubjectInfoList
from backend.service.engine import EngineService
from backend.service.models import Subject
from backend.apps.policy.models import Policy


def list_subject_by_custom(system_id, action_id, limit):
    policys = Policy.objects.filter(system_id=system_id, action_id=action_id)[0: limit]
    results = []
    subject_list = []
    for policy in policys:
        subject_obj = Subject(type=policy.subject_type, id=policy.subject_id)
        subject_list.append(subject_obj)

    subject_info_list = SubjectInfoList(subject_list)._to_subject_infos(subject_list)

    for subject_info in subject_info_list:
        data = {
            "name": subject_info.name,
            "type": subject_info.type,
            "id": subject_info.id
        }
        results.append(data)
    return results


def list_subject_by_template(system_id, action_id, limit):
    action_id = '"' + action_id + '"'
    template_id = PermTemplate.objects.filter(
        system_id=system_id, _action_ids__contains=action_id).first().id

    perm_template_policys = PermTemplatePolicyAuthorized.objects.filter(template_id=template_id)[0: limit]
    subject_list = []
    results = []

    for perm_template_policy in perm_template_policys:
        subject_obj = Subject(type=perm_template_policy.subject_type, id=perm_template_policy.subject_id)
        subject_list.append(subject_obj)

    subject_info_list = SubjectInfoList(subject_list)._to_subject_infos(subject_list)

    for subject_info in subject_info_list:
        data = {
            "name": subject_info.name,
            "type": subject_info.type,
            "id": subject_info.id
        }
        results.append(data)

    return results


def list_subject_with_resource(system_id, action_id, resources, limit):
    resource_type = resources["type"]
    resource_id = resources["id"]
    query_data = []
    resources_info = {
        "system": system_id,
        "subject_type": "all",
        "action": {
            "id": action_id
        },
        "resources": [{
            "system": system_id,
            "type": resource_type,
            "id": resource_id,
            # "attribute": resource_attr
        }],
        "limit": limit
    }
    query_data.append(resources_info)

    resource_attr = GroupBiz()._fill_resources_attribute(resources_info["resources"])
    resources_info["resources"]["attribute"] == resource_attr

    results = EngineService().query_subjects_by_resources(query_data=query_data)
    return results

