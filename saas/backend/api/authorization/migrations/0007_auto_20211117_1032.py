# Generated by Django 2.2.24 on 2021-11-17 02:32

from django.db import migrations

from backend.api.authorization.constants import (
    ALLOW_LIST_OBJECT_OPERATION_STEP,
    AllowListMatchOperationEnum,
    AuthorizationAPIEnum,
)


def add_allow_list(apps, schema_editor):
    """初始化授权API白名单"""
    AuthAPIAllowListConfig = apps.get_model("authorization", "AuthAPIAllowListConfig")
    # 查询已存在白名单，避免重复
    all_allow_list = AuthAPIAllowListConfig.objects.all()
    allow_set = set([(a.type, a.system_id, a.object_id) for a in all_allow_list])
    # 实例授权API 白名单
    system_actions = {
        "bk_cmdb": [
            "".join([AllowListMatchOperationEnum.STARTS_WITH.value, ALLOW_LIST_OBJECT_OPERATION_STEP, "create_comobj"]),
            "".join([AllowListMatchOperationEnum.STARTS_WITH.value, ALLOW_LIST_OBJECT_OPERATION_STEP, "edit_comobj"]),
            "".join([AllowListMatchOperationEnum.STARTS_WITH.value, ALLOW_LIST_OBJECT_OPERATION_STEP, "delete_comobj"]),
        ],
    }
    auth_api_allow_list_config = []
    for system_id, object_ids in system_actions.items():
        for object_id in object_ids:
            # 已存在，则直接忽略
            if (AuthorizationAPIEnum.AUTHORIZATION_INSTANCE.value, system_id, object_id) in allow_set:
                continue
            auth_api_allow_list_config.append(
                AuthAPIAllowListConfig(
                    type=AuthorizationAPIEnum.AUTHORIZATION_INSTANCE.value,
                    system_id=system_id,
                    object_id=object_id
                )
            )
    if len(auth_api_allow_list_config) != 0:
        AuthAPIAllowListConfig.objects.bulk_create(auth_api_allow_list_config)


class Migration(migrations.Migration):

    dependencies = [
        ('authorization', '0006_auto_20210826_1642'),
    ]

    operations = [
        migrations.RunPython(add_allow_list)
    ]
