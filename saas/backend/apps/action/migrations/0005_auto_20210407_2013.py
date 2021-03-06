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
# Generated by Django 2.2.14 on 2021-04-07 12:13

import json

from django.db import migrations

from backend.util.json import json_dumps


def update_job_aggregate_action(apps, schema_editor):
    AggregateAction = apps.get_model("action", "AggregateAction")

    system_id = "bk_job"
    # 删除旧数据
    AggregateAction.objects.filter(system_id=system_id).delete()
    # 更新新数据
    agg_action = AggregateAction(
        system_id=system_id,
        _action_ids=json_dumps(
            [
                "access_business",
                "quick_execute_script",
                "quick_transfer_file",
                "execute_script",
                "create_script",
                "view_script",
                "manage_script",
                "create_job_template",
                "view_job_template",
                "edit_job_template",
                "delete_job_template",
                "debug_job_template",
                "launch_job_plan",
                "create_job_plan",
                "view_job_plan",
                "edit_job_plan",
                "delete_job_plan",
                "sync_job_plan",
                "create_tag",
                "manage_tag",
                "create_cron",
                "manage_cron",
                "view_history",
                "notification_setting",
                "create_account",
                "manage_account",
                "use_account",
                "view_file_source",
                "create_file_source",
                "manage_file_source",
            ]
        ),
        _aggregate_resource_type=json_dumps({"system_id": "bk_cmdb", "id": "biz"}),
    )
    agg_action.save()


class Migration(migrations.Migration):

    dependencies = [
        ("action", "0004_auto_20210324_1439"),
    ]

    operations = [
        migrations.RunPython(update_job_aggregate_action),
    ]
