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
# Generated by Django 2.2.14 on 2020-08-12 03:59

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AggregateAction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('system_id', models.CharField(max_length=32, verbose_name='系统ID')),
                ('_action_ids', models.TextField(db_column='action_ids', verbose_name='操作列表')),
                ('_aggregate_resource_type', models.TextField(db_column='aggregate_resource_type', verbose_name='操作列表')),
            ],
            options={
                'verbose_name': '聚合操作',
                'verbose_name_plural': '聚合操作',
                'index_together': {('system_id',)},
            },
        ),
    ]
