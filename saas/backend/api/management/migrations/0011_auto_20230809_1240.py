# Generated by Django 3.2.16 on 2023-08-09 04:40

from django.db import migrations

from backend.api.constants import ALLOW_ANY


def init_allow_list(apps, schema_editor):
    """初始化授权API白名单"""
    ManagementAPIAllowListConfig = apps.get_model("management", "ManagementAPIAllowListConfig")

    # 查询已存在白名单，避免重复
    all_allow_list = ManagementAPIAllowListConfig.objects.all()
    allow_set = set([(a.system_id, a.api) for a in all_allow_list])

    # 白名单列表
    system_id_allow_apis = {
        "bk_monitorv3": [ALLOW_ANY],
        "bk_log_search": [ALLOW_ANY],
    }

    # 组装成Model对象
    mgmt_api_allow_list_config = []
    for system_id, apis in system_id_allow_apis.items():
        for api in apis:
            # 已存在，则直接忽略
            if (system_id, api) in allow_set:
                continue
            mgmt_api_allow_list_config.append(ManagementAPIAllowListConfig(system_id=system_id, api=api))
    # 批量创建
    if len(mgmt_api_allow_list_config) != 0:
        ManagementAPIAllowListConfig.objects.bulk_create(mgmt_api_allow_list_config)

    SystemAllowAuthSystem = apps.get_model("management", "SystemAllowAuthSystem")

    # 查询已存在白名单，避免重复
    all_allow_auth_list = SystemAllowAuthSystem.objects.all()
    allow_auth_set = set([(a.system_id, a.auth_system_id) for a in all_allow_auth_list])

    # 白名单列表
    system_id_allow_auth_apis = {
        "bk_paas3": ["bk_monitorv3", "bk_log_search"],
        "paasv3cli": ["bk_monitorv3", "bk_log_search"],
    }

    # 组装成Model对象
    mgmt_auth_allow_list_config = []
    for system_id, auth_system_ids in system_id_allow_auth_apis.items():
        for auth_system_id in auth_system_ids:
            if (system_id, auth_system_id) in allow_auth_set:
                continue
            mgmt_auth_allow_list_config.append(
                SystemAllowAuthSystem(system_id=system_id, auth_system_id=auth_system_id)
            )
    # 批量创建
    if len(mgmt_auth_allow_list_config) != 0:
        SystemAllowAuthSystem.objects.bulk_create(mgmt_auth_allow_list_config)


class Migration(migrations.Migration):

    dependencies = [
        ("management", "0010_auto_20230529_1709"),
    ]

    operations = [migrations.RunPython(init_allow_list)]
