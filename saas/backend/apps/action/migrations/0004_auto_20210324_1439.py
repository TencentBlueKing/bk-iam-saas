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
# Generated by Django 2.2.14 on 2021-03-24 06:39

import json

from django.db import migrations

from backend.util.json import json_dumps


def init_gsekit_aggregate_action(apps, schema_editor):
    AggregateAction = apps.get_model("action", "AggregateAction")
    agg_action = AggregateAction(
        system_id="bk_gsekit",
        _action_ids=json_dumps(
            [
                "view_business",
                "manage_process",
                "create_config_template",
                "edit_config_template",
                "delete_config_template",
                "generate_config",
                "release_config",
                "operate_config",
            ]
        ),
        _aggregate_resource_type=json_dumps({"system_id": "bk_cmdb", "id": "biz"}),
    )
    agg_action.save()


class Migration(migrations.Migration):

    dependencies = [
        ("action", "0003_auto_20201009_1216"),
    ]

    operations = [
        migrations.RunPython(init_gsekit_aggregate_action),
    ]
